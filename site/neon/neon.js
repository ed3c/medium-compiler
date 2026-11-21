import {VisitAttribution} from "./visit_attribution.mjs";

export class EeonForm {
  static FIELD = {
    invalid_name: "caller",
    invalid_email: "email",
    invalid_detail: "detail",
    invalid_consent: "consent",
    invalid_type: "type-short",
  };

  static bind(documentRef, storage, locationRef) {
    const brand = documentRef.querySelector("[data-brand]");
    const brandName = brand ? brand.textContent.trim() : "";
    if (brandName) documentRef.title = `${brandName} — ${documentRef.title}`;
    const form = documentRef.querySelector("#proposal");
    if (!form) return;
    VisitAttribution.apply(form, VisitAttribution.remember(storage, locationRef.search));
    form.addEventListener("change", event => EeonForm.clearTypeError(form, event));
    form.addEventListener("submit", event => {
      EeonForm.submit(event, form, storage);
    });
  }

  static async submit(event, form, storage) {
    event.preventDefault();
    const status = form.querySelector("#proposal-status");
    if (!form.reportValidity()) return;
    if (!EeonForm.requireType(form, status)) return;
    const button = form.querySelector("[type=submit]");
    button.disabled = true;
    if (status) status.textContent = "";
    try {
      const response = await fetch(form.action, {method: "POST", body: new URLSearchParams(new FormData(form))});
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok !== true) {
        EeonForm.fail(form, status, payload.error);
        button.disabled = false;
        return;
      }
      if (status) status.textContent = "已收到你的提案。我們會用這封 email 回覆。";
      form.reset();
      VisitAttribution.apply(form, VisitAttribution.recall(storage));
    } catch {
      EeonForm.fail(form, status, "");
      button.disabled = false;
    }
  }

  static requireType(form, status) {
    const chosen = [...form.querySelectorAll('input[name="type"]')].some(input => input.checked);
    const group = form.querySelector("#types");
    if (chosen) {
      if (group) group.removeAttribute("aria-invalid");
      return true;
    }
    if (group) group.setAttribute("aria-invalid", "true");
    if (status) status.textContent = "請至少選一種類型。";
    form.querySelector("#type-short")?.focus();
    return false;
  }

  static clearTypeError(form, event) {
    if (!event.target || event.target.name !== "type" || !event.target.checked) return;
    form.querySelector("#types")?.removeAttribute("aria-invalid");
    const status = form.querySelector("#proposal-status");
    if (status && status.textContent === "請至少選一種類型。") status.textContent = "";
  }

  static fail(form, status, code) {
    if (status) status.textContent = EeonForm.message(code);
    const fieldId = EeonForm.FIELD[code];
    if (fieldId) form.querySelector(`#${fieldId}`)?.focus();
  }

  static message(code) {
    if (code === "invalid_name") return "請填寫稱呼。";
    if (code === "invalid_email") return "請填寫有效的 email，例如 you@example.com。";
    if (code === "invalid_detail") return "請寫下這次想做的內容。";
    if (code === "invalid_consent") return "請勾選同意後再送出。";
    if (code === "invalid_type") return "請至少選一種類型。";
    return "送出失敗，請稍後再試。";
  }
}

if (globalThis.document && globalThis.sessionStorage && globalThis.location) {
  EeonForm.bind(globalThis.document, globalThis.sessionStorage, globalThis.location);
}
