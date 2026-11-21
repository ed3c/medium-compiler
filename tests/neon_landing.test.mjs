import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {ProposalLead} from "../workers/neon/index.mjs";
import {LeadMail} from "../workers/neon/lead_mail.mjs";
import {VisitAttribution} from "../site/neon/visit_attribution.mjs";

const html = readFileSync(new URL("../site/neon/index.html", import.meta.url), "utf8");

function store() {
  const rows = new Map();
  return {rows, async put(key, value) { rows.set(key, value); }};
}

function envWith(leads = store()) {
  return {LEADS: leads, ASSETS: {fetch: async () => new Response("asset", {status: 200})}};
}

function post(fields, {path = "/api/proposal", method = "POST", contentType = "application/x-www-form-urlencoded"} = {}) {
  const body = new URLSearchParams();
  for (const [key, value] of Object.entries(fields)) {
    const values = Array.isArray(value) ? value : [value];
    for (const item of values) body.append(key, item);
  }
  return new Request(`https://neon.test${path}`, {method, headers: {"Content-Type": contentType}, body});
}

const valid = {
  name: "阿明",
  email: "ming@example.com",
  type: ["短影音", "圖片"],
  detail: "一支 15 秒的產品短影音。",
  consent: "yes",
  utm_source: "x",
  utm_medium: "social",
  utm_campaign: "neon-launch",
  utm_content: "bio",
  utm_term: "short-video",
};

test("valid proposal stores the lead and the five utm values", async () => {
  const leads = store();
  const response = await ProposalLead.respond(post(valid), envWith(leads));
  assert.equal(response.status, 201);
  assert.equal(response.headers.get("cache-control"), "no-store");
  const payload = await response.json();
  assert.equal(payload.ok, true);
  assert.equal(leads.rows.size, 1);
  const [key, raw] = [...leads.rows.entries()][0];
  assert.match(key, new RegExp(`^proposal/\\d{4}-\\d{2}-\\d{2}/${payload.id}$`));
  const record = JSON.parse(raw);
  assert.equal(record.name, "阿明");
  assert.equal(record.email, "ming@example.com");
  assert.deepEqual(record.types, ["短影音", "圖片"]);
  assert.equal(record.detail, "一支 15 秒的產品短影音。");
  assert.equal(record.consent, "yes");
  assert.equal(record.utm_source, "x");
  assert.equal(record.utm_medium, "social");
  assert.equal(record.utm_campaign, "neon-launch");
  assert.equal(record.utm_content, "bio");
  assert.equal(record.utm_term, "short-video");
  assert.equal(record.extra, undefined);
});

test("validation rejects empty, illegal, and unknown type values before any write", async () => {
  const cases = [
    [{...valid, name: "  "}, "invalid_name"],
    [{...valid, email: "not-an-email"}, "invalid_email"],
    [{...valid, type: []}, "invalid_type"],
    [{...valid, type: ["其他"]}, "invalid_type"],
    [{...valid, detail: ""}, "invalid_detail"],
    [{...valid, detail: "x".repeat(ProposalLead.LIMIT.detail + 1)}, "invalid_detail"],
    [{...valid, consent: ""}, "invalid_consent"],
  ];
  for (const [fields, code] of cases) {
    const leads = store();
    const response = await ProposalLead.respond(post(fields), envWith(leads));
    assert.equal(response.status, 400, code);
    assert.deepEqual(await response.json(), {error: code});
    assert.equal(leads.rows.size, 0, code);
  }
});

test("honeypot accepts the request and writes nothing", async () => {
  const leads = store();
  const response = await ProposalLead.respond(post({...valid, company_website: "https://spam.example"}), envWith(leads));
  assert.equal(response.status, 201);
  assert.deepEqual(await response.json(), {ok: true});
  assert.equal(leads.rows.size, 0);
});

test("utm values are clipped to the worker limit and unknown fields are dropped", async () => {
  const leads = store();
  const long = `${"a".repeat(ProposalLead.LIMIT.utm - 1)}😀z`;
  const response = await ProposalLead.respond(post({...valid, utm_source: long, utm_campaign: "  launch  ", admin: "true"}), envWith(leads));
  assert.equal(response.status, 201);
  const record = JSON.parse([...leads.rows.values()][0]);
  assert.equal([...record.utm_source].length, ProposalLead.LIMIT.utm);
  assert.equal(record.utm_source, `${"a".repeat(ProposalLead.LIMIT.utm - 1)}😀`);
  assert.equal(record.utm_campaign, "launch");
  assert.equal(record.admin, undefined);
  assert.equal(Object.hasOwn(record, "company_website"), false);
});

