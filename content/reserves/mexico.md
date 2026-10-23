---
title: "Mexico petroleum reserves"
date: "2026-10-23"
lede: "Mexico: obligated industry stockholding under the IEA system, administered by Ministry of Energy (SENER) Public Policy on Minimum Storage of Petroleum Products, mandatory for marketing and distribution permit holders selling gasoline, diesel and jet fuel. No government strategic petroleum reserve."
data_as_of: "No current level published by this government. See the note below."
---

<dl class="bw-summary"><div class="bw-sum-item"><dt>System</dt><dd>IEA</dd></div><div class="bw-sum-item"><dt>Holding model</dt><dd>obligated industry</dd></div><div class="bw-sum-item"><dt>Stockholding body</dt><dd>Ministry of Energy (SENER) Public Policy on Minimum Storage of Petroleum Products, mandatory for marketing and distribution permit holders selling gasoline, diesel and jet fuel. No government strategic petroleum reserve</dd></div><div class="bw-sum-item"><dt>Obligation</dt><dd>No IEA stockholding obligation as a net exporter. Domestically, the SENER minimum storage policy is mandatory for permit holders that sell gasoline, diesel and jet fuel to service stations or end users (IEA policy page)</dd></div><div class="bw-sum-item"><dt>Reporting</dt><dd>not published</dd></div></dl><p>Mexico's operative national rule is the domestic minimum storage policy for petroleum products; there is no government owned crude reserve.</p><h2>Latest disclosure</h2><p>The government does not publish a current strategic petroleum reserve level. No government SPR level was found on an official page; commercial and Pemex operating stocks are not published as an SPR total.</p><h2>Last recorded action</h2><p>2026-03-11: release of 3.9 million barrels. Mexican contribution to the IEA collective action of 11 March 2026 was 3.9 million barrels recorded by the IEA as an other contribution (a production increase), not a stock release. Public stocks and obligated industry stocks were both zero in the IEA table. (<a href="https://www.iea.org/news/iea-confirms-member-country-contributions-to-collective-action-to-release-oil-stocks-in-response-to-middle-east-disruptions">source</a>)</p><p class="data-vintage">Confidence note: Model and policy fields verified from IEA pages opened; the level field is a verified absence from those pages rather than a published figure.</p><script>
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
