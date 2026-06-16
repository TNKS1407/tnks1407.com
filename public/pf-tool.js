/* pf-tool.js — ツール用フィードバック（読者の3票＋開発者の修正指示）。
   使い方:
     <script src="https://tnks1407.com/pf-tool.js" data-pf-slug="seigou" data-pf-label="SEIGOU"></script>
   裏は記事と共通の feedback.tnks1407.com/para・/fix を key=slug, para=0 で叩く。
   段落スニペットの代わりに、その場の input/select の値を文脈として自動で添える。
   開発者モード: 記事と同じ ?dev＋合言葉（localStorage pf_dev）。 */
(function () {
  'use strict';
  if (window.__pfTool) return; window.__pfTool = true;
  var API = 'https://feedback.tnks1407.com';

  var me = document.currentScript || (function () { var s = document.getElementsByTagName('script'); return s[s.length - 1]; })();
  var slug = ((me && me.getAttribute('data-pf-slug')) || location.hostname.split('.')[0] || 'tool')
    .toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 60) || 'tool';
  var label = ((me && me.getAttribute('data-pf-label')) || document.title || slug).slice(0, 60);

  // 開発者モードの有効化（?dev＋合言葉。?dev=off で解除）
  try {
    var u = new URL(location.href);
    if (u.searchParams.has('dev')) {
      var v = u.searchParams.get('dev');
      if (v === 'off') localStorage.removeItem('pf_dev');
      else { var ent = (v && v.length > 3) ? v : prompt('開発者モードの合言葉'); if (ent) localStorage.setItem('pf_dev', ent); }
      u.searchParams.delete('dev'); history.replaceState(null, '', u.pathname + (u.search || '') + (u.hash || ''));
    }
  } catch (e) {}
  var DEV = null; try { DEV = localStorage.getItem('pf_dev'); } catch (e) {}

  // いまの操作状態（スライダー・選択・トグルの値）を文脈として集める
  function collectState() {
    var parts = [];
    try {
      Array.prototype.forEach.call(document.querySelectorAll('input,select'), function (el) {
        var t = (el.type || '').toLowerCase();
        if (['hidden', 'password', 'file', 'submit', 'button', 'reset'].indexOf(t) >= 0) return;
        if (el.offsetParent === null && t !== 'range') return;
        var lab = '';
        try { if (el.id) { var lb = document.querySelector('label[for="' + el.id.replace(/"/g, '') + '"]'); if (lb) lab = lb.textContent; } } catch (e) {}
        if (!lab) lab = el.getAttribute('aria-label') || el.getAttribute('name') || el.getAttribute('placeholder') || el.id || '';
        var val;
        if (t === 'checkbox' || t === 'radio') { if (!el.checked) return; val = (t === 'radio' && el.value) ? el.value : 'on'; }
        else if (el.tagName === 'SELECT') { val = el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : el.value; }
        else { val = el.value; }
        if (val === '' || val == null) return;
        lab = String(lab || '?').replace(/\s+/g, ' ').trim().slice(0, 22);
        parts.push(lab + '=' + String(val).replace(/\s+/g, ' ').trim().slice(0, 22));
      });
    } catch (e) {}
    return parts.slice(0, 12).join(', ').slice(0, 220);
  }
  function ctx() { var s = collectState(); return s ? '[' + s + '] ' : ''; }

  function post(path, body) {
    return fetch(API + path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().catch(function () { return {}; }); }).catch(function () { return {}; });
  }

  function boot() {
    var css =
      '#pft-btn{position:fixed;right:14px;bottom:14px;z-index:2147483000;width:42px;height:42px;border-radius:50%;border:none;cursor:pointer;background:#3c7876;color:#fff;font-size:19px;box-shadow:0 4px 14px rgba(0,0,0,.28);font-family:sans-serif;padding:0}' +
      '#pft-panel{position:fixed;right:14px;bottom:64px;z-index:2147483000;width:300px;max-width:92vw;background:#fff;color:#1d1b17;border:1px solid #e3dbd0;border-radius:14px;box-shadow:0 12px 36px rgba(0,0,0,.25);padding:12px 13px;font-family:"Hiragino Sans","Yu Gothic UI",sans-serif;font-size:13px;line-height:1.6;display:none;box-sizing:border-box}' +
      '#pft-panel.open{display:block}' +
      '#pft-panel *{box-sizing:border-box}' +
      '.pft-h{display:flex;justify-content:space-between;align-items:center;font-weight:700;margin-bottom:8px}' +
      '.pft-x{background:none;border:none;font-size:16px;cursor:pointer;color:#7d7568;line-height:1;padding:0}' +
      '.pft-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}' +
      '.pft-b{background:#faf8f4;border:1px solid #e3dbd0;border-radius:999px;padding:5px 10px;font-size:12.5px;cursor:pointer;color:#1d1b17;font-family:inherit}' +
      '.pft-b:hover{border-color:#3c7876;color:#3c7876}' +
      '.pft-b.on{background:#3c7876;color:#fff;border-color:#3c7876}' +
      '.pft-ta{width:100%;border:1px solid #e3dbd0;border-radius:8px;padding:6px 8px;font-size:12.5px;font-family:inherit;resize:vertical;color:#1d1b17;background:#faf8f4;outline:none;line-height:1.55}' +
      '.pft-ta:focus{border-color:#3c7876}' +
      '.pft-send{background:#3c7876;color:#fff;border:none;border-radius:8px;padding:6px 12px;font-size:12.5px;cursor:pointer;font-family:inherit;margin-top:6px}' +
      '.pft-send:disabled{opacity:.5}' +
      '.pft-dev{border-top:1px dashed #e3dbd0;margin-top:10px;padding-top:9px}' +
      '.pft-lbl{font-size:11.5px;color:#7d7568;margin-bottom:5px}' +
      '.pft-msg{font-size:12px;color:#3c7876;margin-top:5px;min-height:14px}' +
      '.pft-ctx{font-size:10.5px;color:#aaa49b;margin-top:7px;word-break:break-all}';
    var stEl = document.createElement('style'); stEl.textContent = css; document.head.appendChild(stEl);

    var btn = document.createElement('button'); btn.id = 'pft-btn'; btn.type = 'button';
    btn.title = 'このツールの感想・改善を送る'; btn.textContent = '💬';
    var panel = document.createElement('div'); panel.id = 'pft-panel';
    var devHtml = DEV ?
      ('<div class="pft-dev"><div class="pft-lbl">🔧 修正指示（開発者）</div>' +
        '<textarea class="pft-ta pft-fta" rows="2" placeholder="例: このスライダーの効きが急／ここが発散する"></textarea>' +
        '<div class="pft-row" style="margin-top:6px">' +
        '<button type="button" class="pft-b pft-fadd">📋 ためる</button>' +
        '<button type="button" class="pft-b pft-fnow">⚡今すぐ送る</button>' +
        '<button type="button" class="pft-b pft-fsend" style="display:none"></button>' +
        '</div></div>') : '';
    panel.innerHTML =
      '<div class="pft-h"><span>このツール、どう？</span><button type="button" class="pft-x">✕</button></div>' +
      '<div class="pft-row">' +
      '<button type="button" class="pft-b pft-r" data-t="stuck">🤔 詰まった</button>' +
      '<button type="button" class="pft-b pft-r" data-t="curious">👀 気になった</button>' +
      '<button type="button" class="pft-b pft-r" data-t="liked">❤️ 好き</button>' +
      '</div>' +
      '<textarea class="pft-ta pft-note" rows="2" placeholder="よかったら一言（任意）"></textarea>' +
      '<button type="button" class="pft-send pft-nsend">送る</button>' +
      '<div class="pft-msg pft-rmsg"></div>' +
      devHtml +
      '<div class="pft-ctx"></div>';
    document.body.appendChild(btn); document.body.appendChild(panel);

    var curType = null;
    var rmsg = panel.querySelector('.pft-rmsg');
    var note = panel.querySelector('.pft-note');
    var ctxEl = panel.querySelector('.pft-ctx');

    function openPanel() {
      var s = collectState();
      ctxEl.textContent = s ? 'いまの状態: ' + s : '（状態の自動取得なし）';
      panel.classList.add('open');
    }
    function closePanel() { panel.classList.remove('open'); }
    btn.addEventListener('click', function () { panel.classList.contains('open') ? closePanel() : openPanel(); });
    panel.querySelector('.pft-x').addEventListener('click', closePanel);

    Array.prototype.forEach.call(panel.querySelectorAll('.pft-r'), function (b) {
      b.addEventListener('click', function () {
        curType = b.getAttribute('data-t');
        Array.prototype.forEach.call(panel.querySelectorAll('.pft-r'), function (x) { x.classList.remove('on'); });
        b.classList.add('on');
        post('/para?key=' + encodeURIComponent(slug), { para: 0, type: curType, snippet: label });
        rmsg.textContent = 'ありがとう。よかったら一言どうぞ。';
        note.focus();
      });
    });
    panel.querySelector('.pft-nsend').addEventListener('click', function () {
      var n = (note.value || '').trim();
      if (!curType) { rmsg.textContent = 'まず 🤔/👀/❤️ を選んでね。'; return; }
      if (!n) { closePanel(); return; }
      post('/para?key=' + encodeURIComponent(slug), { para: 0, type: curType, snippet: label, reason: ctx() + n }).then(function () {
        note.value = ''; rmsg.textContent = '届いたよ。ありがとう。'; setTimeout(closePanel, 1100);
      });
    });

    if (DEV) {
      var DKEY = 'pf_fixdraft:' + slug;
      var draft = []; try { draft = JSON.parse(localStorage.getItem(DKEY)) || []; } catch (e) {}
      var fta = panel.querySelector('.pft-fta');
      var fsend = panel.querySelector('.pft-fsend');
      var updFsend = function () { if (draft.length) { fsend.style.display = ''; fsend.textContent = '📋 ためた分を送る（' + draft.length + '）'; } else fsend.style.display = 'none'; };
      var saveDraft = function () { try { localStorage.setItem(DKEY, JSON.stringify(draft)); } catch (e) {} updFsend(); };
      panel.querySelector('.pft-fadd').addEventListener('click', function () {
        var t = (fta.value || '').trim(); if (!t) return;
        draft.push({ para: 0, snippet: label, text: ctx() + t }); saveDraft();
        fta.value = ''; rmsg.textContent = 'ためた（' + draft.length + '件）。';
      });
      panel.querySelector('.pft-fnow').addEventListener('click', function () {
        var t = (fta.value || '').trim(); if (!t) return;
        post('/fix?key=' + encodeURIComponent(slug), { dev: DEV, now: true, items: [{ para: 0, snippet: label, text: ctx() + t }] }).then(function (d) {
          if (d && d.ok) { fta.value = ''; rmsg.textContent = '⚡送った。'; }
          else rmsg.textContent = (d && d.error === 'forbidden') ? '合言葉が違うみたい。' : '送れなかった。';
        });
      });
      fsend.addEventListener('click', function () {
        if (!draft.length) return; fsend.disabled = true;
        post('/fix?key=' + encodeURIComponent(slug), { dev: DEV, items: draft }).then(function (d) {
          fsend.disabled = false;
          if (d && d.ok) { draft = []; saveDraft(); rmsg.textContent = '送ったよ ✓'; }
          else rmsg.textContent = (d && d.error === 'forbidden') ? '合言葉が違う' : '送れなかった';
        });
      });
      updFsend();
    }
  }

  if (document.body) boot();
  else document.addEventListener('DOMContentLoaded', boot);
})();