test("other api routes 404 and a non-post proposal is refused", async () => {
  const env = envWith();
  assert.equal((await ProposalLead.respond(new Request("https://neon.test/api/leads"), env)).status, 404);
  assert.equal((await ProposalLead.respond(new Request("https://neon.test/api/proposal"), env)).status, 405);
  const asset = await ProposalLead.respond(new Request("https://neon.test/"), env);
  assert.equal(asset.status, 200);
  assert.equal(await asset.text(), "asset");
});

test("a later utm link replaces the tab set and a bare visit keeps it", () => {
  const storage = new Map();
  const memory = {getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value)};
  const first = VisitAttribution.remember(memory, "?utm_source=instagram&utm_medium=bio");
  assert.equal(first.utm_source, "instagram");
  assert.equal(first.utm_campaign, "");
  const second = VisitAttribution.remember(memory, "?utm_source=tiktok&utm_term=ad");
  assert.equal(second.utm_source, "tiktok");
  assert.equal(second.utm_medium, "");
  assert.equal(second.utm_term, "ad");
  const kept = VisitAttribution.remember(memory, "");
  assert.equal(kept.utm_source, "tiktok");
  assert.equal(kept.utm_term, "ad");
  assert.deepEqual(VisitAttribution.KEYS, ProposalLead.UTM_KEYS);
});

function mailSpy({status = 200, fail = false} = {}) {
  const calls = [];
  const impl = async (url, init) => {
    calls.push({url, init});
    if (fail) throw new Error("mail down");
    return new Response("{}", {status});
  };
  return {calls, impl};
}

async function withMail(impl, run) {
  const previous = LeadMail.fetch;
  LeadMail.fetch = impl;
  try {
    return await run();
  } finally {
    LeadMail.fetch = previous;
  }
}

test("mail failure still returns 201 and keeps the kv lead", async () => {
  for (const mode of ["refused", "network"]) {
    const leads = store();
    const spy = mailSpy({status: 500, fail: mode === "network"});
    const response = await withMail(spy.impl, () => ProposalLead.respond(post(valid), {
      ...envWith(leads),
      [LeadMail.SECRET]: "re_test_secret",
    }));
    assert.equal(response.status, 201, mode);
    assert.equal((await response.json()).ok, true, mode);
    assert.equal(leads.rows.size, 1, mode);
    assert.equal(spy.calls.length, 1, mode);
  }
});

test("a successful mail copy sends the lead and utm values without the secret", async () => {
  const leads = store();
  const spy = mailSpy();
  await withMail(spy.impl, () => ProposalLead.respond(post(valid), {
    ...envWith(leads),
    [LeadMail.SECRET]: "re_test_secret",
  }));
  assert.equal(spy.calls.length, 1);
  assert.equal(spy.calls[0].url, LeadMail.ENDPOINT);
  assert.equal(spy.calls[0].init.headers.Authorization, "Bearer re_test_secret");
  const message = JSON.parse(spy.calls[0].init.body);
  assert.equal(message.from, LeadMail.FROM);
  assert.deepEqual(message.to, [LeadMail.TO]);
  assert.equal(message.reply_to, "ming@example.com");
  assert.match(message.subject, /^EEON 免費創意提案 阿明$/);
  assert.match(message.text, /utm_source: x/);
  assert.match(message.text, /utm_term: short-video/);
  assert.equal(JSON.stringify(message).includes("re_test_secret"), false);
});

test("missing secret, honeypot, and invalid leads do not send mail", async () => {
  const spy = mailSpy();
  await withMail(spy.impl, async () => {
    const stored = store();
    const response = await ProposalLead.respond(post(valid), envWith(stored));
    assert.equal(response.status, 201);
    assert.equal(stored.rows.size, 1);
    const honeypot = store();
    await ProposalLead.respond(post({...valid, company_website: "https://spam.example"}), {
      ...envWith(honeypot),
      [LeadMail.SECRET]: "re_test_secret",
    });
    assert.equal(honeypot.rows.size, 0);
    const invalid = store();
    const rejected = await ProposalLead.respond(post({...valid, email: "nope"}), {
      ...envWith(invalid),
      [LeadMail.SECRET]: "re_test_secret",
    });
    assert.equal(rejected.status, 400);
    assert.equal(invalid.rows.size, 0);
  });
  assert.equal(spy.calls.length, 0);
});

test("the page keeps one brand string and the worker field limits", () => {
  assert.equal(html.match(/EEON/g)?.length, 1);
  assert.equal(html.match(/Neon/g), null);
  assert.match(html, /data-brand>EEON</);
  assert.match(html, new RegExp(`maxlength="${ProposalLead.LIMIT.name}"`));
  assert.match(html, new RegExp(`maxlength="${ProposalLead.LIMIT.email}"`));
  assert.match(html, new RegExp(`maxlength="${ProposalLead.LIMIT.detail}"`));
  assert.match(html, /id="consent"[^>]*required/);
  assert.match(html, /name="company_website"/);
  for (const key of ProposalLead.UTM_KEYS) assert.match(html, new RegExp(`name="${key}"`));
});
