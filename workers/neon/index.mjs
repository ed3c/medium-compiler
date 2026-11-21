import {LeadMail} from "./lead_mail.mjs";

// Public lead intake for the EEON landing Worker. Static assets serve every other route.

export class ProposalLead {
  static TYPES = ["短影音", "產品廣告", "圖片"];
  static UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
  static LIMIT = {name: 80, email: 254, detail: 2000, utm: 120};
  static HONEYPOT = "company_website";
  static CONSENT = "yes";
  static MAX_BODY = 16 * 1024;
  static EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/u;

  static respond(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/proposal") return ProposalLead.accept(request, env);
    if (url.pathname.startsWith("/api/")) return ProposalLead.json({error: "unknown_route"}, 404);
    return env.ASSETS.fetch(request);
  }

  static async accept(request, env) {
    if (request.method !== "POST") {
      return ProposalLead.json({error: "method_not_allowed"}, 405, {Allow: "POST"});
    }
    const media = (request.headers.get("content-type") ?? "").split(";")[0].trim().toLowerCase();
    if (media !== "application/x-www-form-urlencoded" && media !== "multipart/form-data") {
      return ProposalLead.json({error: "unsupported_media"}, 415);
    }
    const length = Number(request.headers.get("content-length") ?? "0");
    if (request.headers.has("content-length") && (!Number.isFinite(length) || length > ProposalLead.MAX_BODY)) {
      return ProposalLead.json({error: "body_too_large"}, 413);
    }
    let form;
    try {
      form = await request.formData();
    } catch {
      return ProposalLead.json({error: "invalid_body"}, 400);
    }
    if (ProposalLead.honeypotTripped(form)) return ProposalLead.json({ok: true}, 201);
    const parsed = ProposalLead.parse(form);
    if (parsed.error) return ProposalLead.json({error: parsed.error}, 400);
    const id = crypto.randomUUID();
    const receivedAt = new Date().toISOString();
    const record = {id, received_at: receivedAt, ...parsed.lead};
    try {
      await env.LEADS.put(ProposalLead.storageKey(id, receivedAt), JSON.stringify(record));
    } catch {
      return ProposalLead.json({error: "store_unavailable"}, 503);
    }
    try {
      await LeadMail.notify(env, record);
    } catch {
      // KV already holds the lead. Mail is a copy.
    }
    return ProposalLead.json({ok: true, id}, 201);
  }

  static honeypotTripped(form) {
    return form.getAll(ProposalLead.HONEYPOT).some(value => String(value).trim() !== "");
  }

  static parse(form) {
    const name = ProposalLead.text(form, "name", ProposalLead.LIMIT.name, false);
    if (name.error) return name;
    const email = ProposalLead.email(form);
    if (email.error) return email;
    const types = ProposalLead.types(form);
    if (types.error) return types;
    const detail = ProposalLead.text(form, "detail", ProposalLead.LIMIT.detail, true);
    if (detail.error) return detail;
    if (form.get("consent") !== ProposalLead.CONSENT) return {error: "invalid_consent"};
    return {lead: {name: name.value, email: email.value, types: types.value, detail: detail.value, consent: ProposalLead.CONSENT, ...ProposalLead.utm(form)}};
  }

  static text(form, field, limit, newlines) {
    const raw = form.get(field);
    if (typeof raw !== "string") return {error: `invalid_${field}`};
    const value = raw.trim();
    if (value.length === 0 || [...value].length > limit) return {error: `invalid_${field}`};
    if ([...value].some(char => ProposalLead.isForbidden(char, newlines))) return {error: `invalid_${field}`};
    return {value};
  }

  static email(form) {
    const raw = form.get("email");
    if (typeof raw !== "string") return {error: "invalid_email"};
    const value = raw.trim();
    if (value.length === 0 || value.length > ProposalLead.LIMIT.email || !ProposalLead.EMAIL.test(value)) {
      return {error: "invalid_email"};
    }
    return {value};
  }

  static types(form) {
    const unique = [];
    for (const value of form.getAll("type")) {
      if (typeof value !== "string" || !ProposalLead.TYPES.includes(value)) return {error: "invalid_type"};
      if (!unique.includes(value)) unique.push(value);
    }
    if (unique.length === 0) return {error: "invalid_type"};
    return {value: unique};
  }

  static utm(form) {
    const record = {};
    for (const key of ProposalLead.UTM_KEYS) {
      const raw = form.get(key);
      record[key] = typeof raw === "string" ? ProposalLead.clip(raw, ProposalLead.LIMIT.utm) : "";
    }
    return record;
  }

  static clip(value, limit) {
    return [...value.trim()].slice(0, limit).join("");
  }

  static isForbidden(char, newlines) {
    const code = char.codePointAt(0);
    if (newlines && (code === 9 || code === 10 || code === 13)) return false;
    return code < 32 || code === 127;
  }

  static storageKey(id, receivedAt) {
    return `proposal/${receivedAt.slice(0, 10)}/${id}`;
  }

  static json(body, status, headers = {}) {
    return Response.json(body, {status, headers: {"Cache-Control": "no-store", ...headers}});
  }
}

export default {
  fetch(request, env) {
    return ProposalLead.respond(request, env);
  },
};
