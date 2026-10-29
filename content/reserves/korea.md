---
title: "Korea petroleum reserves"
date: "2026-10-29"
lede: "Korea: mixed stockholding under the IEA system, administered by Ministry of Trade, Industry and Resources sets policy; Korea National Oil Corporation (KNOC) operates nine stockpiling bases with total capacity reported at 146 million barrels."
data_as_of: "Latest level: 2025-12-22, from Ministry of Trade, Industry and Resources statement, via Yonhap and Korea JoongAng Daily."
---

<dl class="bw-summary"><div class="bw-sum-item"><dt>System</dt><dd>IEA</dd></div><div class="bw-sum-item"><dt>Holding model</dt><dd>mixed</dd></div><div class="bw-sum-item"><dt>Stockholding body</dt><dd>Ministry of Trade, Industry and Resources sets policy; Korea National Oil Corporation (KNOC) operates nine stockpiling bases with total capacity reported at 146 million barrels</dd></div><div class="bw-sum-item"><dt>Obligation</dt><dd>IEA: 90 days of net imports</dd></div><div class="bw-sum-item"><dt>Reporting</dt><dd>irregular</dd></div><div class="bw-sum-item"><dt>Latest level</dt><dd>195.0 million barrels</dd></div><div class="bw-sum-item"><dt>Level date</dt><dd>2025-12-22</dd></div><div class="bw-sum-item"><dt>Cover</dt><dd>210 days</dd></div></dl><p>The December 2025 ministry figure is government stocks of about 100 million barrels plus private stocks of about 95 million barrels, and it predates the 2026 drawdown. Korea also holds joint storage with foreign national oil companies.</p><h2>Last recorded action</h2><p>2026-03-11: release of 22.5 million barrels. Korean contribution to the IEA collective action of 11 March 2026, recorded by the IEA at 22.5 million barrels (22.46 in Korean ministry reporting) and described by the ministry as the largest Korean release decision to date. (<a href="https://www.iea.org/news/iea-confirms-member-country-contributions-to-collective-action-to-release-oil-stocks-in-response-to-middle-east-disruptions">source</a>)</p><h2>Recorded actions</h2><table class="market-table bw-grid" data-tid="res-ev-korea" data-def="[96, 150, 92, 130, 130, 100, 90]" data-min="[84, 110, 76, 110, 110, 84, 70]" data-fixed="[]" data-sort="1">
<colgroup><col style="width:96px"><col style="width:150px"><col style="width:92px"><col style="width:130px"><col style="width:130px"><col style="width:100px"><col style="width:90px"></colgroup>
<thead><tr><th>Date</th><th>Actor</th><th>Type</th><th data-num="1">Announced (million barrels)</th><th data-num="1">Delivered (million barrels)</th><th>Status</th><th>Source</th></tr></thead>
<tbody><tr><td>2022-04</td><td>South Korea (Ministry of Trade, Industry and Energy)</td><td>release</td><td>7.2</td><td>not stated</td><td>committed</td><td><a href="https://www.iea.org/news/iea-confirms-member-country-contributions-to-second-collective-action-to-release-oil-stocks-in-response-to-russias-invasion-of-ukraine">IEA second action country contributions as reported in secondary coverage; combined total reported by Yonhap in 2026</a></td></tr><tr><td>2022-03-05</td><td>South Korea (Ministry of Trade, Industry and Energy)</td><td>release</td><td>4.4</td><td>not stated</td><td>committed</td><td><a href="https://www.koreajoongangdaily.com/business/korea-to-release-442-million-barrels-of-oil-reserves-due-to-ukraine-crisis/10281725">Korea JoongAng Daily (Yonhap), reporting the ministry</a></td></tr><tr><td>2021-12-23</td><td>South Korea (Ministry of Trade, Industry and Energy; KNOC distribution)</td><td>loan</td><td>3.2</td><td>not stated</td><td>committed</td><td><a href="https://www.koreajoongangdaily.com/business/317-million-barrels-of-oil-to-be-released-from-strategic-reserves/11311987">Korea JoongAng Daily, reporting the ministry announcement</a></td></tr></tbody></table> <button type="button" class="bw-reset" data-reset-for="res-ev-korea">Reset layout</button><p class="data-vintage">Level source: <a href="https://koreajoongangdaily.joins.com/news/2025-12-26/business/industry/Govt-expands-oil-reserves-to-100-million-barrels-to-better-manage-petroleum-supply/2483480">Ministry of Trade, Industry and Resources statement, via Yonhap and Korea JoongAng Daily</a>. Record confidence: partial.</p><p class="data-vintage">Confidence note: System and IEA action verified from IEA pages; the latest level and capacity details rest on secondary reporting of ministry and KNOC statements.</p><script>
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
