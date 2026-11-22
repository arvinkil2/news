/* Model-implied CDS chart for the per-issuer pages under
   /leverage/issuer/ (Apache ECharts). Progressive enhancement: the
   container holds a server-rendered SVG of the latest fitted curve;
   this script replaces it with an interactive chart built from the
   JSON data block in the same CDS section. Two views, switched by
   the buttons above the chart, with no reload and no server calls:

   - Curve: the latest fit across the six tenors, with the previous
     fitted date's curve overlaid as a quieter dashed line.
   - History: every published fit, one line per tenor (all six, or a
     single tenor via the tenor buttons). A point exists only on a
     day a fit was published; the line breaks across gaps longer
     than 31 days and wherever a tenor has no value, so sparse early
     history (the stored tape is thin before November 2026) reads as
     points, never as an invented continuous line. */
(function () {
  "use strict";
  var box = document.querySelector(".cds-chart-e");
  if (!box || typeof echarts === "undefined") return;
  var dataEl = document.querySelector(".cds-chart-data");
  if (!dataEl) return;
  var D;
  try { D = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var TENORS = D.tenors || [1, 2, 3, 5, 7, 10];
  var latest = D.latest || null;
  var prev = D.prev || null;
  var history = D.history || [];
  if (!latest && !history.length) return;
  var DAY = 86400000;
  var INK = "#3f4750", FAINT = "#a8adb3", GRID = "#e3ded2",
      MUTED = "#6b675c";
  var TENOR_COLORS = { "1": "#e69f00", "2": "#56b4e9",
                       "3": "#009e73", "5": "#b25f09",
                       "7": "#0072b2", "10": "#cc79a7" };
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  function isSmall() { return (box.clientWidth || 9999) < 560; }
  var small = isSmall();
  function fmtDate(iso) {
    var p = iso.split("-");
    return Number(p[2]) + " " + MONTHS[Number(p[1]) - 1] + " " +
      p[0];
  }
  function tsOf(iso) {
    var p = iso.split("-");
    return Date.UTC(Number(p[0]), Number(p[1]) - 1, Number(p[2]),
                    12);
  }
  function fmtTs(ts) {
    var d = new Date(ts);
    return d.getUTCDate() + " " + MONTHS[d.getUTCMonth()] + " " +
      d.getUTCFullYear();
  }
  /* Break a point list wherever consecutive fitted dates are more
     than maxDays apart: a null point just before the next real one,
     so the line stops instead of spanning the gap. */
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
  function yAxis() {
    return { type: "value", scale: true,
      name: "Par CDS (bp)", nameLocation: "end",
      nameTextStyle: { fontSize: small ? 11 : 12, color: MUTED },
      axisLabel: { show: true, fontSize: small ? 11 : 12,
        color: MUTED,
        formatter: function (v) { return String(Math.round(v)); } },
      splitLine: { show: true, lineStyle: { color: GRID } } };
  }
  function baseOption() {
    return {
      animation: false,
      textStyle: { fontFamily: "inherit", color: "#1a1a1a" },
      grid: { left: small ? 46 : 52, right: small ? 10 : 18,
              top: 34, bottom: 28 },
      legend: { show: false, top: 0,
        textStyle: { fontSize: 11, color: INK } }
    };
  }

  function curveOption() {
    var o = baseOption();
    var labels = TENORS.map(function (t) { return t + "Y"; });
    var series = [];
    if (prev) {
      series.push({
        name: "Previous fit, " + fmtDate(prev.date), type: "line",
        data: prev.values, showSymbol: true, symbolSize: 4,
        connectNulls: false,
        lineStyle: { width: 1.2, color: FAINT, type: "dashed" },
        itemStyle: { color: FAINT }, z: 2 });
    }
    if (latest) {
      series.push({
        name: "Latest fit, " + fmtDate(latest.date), type: "line",
        data: latest.values, showSymbol: true, symbolSize: 5,
        connectNulls: false,
        lineStyle: { width: 1.6, color: INK },
        itemStyle: { color: INK }, z: 3 });
    }
    o.legend.show = true;
    o.xAxis = { type: "category", data: labels,
      axisLine: { lineStyle: { color: "#999" } },
      axisLabel: { show: true, fontSize: small ? 11 : 12,
        color: MUTED },
      splitLine: { show: false } };
    o.yAxis = yAxis();
    o.tooltip = {
      trigger: "axis", confine: small,
      axisPointer: { type: "line", lineStyle: { color: "#999" } },
      formatter: function (ps) {
        if (!ps || !ps.length) return "";
        var out = ["Tenor " + ps[0].name];
        ps.forEach(function (p) {
          if (p.value !== null && p.value !== undefined) {
            out.push(p.marker + p.seriesName + ": " +
                     Number(p.value).toFixed(1) + " bp");
          }
        });
        return out.join("<br/>");
      }
    };
    o.series = series;
    return o;
  }

  function historyOption(tenorSel) {
    var o = baseOption();
    var series = [];
    TENORS.forEach(function (t, ti) {
      if (tenorSel !== "all" && tenorSel !== String(t)) return;
      var pts = [];
      history.forEach(function (h) {
        var v = h.v[ti];
        if (v !== null && v !== undefined) {
          pts.push([tsOf(h.d), v]);
        }
      });
      series.push({
        name: t + "Y", type: "line",
        data: gapped(pts, 31), showSymbol: true, symbolSize: 4,
        connectNulls: false,
        lineStyle: { width: String(t) === "5" ? 1.6 : 1.3,
                     color: TENOR_COLORS[String(t)] },
        itemStyle: { color: TENOR_COLORS[String(t)] }, z: 3 });
    });
    o.legend.show = tenorSel === "all";
    o.xAxis = { type: "time",
      axisLine: { lineStyle: { color: "#999" } },
      axisLabel: { show: true, hideOverlap: true,
        fontSize: small ? 11 : 12, color: MUTED,
        formatter: function (value) {
          var d = new Date(value);
          return d.getUTCDate() + " " + MONTHS[d.getUTCMonth()] +
            " " + String(d.getUTCFullYear()).slice(2);
        } },
      splitLine: { show: true, lineStyle: { color: GRID } } };
    o.yAxis = yAxis();
    o.tooltip = {
      trigger: "axis", confine: small,
      axisPointer: { type: "line", lineStyle: { color: "#999" } },
      formatter: function (ps) {
        if (!ps || !ps.length) return "";
        var out = [fmtTs(ps[0].value[0])];
        ps.forEach(function (p) {
          if (p.value[1] !== null && p.value[1] !== undefined) {
            out.push(p.marker + p.seriesName + ": " +
                     Number(p.value[1]).toFixed(1) + " bp");
          }
        });
        return out.join("<br/>");
      }
    };
    o.series = series;
    return o;
  }

  box.innerHTML = "";
  var chart = echarts.init(box, null, { renderer: "canvas" });
  var view = "curve";
  var tenorSel = "all";
  function render() {
    chart.setOption(
      view === "curve" ? curveOption() : historyOption(tenorSel),
      { notMerge: true });
  }
  render();

  function wireToggle(sel, attr, fn) {
    var btns = document.querySelectorAll(sel + " button");
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        btns.forEach(function (x) {
          x.setAttribute("aria-pressed",
                         x === b ? "true" : "false");
        });
        fn(b.getAttribute(attr));
      });
    });
    return btns;
  }
  var tenorRow = document.querySelector(".cds-tenor-toggle");
  wireToggle(".cds-view-toggle", "data-view", function (v) {
    view = v;
    if (tenorRow) tenorRow.hidden = v !== "history";
    render();
  });
  wireToggle(".cds-tenor-toggle", "data-tenor", function (t) {
    tenorSel = t;
    if (view === "history") render();
  });
  var rzTimer = null;
  window.addEventListener("resize", function () {
    clearTimeout(rzTimer);
    rzTimer = setTimeout(function () {
      if (isSmall() !== small) {
        small = isSmall();
        render();
      }
      chart.resize();
    }, 120);
  });
})();
