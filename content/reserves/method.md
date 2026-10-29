---
title: "Method and data notes"
date: "2026-10-29"
lede: "Definitions, unit policy, confidence grades and the update cadence of every source behind the reserves section."
data_as_of: "Method as of 23 October 2026."
---

<h2>What counts as a reserve</h2>
<p>The dataset covers stocks held for emergency purposes: government
stocks in state storage, stocks held by a central stockholding entity,
and industry stocks held under a legal stockholding obligation. Ordinary
commercial inventories above the obligated level are excluded. Where a
source publishes a combined figure, the page says so.</p>
<h2>Holding models</h2>
<p><strong>Government</strong>: the state owns the stock and the storage.
<strong>Agency</strong>: a central stockholding entity owns or controls
the stock, funded by levies on industry or consumers.
<strong>Obligated industry</strong>: refiners and importers must hold a
set number of days of supply on their own sites.
<strong>Mixed</strong>: a combination, most often government crude
stocks alongside obligated product stocks.</p>
<h2>Units</h2>
<p>Figures are printed in the unit the source publishes. Eurostat
reports thousand tonnes. The United States reports barrels. Japan
reports kilolitres in product equivalent. No conversion is applied
inside any table, because crude and product tonnes convert at different
rates and a silent conversion would invent precision.</p>
<h2>Announced and delivered</h2>
<p>Announced is the volume pledged at the decision date. Delivered is
the volume official sources record as moved. Where no final delivered
total is published, the delivered field reads not stated. Estimates by
third parties are never entered as delivered figures.</p>
<h2>Confidence grades</h2>
<p><strong>Verified</strong>: the record rests on an official page or
dataset read directly. <strong>Partial</strong>: most fields are
verified, and the country page states which field rests on secondary
reporting. <strong>Reported</strong>: used in the event ledger where an
action is documented by credible reporting but no official figure was
published.</p>
<h2>Update cadences</h2>
<table class="market-table bw-grid" data-tid="res-cadence" data-def="[260, 120, 340]" data-min="[180, 90, 220]" data-fixed="[]">
<colgroup><col style="width:260px"><col style="width:120px"><col style="width:340px"></colgroup>
<thead><tr><th>Source</th><th>Cadence</th><th>What it feeds</th></tr></thead>
<tbody><tr><td>EIA Weekly Petroleum Status Report</td><td>Weekly</td><td>United States level</td></tr><tr><td>Eurostat nrg_stk_oilm</td><td>Monthly</td><td>All 27 EU member levels and histories</td></tr><tr><td>METI and Agency for Natural Resources and Energy</td><td>Monthly</td><td>Japan level and cover days</td></tr><tr><td>IEA and DOE releases</td><td>Event driven</td><td>Collective actions and the event ledger</td></tr><tr><td>KNOC, ISPRL, national ministries</td><td>Irregular, checked monthly</td><td>Korea, India and other non EU national levels</td></tr><tr><td>China National Bureau of Statistics and NEA</td><td>Irregular, checked quarterly</td><td>China official disclosures, when any are made</td></tr></tbody></table> <button type="button" class="bw-reset" data-reset-for="res-cadence">Reset layout</button>
<h2>Known gaps</h2>
<p>China does not publish a current strategic reserve level. Its page
records the last official disclosure and its date, and no estimate is
substituted. The United States weekly history chart is pending: the
EIA retired the legacy data feeds behind its old series pages in a
site redesign, and the replacement route is being restored. The
current United States level is taken from the Weekly Petroleum Status
Report each week in the meantime. Czechia's Eurostat return for August
2026 shows 360 thousand tonnes against 2,031 thousand tonnes in July;
it is printed as published and may be a partial return.</p>
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
