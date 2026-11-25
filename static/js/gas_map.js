/* EU Gas overview flow map (Apache ECharts graph series, SVG
   renderer). Progressive enhancement: the container holds a text
   fallback; this script replaces it with the interactive diagram
   built from the JSON data block on the same page.

   Fixed schematic layout: node positions are set by hand in the
   data (a 960 by 620 design space) and two invisible frame nodes
   pin the graph view's fit, so the arrangement is identical at
   every width and on every refresh. Flows are 30-day mean GWh/d
   from the ENTSOG zone aggregates; flows under 10 GWh/d are not
   in the data (the caption on the page states the count and the
   combined value removed).

   Encoding, per the library study: edge width carries the value
   on a square root scale, width in px = 1 + 9 * sqrt(value /
   window maximum), and the printed value on every edge is the
   authority. Arrowheads are a fixed 7 px at the target end only.
   Colour is one ink grey for every edge; direction is carried by
   the arrowhead, never by colour. The two directions of a hub
   pair take the same curveness sign at magnitude about 0.25,
   which bends them to opposite sides of the shared chord (with
   ECharts 6.1 the same sign separates the pair; opposite signs
   overlap it). Duplicate reports of one direction fan out by
   0.13 of curveness per extra edge. Single edges take curveness
   about 0.12, signed so the arc bows away from the centre of the
   diagram. Edge labels follow the arc.

   The chart uses the SVG renderer so that every label is a DOM
   text element whose rendered position can be measured in the
   browser. After each render, a label pass works largest first:
   a value label that overlaps a hub box, a node label or a label
   already placed is shifted along its arc in steps until it is
   clear, and a label that cannot be cleared is hidden (its
   figure remains in the tooltip and in the route tables on the
   hub pages). This is the study's shift-and-hide rule, applied
   to measured positions: the library's own switches could not
   be used, because labelLayout hideOverlap hid 32 of 33 labels
   on this graph in testing, the labelRect the layout callback
   reports carries no usable position, and in this build the
   mere presence of a labelLayout callback moves edge labels
   off the view transform entirely (they land at raw design
   coordinates, at phone width mostly off the page). So the
   option carries no labelLayout at all, and node labels use
   the default placement.

   Compact layout: ECharts graph symbols and labels render at a
   constant screen size whatever the view fit, so below a 640 px
   container width the desktop arrangement cannot shrink (the
   hub boxes would sit on each other). The data therefore also
   carries a portrait arrangement in a 620 by 960 design space,
   used at phone width with the container's aspect ratio
   switched to match, and in that mode edge value labels are
   kept only on edges of 100 GWh/d and above. */
