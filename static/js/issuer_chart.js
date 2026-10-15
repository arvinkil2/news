/* Issuer browser for the Bond Analytics page: one ECharts instance
   (month-end median last print + trades per month) whose data swaps
   with the selected issuer, and panel switching for the per-issuer
   bonds / trend / curve / holders blocks. Progressive enhancement:
   without JS every panel renders and the index links anchor-jump;
   the chart container then keeps its server-rendered SVG. */
(function () {
  var dataEl = document.getElementById("issuer-chart-data");
  var box = document.getElementById("issuer-chart-e");
  if (!dataEl) return;
  var DATA = {};
  try { DATA = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var keys = Object.keys(DATA);
  if (!keys.length) return;
  var panels = {};
  document.querySelectorAll(".issuer-panel").forEach(function (p) {
    panels[p.id.replace("issuer-", "")] = p;
  });
  var chart = null;
  function fmtMonth(ms) {
    var d = new Date(ms);
    return d.toLocaleDateString("en-GB", { month: "short", year: "numeric", timeZone: "UTC" });
  }
  function option(key) {
    var d = DATA[key];
    return {
      animation: false,
      textStyle: { color: "#3f4750", fontFamily: "inherit" },
      grid: [
        { left: 52, right: 16, top: 26, height: "56%" },
        { left: 52, right: 16, top: "74%", height: "14%" }
      ],
      axisPointer: { link: [{ xAxisIndex: "all" }] },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "cross" },
        formatter: function (ps) {
          var out = "<b>" + fmtMonth(ps[0].value[0]) + "</b>";
          ps.forEach(function (p) {
            if (p.seriesName === "Median last print") {
              out += "<br/>Median last print: " + Number(p.value[1]).toFixed(2);
            } else {
              out += "<br/>Trades: " + Number(p.value[1]).toLocaleString("en-US");
            }
          });
          return out;
        }
      },
      xAxis: [
        { type: "time", gridIndex: 0, axisLabel: { show: false },
          axisTick: { show: false } },
        { type: "time", gridIndex: 1,
          axisLabel: { color: "#6b675c", fontSize: 10 } }
      ],
      yAxis: [
        { type: "value", gridIndex: 0, name: "Median price, % of par",
          scale: true, nameTextStyle: { color: "#6b675c", fontSize: 10 },
          axisLabel: { color: "#6b675c", fontSize: 10 },
          splitLine: { lineStyle: { color: "#e3ded2" } } },
        { type: "value", gridIndex: 1, name: "Trades",
          nameTextStyle: { color: "#6b675c", fontSize: 10 },
          axisLabel: { color: "#6b675c", fontSize: 10 },
          splitLine: { show: false } }
      ],
      dataZoom: [
        { type: "inside", xAxisIndex: [0, 1] },
        { type: "slider", xAxisIndex: [0, 1], height: 16, bottom: 2,
          textStyle: { color: "#6b675c", fontSize: 10 } }
      ],
      series: [
        { name: "Median last print", type: "line", xAxisIndex: 0,
          yAxisIndex: 0, data: d.price, showSymbol: true, symbolSize: 4,
          lineStyle: { color: "#3f4750", width: 1.4 },
          itemStyle: { color: "#1a1a1a" } },
        { name: "Trades", type: "bar", xAxisIndex: 1, yAxisIndex: 1,
          data: d.vol, itemStyle: { color: "#b9b2a2" } }
      ]
    };
  }
  function activate(key, scroll, writeHash) {
    if (!DATA[key]) key = keys[0];
    Object.keys(panels).forEach(function (k) {
      panels[k].hidden = (k !== key);
    });
    document.querySelectorAll(".issuer-link").forEach(function (a) {
      a.classList.toggle("active", a.getAttribute("data-key") === key);
    });
    if (chart) {
      chart.setOption(option(key), true);
      box.setAttribute("aria-label",
        "Issuer trend chart: " + DATA[key].name);
    }
    if (scroll && panels[key]) panels[key].scrollIntoView();
    if (writeHash) {
      try { history.replaceState(null, "", "#issuer-" + key); }
      catch (e) {}
    }
  }
  if (box && window.echarts) {
    box.innerHTML = "";
    chart = echarts.init(box, null, { renderer: "canvas" });
    window.addEventListener("resize", function () { chart.resize(); });
  }
  document.querySelectorAll(".issuer-link").forEach(function (a) {
    a.addEventListener("click", function (ev) {
      ev.preventDefault();
      activate(a.getAttribute("data-key"), true, true);
    });
  });
  /* On load: show the first issuer's panel and chart, but never
     scroll and never write the issuer into the URL. Writing the
     hash on load made later visits land mid-page on CoreWeave,
     which read as a redirect. The hash is written only after an
     explicit issuer click. */
  var start = (location.hash || "").replace("#issuer-", "");
  activate(DATA[start] ? start : keys[0], false, false);
})();
