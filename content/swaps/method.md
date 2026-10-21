---
title: "Method and data notes"
date: "2026-10-21"
lede: "Flow accounting, price-forming rules, spread conversion and the limits of the DTCC tape."
data_as_of: "Data: September 2026 file month (60,245,115 disseminated trades). Full history from September 2024 follows when the full parse completes."
---

<dl class="bw-summary"><div class="bw-sum-item"><dt>Data through</dt><dd>2026-09-30</dd></div><div class="bw-sum-item"><dt>Build date</dt><dd>2026-10-21</dd></div></dl><h2>What this section is</h2><p>Daily statistics computed from the DTCC swap data repository public tape: the record of swaps trades as disseminated under CFTC and SEC rules. DTCC's terms permit the publication of derived analytics and indicators from the tape and prohibit republishing it as a trade-level database. Every exhibit in this section is therefore an aggregate: the finest grain anywhere is one statistic per instrument per day, and no individual trade record appears on any page.</p><h2>Data window and depth</h2><p>This build consumes one file month, September 2026: 60,245,115 disseminated trades across the partitions listed below. Flow exhibits reach back to 1 June 2026 because the September files carry late disseminations of trades executed in the prior quarter; the dense record is September itself. The full parse, when it completes, extends every series back to September 2024, the start of the readable tape. Until then the exhibits grade as follows.</p><p>September-depth series: daily readings over the September window. The index five-year medians and dispersions, the currency par grids, curve spreads and tenor distributions, the flow counts and the chain lifecycle tables are computed daily over the window; they are series of September readings, not of full history.</p><p>September-depth indications: monthly levels, not series. The index-against-basket basis rests on the single names that disseminated a spread in the window; its supported form at this depth is a monthly level, and the daily line on the basis page is an indication. CMBX and the other thin index families support a monthly level indication only, from upfront-carrying records; no CMBX exhibit is published in this build.</p><p>Single-name curves: a name carries a curve page only where at least three tenor points clear the three-priced-trade floor in the window; eight names qualify in this build and are linked from the panel. Every other name with a priced five-year point appears in the five-year panel as a point, and no curve is drawn for it.</p><p>Withheld until full history: the tape-observed outstanding exhibit (see Outstanding and truncation below). Maturity walls are supported by chain counts by expiry year at this depth; notional sums by expiry year are not measured and are not published.</p><h2>Flow accounting</h2><p>A new trade is counted once, under its dissemination identifier, on the New York calendar date of its execution timestamp. Later records in the same chain (modifications and corrections) replace the original values rather than adding to them: price and notional statistics for a past day are computed on the final state of each chain as known at build time, so a page rebuilt after a correction shows the corrected figure, and each page prints its build date. A chain that contains an error record is excluded from every statistic. A termination removes the trade from outstanding at its termination date and is counted in the terminations exhibit, never in new-trade flow.</p><h2>Price-forming trades</h2><p>Price statistics (volume-weighted means, medians, curves, candles) use outright trades only. Package legs, curve and butterfly packages, compression trades and option exercises are excluded from prices and included in volume, with the excluded population identified by the tape's package indicator and event type fields. Where a cell rests on fewer than three trades it is suppressed and the coarser supported figure is printed instead.</p><h2>Notionals and caps</h2><p class="data-vintage">Notional amounts are as publicly disseminated by the swap data repository. A trade larger than the regulatory cap for its asset class is disseminated at the cap value and is flagged in the source data. All notional totals are therefore lower bounds on true traded notional. The share of trades and of disseminated notional that is capped is printed beside each exhibit. Cap thresholds were revised effective 7 October 2024; comparisons across that date partly reflect the change in disclosure, not only in activity.</p><p>Cross-currency notional totals are summed over trades whose first leg is denominated in US dollars and are labelled as such: the tape carries no conversion rates. Per-currency pages use native-currency notionals. A small number of disseminations carry a corrupt notional of exactly 1e20 (605 trades in this build, recorded per partition in the build manifest); any leg notional above one trillion dollars, or above 1e14 in another currency, is excluded from every notional aggregate.</p><h2>DV01</h2><p>DV01 is the par annuity approximation: DV01 equals notional times A times 0.0001, with A equal to (1 - (1 + r) to the power of -T) divided by r, r the traded fixed rate (for credit, the traded spread) and T the tenor in years. It is an activity measure for comparing flow across tenors, not a valuation.</p><h2>CDS spreads</h2><p>The traded spread is read from the dissemination's spread field, normalised by its notation code. Decimal form is used as printed. One notation code carries a price in points rather than a spread; those records are converted with the CDSW relation, spread equals coupon less (price minus 100) divided by 100 times the risky annuity, the annuity taken at the coupon plus 3 percent over the contract tenor. A third code carries basis points when the value exceeds 3 and is unusable below that. Two indices, CDX North America High Yield and CDX Emerging Markets, trade on price: part of their record places the contract price in the spread field under decimal notation, scaled by ten thousand. The statistics layer detects this per underlier (the two notations' medians agree as prices, within 3 points, on at least 20 trades each) and converts every affected record from price before any spread is computed. Single-name contracts trade at a standard coupon of 100 or 500 basis points with the difference settled as an upfront payment. The tape disseminates the upfront amount without its direction, so no spread is inferred from upfronts in this section: single-name spreads come only from trades that disseminate a spread directly, and pages print the priced-trade count beside every spread. The median upfront as a share of notional is printed on name pages as the distance measure the tape does support.</p><h2>Tenors</h2><p>For interest rate swaps, tenor is the period from the effective date to the expiry date, bucketed by exact months. For credit default swaps, tenor is the period from the execution date to the expiry date, which places the standard five-year contract in a four-to-six-year bucket around the semiannual roll dates. Bucket ranges are printed on the pages that use them.</p><h2>Clearing and venue fields</h2><p>The cleared field is disseminated as Y (cleared), I (submitted for clearing) or N (not cleared). This section prints both components and the sum; in the rates record the I code carries most cleared flow. The venue field carries a market identifier code; trades coded XOFF are off-facility and XXXX anonymised, and the on-SEF share counts the remainder. The collateralisation field is not populated in the partitions consumed by this build; the coverage is printed on the clearing page and no collateral mix is shown until a consumed partition populates the field.</p><h2>Outstanding and truncation</h2><p>The readable tape begins 2 September 2024. DTCC store files before that date are sealed in deep archive and are not retrievable, so positions executed before September 2024 and still open never appear. Any outstanding exhibit in this section is titled tape-observed and carries this note. In the current build the parsed window covers the file months listed below, and the outstanding exhibit is withheld until the parsed window covers the readable tape, because a stock figure built from a single month of flow would understate the market by construction.</p><h2>What the tape cannot say</h2><p>Counterparty identity is never disseminated, by law, so no participant breakdown exists in this section. The tape carries no valuations, so gross market value in the BIS sense cannot be computed from it. The clearing house is not identified in the public dissemination; clearing houses publish their own cleared volumes and open interest, which are the external context for the cleared shares shown here.</p><h2>Partitions consumed by this build</h2><p>CFTC commodities 2026 (112,513 rows), CFTC credits 2026 (55,183 rows), CFTC equities 2026 (15,851,375 rows), CFTC forex 2026 (1,387,913 rows), CFTC rates 2026 (603,383 rows), SEC credits 2026 (74,396 rows), SEC equities 2026 (42,158,191 rows), SEC rates 2026 (2,161 rows). Total records: 60,245,115. Every figure in the section is reproducible from these partitions alone.</p><script>
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
