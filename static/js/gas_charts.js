// EU Gas section charts: interactive ECharts versions of the storage
// band, the path and projection panel, the 60-day drain, the weekly
// flow stacks, nominations against physical flow, LNG send-out,
// cumulative degree days and the March 31 revision history. Each
// chart's data is embedded in the page as a JSON payload in a script
// tag of class gas-chart-data immediately after its container, paired
// by document order; the values are the same series the builder
// computed for the static charts these replace. Same pattern as
// gas_map.js: SVG renderer, site sans stack, ink colour, animation
// off, container cleared before init so the no-JS fallback line only
// shows when this script does not run.
(function () {
  "use strict";
  if (typeof echarts === "undefined") return;
  var SANS = '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
  var INK = "#3f4750", MUTED = "#6f6a5e", GRID = "#e5ddc8";
  var GREY = "#8a8378", GREEN = "#009e73", BLUE = "#0072b2",
      VERM = "#d55e00", BAND = "#e8e2d0", PAST = "#c9c2ae";
  var MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  function commas(v) {
    var n = Math.round(v);
    var s = String(Math.abs(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return (n < 0 ? "-" : "") + s;
  }
  function p1(v) { return (Math.round(v * 10) / 10).toFixed(1); }
  function shortDate(iso) {
    return parseInt(iso.slice(8), 10) + " " +
           MON[parseInt(iso.slice(5, 7), 10) - 1];
  }
  function monthStart(iso) {
    return iso.slice(8) === "01"
      ? MON[parseInt(iso.slice(5, 7), 10) - 1] : "";
  }

  function yAxis(o, small) {
    var a = {
      type: "value", min: o.min, max: o.max, name: o.name || "",
      nameLocation: "end",
      nameTextStyle: { color: MUTED, fontFamily: SANS,
                       fontSize: small ? 10.5 : 11.5, align: "left" },
      nameGap: 6,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { show: true, color: MUTED, fontFamily: SANS,
                   fontSize: small ? 10.5 : 11.5, formatter: o.fmt },
      splitLine: { show: true, lineStyle: { color: GRID, width: 1 } }
    };
    if (o.interval) a.interval = o.interval;
    return a;
  }
  function catAxis(data, fmt, small, gap, intervalFn) {
    var a = {
      type: "category", data: data, boundaryGap: !!gap,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { show: true, color: MUTED, fontFamily: SANS,
                   fontSize: small ? 10.5 : 11.5, formatter: fmt,
                   hideOverlap: true },
      splitLine: { show: false }
    };
    if (intervalFn) a.axisLabel.interval = intervalFn;
    return a;
  }
  function monthInterval(dates) {
    return function (i) { return dates[i].slice(8) === "01"; };
  }
  function tip() {
    return {
      trigger: "axis", confine: true,
      axisPointer: { type: "cross",
                     lineStyle: { color: "#999999" },
                     crossStyle: { color: "#999999" },
                     label: { show: false } },
      textStyle: { fontFamily: SANS, fontSize: 12.5, color: INK }
    };
  }
  function legend(names, small) {
    if (!names) return { show: false };
    return { show: true, top: 0, right: 0, data: names,
             textStyle: { fontFamily: SANS,
                          fontSize: small ? 10.5 : 11.5, color: INK },
             itemWidth: 16, itemHeight: 8, itemGap: 10 };
  }
  function grid(legendNames, right, small) {
    return { left: 6, right: right,
             top: legendNames ? (small ? 56 : 34) : 16,
             bottom: 6, containLabel: true };
  }
  function line(name, data, color, width, dash, extra) {
    var s = { name: name, type: "line", data: data, symbol: "none",
              smooth: false, connectNulls: false, z: 3,
              lineStyle: { color: color, width: width,
                           type: dash || "solid" },
              itemStyle: { color: color },
              emphasis: { disabled: true } };
    if (extra) for (var k in extra) s[k] = extra[k];
    return s;
  }
  function endMark(color, coord, text, small) {
    return { silent: true, symbol: "circle", symbolSize: 6,
             itemStyle: { color: color },
             label: { show: true, position: small ? "left" : "right",
                      distance: small ? 6 : 5, color: MUTED,
                      fontFamily: SANS,
                      fontSize: small ? 10.5 : 11.5,
                      formatter: text },
             data: [{ coord: coord }] };
  }
  // Generic axis tooltip: header, then every series value at the
  // pointer, formatted by fmt.
  function rowsTip(fmt) {
    var t = tip();
    t.formatter = function (ps) {
      var rows = [ps[0].name];
      ps.forEach(function (p) {
        if (p.value == null) return;
        var v = (p.value && typeof p.value === "object")
          ? p.value[p.value.length - 1] : p.value;
        if (v == null) return;
        rows.push(p.marker + p.seriesName + ": " + fmt(v));
      });
      return rows.join("<br/>");
    };
    return t;
  }
  function pct(v) { return p1(v) + "%"; }
  function gwhd(v) { return commas(v) + " GWh/d"; }

  function optBand(D, small) {
    var delta = D.hi.map(function (h, i) {
      return (h == null || D.lo[i] == null) ? null : h - D.lo[i];
    });
    var cur = line(D.curName, D.cur, INK, 2.2, "solid");
    if (D.mark) cur.markPoint = endMark(INK, [D.mark.i, D.mark.v],
                                        D.mark.text, false);
    var series = [
      { name: "Five-winter range", type: "line", stack: "band",
        data: D.lo, symbol: "none", z: 1, silent: true,
        lineStyle: { opacity: 0 }, areaStyle: { opacity: 0 },
        itemStyle: { color: BAND }, emphasis: { disabled: true } },
      { name: "Five-winter range", type: "line", stack: "band",
        data: delta, symbol: "none", z: 1, silent: true,
        lineStyle: { opacity: 0 },
        areaStyle: { color: BAND, opacity: 1 },
        itemStyle: { color: BAND }, emphasis: { disabled: true } },
      line(D.meanName, D.mean, GREY, 1.2, [2, 3]),
      line(D.lastName, D.last, GREY, 1.2, [6, 3]),
      cur
    ];
    var t = tip();
    t.formatter = function (ps) {
      var i = ps[0].dataIndex;
      var rows = [D.dates[i],
        '<span style="display:inline-block;width:9px;height:9px;' +
        'background:' + BAND + ';margin-right:5px"></span>' +
        "Five-winter range: " + p1(D.lo[i]) + " to " + p1(D.hi[i]) + "%"];
      ps.forEach(function (p) {
        if (p.seriesName === "Five-winter range" || p.value == null)
          return;
        rows.push(p.marker + p.seriesName + ": " + pct(p.value));
      });
      return rows.join("<br/>");
    };
    var names = ["Five-winter range", D.meanName, D.lastName, D.curName];
    return { animation: false, textStyle: { fontFamily: SANS },
             legend: legend(names, small), tooltip: t,
             grid: grid(names, 46, small),
             xAxis: catAxis(D.dates, monthStart, small, false,
                            monthInterval(D.dates)),
             yAxis: yAxis({ min: 0, max: 100, interval: 25,
                            name: "%", fmt: function (v) { return v; } },
                          small),
             series: series };
  }

  function optPanel(D, small) {
    var series = [];
    if (D.exp) series.push(line("Weather-expected path", D.exp,
                                GREEN, 1.6, "solid"));
    series.push(line("Actual path", D.act, INK, 2.2, "solid"));
    var proj = line("Projection at normal weather", D.proj,
                    BLUE, 1.8, [7, 4]);
    proj.markLine = {
      silent: true, symbol: "none",
      lineStyle: { color: VERM, width: 1, type: [5, 4] },
      label: { show: true, color: MUTED, fontFamily: SANS,
               fontSize: small ? 10.5 : 11.5,
               position: "insideStartTop", distance: 3 },
      data: [{ yAxis: 30, label: { formatter: "30%" } },
             { yAxis: 11, label: { formatter: "11%" } }]
    };
    if (D.end) proj.markPoint = endMark(BLUE, [D.end.i, D.end.v],
                                        D.endText, small);
    series.push(proj);
    var names = D.exp ? ["Weather-expected path", "Actual path",
                         "Projection at normal weather"] : null;
    return { animation: false, textStyle: { fontFamily: SANS },
             legend: legend(names, small), tooltip: rowsTip(pct),
             grid: grid(names, small ? 14 : "13%", small),
             xAxis: catAxis(D.dates, monthStart, small, false,
                            monthInterval(D.dates)),
             yAxis: yAxis({ min: 0, max: 100, interval: 25,
                            name: "%", fmt: function (v) { return v; } },
                          small),
             series: series };
  }

  function optDrain(D, small) {
    var bars = D.net.map(function (v) {
      return v == null ? null
        : { value: v, itemStyle: { color: v >= 0 ? INK : "#9aa3ab" } };
    });
    var series = [{
      name: "Net withdrawal", type: "bar", data: bars,
      barCategoryGap: "30%", z: 2,
      markLine: { silent: true, symbol: "none",
                  lineStyle: { color: INK, width: 1 },
                  label: { show: false }, data: [{ yAxis: 0 }] }
    }];
    if (D.fit) series.push(line("Fitted value", D.fit,
                                GREEN, 1.6, "solid"));
    return { animation: false, textStyle: { fontFamily: SANS },
             legend: legend(null, small), tooltip: rowsTip(gwhd),
             grid: grid(null, 14, small),
             xAxis: catAxis(D.dates, shortDate, small, true),
             yAxis: yAxis({ min: -D.peak, max: D.peak,
                            interval: D.peak, name: "GWh/d",
                            fmt: commas }, small),
             series: series };
  }

  function optStacked(D, small) {
    var series = D.classes.map(function (c) {
      return { name: c.name, type: "bar", stack: "flow",
               data: c.data, itemStyle: { color: c.color } };
    });
    var names = D.classes.map(function (c) { return c.name; });
    var t = tip();
    t.formatter = function (ps) {
      var rows = ["Week of " + ps[0].name];
      var total = 0;
      ps.forEach(function (p) {
        if (!p.value) return;
        total += p.value;
        rows.push(p.marker + p.seriesName + ": " + commas(p.value) +
                  " GWh/d");
      });
      rows.push("Total: " + commas(total) + " GWh/d");
      return rows.join("<br/>");
    };
    return { animation: false, textStyle: { fontFamily: SANS },
             legend: legend(names, small), tooltip: t,
             grid: grid(names, 14, small),
             xAxis: catAxis(D.weeks, function (v) {
               return "week of " + v.slice(5);
             }, small, true),
             yAxis: yAxis({ min: 0, max: D.peak, interval: D.peak / 2,
                            name: "GWh per day", fmt: commas }, small),
             series: series };
  }

  function optNvp(D, small) {
    var series = [
      line("Physical flow", D.phys, INK, 1.8, "solid"),
      line("Nominations and renominations", D.nom, BLUE, 1.5, [6, 3])
    ];
    return { animation: false, textStyle: { fontFamily: SANS },
             legend: legend(null, small), tooltip: rowsTip(gwhd),
             grid: grid(null, 14, small),
             xAxis: catAxis(D.dates, shortDate, small),
             yAxis: yAxis({ min: 0, max: D.peak, interval: D.peak / 2,
                            name: "GWh/d", fmt: commas }, small),
             series: series };
  }

  function optLine(D, small) {
    var series = [line(D.name, D.data, INK, 1.6, "solid")];
    return { animation: false, textStyle: { fontFamily: SANS },
             legend: legend(null, small), tooltip: rowsTip(gwhd),
             grid: grid(null, 14, small),
             xAxis: catAxis(D.dates, shortDate, small),
             yAxis: yAxis({ min: 0, max: D.peak, interval: D.peak / 2,
                            name: "GWh/d", fmt: commas }, small),
             series: series };
  }

  function optHdd(D, small) {
    var series = [
      line("Normal path", D.norm, GREY, 1.4, [6, 3]),
      line("This winter", D.act, INK, 1.8, "solid")
    ];
    var t = rowsTip(function (v) {
      return commas(v) + " degree days";
    });
    return { animation: false, textStyle: { fontFamily: SANS },
             legend: legend(null, small), tooltip: t,
             grid: grid(null, 14, small),
             xAxis: catAxis(D.dates, monthStart, small, false,
                            monthInterval(D.dates)),
             yAxis: yAxis({ min: 0, max: D.peak, interval: D.peak / 2,
                            name: "degree days", fmt: commas }, small),
             series: series };
  }

  function optRevision(D, small) {
    var series = D.past.map(function (arr) {
      return line("Past winters, plain method", arr, PAST, 1,
                  "solid", { z: 1 });
    });
    var names = ["Past winters, plain method",
                 "This winter, plain method"];
    if (D.norm) {
      var ns = line("This winter, weather-normalized", D.norm,
                    BLUE, 1.8, [7, 4], { z: 3 });
      if (D.switchIdx != null) {
        ns.markLine = {
          silent: true, symbol: "none",
          lineStyle: { color: VERM, width: 1 },
          label: { show: true, color: MUTED, fontFamily: SANS,
                   fontSize: small ? 10 : 11.5, rotate: 0,
                   position: "insideEndTop", distance: 4,
                   offset: small ? [64, 0] : [0, 0],
                   formatter: small
                     ? D.switchText.replace(" method starts ",
                                            " method\nstarts ")
                     : D.switchText },
          data: [{ xAxis: D.switchIdx }]
        };
      }
      series.push(ns);
      names.push("This winter, weather-normalized");
    }
    if (D.cur) series.push(line("This winter, plain method", D.cur,
                                INK, 1.8, "solid", { z: 4 }));
    series.push({
      name: "Actual March 31 outcome", type: "scatter",
      symbolSize: 6, z: 5, emphasis: { disabled: true },
      data: D.outcomes.map(function (o) {
        return { value: [181, o.v],
                 itemStyle: { color: o.cur ? INK : GREY } };
      })
    });
    names.push("Actual March 31 outcome");
    var t = tip();
    t.formatter = function (ps) {
      var rows = [shortDate(D.cats[ps[0].dataIndex])];
      var past = [], curV = null, normV = null, outV = null;
      ps.forEach(function (p) {
        if (p.seriesName === "Past winters, plain method") {
          if (p.value != null) past.push(p.value);
        } else if (p.seriesName === "This winter, plain method") {
          curV = p.value;
        } else if (p.seriesName ===
                   "This winter, weather-normalized") {
          normV = p.value;
        } else if (p.seriesName === "Actual March 31 outcome") {
          outV = (p.value && typeof p.value === "object")
            ? p.value[1] : p.value;
        }
      });
      if (past.length) rows.push("Past winters, plain method: " +
        p1(Math.min.apply(null, past)) + " to " +
        p1(Math.max.apply(null, past)) + "%");
      if (curV != null) rows.push("This winter, plain method: " +
                                  pct(curV));
      if (normV != null) rows.push("This winter, weather-" +
                                   "normalized: " + pct(normV));
      if (outV != null) rows.push("Actual March 31 outcome: " +
                                  pct(outV));
      return rows.join("<br/>");
    };
    var marks = { 0: "Oct 1", 61: "Dec 1", 123: "Feb 1",
                  181: "Mar 31" };
    return { animation: false, textStyle: { fontFamily: SANS },
             legend: legend(names, small), tooltip: t,
             grid: grid(names, 30, small),
             xAxis: catAxis(D.cats, function (v, i) {
               return marks[i] || "";
             }, small, false, function (i) {
               return marks[i] !== undefined;
             }),
             yAxis: yAxis({ min: 0, max: D.peak,
                            interval: D.peak / 2, name: "%",
                            fmt: commas }, small),
             series: series };
  }

  var BUILDERS = { band: optBand, panel: optPanel, drain: optDrain,
                   stacked: optStacked, nvp: optNvp, line: optLine,
                   hdd: optHdd, revision: optRevision };

  function render(box, D) {
    if (!BUILDERS[D.kind]) return;
    var small = box.clientWidth < 640;
    box.style.aspectRatio = "960 / " +
      (small ? Math.round(D.h * 1.5) : D.h);
    box.innerHTML = "";
    var chart = echarts.init(box, null, { renderer: "svg" });
    chart.setOption(BUILDERS[D.kind](D, small));
    window.addEventListener("resize", function () {
      var nowSmall = box.clientWidth < 640;
      if (nowSmall !== small) {
        small = nowSmall;
        box.style.aspectRatio = "960 / " +
          (small ? Math.round(D.h * 1.5) : D.h);
        chart.setOption(BUILDERS[D.kind](D, small), true);
      }
      chart.resize();
    });
  }

  var boxes = document.querySelectorAll(".gas-chart-e");
  var datas = document.querySelectorAll(".gas-chart-data");
  for (var i = 0; i < boxes.length && i < datas.length; i++) {
    try { render(boxes[i], JSON.parse(datas[i].textContent)); }
    catch (e) { /* leave the fallback line in place */ }
  }
})();
