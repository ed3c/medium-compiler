import { layoutGraph } from './loop-graph-layout.mjs';
import { mountPanorama, projectPanorama, readStructuredField } from './loop-panorama.mjs';

const svgNS = 'http://www.w3.org/2000/svg';
const unknown = value => value == null ? 'UNKNOWN' : String(value);
const unique = values => [...new Set(values)];
const refs = item => [...(item.input_artifact_ids || []), ...(item.output_artifact_ids || []), ...(item.evidence_artifact_ids || []), ...(item.source_artifact_ids || [])];
export const edgeClass = edge => edge.status === 'failed' ? 'failed' : edge.status === 'observed' && edge.kind === 'handoff' ? (edge.current_validity === 'current' ? 'observed' : edge.current_validity === 'stale' ? 'stale' : 'unknown') : 'unknown';
export function sourceRelations(graph, artifactIds, nodeIds = []) {
  const artifacts = new Set(artifactIds);
  const nodes = graph.nodes.filter(n => nodeIds.includes(n.id) || refs(n).some(id => artifacts.has(id)));
  const nodeSet = new Set(nodes.map(n => n.id));
  return { nodes: nodeSet,
    edges: new Set(graph.edges.filter(e => refs(e).some(id => artifacts.has(id)) || nodeSet.has(e.from_node_id) || nodeSet.has(e.to_node_id)).map(e => e.id)),
    objects: new Set(graph.objects.filter(o => o.source_artifact_ids.some(id => artifacts.has(id)) || nodes.some(n => n.object_id === o.id)).map(o => o.id)) };
}
export function compareText(left, right) {
  const a = left.split('\n'), b = right.split('\n');
  let first = 0, last = 0;
  while (first < a.length && first < b.length && a[first] === b[first]) first++;
  while (last < a.length - first && last < b.length - first && a[a.length - 1 - last] === b[b.length - 1 - last]) last++;
  const result = { equal: left === right, leftPoints: [...left].length, rightPoints: [...right].length,
    removed: a.slice(first, a.length - last), added: b.slice(first, b.length - last), fields: null };
  try {
    const flatten = (value, path = '$', out = {}) => {
      if (value && typeof value === 'object') {
        const keys = Object.keys(value).sort();
        if (!keys.length) out[path] = JSON.stringify(value);
        keys.forEach(key => flatten(value[key], path + '[' + JSON.stringify(key) + ']', out));
      } else out[path] = JSON.stringify(value);
      return out;
    };
    const x = flatten(JSON.parse(left)), y = flatten(JSON.parse(right));
    result.fields = unique([...Object.keys(x), ...Object.keys(y)]).sort().filter(k => x[k] !== y[k]).map(k => ({ path: k, before: x[k], after: y[k] }));
  } catch { /* Text is still comparable when either representation is not JSON. */ }
  return result;
}
function element(tag, text, attrs = {}) {
  const item = document.createElement(tag);
  if (text !== undefined && text !== null) item.textContent = text;
  for (const [key, value] of Object.entries(attrs)) item.setAttribute(key, value);
  return item;
}
function svg(tag, attrs = {}, text) {
  const item = document.createElementNS(svgNS, tag);
  for (const [key, value] of Object.entries(attrs)) item.setAttribute(key, value);
  if (text != null) item.textContent = text;
  return item;
}
function button(label, action, attrs = {}) {
  const item = element('button', label, { type: 'button', ...attrs });
  item.addEventListener('click', action);
  return item;
}
function select(label, choices, value, action) {
  const wrapper = element('label', label + ' '), input = element('select', null, { 'aria-label': label });
  choices.forEach(([id, name]) => input.append(element('option', name, { value: id })));
  input.value = value;
  input.addEventListener('change', () => action(input.value));
  wrapper.append(input);
  return wrapper;
}
async function readStatic(url, asJSON = true) {
  const target = new URL(url, location.href);
  if (target.origin !== location.origin || !target.pathname.startsWith('/assets/loop-data/')) throw new Error('非此快照的公開靜態資源');
  const response = await fetch(target, { credentials: 'omit', redirect: 'error' });
  if (!response.ok) throw new Error('公開內容讀取失敗：' + response.status);
  return asJSON ? response.json() : response.text();
}

