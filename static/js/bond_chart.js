/* Bond detail chart (Apache ECharts). Progressive enhancement: the
   container holds a server-rendered SVG fallback; this script
   replaces it with an interactive chart built from the JSON data
   block on the same page. Trades are aggregated to one point per
   trade date: the line is the day's last print, the whisker at
   each point spans the day's high and low prints, and the line
   breaks across gaps longer than 30 days (these bonds trade
   episodically; the chart does not imply a continuous market).
   The yield view is the same construction from the day's yield
   values; days whose trades carry no yield never enter it.
   Fund marks are hollow squares at period end, price view only.
   Volume is the day total of reported floors, in a lower panel. */
(function () {
  "use strict";
  var box = document.querySelector(".bond-chart-e");
  if (!box || typeof echarts === "undefined") return;
  var dataEl = document.querySelector(".bond-chart-data");
  if (!dataEl) return;
  var D;
  try { D = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var trades = D.t || [];   /* [ts, price, yield, volFloor|null] */
  var marks = D.m || [];    /* [ts, price] */
  if (!trades.length && !marks.length) return;
  var DAY = 86400000;
  var INK = "#3f4750", MARK = "#b25f09", GRID = "#e3ded2",
      WHISK = "#a8adb3";

  /* Daily aggregation. Embed timestamps are the trade datetime
     (naive UTC epoch) plus 12 hours, so the trade date is the UTC
     date of (ts - 12h). Trades arrive sorted by (date, time), so
     the last row of a day is its last print. The point sits at
     noon UTC on the trade date. */
  var days = [];
  var dayByTs = {};
  trades.forEach(function (r) {
    var d = new Date(r[0] - 12 * 3600 * 1000);
    var x = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(),
                     d.getUTCDate(), 12);
    var g = dayByTs[x];
    if (!g) {
      g = dayByTs[x] = { x: x, n: 0,
        pc: null, ph: null, pl: null,
        yc: null, yh: null, yl: null,
        vol: 0, volN: 0 };
      days.push(g);
    }
    g.n += 1;
    if (r[1] !== null && r[1] !== undefined) {
      g.pc = r[1];
      g.ph = g.ph === null ? r[1] : Math.max(g.ph, r[1]);
      g.pl = g.pl === null ? r[1] : Math.min(g.pl, r[1]);
    }
    if (r[2] !== null && r[2] !== undefined) {
      g.yc = r[2];
      g.yh = g.yh === null ? r[2] : Math.max(g.yh, r[2]);
      g.yl = g.yl === null ? r[2] : Math.min(g.yl, r[2]);
    }
    if (r[3] !== null && r[3] !== undefined) {
      g.vol += r[3]; g.volN += 1;
    }
  });
  var yieldDays = days.filter(function (g) { return g.yc !== null; });

  function gapped(pts, maxDays) {
    var out = [];
    for (var i = 0; i < pts.length; i++) {
      if (i && pts[i][0] - pts[i - 1][0] > maxDays * DAY) {
        out.push([pts[i][0] - 1, null]);
      }
      out.push(pts[i]);
    }
    return out;
  }
  function fmtVol(v) {
    if (v === null || v === undefined) return "n/a";
    return "$" + Math.round(v).toLocaleString("en-US");
  }
  function fmtDate(ts) {
    var d = new Date(ts);
    return d.getUTCFullYear() + "-" +
      String(d.getUTCMonth() + 1).padStart(2, "0") + "-" +
      String(d.getUTCDate()).padStart(2, "0");
  }

  function option(mode) {
    var isPrice = mode === "price";
    var src = isPrice ? days : yieldDays;
    var linePts = [], whisk = [], vPts = [];
    src.forEach(function (g) {
      var c = isPrice ? g.pc : g.yc,
          h = isPrice ? g.ph : g.yh,
          l = isPrice ? g.pl : g.yl;
      if (c === null) return;
      linePts.push([g.x, c]);
      whisk.push([g.x, l, h]);
    });
    days.forEach(function (g) {
      if (g.volN) vPts.push([g.x, g.vol]);
    });
    var series = [
      { name: "Daily high–low", type: "custom",
        xAxisIndex: 0, yAxisIndex: 0, data: whisk, silent: true,
        renderItem: function (params, api) {
          var x = api.value(0), lo = api.value(1),
              hi = api.value(2);
          var pLo = api.coord([x, lo]), pHi = api.coord([x, hi]);
          if (Math.abs(pLo[1] - pHi[1]) < 0.6) {
            return { type: "line",
              shape: { x1: pLo[0] - 2, y1: pLo[1],
                       x2: pLo[0] + 2, y2: pLo[1] },
              style: { stroke: WHISK, lineWidth: 1 } };
          }
          return { type: "line",
            shape: { x1: pLo[0], y1: pLo[1],
                     x2: pHi[0], y2: pHi[1] },
            style: { stroke: WHISK, lineWidth: 1 } };
        }, z: 2 },
      { name: isPrice ? "Last print (daily)" : "Yield (daily)",
        type: "line", xAxisIndex: 0, yAxisIndex: 0,
        data: gapped(linePts, 30), showSymbol: true,
        symbolSize: 4, connectNulls: false,
        lineStyle: { width: 1.3, color: INK },
        itemStyle: { color: INK }, z: 3 },
      { name: "Volume (reported floor)", type: "bar",
        xAxisIndex: 1, yAxisIndex: 1, data: vPts, silent: true,
        itemStyle: { color: INK, opacity: 0.45 }, z: 2 }
    ];
    if (isPrice && marks.length) {
      series.push(
        { name: "Fund marks", type: "line", xAxisIndex: 0,
          yAxisIndex: 0, data: marks, showSymbol: false,
          connectNulls: false, silent: true,
          lineStyle: { width: 1.2, color: MARK, type: "dashed",
                       opacity: 0.7 },
          itemStyle: { color: MARK }, z: 4 },
        { name: "Fund marks", type: "scatter", xAxisIndex: 0,
          yAxisIndex: 0, data: marks, symbol: "rect", symbolSize: 9,
          itemStyle: { color: "none", borderColor: MARK,
                       borderWidth: 1.6 }, z: 5 });
    }
    return {
      animation: false,
      textStyle: { fontFamily: "inherit", color: "#1a1a1a" },
      grid: [
        { left: 56, right: 18, top: 26, height: "56%" },
        { left: 56, right: 18, top: "74%", height: "13%" }
      ],
      xAxis: [
        { type: "time", gridIndex: 0,
          axisLine: { lineStyle: { color: "#999" } },
          splitLine: { show: true, lineStyle: { color: GRID } } },
        { type: "time", gridIndex: 1,
          axisLine: { lineStyle: { color: "#999" } },
          axisLabel: { show: false },
          splitLine: { show: false } }
      ],
      yAxis: [
        { type: "value", scale: true, gridIndex: 0,
          name: isPrice ? "Price, % of par" : "Yield, %",
          nameLocation: "end",
          splitLine: { lineStyle: { color: GRID } } },
        { type: "value", gridIndex: 1, name: "Volume $",
          nameLocation: "end",
          axisLabel: { formatter: function (v) {
            return v >= 1e6 ? (v / 1e6) + "M" :
                   v >= 1e3 ? (v / 1e3) + "K" : v; } },
          splitLine: { show: false } }
      ],
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "cross",
                       lineStyle: { color: "#999" } },
        formatter: function (ps) {
          if (!ps || !ps.length) return "";
          var ts = ps[0].value[0];
          var dec = isPrice ? 2 : 3;
          var out = [fmtDate(ts)];
          var g = dayByTs[ts];
          if (g) {
            var c = isPrice ? g.pc : g.yc,
                h = isPrice ? g.ph : g.yh,
                l = isPrice ? g.pl : g.yl;
            if (c !== null && c !== undefined) {
              out.push((isPrice ? "Last " : "Yield ") +
                       c.toFixed(dec));
              out.push("High " + h.toFixed(dec));
              out.push("Low " + l.toFixed(dec));
            }
            out.push("Trades " + g.n.toLocaleString("en-US"));
            out.push("Volume " +
                     (g.volN ? fmtVol(g.vol) : "n/a"));
          }
          ps.forEach(function (p) {
            if (p.seriesName === "Fund marks" &&
                p.value[1] !== null && p.value[1] !== undefined) {
              out.push(p.marker + "Fund mark " +
                       p.value[1].toFixed(2));
            }
          });
          return out.join("<br/>");
        }
      },
      dataZoom: [
        { type: "inside", xAxisIndex: [0, 1] },
        { type: "slider", xAxisIndex: [0, 1], height: 16,
          bottom: 4, showDetail: false,
          borderColor: "#3f4750",
          fillerColor: "rgba(63,71,80,0.15)",
          handleStyle: { color: "#3f4750", borderColor: "#3f4750" },
          moveHandleStyle: { color: "#3f4750" },
          textStyle: { color: "#6b7280" },
          dataBackground: {
            lineStyle: { color: "#9aa0a6" },
            areaStyle: { color: "rgba(63,71,80,0.10)" } },
          selectedDataBackground: {
            lineStyle: { color: "#3f4750" },
            areaStyle: { color: "rgba(63,71,80,0.15)" } } }
      ],
      series: series
    };
  }

  box.innerHTML = "";
  var chart = echarts.init(box, null, { renderer: "canvas" });
  var mode = "price";
  chart.setOption(option(mode));
  var bp = document.getElementById("btn-price");
  var by = document.getElementById("btn-yield");
  if (by && !yieldDays.length) {
    /* No trade on record carries a yield (common for ABS):
       do not offer a yield view that would render empty. */
    by.disabled = true;
    by.setAttribute("aria-disabled", "true");
    by.style.opacity = "0.45";
    by.style.pointerEvents = "none";
  }
  function setMode(m) {
    if (m === "yield" && !yieldDays.length) return;
    mode = m;
    if (bp) bp.setAttribute("aria-pressed", m === "price");
    if (by) by.setAttribute("aria-pressed", m === "yield");
    chart.setOption(option(mode), { notMerge: true });
  }
  if (bp) bp.addEventListener("click", function () { setMode("price"); });
  if (by) by.addEventListener("click", function () { setMode("yield"); });
  window.addEventListener("resize", function () { chart.resize(); });
})();
