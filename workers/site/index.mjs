import {transcripts} from "./transcripts.mjs";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/transcripts") {
      if (request.method !== "GET") return Response.json({error: "Method not allowed"}, {
        status: 405, headers: {Allow: "GET", "Cache-Control": "no-store"}
      });
      return transcripts(url);
    }
    if (url.pathname.startsWith("/api/"))
      return Response.json({error: "Unknown API route"}, {status: 404, headers: {"Cache-Control": "no-store"}});
    return env.ASSETS.fetch(request);
  }
};