(function () {
  "use strict";
  var box = document.querySelector(".gas-map-e");
  if (!box || typeof echarts === "undefined") return;
  var dataEl = document.querySelector(".gas-map-data");
  if (!dataEl) return;
  var D;
  try { D = JSON.parse(dataEl.textContent); } catch (e) { return; }
  if (!D.nodes || !D.nodes.length || !D.links) return;

  var INK = "#3f4750", EDGE = "#7a756a", MUTED = "#6f6a5e",
      PAPER = "#ffffff",
      SANS = "\"Inter\", -apple-system, BlinkMacSystemFont, " +
             "\"Segoe UI\", Helvetica, Arial, sans-serif";

  var byId = {};
  D.nodes.forEach(function (n) { byId[n.id] = n; });

  function fmt(v) {
    return Math.round(v).toString()
      .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  function width(v) {
    if (!D.max) return 1;
    return 1 + 9 * Math.sqrt(v / D.max);
  }

  /* Per-mode geometry: positions for the active layout, the
     frame that pins the view fit, and each link's curveness. */
  var pos = {}, centre = { x: 480, y: 310 }, data = [];

  function nodeDatum(n) {
    var p = pos[n.id];
    if (n.kind === "hub") {
      return {
        name: n.id, x: p.x, y: p.y, symbol: "rect",
        symbolSize: [108, 44],
        itemStyle: { color: PAPER, borderColor: INK,
                     borderWidth: 1.2 },
        label: { show: true, position: "inside", color: INK,
          fontFamily: SANS, lineHeight: 17,
          formatter: "{name|" + n.label + "}\n{fill|" +
            (n.fill == null ? "not published"
                            : n.fill.toFixed(1) + "% full") + "}",
          rich: {
            name: { fontSize: 14, fontWeight: 600, color: INK,
                    fontFamily: SANS },
            fill: { fontSize: 11, color: MUTED, fontFamily: SANS }
          } },
        cursor: "pointer", href: n.path || null
      };
    }
    return {
      name: n.id, x: p.x, y: p.y, symbol: "circle", symbolSize: 6,
      itemStyle: { color: EDGE, borderColor: EDGE, borderWidth: 1 },
      label: { show: true, position: p.side || "top", distance: 7,
        fontSize: 11.5, color: INK, fontFamily: SANS,
        formatter: function () { return n.label; } }
    };
  }

  function setMode(compactMode) {
    var fw = compactMode ? 620 : 960;
    var fh = compactMode ? 960 : 620;
    centre = { x: fw / 2, y: fh / 2 };
    pos = {};
    D.nodes.forEach(function (n) {
      if (compactMode && n.cx != null) {
        pos[n.id] = { x: n.cx, y: n.cy, side: n.cside || "top" };
      } else {
        pos[n.id] = { x: n.x, y: n.y, side: n.side };
      }
    });
    /* Curveness per link. The sign that bows an edge away from
       the centre: for travel direction (dx, dy), positive
       curveness offsets the arc along (dy, -dx). */
    function awaySign(l) {
      var a = pos[l.source], b = pos[l.target];
      if (!a || !b) return 1;
      var dx = b.x - a.x, dy = b.y - a.y;
      var mx = (a.x + b.x) / 2 - centre.x;
      var my = (a.y + b.y) / 2 - centre.y;
      return (dy * mx - dx * my) < 0 ? -1 : 1;
    }
    function ukey(a, b) { return a < b ? a + "|" + b : b + "|" + a; }
    var pairDirs = {}, pairSign = {}, dirSign = {}, dirSeen = {};
    D.links.forEach(function (l) {
      var k = ukey(l.source, l.target);
      pairDirs[k] = pairDirs[k] || {};
      pairDirs[k][l.source + ">" + l.target] = true;
      if (pairSign[k] === undefined) pairSign[k] = awaySign(l);
    });
    D.links.forEach(function (l) {
      var k = ukey(l.source, l.target);
      var dk = l.source + ">" + l.target;
      var idx = dirSeen[dk] || 0;
      dirSeen[dk] = idx + 1;
      if (dirSign[dk] === undefined) dirSign[dk] = awaySign(l);
      var both = Object.keys(pairDirs[k]).length > 1;
      if (both) {
        l.curveness = pairSign[k] * (0.25 + idx * 0.13);
      } else {
        l.curveness = dirSign[dk] * (0.12 + idx * 0.13);
      }
    });
    data = D.nodes.map(nodeDatum);
    /* Invisible frame nodes pin the view fit to the design
       space of the active layout. */
    data.push({ name: "__frame0", x: 0, y: 0, symbol: "none",
                silent: true, label: { show: false },
                itemStyle: { opacity: 0 } });
    data.push({ name: "__frame1", x: fw, y: fh, symbol: "none",
                silent: true, label: { show: false },
                itemStyle: { opacity: 0 } });
  }

  /* Largest first, so the label pass places the big values and
     hides smaller ones where labels still collide. */
  var sorted = D.links.slice().sort(function (a, b) {
    return b.value - a.value;
  });

  function buildOption(compactMode) {
    return {
      animation: false,
      tooltip: {
        show: true, confine: true,
        textStyle: { fontFamily: SANS, fontSize: 12.5, color: INK },
        formatter: function (p) {
          if (p.dataType === "node") {
            var n = byId[p.data.name];
            if (!n) return "";
            if (n.kind === "hub") {
              return "<b>" + n.long + "</b><br/>Fill " +
                (n.fill == null ? "not published"
                                : n.fill.toFixed(1) + "%") +
                "<br/>Click for the full page";
            }
            return n.long;
          }
          if (p.dataType === "edge") {
            var s = byId[p.data.source], t = byId[p.data.target];
            return (s ? s.long : p.data.source) + " to " +
                   (t ? t.long : p.data.target) + "<br/><b>" +
                   fmt(p.data.value) + " GWh/d</b>, 30-day mean";
          }
          return "";
        }
      },
      series: [{
        type: "graph", layout: "none", roam: false,
        draggable: false,
        edgeSymbol: ["none", "arrow"], edgeSymbolSize: 7,
        label: { show: true, fontSize: 11.5, color: INK,
                 fontFamily: SANS },
        edgeLabel: { show: true, fontSize: 11, color: INK,
          fontFamily: SANS,
          formatter: function (p) { return fmt(p.data.value); } },
        emphasis: { focus: "adjacency",
                    lineStyle: { opacity: 1 } },
        lineStyle: { color: EDGE, opacity: 0.55, width: 1 },
        data: data,
        links: sorted.map(function (l) {
          return {
            source: l.source, target: l.target, value: l.value,
            lineStyle: { width: width(l.value),
                         curveness: l.curveness,
                         color: EDGE, opacity: 0.55 },
            label: { show: !compactMode || l.value >= 100 }
          };
        })
      }]
    };
  }

  /* ---- measured label pass (see the header comment) ---- */
  function relRect(el, br) {
    var r = el.getBoundingClientRect();
    return { x: r.left - br.left, y: r.top - br.top,
             width: r.width, height: r.height };
  }
  function hit(a, b, pad) {
    return a.x - pad < b.x + b.width && b.x - pad < a.x + a.width &&
           a.y - pad < b.y + b.height && b.y - pad < a.y + a.height;
  }
  var fixing = false;
  function fixLabels() {
    if (fixing) return;
    var svg = box.querySelector("svg");
    if (!svg) return;
    fixing = true;
    try {
      var br = box.getBoundingClientRect();
      var shown = sorted.filter(function (l) {
        return !(compact && l.value < 100);
      });
      var want = {};
      shown.forEach(function (l) { want[fmt(l.value)] = true; });
      var texts = Array.prototype.slice.call(
        svg.querySelectorAll("text"));
      var edgeEls = [], placed = [];
      texts.forEach(function (el) {
        if (want[el.textContent]) edgeEls.push(el);
        else placed.push(relRect(el, br));
      });
      /* Hub boxes: a hub's name text sits in the top half of its
         box and its fill line in the bottom half, so the box
         centre is the midpoint of the two text centres. */
      var byText = {};
      texts.forEach(function (el) {
        (byText[el.textContent] =
         byText[el.textContent] || []).push(el);
      });
      function centreOf(el) {
        var r = relRect(el, br);
        return [r.x + r.width / 2, r.y + r.height / 2];
      }
      var hubC = {};
      D.nodes.forEach(function (n) {
        if (n.kind !== "hub") return;
        var nameEl = (byText[n.label] || [])[0];
        if (!nameEl) return;
        var idx = texts.indexOf(nameEl);
        var fillEl = texts[idx + 1];
        var c1 = centreOf(nameEl);
        var c2 = fillEl ? centreOf(fillEl) : c1;
        hubC[n.id] = [(c1[0] + c2[0]) / 2, (c1[1] + c2[1]) / 2];
      });
      /* The hub boxes render at a constant 108 by 44 CSS px
         whatever the view fit, so the obstacle is that size
         plus padding, not a scaled design size. */
      Object.keys(hubC).forEach(function (id) {
        placed.push({ x: hubC[id][0] - 58, y: hubC[id][1] - 26,
                      width: 116, height: 52 });
      });
      /* Edge labels, in link order (largest first). */
      edgeEls.forEach(function (el, i) {
        if (!shown[i]) return;
        var base = el.getAttribute("transform") || "";
        var r = relRect(el, br);
        var clear = r.x >= -4 && r.y >= -4 &&
          r.x + r.width <= br.width + 4 &&
          r.y + r.height <= br.height + 4 &&
          !placed.some(function (p) {
            return hit(r, p, 2);
          });
        if (clear) { placed.push(r); return; }
        var done = false;
        /* First along the arc (the label's local x), then, as a
           second resort, across it (local y), which leaves the
           label sitting beside its line. */
        var moves = [];
        [16, 32, 48, 64].forEach(function (st) {
          moves.push([st, 0]);
          moves.push([-st, 0]);
        });
        [18, 36].forEach(function (st) {
          moves.push([0, st]);
          moves.push([0, -st]);
        });
        for (var mi = 0; mi < moves.length && !done; mi++) {
          /* The appended translate is in the label's local
             units, which the element's transform maps 1 to 1
             to CSS px (its scale factor is 1). */
          el.setAttribute("transform",
                          base + " translate(" + moves[mi][0] +
                          " " + moves[mi][1] + ")");
          var cand = relRect(el, br);
          var inBox = cand.x >= -4 && cand.y >= -4 &&
            cand.x + cand.width <= br.width + 4 &&
            cand.y + cand.height <= br.height + 4;
          if (inBox && !placed.some(function (p) {
                return hit(cand, p, 2);
              })) {
            placed.push(cand);
            done = true;
          }
        }
        if (!done) {
          el.setAttribute("transform", base);
          el.style.display = "none";
        }
      });
    } finally {
      fixing = false;
    }
  }

  box.innerHTML = "";
  var chart = echarts.init(box, null, { renderer: "svg" });
  var compact = null, builtWidth = 0;
  function render() {
    var c = box.clientWidth < 640;
    if (c === compact &&
        Math.abs(box.clientWidth - builtWidth) <= 120) {
      chart.resize();
      return;
    }
    compact = c;
    builtWidth = box.clientWidth;
    box.style.aspectRatio = c ? "620 / 960" : "960 / 620";
    setMode(c);
    chart.setOption(buildOption(c), true);
    chart.resize();
  }
  render();
  chart.on("finished", fixLabels);
  window.addEventListener("resize", render);
  chart.on("click", function (p) {
    if (p.dataType === "node" && p.data.href) {
      window.location.href = p.data.href;
    }
  });
})();
