---
title: "Tesla"
date: "2026-10-31"
lede: "Benchmark issuer, 1 bonds: prices, trend, yield curve and fund holders from the FINRA tape and SEC fund filings."
data_as_of: "2026-10-30"
---


<p class="src"><a href="/leverage/bond-analytics/">&larr; Bond Analytics</a></p>
<dl class="bw-summary"><div class="bw-sum-item"><dt>Bonds</dt><dd>1</dd></div><div class="bw-sum-item"><dt>Median last print</dt><dd>n/a</dd></div><div class="bw-sum-item"><dt>Below 90</dt><dd>0 of 0 priced</dd></div><div class="bw-sum-item"><dt>Latest trade</dt><dd>—</dd></div></dl>
<h2>Bonds</h2>
<div class="market-table-scroll"><table class="market-table bw-grid " data-tid="iss-b-tesla" data-def="[300, 104, 124, 110, 84, 110, 96, 108]" data-min="[180, 72, 76, 92, 72, 92, 64, 96]" data-fixed="[]" data-sort="1">
<colgroup><col style="width:300px"><col style="width:104px"><col style="width:124px"><col style="width:110px"><col style="width:84px"><col style="width:110px"><col style="width:96px"><col style="width:108px"></colgroup>
<thead><tr><th>Bond</th><th>Issued ($M)</th><th>Last print (% of par)</th><th>Traded</th><th>Coupon (%)</th><th>Matures</th><th>Rating</th><th>CUSIP</th></tr></thead>
<tbody>
<tr><td data-v="TESLA INC — Notes"><a class="bond-link" href="/leverage/bond/88160raf8/"><span class="bond-name">TESLA INC</span><span class="bond-sub">Notes</span></a></td><td class="muted" data-v="-999"></td><td data-v="-999">n/a</td><td data-v="">no trades in the stored record</td><td data-v="-1">—</td><td data-v="">—</td><td class="muted" data-v="">—</td><td data-v="88160RAF8">88160RAF8</td></tr>
</tbody></table></div>

<p class="src">Sources: FINRA TRACE via the public lookup (trades) and SEC N-PORT bulk filings (fund marks and holders). Coverage: 0 trades are stored in the dataset for this issuer's bonds. Issued ($M) is the note's original amount issued, from the issuer's pricing filing where one is on record; blank where no held source states it.</p>
<script defer src="/js/echarts.min.js"></script>
<script defer src="/js/issuer_chart.js"></script>
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
  function cellKey(v){
    v = String(v == null ? '' : v).trim();
    if (v === '' || v === '—') return null;
    if (/^\d{4}-\d{2}-\d{2}/.test(v)) return {k: 1, s: v.slice(0, 10)};
    var num = v.replace(/,/g, '');
    if (/^[+-]?(\d+\.?\d*|\.\d+)$/.test(num)) return {k: 0, n: parseFloat(num)};
    var m = v.match(/^(\d{1,2}) ([A-Za-z]{3})[a-z]* (\d{4})$/);
    if (m) {
      var mi = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].indexOf(m[2]);
      if (mi >= 0) return {k: 1, s: m[3] + '-' + ('0' + (mi + 1)).slice(-2) + '-' + ('0' + m[1]).slice(-2)};
    }
    return {k: 2, s: v.toLowerCase()};
  }
  function sortRows(i, asc){
    var rows = Array.prototype.slice.call(t.querySelectorAll(':scope > tbody > tr'));
    rows.sort(function(a, b){
      var x = a.children[i], y = b.children[i];
      var xv = x && x.hasAttribute('data-v') ? x.getAttribute('data-v') : (x ? x.textContent.trim() : '');
      var yv = y && y.hasAttribute('data-v') ? y.getAttribute('data-v') : (y ? y.textContent.trim() : '');
      var kx = cellKey(xv), ky = cellKey(yv);
      if (kx === null || ky === null) {
        if (kx === ky) return 0;
        return kx === null ? 1 : -1;
      }
      var c;
      if (kx.k !== ky.k) c = kx.k - ky.k;
      else if (kx.k === 0) c = kx.n - ky.n;
      else c = kx.s < ky.s ? -1 : (kx.s > ky.s ? 1 : 0);
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
