# Stable TypeScript 7 + Bun + TanStack Start + tsrs WASM — isolated workbench

## Original consumers and compiler identity

- Existing React/TanStack Start preview remains `apps/loop-workbench`, separate from medium-compiler's original Python static builder and its Cloudflare Workers routes.
- **Official TypeScript stable 7.0.2** via `@typescript/native: npm:typescript@7.0.2`: the native **Go** compiler providing the project's `tsc --noEmit` Typecheck.
- **Compatibility JS Compiler API** via `typescript: npm:@typescript/typescript6@6.0.2`: original `aifs-code-intel.mjs` imports TypeScript AST through this API; native TS7 provides no equivalent JavaScript API. Do not replace it without an independent parser/consumer migration.
- **Bun** is installed on CI for an alternate runtime, `bun check`, and Bun-driven Node-compatible tests. The CI run generated an exact npm `package-lock.json` containing 190 resolved packages; its original bytes were committed, then the workflow was restored to `npm ci --ignore-scripts`. This is an npm-frozen install (not a `bun.lock` or Bun package-manager claim). Bun itself is a secondary runner and is not the package manager.
- **tsrs Rust/WebAssembly** `@tsrs/wasm@0.18.0-ts7.1.0-dev.20260929` has an isolated in-memory TypeScript 7.1-dev diagnostic smoke, NOT a drop-in TypeScript 7.0 stable compiler and not a browser Typed Code Explorer. WASI Preview 1, in-memory files and single-threaded; Node/Bun use different worker stack behavior. No Host, credential, provider or raw checkout exposed to arbitrary snippets.

## Verification and stop

[Latest source/Browser/tsrs control run 39590649274](https://github.com/ed3c/medium-compiler/actions/runs/39590649274) completed SUCCESS, exercising native TypeScript7 CLI, Bun 1.4.3 checker, Bun node:test-compatible runner, TypeScript6 JS AST and Rust tsrs WASM positive/negative tests, with the original isolated Chromium routes. The original TypeScript 7 stable `tsc` must pass before any parity claim. Bun `check` uses a bundled TypeScript 7 implementation potentially different from the 7.0.2 CLI; record its actual version and compare selected diagnostics before claiming equal results. The Rust `tsrs` input is version 7.1 development; a 7.0 vs 7.1 difference is **not** a tsrs regression. Correct parity requires matching source revision of tsgo and tsrs and original Consumer-observable Diagnostic Oracle. This project's tiny in-memory smoke only proves tsrs actually executed and returned an error code and a valid neighbor, not full parity or product admission.

CI should run source pin/rights controls, TS7 `tsc`, TS6 AST Code-intel, Bun check, Vite build, selected Chromium Browser tests, and tsrs WASM positive/negative controls. Any missing browser permission/resource remains UNKNOWN; do not silently downgrade to Source-only PASS. No native Agent acceptance, Soodles Manager effect, Noodle Host upgrade, Production deployment or PR merge is inferred.

Official sources:
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- https://bun.com/docs/runtime/check
- https://tanstack.com/start/latest/docs/framework/react/guide/hosting
- https://github.com/oxc-project/tsrs/blob/main/npm/tsrs-wasm/README.md
- https://github.com/oxc-project/tsrs/blob/main/docs/COMPATIBILITY.md
