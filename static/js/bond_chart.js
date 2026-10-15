/* Bond detail chart (Apache ECharts). Progressive enhancement: the
   container holds a server-rendered SVG fallback; this script
   replaces it with an interactive chart built from the JSON data
   block on the same page. Trades are points on a true time axis,
   joined by a line only across gaps of 30 days or less. Fund marks
   are hollow squares at period end. Volume is a separate panel. */
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
  var INK = "#3f4750", MARK = "#b3541e", GRID = "#e3ded2";

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
    var tPts = [], vPts = [];
    trades.forEach(function (r) {
      var v = isPrice ? r[1] : r[2];
      if (v !== null && v !== undefined) tPts.push([r[0], v]);
      if (r[3] !== null && r[3] !== undefined) vPts.push([r[0], r[3]]);
    });
    var series = [
      { name: isPrice ? "Trades (price)" : "Trades (yield)",
        type: "line", xAxisIndex: 0, yAxisIndex: 0,
        data: gapped(tPts, 30), showSymbol: false,
        connectNulls: false, silent: true,
        lineStyle: { width: 1.2, color: INK, opacity: 0.55 },
        itemStyle: { color: INK }, z: 2 },
      { name: isPrice ? "Trades" : "Trades",
        type: "scatter", xAxisIndex: 0, yAxisIndex: 0,
        data: tPts, symbolSize: 5,
        itemStyle: { color: INK, opacity: 0.85 }, z: 3 },
      { name: "Volume (reported floor)", type: "bar",
        xAxisIndex: 1, yAxisIndex: 1, data: vPts,
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
          var out = [fmtDate(ps[0].value[0])];
          ps.forEach(function (p) {
            if (p.value[1] === null ||
                p.value[1] === undefined) return;
            if (p.seriesName.indexOf("Volume") === 0) {
              out.push(p.marker + "Volume " + fmtVol(p.value[1]));
            } else if (p.seriesName === "Fund marks") {
              out.push(p.marker + "Fund mark " +
                       p.value[1].toFixed(2));
            } else {
              out.push(p.marker + p.seriesName + " " +
                       p.value[1].toFixed(isPrice ? 2 : 3));
            }
          });
          return out.join("<br/>");
        }
      },
      dataZoom: [
        { type: "inside", xAxisIndex: [0, 1] },
        { type: "slider", xAxisIndex: [0, 1], height: 16,
          bottom: 4, showDetail: false,
          borderColor: "#ccc", fillerColor: "rgba(63,71,80,0.12)",
          handleStyle: { color: "#3f4750" } }
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
  function setMode(m) {
    mode = m;
    if (bp) bp.setAttribute("aria-pressed", m === "price");
    if (by) by.setAttribute("aria-pressed", m === "yield");
    chart.setOption(option(mode), { notMerge: true });
  }
  if (bp) bp.addEventListener("click", function () { setMode("price"); });
  if (by) by.addEventListener("click", function () { setMode("yield"); });
  window.addEventListener("resize", function () { chart.resize(); });
})();
