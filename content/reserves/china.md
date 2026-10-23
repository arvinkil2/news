---
title: "China petroleum reserves"
date: "2026-10-23"
lede: "China: mixed stockholding under the National system, administered by National Development and Reform Commission and National Energy Administration for energy policy; National Food and Strategic Reserves Administration for national reserve operations and auctions; state oil companies hold and rotate much of the physical stock."
data_as_of: "No current level published by this government. See the note below."
---

<dl class="bw-summary"><div class="bw-sum-item"><dt>System</dt><dd>National</dd></div><div class="bw-sum-item"><dt>Holding model</dt><dd>mixed</dd></div><div class="bw-sum-item"><dt>Stockholding body</dt><dd>National Development and Reform Commission and National Energy Administration for energy policy; National Food and Strategic Reserves Administration for national reserve operations and auctions; state oil companies hold and rotate much of the physical stock</dd></div><div class="bw-sum-item"><dt>Obligation</dt><dd>No published numeric SPR obligation was found in an official source checked. China is an IEA association country, not an IEA member, so the IEA 90 day member obligation does not apply. The Energy Law framework in force from 2025 combines government reserves with enterprise reserves</dd></div><div class="bw-sum-item"><dt>Reporting</dt><dd>no regular publication</dd></div></dl><p>Inferred draws and builds in 2026 calculated by analysts from imports, production and refinery runs are estimates, not government published actions, so no 2026 release volume is recorded.</p><h2>Latest disclosure</h2><p>China does not publish a current strategic petroleum reserve level. Official disclosures have been sporadic and partial, covering build phases and individual auctions rather than a running total, and no current official total was published in the sources checked. Analyst estimates of total Chinese crude inventories are not official figures and are not used here.</p><h2>Last recorded action</h2><p>2021-09-14: sale of 7.4 million barrels. First public auction from Chinese state reserves, announced by the National Food and Strategic Reserves Administration to ease raw material price pressure, with the auction held on 24 September 2021. A further release process was confirmed in November 2021 without a published volume. (<a href="https://www.oxfordenergy.org/publications/chinas-spr-release-a-test-of-mechanisms-rather-than-a-show-of-market-might/">source</a>)</p><h2>Recorded actions</h2><table class="market-table bw-grid" data-tid="res-ev-china" data-def="[96, 150, 92, 130, 130, 100, 90]" data-min="[84, 110, 76, 110, 110, 84, 70]" data-fixed="[]" data-sort="1">
<colgroup><col style="width:96px"><col style="width:150px"><col style="width:92px"><col style="width:130px"><col style="width:130px"><col style="width:100px"><col style="width:90px"></colgroup>
<thead><tr><th>Date</th><th>Actor</th><th>Type</th><th data-num="1">Announced (million barrels)</th><th data-num="1">Delivered (million barrels)</th><th>Status</th><th>Source</th></tr></thead>
<tbody><tr><td>2021-09-14</td><td>China (National Food and Strategic Reserves Administration)</td><td>sale</td><td>7.4</td><td>not stated</td><td>committed</td><td><a href="https://www.hellenicshippingnews.com/china-to-release-first-batch-of-7-38-mil-barrels-from-state-reserves-for-sept-24-auction/">S and P Global Platts reporting of the NFSRA statement, via Hellenic Shipping News</a></td></tr></tbody></table> <button type="button" class="bw-reset" data-reset-for="res-ev-china">Reset layout</button><p class="data-vintage">Confidence note: Non publication and IEA association status are well supported; the obligation summary and the 2021 auction volume rest on secondary legal and Oxford Institute for Energy Studies reporting rather than an official Chinese page opened.</p><script>
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
