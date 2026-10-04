(() => {
  'use strict';
  const form = document.querySelector('#transcript-form');
  const query = document.querySelector('#transcript-query');
  const podcast = document.querySelector('#transcript-podcast');
  const mode = document.querySelector('#transcript-mode');
  const status = document.querySelector('#transcript-status');
  const results = document.querySelector('#transcript-results');
  const submit = document.querySelector('#transcript-submit');
  let request = 0;
  let controller;
  function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function link(text, url) {
    const node = el('a', text);
    node.href = url;
    node.target = '_blank';
    node.rel = 'noopener noreferrer';
    return node;
  }
  async function api(params, signal) {
    const response = await fetch('/api/transcripts?' + new URLSearchParams(params), {signal});
    let body;
    try { body = await response.json(); } catch (_) { throw new Error('搜尋服務暫時無法使用，請稍後再試。'); }
    if (!response.ok) throw new Error(body.error || '來源暫時無法讀取。');
    return body;
  }
  async function inspect(item, box, button, id, signal) {
    button.disabled = true;
    button.textContent = '正在確認時間戳…';
    try {
      const data = await api({action: 'inspect', url: item.source_url}, signal);
      if (id !== request) return;
      box.replaceChildren(el('p', `已讀到逐字稿 · ${data.segment_count} 段 · ${data.first_timestamp}–${data.last_timestamp}`, 'transcript-found'));
      if (data.excerpt) {
        box.append(el('p', `來源短摘錄 · ${data.excerpt_timestamp}`, 'meta'), el('blockquote', data.excerpt + '…'));
      }
      box.append(el('p', '時間戳與文字來自第三方，尚未核對音訊、發言者與整集完整性。', 'meta'));
      const details = el('details');
      details.append(el('summary', '來源紀錄與 CLI'));
      details.append(el('p', `讀取時間：${data.checked_at}`), el('p', `原始 HTML SHA-256：${data.source_sha256}`, 'transcript-hash'));
      details.append(el('pre', `python3 scripts/transcript.py inspect --url '${item.source_url}'`));
      box.append(details);
      button.remove();
    } catch (error) {
      if (id !== request || error.name === 'AbortError') return;
      box.replaceChildren(el('p', error.message, 'transcript-error'));
      button.disabled = false;
      button.textContent = '重試讀取逐字稿';
    }
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    controller?.abort();
    controller = new AbortController();
    const signal = controller.signal;
    const id = ++request;
    const params = {q: query.value.trim(), podcast: podcast.value, mode: mode.value};
    submit.disabled = true;
    status.textContent = '正在搜尋公開來源…';
    results.replaceChildren();
    const url = new URL(location.href);
    url.search = new URLSearchParams(params).toString();
    history.replaceState(null, '', url);
    try {
      const data = await api(params, signal);
      if (id !== request) return;
      status.textContent = `${data.podcast} · 搜尋詞「${data.search_terms}」· ${data.results.length} 個候選結果`;
      results.append(link('在 PodScripts 查看這次搜尋 ↗', data.provider_search_url));
      if (data.attempted_terms.length > 1) results.append(el('p', `原搜尋「${data.attempted_terms[0]}」未命中，已放寬為「${data.search_terms}」。請核對候選是否相關。`, 'meta'));
      if (data.video_url) results.append(el('p', '影片連結用於尋找候選來源；找到相似標題不代表已確認同一集或原話。', 'meta'));
      if (!data.results.length) {
        results.append(el('p', '此節目目前沒有符合的公開結果。試試較短的英文關鍵字、來賓姓氏，或切換節目。'));
        return;
      }
      data.results.forEach((item, index) => {
        const card = el('article', undefined, 'transcript-result');
        card.append(el('div', `候選 ${index + 1} · PodScripts`, 'eyebrow'), el('h3', item.title), link('閱讀原站逐字稿全文 ↗', item.source_url));
        const box = el('div');
        const button = el('button', '確認逐字稿與時間戳', 'button secondary');
        button.type = 'button';
        button.addEventListener('click', () => inspect(item, box, button, id, signal));
        card.append(box, button);
        results.append(card);
        if (index === 0) inspect(item, box, button, id, signal);
      });
    } catch (error) {
      if (id === request && error.name !== 'AbortError') status.textContent = error.message;
    } finally {
      if (id === request) submit.disabled = false;
    }
  });
  document.querySelectorAll('[data-query]').forEach(button => {
    button.addEventListener('click', () => {
      query.value = button.dataset.query;
      podcast.value = button.dataset.podcast;
      mode.value = 'basic';
      form.requestSubmit();
    });
  });
  const params = new URLSearchParams(location.search);
  if (params.has('q')) {
    query.value = params.get('q').slice(0, 240);
    if ([...podcast.options].some(o => o.value === params.get('podcast'))) podcast.value = params.get('podcast');
    if (['basic', 'episode'].includes(params.get('mode'))) mode.value = params.get('mode');
    form.requestSubmit();
  }
})();