async function readVersioned(reference) {
  const value = await readStatic(reference.url, false), bytes = new TextEncoder().encode(value);
  const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(n => n.toString(16).padStart(2, '0')).join('');
  if (bytes.length !== reference.bytes || digest !== reference.sha256) throw new Error('公開內容版本漂移；保留原選取，不替換為其他內容。');
  return value;
}

export async function mount(app) {
  const started = performance.now();
  const data = await readStatic(app.dataset.manifest), graph = data.graph;
  const artifacts = new Map(graph.artifacts.map(a => [a.id, a]));
  const objects = new Map(graph.objects.map(o => [o.id, o]));
  let panoramaController;
  let runId = '*', layer = 'observed', selection = null, generation = 0, loadedBytes = 0, zoom = 1, initialRenderMs = null, visibleNodes = 0, visibleEdges = 0, tabGeneration = 0;
  let workspace = { goal: '', runIds: null }, focus = null;
  const contentCache = new Map(), collectionCache = new Map(), sourcePages = new Map();
  app.replaceChildren();
  const panorama = element('section', null, { 'aria-label': 'Workspace 全景圖' });
  const toolbar = element('div', null, { class: 'lg-toolbar' });
  const tabs = element('div', null, { class: 'lg-tabs', role: 'tablist', 'aria-label': '資料工作台' });
  const graphPanel = element('div', null, { class: 'lg-workspace' });
  const otherPanel = element('div', null, { class: 'lg-collections', hidden: '' });
  const sidebar = element('aside', null, { class: 'lg-index', 'aria-label': '來源目錄索引' });
  const canvasArea = element('div', null, { class: 'lg-canvas-area' });
  const ownerPanel = element('div', null, { class: 'lg-owners' });
  const canvas = element('div', null, { class: 'lg-canvas', tabindex: '0', 'aria-label': '資料流圖；可水平捲動' });
  const findings = element('div', null, { class: 'lg-findings' });
  const inspector = element('section', null, { class: 'lg-inspector', 'aria-label': '同窗來源審查', hidden: '' });
  const announce = element('p', '選取來源、節點或交接線查看證據。', { role: 'status', class: 'lg-notice' });
  const cost = element('p', null, { class: 'loop-note' });
  graphPanel.append(sidebar, canvasArea); canvasArea.append(ownerPanel, element('p', '節點依序顯示執行／傳遞／驗收。綠色實線：已證實且目前有效；灰色虛線：有效性未知或歷史版本；紅 X：已證實失敗。', { class: 'lg-legend' }), canvas, findings);
  app.append(panorama, toolbar, tabs, announce, graphPanel, otherPanel, inspector, cost);
  toolbar.append(select('Run', [['*', '全部 repo / runs'], ...data.runs.map(r => [r.id, r.repository + ' · ' + r.id])], runId, value => { runId = value; draw(); showTab('graph'); }));
  toolbar.append(select('圖層', [['observed', '已證實交接'], ['all', '全部證據'], ['failed', '斷點']], layer, value => { layer = value; draw(); }));
  toolbar.append(button('縮小', () => setZoom(Math.max(.4, zoom - .2))), button('放大', () => setZoom(Math.min(2, zoom + .2))), button('原比例', () => setZoom(1)));
  function setZoom(value) { zoom = value; const drawing = canvas.querySelector('svg'); if (drawing) { drawing.style.width = drawing.dataset.width * zoom + 'px'; drawing.style.height = drawing.dataset.height * zoom + 'px'; } }
  const tabNames = [['graph', '資料圖'], ['cards', '全部卡片'], ['notes', '全部筆記'], ['requirements', '需求與驗收'], ['metrics', '成本與量測']];
  tabNames.forEach(([id, label]) => { const control = button(label, () => showTab(id).catch(error => otherPanel.append(element('p', error.message, { role: 'alert' }))), { role: 'tab', 'data-tab': id, 'aria-selected': String(id === 'graph') }); tabs.append(control); });
  const metricLabel = metric => metric.status === 'not_applicable' || metric.denominator === 0 ? 'N/A' : metric.status !== 'observed' || metric.value == null ? 'UNKNOWN' : metric.value + ' ' + metric.unit;
  function currentNodes() {
    const endpoints = new Set(graph.edges.filter(e => e.run_id === runId).flatMap(e => [e.from_node_id, e.to_node_id]));
    const scoped = projectPanorama(graph, workspace.runIds);
    return scoped.nodes.filter(n => (runId === '*' || n.run_id === runId || endpoints.has(n.id)) &&
      (!focus || focus.node_ids.includes(n.id) || scoped.edges.some(e => focus.edge_ids.includes(e.id) && (e.from_node_id === n.id || e.to_node_id === n.id))));
  }
  function highlight(related) {
    app.querySelectorAll('[data-node], [data-edge], [data-object]').forEach(el => {
      const kind = el.dataset.node ? 'nodes' : el.dataset.edge ? 'edges' : 'objects';
      const id = el.dataset.node || el.dataset.edge || el.dataset.object;
      el.classList.toggle('lg-highlight', !!related && related[kind].has(id));
    });
    panorama.querySelectorAll('[data-detail-node]').forEach(el => el.classList.toggle('is-linked', !!related && related.nodes.has(el.dataset.detailNode)));
    panorama.querySelectorAll('[data-panorama-object]').forEach(el => {
      el.classList.toggle('lg-highlight', !!related && related.objects.has(el.dataset.panoramaObject));
    });
  }
  function highlightSources(artifactIds = [], nodeIds = []) {
    sidebar.querySelectorAll('[data-file]').forEach(control => {
      const matches = control.dataset.artifacts.split(' ').some(id => artifactIds.includes(id)) || control.dataset.nodes.split(' ').some(id => nodeIds.includes(id));
      control.classList.toggle('lg-source-highlight', matches);
    });
  }
  function updateCost() {
    cost.textContent = `公開快照 ${data.snapshot_sha256.slice(0, 12)} · ${visibleNodes} 次已記錄發生 · ${visibleEdges} 條可見邊 · 首次載入 ${initialRenderMs ?? 'UNKNOWN'} ms · 已載入產物原文 ${loadedBytes} bytes。這些是展示量測，不是自動化率。`;
  }
  function sourceFocus(entries) {
    const related = sourceRelations(graph, entries.flatMap(f => f.artifact_ids), entries.flatMap(f => f.node_ids));
    highlight(related);
    announce.textContent = related.nodes.size || related.objects.size || related.edges.size ? `已記錄關聯：${related.objects.size} 個物件、${related.nodes.size} 次發生、${related.edges.size} 條邊。` : '未找到已記錄關聯；這不表示來源不存在。';
  }
  function wireSource(control, entries) {
    control.addEventListener('mouseenter', () => sourceFocus(entries));
    control.addEventListener('focus', () => sourceFocus(entries));
    control.addEventListener('mouseleave', () => highlight(null));
    control.addEventListener('blur', () => highlight(null));
  }
  function drawIndex(targetNode = null) {
    sidebar.replaceChildren(element('h2', '來源總索引'));
    for (const repo of graph.repositories) {
      const files = [...repo.tracked_files.map(f => ({ ...f, origin: 'Git revision' })), ...repo.selected_files.map(f => ({ ...f, origin: 'Selected workspace' }))];
      const related = targetNode ? files.findIndex(f => f.node_ids.includes(targetNode.id) || f.artifact_ids.some(id => refs(targetNode).includes(id))) : -1;
      if (related >= 0) sourcePages.set(repo.id, Math.floor(related / 80));
      const section = element('details', null, { class: 'lg-repo-index' });
      section.open = related >= 0 || currentNodes().some(n => n.repository_id === repo.id);
      section.append(element('summary', repo.label + ' · ' + files.length + ' 已索引項目'));
      section.append(element('p', '索引範圍：' + repo.index_status + ' · revision ' + unknown(repo.revision), { class: 'loop-note' }));
      repo.gaps.forEach(gap => section.append(element('p', gap, { class: 'lg-unknown' })));
      const page = sourcePages.get(repo.id) || 0, list = element('div', null, { class: 'lg-file-list' });
      let lastDirectory = null;
      files.slice(page * 80, page * 80 + 80).forEach(file => {
        const directory = file.path.includes('/') ? file.path.slice(0, file.path.lastIndexOf('/')) : '.';
        if (directory !== lastDirectory) {
          const dir = button(directory + '/', () => sourceFocus(files.filter(f => directory === '.' ? !f.path.includes('/') : f.path.startsWith(directory + '/'))), { class: 'lg-directory' });
          wireSource(dir, files.filter(f => directory === '.' ? !f.path.includes('/') : f.path.startsWith(directory + '/'))); list.append(dir); lastDirectory = directory;
        }
        const control = button(file.path.split('/').at(-1), () => inspectArtifacts(file.artifact_ids, file.path, file), { class: 'lg-file', title: file.path + ' · ' + file.origin, 'data-file': file.id, 'data-artifacts': file.artifact_ids.join(' '), 'data-nodes': file.node_ids.join(' ') });
        if (targetNode && (file.node_ids.includes(targetNode.id) || file.artifact_ids.some(id => refs(targetNode).includes(id)))) control.classList.add('lg-source-highlight');
        wireSource(control, [file]); list.append(control);
      });
      section.append(list);
      if (files.length > 80) {
        const previous = button('上一頁', () => { sourcePages.set(repo.id, page - 1); drawIndex(); }); previous.disabled = page === 0;
        const next = button('下一頁', () => { sourcePages.set(repo.id, page + 1); drawIndex(); }); next.disabled = (page + 1) * 80 >= files.length;
        section.append(previous, element('span', ` ${page + 1} / ${Math.ceil(files.length / 80)} `), next);
      }
      sidebar.append(section);
      if (related >= 0) requestAnimationFrame(() => section.querySelector(`[data-file="${files[related].id}"]`)?.scrollIntoView({ block: 'nearest', inline: 'nearest' }));
    }
    const runtime = graph.artifacts.filter(a => (runId === '*' || a.scope === runId || a.scope === 'original_source') && !graph.repositories.some(r => [...r.tracked_files, ...r.selected_files].some(f => f.artifact_ids.includes(a.id))));
    const extra = element('details'); extra.append(element('summary', '已綁定產物 · ' + runtime.length));
    runtime.forEach(a => { const b = button(a.role + ' · ' + a.status, () => inspectArtifacts([a.id], a.role)); wireSource(b, [{ artifact_ids: [a.id], node_ids: [] }]); extra.append(b); }); sidebar.append(extra);
  }
  function draw() {
    const runControl = toolbar.querySelector('[aria-label="Run"]');
    runControl.replaceChildren(...[['*', 'Workspace 全部執行'], ...data.runs.filter(r => !workspace.runIds || workspace.runIds.includes(r.id)).map(r => [r.id, r.repository + ' · ' + r.id])].map(([id, label]) => element('option', label, { value: id })));
    runControl.value = runId;
    toolbar.querySelector('[aria-label="圖層"]').value = layer;
    panoramaController = mountPanorama(panorama, { graph, runs: data.runs, ...workspace,
      readArtifact: async id => (await content(id)).text,
      onReset: () => { focus=null; selection=null; generation++; inspector.hidden=true; draw(); },
      onScope: value => { workspace = value; focus = null; runId = '*'; generation++; inspector.hidden = true; draw(); showTab('graph'); },
      onFocus: value => { focus = value; runId = '*'; layer = 'all'; draw(); showTab('graph'); if(value.reveal !== false) { drawIndex(graph.nodes.find(n=>value.node_ids.includes(n.id))); canvas.scrollIntoView({block:'start'}); } },
      onSelect: value => {
        if(value.kind === 'edge') { const edge = graph.edges.find(e=>e.id===value.id); highlightSources(refs(edge)); inspectEdge(edge); }
        else if(value.kind === 'artifact') { const a=artifacts.get(value.id); highlightSources([a.id],[]); inspectArtifacts([a.id],a.role,a); }
        else if(value.kind === 'finding') { const f=graph.findings.find(f=>f.id===value.id); inspectArtifacts(f.artifact_ids,f.message,f); }
        else if(value.kind === 'node') { const n=graph.nodes.find(n=>n.id===value.id); drawIndex(n); highlightSources(refs(n),[n.id]); inspectArtifacts(refs(n),n.label,n); }
        else { const o=objects.get(value.id); inspectArtifacts(o.source_artifact_ids,o.label,o); }
      }
    });
    if(focus) panorama.append(button('返回 Workspace 全部執行',()=>{focus=null;draw();}));
    drawIndex(); ownerPanel.replaceChildren(element('h2', '唯一責任物件與接口'));
    for (const owner of graph.objects) {
      const box = element('details', null, { class: 'lg-owner', 'data-object': owner.id });
      box.append(element('summary', owner.label + ' · ' + owner.scope));
      box.append(element('p', owner.namespace + ' · ' + owner.kind));
      box.append(button('來源', () => inspectArtifacts(owner.source_artifact_ids, owner.label)));
      graph.ports.filter(p => p.object_id === owner.id).forEach(port => box.append(button(port.direction + ' · ' + port.name, () => inspectArtifacts(port.source_artifact_ids, port.name, port))));
      box.addEventListener('mouseenter', () => highlightSources(owner.source_artifact_ids));
      box.addEventListener('focusin', () => highlightSources(owner.source_artifact_ids));
      box.addEventListener('mouseleave', () => highlightSources());
      ownerPanel.append(box);
    }
    const nodes = currentNodes(), nodeIds = new Set(nodes.map(n => n.id));
    const allEdges = projectPanorama(graph, workspace.runIds).edges.filter(e => (runId === '*' || e.run_id === runId) && nodeIds.has(e.from_node_id) && nodeIds.has(e.to_node_id));
    const shownEdges = allEdges.filter(e => layer === 'all' || (layer === 'failed' ? e.status === 'failed' : e.kind === 'handoff' && e.status === 'observed'));
    const layout = layoutGraph({ nodes: nodes.map(n => ({ id: n.id, repository_id: n.repository_id })), edges: allEdges.filter(e => e.kind === 'handoff').map(e => ({ from: e.from_node_id, to: e.to_node_id })) });
    const positions = new Map(layout.nodes.map(n => [n.id, n]));
    const drawing = svg('svg', { viewBox: `0 0 ${layout.width} ${layout.height}`, role: 'group', 'aria-label': 'Occurrence 因果圖', 'data-width': layout.width, 'data-height': layout.height });
    const definitions = svg('defs'), marker = svg('marker', { id: 'lg-arrow', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: 'auto-start-reverse' });
    marker.append(svg('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: 'currentColor' })); definitions.append(marker); drawing.append(definitions);
    layout.bands.forEach(band => { const repo = graph.repositories.find(r => r.id === band.repository_id); drawing.append(svg('rect', { x: band.x, y: band.y, width: band.width, height: band.height, rx: 12, class: 'lg-band' }), svg('text', { x: band.x + 12, y: band.y + 22, class: 'lg-band-label' }, repo ? repo.label + ' · ' + (repo.revision?.slice(0, 8) || 'revision UNKNOWN') : '共享區域')); });
    for (const edge of shownEdges) {
      const from = positions.get(edge.from_node_id), to = positions.get(edge.to_node_id);
      const x1 = from.x + from.width, y1 = from.y + from.height / 2, x2 = to.x, y2 = to.y + to.height / 2;
      const group = svg('g', { class: 'lg-edge ' + edgeClass(edge), tabindex: 0, role: 'button', 'aria-label': edge.label + ' · ' + edge.status, 'data-edge': edge.id });
      group.append(svg('path', { d: `M ${x1} ${y1} C ${x1 + 45} ${y1}, ${x2 - 45} ${y2}, ${x2} ${y2}`, 'marker-end': 'url(#lg-arrow)' }));
      group.append(svg('text', { x: (x1 + x2) / 2, y: (y1 + y2) / 2 - 9, 'text-anchor': 'middle' }, (edge.status === 'failed' ? '✕ ' : edge.status === 'unknown' ? '? ' : '') + edge.label + (edge.current_validity !== 'current' ? ' · ' + edge.current_validity : '')));
      const activate = () => { highlightSources(refs(edge)); inspectEdge(edge); };
      group.addEventListener('mouseenter', () => highlightSources(refs(edge))); group.addEventListener('focus', () => highlightSources(refs(edge))); group.addEventListener('mouseleave', () => highlightSources()); group.addEventListener('click', activate); group.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); activate(); } }); drawing.append(group);
    }
    for (const node of nodes) {
      const p = positions.get(node.id);
      const group = svg('g', { class: 'lg-node', tabindex: 0, role: 'button', 'aria-label': node.label + ' · ' + node.identity.status, 'data-node': node.id, transform: `translate(${p.x},${p.y})` });
      group.append(svg('rect', { width: p.width, height: p.height, rx: 10 }), svg('text', { x: 12, y: 24, class: 'lg-node-kind' }, node.kind + ' · ' + node.identity.status), svg('text', { x: 12, y: 47 }, node.label.slice(0, 28)), svg('text', { x: 12, y: 71, class: 'lg-node-status' }, `${node.status.execution} / ${node.status.transfer} / ${node.status.acceptance}`));
      const activate = () => { selection = node.id; drawIndex(node); highlight(sourceRelations(graph, refs(node), [node.id])); inspectArtifacts(refs(node), node.label, { ...node, object: objects.get(node.object_id) }); };
      group.addEventListener('click', activate); group.addEventListener('focus', () => { highlight(sourceRelations(graph, refs(node), [node.id])); highlightSources(refs(node), [node.id]); }); group.addEventListener('mouseenter', () => highlightSources(refs(node), [node.id])); group.addEventListener('mouseleave', () => highlightSources()); group.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); activate(); } }); drawing.append(group);
    }
    canvas.replaceChildren(drawing); setZoom(zoom);
    findings.replaceChildren(element('h3', '已知斷點與證據缺口'));
    if (!shownEdges.length) findings.append(element('p', '此圖層沒有已記錄的交接；未連接節點不代表自動化成功。'));
    graph.findings.filter(f => (!workspace.runIds || workspace.runIds.includes(f.run_id)) && (runId === '*' || f.run_id === runId)).forEach(f => { const item = element('article', null, { class: f.status === 'failed' ? 'lg-failed' : 'lg-unknown' }); item.append(element('strong', (f.status === 'failed' ? '✕ ' : f.status === 'unknown' ? '? ' : f.status === 'resolved' ? '✓ ' : 'N/A ') + f.kind + ' · ' + f.status), element('p', f.message), button('查看原證據與下一步', () => inspectArtifacts(f.artifact_ids, f.message, f))); findings.append(item); });
    visibleNodes = nodes.length; visibleEdges = shownEdges.length;
    if (initialRenderMs === null) initialRenderMs = Math.round(performance.now() - started);
    updateCost();
  }
  async function content(id) {
    if (contentCache.has(id)) return contentCache.get(id);
    const artifact = artifacts.get(id), url = data.content_urls[id];
    if (!url) return { text: null, reason: artifact.status === 'not_public' ? '未公開：保留原私有證據身份。' : '此公開包未提供內容；不表示原檔案不存在。' };
    const value = await readVersioned({ url, bytes: artifact.public_bytes, sha256: artifact.public_sha256 });
    loadedBytes += artifact.public_bytes; updateCost();
    const result = { text: value }; contentCache.set(id, result); return result;
  }
  function heading(label, metadata) { inspector.hidden = false; inspector.replaceChildren(button('關閉審查窗', () => { inspector.hidden = true; generation++; }, { class: 'lg-close' }), element('h2', label)); if (metadata) { const detail = element('details'); detail.append(element('summary', '來源、版本與原 Owner 資料'), element('pre', JSON.stringify(metadata, null, 2))); inspector.append(detail); } }
  async function artifactPane(ids, label, parent, ticket, changed = () => {}) {
    const pane = element('div', null, { class: 'lg-artifact-pane' }), pre = element('pre', '載入中…');
    pane.append(element('h3', label)); parent.append(pane);
    if (!ids.length) { pre.textContent = '未提供已綁定內容'; pane.append(pre); return { text: null }; }
    let chosen = ids[0], loadGeneration = 0;
    if (ids.length > 1) pane.append(select('Component', ids.map(id => [id, artifacts.get(id).role + ' · ' + id]), chosen, async id => { chosen = id; await load(); }));
    const metadata = element('details'); metadata.append(element('summary', '格式、角色與兩種來源身份'));
    const meta = element('pre'); metadata.append(meta); pane.append(metadata, pre);
    async function load() { const loadTicket = ++loadGeneration, artifact = artifacts.get(chosen); meta.textContent = JSON.stringify(artifact, null, 2); pre.textContent = '載入中…'; changed({ text: null }); try { const result = await content(chosen); if (ticket === generation && loadTicket === loadGeneration) { pre.textContent = result.text ?? result.reason; changed(result); } return result; } catch (error) { if (ticket === generation && loadTicket === loadGeneration) { pre.textContent = error.message; changed({ text: null }); } return { text: null }; } }
    return load();
  }
  async function inspectArtifacts(ids, label, metadata) {
    const originalNode = graph.nodes.find(n=>n.id===metadata?.id);
    if(originalNode) panoramaController?.setSelection({kind:'node',id:originalNode.id});
    const ticket = ++generation; selection = label; heading(label, metadata);
    const source = unique(ids).map(id => artifacts.get(id)).find(a => a.source && metadata?.identity?.locator?.startsWith(a.source.path + '#/'));
    if (source) {
      const fieldPanel = element('section', null, { 'aria-label': '結構化欄位內容' });
      inspector.append(fieldPanel);
      let loaded;
      try { loaded = await content(source.id); }
      catch (error) { loaded = { text: null, reason: error.message }; }
      if (ticket !== generation) return;
      const field = loaded.text == null ? null : readStructuredField(loaded.text, metadata.identity.locator, source.source.path);
      fieldPanel.append(element('h3', '原 Schema 欄位'), element('p', '欄位狀態：' + (field?.status || 'unknown')), element('p', field?.pointer || metadata.identity.locator), element('pre', field?.text || loaded.reason), element('p', '欄位投影不代表 Session 判斷正確或 next 已執行。'));
    }
    if (!ids.length) inspector.append(element('p', '只有已公開的索引或接口資料；沒有註冊可讀內容。'));
    for (const id of unique(ids)) { if (ticket !== generation) break; await artifactPane([id], artifacts.get(id).role, inspector, ticket); }
  }
  async function inspectEdge(edge) {
    panoramaController?.setSelection({kind:'edge',id:edge.id});
    const ticket = ++generation; selection = edge.id; heading(edge.label, edge);
    inspector.append(element('p', '表示法轉換不自動證明語義保留、指引遵循或驗收完成。'));
    const columns = element('div', null, { class: 'lg-comparison' }); inspector.append(columns);
    const comparison = element('div'); inspector.append(comparison);
    const sides = [{ text: null }, { text: null }];
    const updateComparison = (index, value) => {
      sides[index] = value;
      if (ticket !== generation) return;
      comparison.replaceChildren();
      if (sides.some(side => side.text == null)) { comparison.append(element('p', '比較 UNKNOWN：有一側原文尚未載入、未公開或未提供。')); return; }
      const diff = compareText(sides[0].text, sides[1].text), details = element('details');
      details.append(element('summary', `文字比較 · ${diff.leftPoints} → ${diff.rightPoints} code points · ${diff.equal ? '相同' : '不同'}`));
      details.append(element('p', '以下標示共同前後文之間的替換區塊；不是語義 review 或最小編輯距離。'), element('pre', diff.removed.map(line => '- ' + line).concat(diff.added.map(line => '+ ' + line)).join('\n')));
      if (diff.fields) details.append(element('h3', 'JSON 欄位差異'), element('pre', JSON.stringify(diff.fields, null, 2)));
      comparison.append(details);
    };
    await Promise.all([artifactPane(edge.input_artifact_ids, '實際輸入', columns, ticket, value => updateComparison(0, value)), artifactPane(edge.output_artifact_ids, '實際輸出', columns, ticket, value => updateComparison(1, value))]);
    if (ticket !== generation) return;
    const panes = columns.querySelectorAll('.lg-artifact-pane > pre'); let syncing = false;
    panes.forEach((pane, index) => pane.addEventListener('scroll', () => { if (syncing || !panes[1 - index]) return; syncing = true; panes[1 - index].scrollTop = pane.scrollTop; requestAnimationFrame(() => { syncing = false; }); }));
    for (const id of edge.evidence_artifact_ids) { if (ticket !== generation) break; await artifactPane([id], '轉換／接收證據', inspector, ticket); }
  }
  async function showTab(id) {
    const tabTicket = ++tabGeneration;
    tabs.querySelectorAll('[data-tab]').forEach(tab => tab.setAttribute('aria-selected', String(tab.dataset.tab === id)));
    graphPanel.hidden = id !== 'graph'; otherPanel.hidden = id === 'graph';
    if (id === 'graph') return;
    otherPanel.replaceChildren(element('h2', tabNames.find(t => t[0] === id)[1]));
    if (id === 'metrics') {
      graph.metrics.filter(m => (!workspace.runIds || workspace.runIds.includes(m.run_id)) && (runId === '*' || m.run_id === runId)).forEach(m => { const row = element('article'); row.append(element('h3', m.name + ' · ' + metricLabel(m)), element('p', `原計數：${unknown(m.numerator)} / ${unknown(m.denominator)} · ${m.status}`), element('p', m.gaps.join('；')), button('量測來源', () => inspectArtifacts(m.source_artifact_ids, m.name, m))); if (m.observation_scope) { const scope = m.observation_scope; row.append(element('p', '歷史量測 · ' + scope.host_version + ' · ' + unknown(scope.started_at) + ' → ' + unknown(scope.finished_at)), element('p', scope.formula), element('p', scope.limitations.join('；'))); } otherPanel.append(row); });
      if (!otherPanel.querySelector('article')) otherPanel.append(element('p', 'UNKNOWN：原 Owner 未提供此範圍的量測。'));
      return;
    }
    if (id === 'requirements') {
      otherPanel.append(element('p', '完整要求分母未由此圖建立。歷史測試結果與驗收標準有效性分開保留。'));
      graph.findings.filter(f => (!workspace.runIds || workspace.runIds.includes(f.run_id)) && (runId === '*' || f.run_id === runId) && (f.requirement_refs.length || f.kind === 'acceptance')).forEach(f => { const row = element('article'); row.append(element('h3', f.status + ' · ' + f.kind), element('p', f.message), element('pre', JSON.stringify({ requirements: f.requirement_refs, original_next: f.original_next }, null, 2))); otherPanel.append(row); }); return;
    }
    otherPanel.append(element('p', '卡片與筆記是資料附著；相同 ID 依 repository、run 與快照版本分開。消費關聯未提供時保留未觀察。'));
    const filter = element('input', null, { type: 'search', placeholder: '篩選 repo、類型、標題或 ID', 'aria-label': '篩選全部卡片或筆記' }), list = element('div'); otherPanel.append(filter, list);
    const rows = [];
    for (const run of data.runs.filter(r => !workspace.runIds || workspace.runIds.includes(r.id))) {
      if (!collectionCache.has(run.id)) collectionCache.set(run.id, JSON.parse(await readVersioned(data.collection_refs[run.id])));
      if (tabTicket !== tabGeneration) return;
      for (const entry of collectionCache.get(run.id)[id]) rows.push({ run, entry });
    }
    let page = 0;
    const render = () => {
      list.replaceChildren();
      const query = filter.value.toLowerCase(), matched = rows.filter(({ run, entry }) => [run.repository, entry.type, entry.title, entry.id].join(' ').toLowerCase().includes(query));
      list.append(element('p', `${matched.length} 個已公開項目 · 來源版本 ${data.snapshot_sha256.slice(0, 12)}`));
      matched.slice(page * 80, page * 80 + 80).forEach(({ run, entry }) => {
        const row = element('details');
        row.append(element('summary', entry.title + ' · ' + (entry.type || 'note')), element('p', run.repository + ' / ' + run.id + ' / ' + entry.id + ' · 消費：未觀察'), element('pre', entry.body), element('pre', entry.source_refs.join('\n')));
        list.append(row);
      });
      if (matched.length > 80) {
        const previous = button('上一頁', () => { page--; render(); }); previous.disabled = page === 0;
        const next = button('下一頁', () => { page++; render(); }); next.disabled = (page + 1) * 80 >= matched.length;
        list.append(previous, element('span', ` ${page + 1} / ${Math.ceil(matched.length / 80)} `), next);
      }
    };
    filter.addEventListener('input', () => { page = 0; render(); }); render();
  }
  draw();
}
if (typeof document !== 'undefined') {
  const app = document.getElementById('loop-graph-app');
  if (app) mount(app).catch(error => { app.replaceChildren(element('p', '公開資料圖無法載入：' + error.message, { role: 'alert' })); });
}
