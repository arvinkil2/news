---
title: "Republic of Panama"
date: "2026-10-20"
lede: "Single-name CDS on Republic of Panama: traded spreads, curve points and activity."
data_as_of: "swap tape through 2026-09-30 (file months 2026-09)"
---

<dl class="bw-summary"><div class="bw-sum-item"><dt>Data through</dt><dd>2026-09-30</dd></div><div class="bw-sum-item"><dt>Trades in window</dt><dd>120</dd></div><div class="bw-sum-item"><dt>Trades with a disseminated spread</dt><dd>45</dd></div><div class="bw-sum-item"><dt>Notional, USD trades</dt><dd>$538.4M</dd></div><div class="bw-sum-item"><dt>Capped share of trades</dt><dd>80.8%</dd></div><div class="bw-sum-item"><dt>Cleared share of trades</dt><dd>54.2%</dd></div></dl><p>Single-name credit default swaps on Republic of Panama. A curve point prints only where at least three priced trades support it in the window; a thinner point reports its trade count and no spread.</p><h2>Spread curve, window medians</h2><table class="market-table bw-grid" data-tid="nm-curve" data-def="[70, 170, 170]" data-min="[56, 110, 110]" data-fixed="[]">
<colgroup><col style="width:70px"><col style="width:170px"><col style="width:170px"></colgroup>
<thead><tr><th>Tenor</th><th data-num="1">Median spread (bp)</th><th data-num="1">Priced trades in window</th></tr></thead>
<tbody><tr><td>1Y</td><td>38.0</td><td>4</td></tr><tr><td>2Y</td><td>no trades in window</td><td>not yet reported</td></tr><tr><td>3Y</td><td>55.0</td><td>3</td></tr><tr><td>4Y</td><td>not enough priced trades</td><td>2</td></tr><tr><td>5Y</td><td>91.0</td><td>33</td></tr><tr><td>7Y</td><td>not enough priced trades</td><td>1</td></tr><tr><td>10Y</td><td>not enough priced trades</td><td>2</td></tr></tbody></table> <button type="button" class="bw-reset" data-reset-for="nm-curve">Reset layout</button><h2>Five-year spread, daily</h2><svg class="bond-chart" viewBox="0 0 720 240" width="100%" role="img" aria-label="Republic of Panama five-year CDS spread"><line x1="52" y1="218.0" x2="710" y2="218.0" stroke="#e5ddc8" stroke-width="1"/><text x="46" y="221.0" text-anchor="end" class="chart-lab">0</text><line x1="52" y1="166.0" x2="710" y2="166.0" stroke="#e5ddc8" stroke-width="1"/><text x="46" y="169.0" text-anchor="end" class="chart-lab">26</text><line x1="52" y1="114.0" x2="710" y2="114.0" stroke="#e5ddc8" stroke-width="1"/><text x="46" y="117.0" text-anchor="end" class="chart-lab">52</text><line x1="52" y1="62.0" x2="710" y2="62.0" stroke="#e5ddc8" stroke-width="1"/><text x="46" y="65.0" text-anchor="end" class="chart-lab">78</text><line x1="52" y1="10.0" x2="710" y2="10.0" stroke="#e5ddc8" stroke-width="1"/><text x="46" y="13.0" text-anchor="end" class="chart-lab">104</text><text x="52.0" y="234" text-anchor="middle" class="chart-lab">2026-09</text><text x="710.0" y="234" text-anchor="middle" class="chart-lab">2026-09</text><polygon points="52.0,46.6 74.7,48.9 120.1,50.6 210.8,40.1 256.2,43.1 347.0,44.6 392.3,48.1 415.0,52.6 505.8,36.6 528.5,36.6 573.9,35.6 687.3,26.6 710.0,12.7 710.0,20.7 687.3,26.6 573.9,35.6 528.5,36.6 505.8,36.6 415.0,52.6 392.3,48.6 347.0,44.6 256.2,44.6 210.8,47.1 120.1,50.6 74.7,57.5 52.0,46.6" fill="#3f4750" fill-opacity="0.14" stroke="none"/><polyline points="52.0,46.6 74.7,53.2 120.1,50.6 210.8,43.6 256.2,44.6 347.0,44.6 392.3,48.6 415.0,52.6 505.8,36.6 528.5,36.6 573.9,35.6 687.3,26.6 710.0,18.7" fill="none" stroke="#1a1a1a" stroke-width="1.4"/></svg><p>Daily median with the interquartile band, over days carrying at least one priced five-year trade.</p><p>Contracts trade at a standard coupon (100 or 500 basis points) with the difference settled upfront. Median upfront in the window: 0.44% of notional, unsigned in the tape, so no spread is inferred from it; spreads above come only from trades that disseminate a spread directly.</p><p>Sector and index membership are not disseminated in the tape and are not asserted here.</p><p class="data-vintage">Notional amounts are as publicly disseminated by the swap data repository. A trade larger than the regulatory cap for its asset class is disseminated at the cap value and is flagged in the source data. All notional totals are therefore lower bounds on true traded notional. The share of trades and of disseminated notional that is capped is printed beside each exhibit. Cap thresholds were revised effective 7 October 2024; comparisons across that date partly reflect the change in disclosure, not only in activity.</p><script>
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
  head.addEventListener('pointerdown', function(ev){
    var i = boundary(ev); if (i < 0) return;
    ev.preventDefault(); ev.stopPropagation();
    var startX = ev.clientX, startW = widths[i], startN = (i + 1 < n) ? widths[i + 1] : 0, shift = ev.shiftKey && i + 1 < n;
    function move(e){
      var dx = e.clientX - startX;
      if (shift) { var w = Math.max(mins[i], Math.min(startW + startN - mins[i + 1], startW + dx)); widths[i] = w; widths[i + 1] = startW + startN - w; }
      else widths[i] = Math.max(mins[i], startW + dx);
      apply(); lastDrag = Date.now();
    }
    function up(){ document.removeEventListener('pointermove', move); document.removeEventListener('pointerup', up); save(); }
    document.addEventListener('pointermove', move);
    document.addEventListener('pointerup', up);
  });
  head.addEventListener('dblclick', function(ev){
    var i = boundary(ev); if (i < 0) return;
    ev.preventDefault();
    var clone = t.cloneNode(true);
    clone.style.cssText = 'position:absolute;visibility:hidden;left:-9999px;top:0;width:auto;table-layout:auto;';
    var ccg = clone.querySelector('colgroup'); if (ccg) ccg.remove();
    document.body.appendChild(clone);
    var cths = clone.querySelectorAll(':scope > thead > tr > th');
    var w = cths[i] ? cths[i].offsetWidth : 0;
    clone.remove();
    if (w > 0) { widths[i] = Math.max(mins[i], w); apply(); save(); }
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
