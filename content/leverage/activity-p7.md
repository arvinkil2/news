---
title: "Bond Activity"
date: "2026-10-27"
lede: "Week trading activity for every watched bond, with the day's most traded, biggest moves and latest prints."
data_as_of: "Tape through 26 Oct 2026"
url: "/leverage/activity/7/"
---

<dl class="bw-summary">
<div class="bw-sum-item"><dt>Updated</dt><dd>Today, 21:18 ET</dd></div>
<div class="bw-sum-item"><dt>Tape through</dt><dd>26 Oct 2026</dd></div>
<div class="bw-sum-item"><dt>Bonds traded</dt><dd>184</dd></div>
<div class="bw-sum-item"><dt>Trades</dt><dd>2,137</dd></div>
<div class="bw-sum-item"><dt>Last prints below 90</dt><dd>62</dd></div>
</dl>
<h2 id="all">All watched bonds, 21 Oct 2026 to 26 Oct 2026 - page 7 of 7</h2>
<div class="market-table-scroll"><table class="market-table bw-grid " data-tid="act-all" data-def="[340, 104, 92, 110, 104, 108, 118, 118, 110, 108]" data-min="[200, 72, 68, 84, 64, 76, 84, 84, 92, 96]" data-fixed="[]" data-sort="1">
<colgroup><col style="width:340px"><col style="width:104px"><col style="width:92px"><col style="width:110px"><col style="width:104px"><col style="width:108px"><col style="width:118px"><col style="width:118px"><col style="width:110px"><col style="width:108px"></colgroup>
<thead><tr><th>Bond</th><th>Issued ($M)</th><th>Trades (5d)</th><th>Volume ($)</th><th>Last (% of par)</th><th>Move (5d, pts)</th><th>High (5d, % of par)</th><th>Low (5d, % of par)</th><th>Last trade</th><th>CUSIP</th></tr></thead>
<tbody>
<tr><td><a href="/leverage/bond/u8528kaa6/">WULF COMPUTE LLC</a><span class="muted activity-sec">7.75% Notes due 2030</span></td><td class="muted" data-v="-999"></td><td data-v="0">0</td><td data-v="0">$0</td><td data-v="103.45">103.45</td><td class="muted">—</td><td class="muted">—</td><td class="muted">—</td><td data-v="2026-10-19">19 Oct 2026</td><td class="muted">U8528KAA6</td></tr>
</tbody></table></div>
<nav class="bw-pager" aria-label="All watched bonds pages"><span class="bw-pager-pos">Page 7 of 7</span><span class="bw-pager-links"><a href="/leverage/activity/">1</a> / <a href="/leverage/activity/2/">2</a> / <a href="/leverage/activity/3/">3</a> / <a href="/leverage/activity/4/">4</a> / <a href="/leverage/activity/5/">5</a> / <a href="/leverage/activity/6/">6</a> / <strong>7</strong></span><span class="bw-pager-ends"><a href="/leverage/activity/6/">Previous</a></span></nav>
<script>
document.querySelectorAll('table.bw-grid').forEach(function(t){
  var tid = t.getAttribute('data-tid'); if (!tid) return;
  var ths = Array.prototype.slice.call(t.querySelectorAll(':scope > thead > tr > th'));
  var n = ths.length;
  var defs = JSON.parse(t.getAttribute('data-def') || '[]');
  var mins = JSON.parse(t.getAttribute('data-min') || '[]');
  var fixed = JSON.parse(t.getAttribute('data-fixed') || '[]');
  if (defs.length !== n) return;
  var cg = t.querySelector(':scope > colgroup'); if (!cg) return;
  var widths = defs.slice(), sort = null, lastDrag = 0;
  try {
    var raw = localStorage.getItem('bondwatch:v1:' + tid);
    if (raw) { var st = JSON.parse(raw);
      if (st && st.w && st.w.length === n) widths = st.w.map(function(w, i){ var v = parseFloat(w); return isNaN(v) ? defs[i] : Math.max(mins[i] || 40, v); });
      if (st && st.s) sort = st.s; }
  } catch (e) {}
  function apply(){ var sum = 0; for (var i = 0; i < n; i++){ cg.children[i].style.width = widths[i] + 'px'; sum += widths[i]; } t.style.width = sum + 'px'; }
  function save(){ try { localStorage.setItem('bondwatch:v1:' + tid, JSON.stringify({w: widths, s: sort})); } catch (e) {} }
  apply();
  var head = t.querySelector(':scope > thead');
  function boundary(ev){
    var best = -1, bestD = 9;
    for (var i = 0; i < n; i++){
      if (fixed.indexOf(i) >= 0) continue;
      var d = Math.abs(ev.clientX - ths[i].getBoundingClientRect().right);
      if (d < bestD) { bestD = d; best = i; }
    }
    return best;
  }
  function startDrag(i, ev, shift){
    var startX = ev.clientX, startW = widths[i], startN = (i + 1 < n) ? widths[i + 1] : 0;
    shift = shift && i + 1 < n;
    function move(e){
      var dx = e.clientX - startX;
      if (shift) { var w = Math.max(mins[i], Math.min(startW + startN - mins[i + 1], startW + dx)); widths[i] = w; widths[i + 1] = startW + startN - w; }
      else widths[i] = Math.max(mins[i], startW + dx);
      apply(); lastDrag = Date.now();
    }
    function up(){ document.removeEventListener('pointermove', move); document.removeEventListener('pointerup', up); document.removeEventListener('pointercancel', up); save(); }
    document.addEventListener('pointermove', move);
    document.addEventListener('pointerup', up);
    document.addEventListener('pointercancel', up);
  }
  function autoFit(i){
    var clone = t.cloneNode(true);
    clone.style.cssText = 'position:absolute;visibility:hidden;left:-9999px;top:0;width:auto;table-layout:auto;';
    var ccg = clone.querySelector('colgroup'); if (ccg) ccg.remove();
    document.body.appendChild(clone);
    var cths = clone.querySelectorAll(':scope > thead > tr > th');
    var w = cths[i] ? cths[i].offsetWidth : 0;
    clone.remove();
    if (w > 0) { widths[i] = Math.max(mins[i], w); apply(); save(); }
  }
  head.addEventListener('pointerdown', function(ev){
    var i = boundary(ev); if (i < 0) return;
    ev.preventDefault(); ev.stopPropagation();
    startDrag(i, ev, ev.shiftKey);
  });
  head.addEventListener('dblclick', function(ev){
    var i = boundary(ev); if (i < 0) return;
    ev.preventDefault();
    autoFit(i);
  });
  ths.forEach(function(th, i){
    if (fixed.indexOf(i) >= 0) return;
    var grip = document.createElement('span');
    grip.className = 'bw-grip';
    grip.setAttribute('aria-hidden', 'true');
    th.appendChild(grip);
    var lastTap = 0, downX = 0;
    grip.addEventListener('pointerdown', function(ev){
      ev.preventDefault(); ev.stopPropagation();
      downX = ev.clientX;
      startDrag(i, ev, false);
    });
    grip.addEventListener('pointerup', function(ev){
      if (Math.abs(ev.clientX - downX) > 6) { lastTap = 0; return; }
      var now = Date.now();
      if (now - lastTap < 300) { lastTap = 0; autoFit(i); }
      else lastTap = now;
    });
    grip.addEventListener('click', function(ev){ ev.stopPropagation(); });
  });
  function sortRows(i, asc){
    var rows = Array.prototype.slice.call(t.querySelectorAll(':scope > tbody > tr'));
    rows.sort(function(a, b){
      var x = a.children[i], y = b.children[i];
      var xv = x && x.hasAttribute('data-v') ? x.getAttribute('data-v') : (x ? x.textContent.trim() : '');
      var yv = y && y.hasAttribute('data-v') ? y.getAttribute('data-v') : (y ? y.textContent.trim() : '');
      var xn = parseFloat(xv), yn = parseFloat(yv);
      var c = (!isNaN(xn) && !isNaN(yn)) ? xn - yn : String(xv).localeCompare(String(yv));
      return asc ? c : -c;
    });
    var tb = t.querySelector(':scope > tbody');
    rows.forEach(function(r){ tb.appendChild(r); });
    ths.forEach(function(h){ h.classList.remove('sasc', 'sdesc'); });
    ths[i].classList.add(asc ? 'sasc' : 'sdesc');
  }
  if (t.hasAttribute('data-sort')) {
    ths.forEach(function(th, i){
      th.addEventListener('click', function(){
        if (Date.now() - lastDrag < 250) return;
        var asc = !th.classList.contains('sasc');
        sort = {i: i, asc: asc};
        sortRows(i, asc); save();
      });
    });
    if (sort && sort.i < n) sortRows(sort.i, sort.asc);
  }
  ths.forEach(function(th, i){
    if (fixed.indexOf(i) >= 0) return;
    th.setAttribute('tabindex', '0');
    th.addEventListener('keydown', function(ev){
      if (!ev.altKey) return;
      if (ev.key === 'ArrowRight') { widths[i] += 8; apply(); save(); ev.preventDefault(); }
      if (ev.key === 'ArrowLeft') { widths[i] = Math.max(mins[i], widths[i] - 8); apply(); save(); ev.preventDefault(); }
    });
  });
  var rb = document.querySelector('[data-reset-for="' + tid + '"]');
  if (rb) rb.addEventListener('click', function(){
    try { localStorage.removeItem('bondwatch:v1:' + tid); } catch (e) {}
    widths = defs.slice(); sort = null; apply();
    ths.forEach(function(h){ h.classList.remove('sasc', 'sdesc'); });
  });
});
</script>
