/* Bond detail chart (Apache ECharts). Progressive enhancement: the
   container holds a server-rendered SVG fallback; this script
   replaces it with an interactive chart built from the JSON data
   block on the same page. Trades are aggregated to one candlestick
   per trade date: the candle spans the day's first print (open) to
   its last print (close), with the day's high and low as the wicks.
   Fund marks are hollow squares at period end. Volume is the day
   total of reported floors, in a separate panel. */
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
  var INK = "#3f4750", MARK = "#b25f09", GRID = "#e3ded2";
  var UP_BORDER = "#1a7f37", UP_FILL = "#fdfcf8", DOWN = "#b42318";

  /* Daily aggregation. Embed timestamps are the trade datetime
     (naive UTC epoch) plus 12 hours, so the trade date is the UTC
     date of (ts - 12h). Trades arrive sorted by (date, time), so
     within a day the first row is the open and the last the close.
     The candle sits at noon UTC on the trade date. */
  var days = [];            /* day records, ascending */
  var dayByTs = {};
  trades.forEach(function (r) {
    var d = new Date(r[0] - 12 * 3600 * 1000);
    var x = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(),
                     d.getUTCDate(), 12);
    var g = dayByTs[x];
    if (!g) {
      g = dayByTs[x] = { x: x, n: 0,
        po: null, ph: null, pl: null, pc: null,
        yo: null, yh: null, yl: null, yc: null,
        vol: 0, volN: 0 };
      days.push(g);
    }
    g.n += 1;
    if (r[1] !== null && r[1] !== undefined) {
      if (g.po === null) g.po = r[1];
      g.pc = r[1];
      g.ph = g.ph === null ? r[1] : Math.max(g.ph, r[1]);
      g.pl = g.pl === null ? r[1] : Math.min(g.pl, r[1]);
    }
    if (r[2] !== null && r[2] !== undefined) {
      if (g.yo === null) g.yo = r[2];
      g.yc = r[2];
      g.yh = g.yh === null ? r[2] : Math.max(g.yh, r[2]);
      g.yl = g.yl === null ? r[2] : Math.min(g.yl, r[2]);
    }
    if (r[3] !== null && r[3] !== undefined) {
      g.vol += r[3]; g.volN += 1;
    }
  });

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
    var candles = [], vPts = [];
    days.forEach(function (g) {
      var o = isPrice ? g.po : g.yo, h = isPrice ? g.ph : g.yh,
          l = isPrice ? g.pl : g.yl, c = isPrice ? g.pc : g.yc;
      if (o !== null && h !== null && l !== null && c !== null) {
        candles.push([g.x, o, c, l, h]);
      }
      if (g.volN) vPts.push([g.x, g.vol]);
    });
    var series = [
      { name: isPrice ? "Daily prints (price)" : "Daily prints (yield)",
        type: "candlestick", xAxisIndex: 0, yAxisIndex: 0,
        data: candles,
        itemStyle: { color: UP_FILL, color0: DOWN,
                     borderColor: UP_BORDER, borderColor0: DOWN,
                     borderWidth: 1 },
        emphasis: { itemStyle: { borderWidth: 1 } }, z: 3 },
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
            var o = isPrice ? g.po : g.yo,
                h = isPrice ? g.ph : g.yh,
                l = isPrice ? g.pl : g.yl,
                c = isPrice ? g.pc : g.yc;
            if (o !== null) {
              out.push("Open " + o.toFixed(dec));
              out.push("High " + h.toFixed(dec));
              out.push("Low " + l.toFixed(dec));
              out.push("Close " + c.toFixed(dec));
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
