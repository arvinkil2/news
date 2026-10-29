/* Positioning section: pos-table sorting and filtering, chart
   range presets, market finder. One file, no dependencies, no
   stored state. Tables are complete as rendered; this script only
   reorders and filters rows already on the page. */
(function () {
  function cellVal(td) {
    var v = td.getAttribute('data-v');
    if (v === null || v === '') return null;
    return v;
  }
  document.querySelectorAll('table.pos-table').forEach(function (t) {
    var tid = t.id;
    var state = document.getElementById(tid + '-state');
    var tbody = t.querySelector('tbody');
    t.querySelectorAll('.pos-sort-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var col = parseInt(btn.getAttribute('data-c'), 10);
        var type = btn.getAttribute('data-type');
        var cur = btn.getAttribute('data-dir');
        var dir;
        if (cur) { dir = (cur === 'desc') ? 'asc' : 'desc'; }
        else { dir = (type === 'num' || type === 'date') ? 'desc' : 'asc'; }
        t.querySelectorAll('.pos-sort-btn').forEach(function (b) {
          b.removeAttribute('data-dir');
          var a = b.querySelector('.arr'); if (a) a.textContent = '';
          b.closest('th').removeAttribute('aria-sort');
        });
        btn.setAttribute('data-dir', dir);
        var arr = btn.querySelector('.arr');
        if (arr) arr.textContent = (dir === 'desc') ? ' \u25BC' : ' \u25B2';
        btn.closest('th').setAttribute('aria-sort',
          dir === 'desc' ? 'descending' : 'ascending');
        var rows = Array.prototype.slice.call(
          tbody.querySelectorAll('tr.pos-row'));
        var mul = (dir === 'desc') ? -1 : 1;
        rows.sort(function (ra, rb) {
          var ca = ra.children[col], cb = rb.children[col];
          var va = ca ? cellVal(ca) : null;
          var vb = cb ? cellVal(cb) : null;
          if (va === null && vb === null) return 0;
          if (va === null) return 1;
          if (vb === null) return -1;
          if (type === 'num' || type === 'date') {
            var na = parseFloat(va), nb = parseFloat(vb);
            if (!isNaN(na) && !isNaN(nb)) return (na - nb) * mul;
          }
          return String(va).localeCompare(String(vb)) * mul;
        });
        rows.forEach(function (r) { tbody.appendChild(r); });
        if (state) {
          state.textContent = 'Sorted by ' + btn.getAttribute('data-label')
            + ', ' + (dir === 'desc' ? 'descending' : 'ascending')
            + '. Order as published: ' + t.getAttribute('data-order');
        }
      });
    });
  });
  document.querySelectorAll('.pos-filter-input').forEach(function (inp) {
    var tid = inp.getAttribute('data-for');
    var t = document.getElementById(tid);
    if (!t) return;
    var count = document.querySelector(
      '.pos-count[data-for="' + tid + '"]');
    var rows = Array.prototype.slice.call(
      t.querySelectorAll('tr.pos-row'));
    function apply() {
      var q = inp.value.trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (r) {
        var nm = r.getAttribute('data-name') || '';
        var ok = (!q || nm.indexOf(q) !== -1);
        r.style.display = ok ? '' : 'none';
        if (ok) shown += 1;
      });
      if (count) {
        count.textContent = q ? (shown + ' of ' + rows.length
          + ' shown') : '';
      }
    }
    inp.addEventListener('input', apply);
  });
  document.querySelectorAll('.pos-range').forEach(function (bar) {
    var cid = bar.getAttribute('data-chart');
    bar.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () {
        var r = b.getAttribute('data-r');
        bar.querySelectorAll('button').forEach(function (x) {
          x.classList.toggle('on', x === b);
        });
        document.querySelectorAll(
          '.pos-panel[data-chart="' + cid + '"]').forEach(
          function (p) {
            p.hidden = (p.getAttribute('data-r') !== r);
          });
      });
    });
  });
  var finder = document.getElementById('pos-finder-input');
  if (finder) {
    var dataEl = document.getElementById('pos-finder-data');
    var out = document.getElementById('pos-finder-results');
    if (dataEl && out) {
      var entries = JSON.parse(dataEl.textContent);
      finder.addEventListener('input', function () {
        var q = finder.value.trim().toLowerCase();
        out.innerHTML = '';
        if (!q) return;
        var n = 0;
        entries.forEach(function (e) {
          if (n >= 12) return;
          if (e.n.toLowerCase().indexOf(q) === -1
              && e.a.indexOf(q) === -1) return;
          var d = document.createElement('div');
          var a = document.createElement('a');
          a.href = e.u; a.textContent = e.n;
          d.appendChild(a);
          var s = document.createElement('span');
          s.className = 'fam';
          s.textContent = e.f + ', ' + e.d;
          d.appendChild(s);
          out.appendChild(d);
          n += 1;
        });
        if (!n) {
          out.textContent = 'No market in the section matches.';
        }
      });
    }
  }
})();
