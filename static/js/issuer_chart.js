/* Issuer trend chart for the per-issuer pages under
   /leverage/issuer/: one ECharts instance (month-end median last
   print + trades per month) for the page's single issuer, embedded
   in the page's chart-data block. Progressive enhancement: without
   JS the container keeps its server-rendered SVG fallback. No
   issuer switching and no URL hash writes on these pages. */
(function () {
  var dataEl = document.getElementById("issuer-chart-data");
  var box = document.getElementById("issuer-chart-e");
  if (!dataEl || !box || !window.echarts) return;
  var DATA = {};
  try { DATA = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var keys = Object.keys(DATA);
  if (!keys.length) return;
  var d = DATA[keys[0]];
  function fmtMonth(ms) {
    var dte = new Date(ms);
    return dte.toLocaleDateString("en-GB", { month: "short", year: "numeric", timeZone: "UTC" });
  }
  var option = {
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
        borderColor: "#3f4750",
        fillerColor: "rgba(63,71,80,0.15)",
        handleStyle: { color: "#3f4750", borderColor: "#3f4750" },
        moveHandleStyle: { color: "#3f4750" },
        textStyle: { color: "#6b7280", fontSize: 10 },
        dataBackground: {
          lineStyle: { color: "#9aa0a6" },
          areaStyle: { color: "rgba(63,71,80,0.10)" } },
        selectedDataBackground: {
          lineStyle: { color: "#3f4750" },
          areaStyle: { color: "rgba(63,71,80,0.15)" } } }
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
  box.innerHTML = "";
  var chart = echarts.init(box, null, { renderer: "canvas" });
  chart.setOption(option);
  window.addEventListener("resize", function () { chart.resize(); });
})();
