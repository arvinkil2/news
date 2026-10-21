---
title: "AMD"
date: "2026-10-21"
lede: "Cross-dataset record for AMD: swaps CDS panel name, bond registry issuer, watched-list entry and fund-mark coverage, with links to each dataset's pages."
data_as_of: "Swaps panel: September 2026 file month. Fund marks: N-PORT 2026 Q3 panel, built 2026-10-20. Bond registry: master registry of 2026-10-14 with daily updates."
---

<dl class="bw-summary"><div class="bw-sum-item"><dt>Bonds in the registry, this issuer</dt><dd>9</dd></div><div class="bw-sum-item"><dt>Bonds with fund marks, latest panel</dt><dd>3 of 9</dd></div><div class="bw-sum-item"><dt>CDS five-year median, Sep 2026 (bp)</dt><dd>91.5</dd></div><div class="bw-sum-item"><dt>Watched list</dt><dd>daily</dd></div></dl><p>Advanced Micro Devices Inc appears under two name forms in two datasets: the swaps single-name CDS panel carries it as Advanced Micro Devices Inc, ADVANCED MICRO DEVICES,INC., and the bond registry carries it as ADVANCED MICRO DEVICES INC. This page records that resolution and links each dataset's own pages. The data itself stays in those pages.</p><h2>Names by dataset</h2><table class="market-table bw-grid" data-tid="ent-names-advanced-micro-devices-inc" data-def="[300, 340, 320]" data-min="[170, 200, 190]" data-fixed="[]">
<colgroup><col style="width:300px"><col style="width:340px"><col style="width:320px"></colgroup>
<thead><tr><th>Dataset</th><th>Name form</th><th>Page</th></tr></thead>
<tbody><tr><td>Swaps, single-name CDS panel</td><td>Advanced Micro Devices Inc</td><td><a href="/swaps/credit/names/">Single-name CDS panel</a></td></tr><tr><td>Swaps, single-name CDS panel</td><td>ADVANCED MICRO DEVICES,INC.</td><td><a href="/swaps/credit/names/">Single-name CDS panel</a></td></tr><tr><td>Bond registry</td><td>ADVANCED MICRO DEVICES INC</td><td><a href="/leverage/issuer/advanced-micro-devices/">Issuer page</a></td></tr><tr><td>FINRA watched list</td><td>ADVANCED MICRO DEVICES INC</td><td><a href="/leverage/monitor/">Leverage Monitor</a> (tier: daily)</td></tr></tbody></table> <button type="button" class="bw-reset" data-reset-for="ent-names-advanced-micro-devices-inc">Reset layout</button><h2>Bonds in the registry</h2><table class="market-table bw-grid" data-tid="ent-bonds-advanced-micro-devices-inc" data-def="[140, 560, 160]" data-min="[100, 300, 110]" data-fixed="[]" data-sort="1">
<colgroup><col style="width:140px"><col style="width:560px"><col style="width:160px"></colgroup>
<thead><tr><th>CUSIP</th><th>Security</th><th>Fund marks</th></tr></thead>
<tbody><tr><td><a href="/leverage/bond/007903ay3/">007903AY3</a></td><td>Notes</td><td>Not held</td></tr><tr><td><a href="/leverage/bond/007903ba4/">007903BA4</a></td><td>Notes</td><td>Not held</td></tr><tr><td><a href="/leverage/bond/007903bf3/">007903BF3</a></td><td>3.924% Notes due 2032</td><td>Priced, latest panel</td></tr><tr><td><a href="/leverage/bond/007903bg1/">007903BG1</a></td><td>4.393% Notes due 2052</td><td>Priced, latest panel</td></tr><tr><td><a href="/leverage/bond/007903bj5/">007903BJ5</a></td><td>4.319% Notes due 2028</td><td>Priced, latest panel</td></tr><tr><td><a href="/leverage/bond/007903bk2/">007903BK2</a></td><td>4.6% Notes due 2029</td><td>Not held</td></tr><tr><td><a href="/leverage/bond/007903bl0/">007903BL0</a></td><td>5% Notes due 2031</td><td>Not held</td></tr><tr><td><a href="/leverage/bond/007903bm8/">007903BM8</a></td><td>5.25% Notes due 2033</td><td>Not held</td></tr><tr><td><a href="/leverage/bond/007903bn6/">007903BN6</a></td><td>5.5% Notes due 2036</td><td>Not held</td></tr></tbody></table> <button type="button" class="bw-reset" data-reset-for="ent-bonds-advanced-micro-devices-inc">Reset layout</button><p>Fund marks, N-PORT 2026 Q3 panel: 3 of 9 of this issuer's bonds carry a priced fund position; the modal fund report date across those positions is 2026-06-30. Marks themselves are on the bond pages.</p><p>Resolution: suffix-unified full name equals registry issuer. Method: exact. Parent and subsidiary issuers are not merged: this page covers only the issuer strings named above.</p><script>
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
