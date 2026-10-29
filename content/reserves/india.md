---
title: "India petroleum reserves"
date: "2026-10-29"
lede: "India: government stockholding under the National system, administered by Indian Strategic Petroleum Reserves Limited (ISPRL), a special purpose vehicle of the Government of India under the Ministry of Petroleum and Natural Gas."
data_as_of: "Latest level: 2026-03-23, from Ministry of Petroleum and Natural Gas written answer to Rajya Sabha Unstarred Question 3501."
---

<dl class="bw-summary"><div class="bw-sum-item"><dt>System</dt><dd>National</dd></div><div class="bw-sum-item"><dt>Holding model</dt><dd>government</dd></div><div class="bw-sum-item"><dt>Stockholding body</dt><dd>Indian Strategic Petroleum Reserves Limited (ISPRL), a special purpose vehicle of the Government of India under the Ministry of Petroleum and Natural Gas</dd></div><div class="bw-sum-item"><dt>Obligation</dt><dd>No statutory days obligation was stated in the official sources checked. Phase I capacity is 5.33 million tonnes, estimated at about 9.5 days of crude oil requirement; Phase II approval covers a further 6.5 million tonnes on a public private partnership basis</dd></div><div class="bw-sum-item"><dt>Reporting</dt><dd>irregular</dd></div><div class="bw-sum-item"><dt>Latest level</dt><dd>3.372 million tonnes</dd></div><div class="bw-sum-item"><dt>Level date</dt><dd>2026-03-23</dd></div><div class="bw-sum-item"><dt>Crude</dt><dd>3.4</dd></div></dl><p>Phase I sites are Visakhapatnam 1.33 million tonnes, Mangaluru 1.5 million tonnes and Padur 2.5 million tonnes. The March 2026 fill of 3.372 million tonnes was about 64 percent of the 5.33 million tonne capacity. PIB stated in 2021 that all Phase I facilities had been filled at that time; the 2026 parliamentary answer supersedes that statement for level purposes.</p><h2>Last recorded action</h2><p>2021-11-23: release of 5.0 million barrels. Government of India agreed to release 5 million barrels of crude from the Strategic Petroleum Reserves in parallel and in consultation with the United States, China, Japan and the Republic of Korea (Press Information Bureau). (<a href="https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1774288&amp;reg=48&amp;lang=2">source</a>)</p><h2>Recorded actions</h2><table class="market-table bw-grid" data-tid="res-ev-india" data-def="[96, 150, 92, 130, 130, 100, 90]" data-min="[84, 110, 76, 110, 110, 84, 70]" data-fixed="[]" data-sort="1">
<colgroup><col style="width:96px"><col style="width:150px"><col style="width:92px"><col style="width:130px"><col style="width:130px"><col style="width:100px"><col style="width:90px"></colgroup>
<thead><tr><th>Date</th><th>Actor</th><th>Type</th><th data-num="1">Announced (million barrels)</th><th data-num="1">Delivered (million barrels)</th><th>Status</th><th>Source</th></tr></thead>
<tbody><tr><td>2021-11-23</td><td>India (Government of India)</td><td>release</td><td>5.0</td><td>not stated</td><td>committed</td><td><a href="https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1774288&amp;reg=48&amp;lang=2">Press Information Bureau, Ministry of Petroleum and Natural Gas, 23 November 2021</a></td></tr></tbody></table> <button type="button" class="bw-reset" data-reset-for="res-ev-india">Reset layout</button><p class="data-vintage">Level source: <a href="https://sansad.in/getFile/annex/270/AU3501_haHCqP.pdf?source=pqars">Ministry of Petroleum and Natural Gas written answer to Rajya Sabha Unstarred Question 3501</a>. Record confidence: verified.</p><script>
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
