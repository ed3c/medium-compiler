// Last-click UTM for the current tab. A link that carries any utm_* key replaces the set.
export class VisitAttribution {
  static KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
  static STORAGE_KEY = "eeon-utm";

  static remember(storage, search) {
    const incoming = VisitAttribution.fromSearch(search);
    if (incoming) {
      storage.setItem(VisitAttribution.STORAGE_KEY, JSON.stringify(incoming));
      return incoming;
    }
    return VisitAttribution.recall(storage);
  }

  static fromSearch(search) {
    const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
    const record = VisitAttribution.empty();
    let found = false;
    for (const key of VisitAttribution.KEYS) {
      const value = params.get(key);
      if (value) {
        record[key] = value;
        found = true;
      }
    }
    return found ? record : null;
  }

  static recall(storage) {
    const raw = storage.getItem(VisitAttribution.STORAGE_KEY);
    if (!raw) return VisitAttribution.empty();
    try {
      const parsed = JSON.parse(raw);
      const record = VisitAttribution.empty();
      for (const key of VisitAttribution.KEYS) {
        if (typeof parsed[key] === "string") record[key] = parsed[key];
      }
      return record;
    } catch {
      return VisitAttribution.empty();
    }
  }

  static apply(form, record) {
    for (const key of VisitAttribution.KEYS) {
      const field = form.elements.namedItem(key);
      if (field && "value" in field) field.value = record[key] ?? "";
    }
  }

  static empty() {
    return Object.fromEntries(VisitAttribution.KEYS.map(key => [key, ""]));
  }
}
