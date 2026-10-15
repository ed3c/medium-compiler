# Public Loop graph snapshots

The existing `scripts/import_loop_snapshot.py` accepts v1 and v2 snapshots.
Import does not deploy. The publisher reviews disclosure before import.
The importer checks known private path and credential patterns. This check cannot
certify that every free-text field is safe to publish.

V1 retains its recorded timeline. It does not acquire causal edges.
V2 uses the original Loop display contract in `contracts/loop-view-v2.schema.json`
and the unchanged portable validator in `scripts/loop_graph_contract.py`.
The public importer additionally validates every graph string and rejects original
`content`, private paths, raw-trace content, and public content with a wrong digest.
It requires reviewed `public_content`, `public_sha256`, and `public_bytes` for
public artifact text. Each artifact is limited to 2 MiB; each snapshot to 32 MiB.
Snapshot file symlinks are refused.

The original `source` identity remains separate from the reviewed public text.
Its path must be a redacted label. Its original digest is not replaced by the
public digest. A `not_public` artifact has no public content. An observed historical
handoff can retain private evidence identity without disclosing its bytes.

The builder extracts public content into content-addressed text files under
`assets/loop-data/<snapshot digest>/artifacts/`. The browser fetches only this
static origin and verifies each public digest before displaying text. Graph data
contains no duplicated artifact bodies. Cards and notes load from static collection
files when their pages are opened. The browser does not contact a local Host,
execute an original next, interpret HTML, or invoke a port.

The source index preserves Git revision, selected workspace entries, index status,
and gaps. Index metadata alone does not grant content access. To make a reviewed
file readable, the public package links its `artifact_ids` to the corresponding
reviewed public artifact. Otherwise the page reports that the public package has
not provided content. It does not call the original file missing.

Object ownership is a separate layer from occurrence edges. Both native and
public renderers use the same portable causal layout. Only supplied handoffs
establish ranks; labels, array position, and simultaneous execution do not create
edges. Hover and keyboard focus follow explicit source references. The graph initially shows all published runs across repositories. Individual runs
remain selectable. Source lists and collection pages are paginated.
`contracts/loop-graph-sources.json` records the exact upstream commits and bytes
for the shared contract, validator, and causal layout.

Selecting an edge retains its input/output versions in the same review panel.
Multi-component selectors change the comparison with the selected content.
Text comparison shows the changed block between shared prefix/suffix lines.
JSON comparison reports changed fields. Neither comparison certifies semantics.
A proven failed finding uses a red X. Unknown, resolved, and non-applicable findings
retain their different states. Original metrics are displayed without constructing
a denominator from visible edges. Historical observation scopes retain their
Host version, time window, formula, and limitations.

Focused controls:

```sh
PYTHONPATH=tests python3 -m unittest test_loop_graph_site test_loop_site test_import_loop_snapshot
node --test tests/loop_graph.test.mjs
python3 scripts/build_site.py --out /absolute/external/build-directory
```

The fixture browser drive verifies rendering and interaction only. It does not
certify new native executions, private source disclosure, or deployment. The
publisher verifies the reviewed real snapshot and deployed page separately.
