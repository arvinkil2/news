---
title: "Projects"
date: "2026-10-30"
lede: "Standing pages for the largest tracked data center projects: the financing, the parties, and the dated record of developments, updated as events land."
data_as_of: ""
---


<p>The leverage program follows named projects through filings, county records and permitting. A project earns a standing page when its scale and record warrant one; the list is deliberately short. Each page carries the development record in date order and updates when a new filing, vote or decision lands.</p>
<div class="market-table-scroll"><table class="market-table bw-grid " data-tid="proj-index" data-def="[300, 150, 130, 420]" data-min="[180, 100, 92, 200]" data-fixed="[]">
<colgroup><col style="width:300px"><col style="width:150px"><col style="width:130px"><col style="width:420px"></colgroup>
<thead><tr><th>Project</th><th>Sponsor</th><th>Latest development</th><th>What happened</th></tr></thead>
<tbody>
<tr><td data-v="Project Jupiter"><a class="bond-link" href="/projects/project-jupiter/"><span class="bond-name">Project Jupiter</span><span class="bond-sub">Santa Teresa, Doña Ana County, New Mexico</span></td><td data-v="Oracle">Oracle</td><td data-v="2026-10-27">27 Oct 2026</td><td data-v="">County authorizes a potential breach notice</td></tr>
<tr><td data-v="Hyperion"><a class="bond-link" href="/projects/hyperion/"><span class="bond-name">Hyperion</span><span class="bond-sub">Richland Parish, Louisiana</span></td><td data-v="Meta Platforms (20% owner, tenant); Blue Owl Capital funds (80%)">Meta Platforms (20% owner, tenant); Blue Owl Capital funds (80%)</td><td data-v="2026-07-13">13 Jul 2026</td><td data-v="">Meta expands Hyperion to 5 GW</td></tr>
<tr><td data-v="Sopaipilla"><a class="bond-link" href="/projects/sopaipilla/"><span class="bond-name">Sopaipilla</span><span class="bond-sub">El Paso, Texas</span></td><td data-v="Meta Platforms (20% owner, tenant); BlackRock funds via GIP and HPS (80%)">Meta Platforms (20% owner, tenant); BlackRock funds via GIP and HPS (80%)</td><td data-v="2026-07-28">28 Jul 2026</td><td data-v="">Meta announces the BlackRock joint venture</td></tr>
<tr><td data-v="Galaxy Helios"><a class="bond-link" href="/projects/galaxy-helios/"><span class="bond-name">Galaxy Helios</span><span class="bond-sub">Dickens County, Texas</span></td><td data-v="Galaxy Digital Inc. (owner and operator); CoreWeave, sole tenant">Galaxy Digital Inc. (owner and operator); CoreWeave, sole tenant</td><td data-v="2026-10-27">27 Oct 2026</td><td data-v="">Q3 2026: first full quarter of Phase I revenue</td></tr>
</tbody></table></div>

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
