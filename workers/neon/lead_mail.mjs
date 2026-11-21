// Copies a stored lead to the owner inbox. A failed send does not remove the KV row.
export class LeadMail {
  static TO = "ga874199@gmail.com";
  static FROM = "EEON <onboarding@resend.dev>";
  static ENDPOINT = "https://api.resend.com/emails";
  static SECRET = "RESEND_API_KEY";
  static TIMEOUT_MS = 5000;
  static fetch = globalThis.fetch.bind(globalThis);

  static async notify(env, record) {
    const key = env?.[LeadMail.SECRET];
    if (typeof key !== "string" || key.length === 0) return {sent: false, reason: "missing_secret"};
    try {
      const response = await LeadMail.fetch(LeadMail.ENDPOINT, {
        method: "POST",
        headers: {Authorization: `Bearer ${key}`, "Content-Type": "application/json"},
        body: JSON.stringify(LeadMail.message(record)),
        signal: AbortSignal.timeout(LeadMail.TIMEOUT_MS),
      });
      if (!response.ok) return {sent: false, reason: "provider_refused"};
      return {sent: true};
    } catch {
      return {sent: false, reason: "network"};
    }
  }

  static message(record) {
    return {
      from: LeadMail.FROM,
      to: [LeadMail.TO],
      reply_to: LeadMail.singleLine(record.email),
      subject: `EEON 免費創意提案 ${LeadMail.singleLine(record.name)}`.trim(),
      text: LeadMail.body(record),
    };
  }

  static body(record) {
    const types = Array.isArray(record.types) ? record.types.map(item => LeadMail.singleLine(item)).join("、") : "";
    return [
      `稱呼: ${LeadMail.singleLine(record.name)}`,
      `Email: ${LeadMail.singleLine(record.email)}`,
      `類型: ${types}`,
      "說明:",
      String(record.detail ?? ""),
      "",
      `utm_source: ${record.utm_source ?? ""}`,
      `utm_medium: ${record.utm_medium ?? ""}`,
      `utm_campaign: ${record.utm_campaign ?? ""}`,
      `utm_content: ${record.utm_content ?? ""}`,
      `utm_term: ${record.utm_term ?? ""}`,
      `id: ${record.id ?? ""}`,
      `received_at: ${record.received_at ?? ""}`,
    ].join("\n");
  }

  static singleLine(value) {
    return String(value ?? "").replace(/[\r\n]+/g, " ").trim();
  }
}
