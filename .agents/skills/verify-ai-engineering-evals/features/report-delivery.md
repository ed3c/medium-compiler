# Read the published report

## Sub-features

Render the report, expose source scope and limits, retain downloadable JSON and provenance.

## How to get to it (user POV)

Homepage → AI Evals → Soodles report. Direct route: `/ai-evals/soodles-claim-refusal/`.

## Driving it with site builder, HTTP and browser

Run the site builder into a new task-owned output. Serve it with a task-owned HTTP server. Read `/ai-evals/`, `/ai-evals/soodles-claim-refusal/`, the report JSON and `/provenance.json`. Click the AI Evals navigation and the report card in a browser. Check visible English assessment, Chinese guide, evidence limits, and source links. For publication, read back the existing Git deployment and public domain with matching report hashes. Stop only the owned server and retain evidence.

## Gotchas

Check visible subject revision, reviewer and calibration scope. Expand pinned sources.
Retrieve the source manifest, English assessment and supplementary attachments as well
as report JSON; compare the delivered bytes with their bound source hashes. Inspect a
concrete engineering finding in the rendered page: its mechanism, code/trace locator and
tradeoff must survive rendering. Historical reports retain the scope of their own review;
a skill update does not retroactively revalidate or enrich them.

Build success is not deployed delivery. Preview is not production. Source hashes do not certify meaning. Never display old model reports as fresh executions or convert unknown dimensions to PASS.
