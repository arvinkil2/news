---
title: "Japan petroleum reserves"
date: "2026-10-23"
lede: "Japan: mixed stockholding under the IEA system, administered by Ministry of Economy, Trade and Industry (METI) and the Agency for Natural Resources and Energy set policy; JOGMEC (Japan Organization for Metals and Energy Security) manages the national stockpile bases; specified importers and distributors hold private stocks."
data_as_of: "Latest level: 2026-07-31, from Agency for Natural Resources and Energy monthly stockpile data, via secondary summary."
---

<dl class="bw-summary"><div class="bw-sum-item"><dt>System</dt><dd>IEA</dd></div><div class="bw-sum-item"><dt>Holding model</dt><dd>mixed</dd></div><div class="bw-sum-item"><dt>Stockholding body</dt><dd>Ministry of Economy, Trade and Industry (METI) and the Agency for Natural Resources and Energy set policy; JOGMEC (Japan Organization for Metals and Energy Security) manages the national stockpile bases; specified importers and distributors hold private stocks</dd></div><div class="bw-sum-item"><dt>Obligation</dt><dd>IEA: 90 days of net imports. Under the Oil Stockpiling Act, JOGMEC manages public stocks and specified oil importers and distributors must hold a minimum level set by METI ordinance, normally 70 days for private stocks, reduced to 55 days in 2026</dd></div><div class="bw-sum-item"><dt>Reporting</dt><dd>monthly</dd></div><div class="bw-sum-item"><dt>Latest level</dt><dd>57.52 million kilolitres (product equivalent)</dd></div><div class="bw-sum-item"><dt>Level date</dt><dd>2026-07-31</dd></div><div class="bw-sum-item"><dt>Cover</dt><dd>206 days</dd></div></dl><p>Japan also holds joint stockpiles with producing countries on Japanese territory. End February 2026 cover was reported at about 243 to 254 days depending on statement date and basis, before the 2026 releases.</p><h2>Last recorded action</h2><p>2026-03-11: release of 79.8 million barrels. Japanese contribution to the IEA collective action of 11 March 2026 recorded by the IEA at 79.8 million barrels (54.0 public stocks and 25.8 obligated industry stocks). National releases began on 26 March 2026 from national bases, and METI maintained the 15 day reduction of the private obligation (70 to 55 days) through 15 June 2026. (<a href="https://www.iea.org/news/iea-confirms-member-country-contributions-to-collective-action-to-release-oil-stocks-in-response-to-middle-east-disruptions">source</a>)</p><h2>Recorded actions</h2><table class="market-table bw-grid" data-tid="res-ev-japan" data-def="[96, 150, 92, 130, 130, 100, 90]" data-min="[84, 110, 76, 110, 110, 84, 70]" data-fixed="[]" data-sort="1">
<colgroup><col style="width:96px"><col style="width:150px"><col style="width:92px"><col style="width:130px"><col style="width:130px"><col style="width:100px"><col style="width:90px"></colgroup>
<thead><tr><th>Date</th><th>Actor</th><th>Type</th><th data-num="1">Announced (million barrels)</th><th data-num="1">Delivered (million barrels)</th><th>Status</th><th>Source</th></tr></thead>
<tbody><tr><td>2022-04-07</td><td>Japan (METI)</td><td>release</td><td>15.0</td><td>not stated</td><td>committed</td><td><a href="https://www.hellenicshippingnews.com/japan-to-start-releasing-6-mil-barrels-private-oil-reserves-in-iea-joint-effort/">METI announcement as reported by S and P Global Platts, via Hellenic Shipping News</a></td></tr><tr><td>2022-03-04</td><td>Japan (METI)</td><td>release</td><td>7.5</td><td>not stated</td><td>committed</td><td><a href="https://www.hellenicshippingnews.com/japan-starts-oil-release-from-private-petroleum-reserves-in-iea-joint-effort/">METI announcement as reported by S and P Global Platts, via Hellenic Shipping News</a></td></tr><tr><td>2011-06-23</td><td>Japan</td><td>release</td><td>7.9</td><td>not stated</td><td>committed</td><td><a href="https://www.energyintel.com/0000017b-a7bf-de4c-a17b-e7ff0ab40000">Energy Intelligence, 29 June 2011</a></td></tr><tr><td>2011-03-14</td><td>Japan (METI)</td><td>release</td><td>not stated</td><td>not stated</td><td>completed</td><td><a href="https://aperc.or.jp/file/2015/12/16/The_Impact_on_Oil_Distribution_by_the_Great_East_Japan_Earthquake_and_the_Future_Issues_and_Countermeasures.pdf">Asia Pacific Energy Research Centre (APERC), The Impact on Oil Distribution by the Great East Japan Earthquake</a></td></tr></tbody></table> <button type="button" class="bw-reset" data-reset-for="res-ev-japan">Reset layout</button><p class="data-vintage">Level source: <a href="https://edgeconsultancykw.com/japan-powerr-asia-energy-financing-ief17-206-days/">Agency for Natural Resources and Energy monthly stockpile data, via secondary summary</a>. Record confidence: partial.</p><p class="data-vintage">Confidence note: Obligation and 2026 actions verified from METI and IEA pages opened; the latest level rests on secondary reporting of Agency for Natural Resources and Energy monthly data, as the official monthly level table was not retrieved as text in this pass.</p><script>
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
