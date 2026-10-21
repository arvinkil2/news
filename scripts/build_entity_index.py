#!/usr/bin/env python3
"""Build the cross-dataset entity index (Step B, first slice).

Reads data/entity_index_resolution.json (produced by
entity_resolve.py) and writes:
  content/entities/_index.md      the index page (coverage first)
  content/entities/<slug>.md      one hub page per company resolved
                                  into two datasets (swaps + bonds)
  layouts/entities/list.html      section layout (mirrors swaps)
  layouts/entities/single.html    hub layout (mirrors swaps)

The index records resolution and links; it copies no dataset content.
Page idiom (bw-summary strip, bw-grid adjustable tables, table
engine script) mirrors build_swaps_pages.py exactly.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from table_engine import TABLE_ENGINE_JS, bw_open, reset_btn  # noqa: E402

NEWS = os.path.expanduser("~/workspace/news-site")
RES = json.load(open(os.path.join(NEWS, "data",
                                  "entity_index_resolution.json")))
BONDS = json.load(open(os.path.join(NEWS, "data/macro/bonds.json")))
BOND_BY_CUSIP = {b["cusip"]: b for b in BONDS["bonds"]}
NPORT = json.load(open(os.path.join(NEWS, "data/macro/nport_panel.json")))
NPORT_BONDS = NPORT.get("bonds", {})
NPORT_LATEST_Q = NPORT.get("latest_quarter")


def bp(v):
    """Spread format identical to the swaps panel (one decimal)."""
    return "%.1f" % v


def mark_flag(cusip):
    e = NPORT_BONDS.get(cusip)
    if not e:
        return "Not held"
    lat = e.get("latest") or {}
    if lat.get("quarter") == NPORT_LATEST_Q and lat.get("median") is not None:
        return "Priced, latest panel"
    return "Held, earlier quarter"
DATE = "2026-10-21"
AS_OF = ("Swaps panel: September 2026 file month. Fund marks: "
         "N-PORT 2026 Q3 panel, built 2026-10-20. Bond registry: "
         "master registry of 2026-10-14 with daily updates.")


def esc(s):
    return html.escape(str(s), quote=True)


def frontmatter(title, lede, data_as_of):
    def q(s):
        return '"' + str(s).replace('"', "'") + '"'
    return ("---\ntitle: %s\ndate: %s\nlede: %s\ndata_as_of: %s\n---\n\n"
            % (q(title), q(DATE), q(lede), q(data_as_of)))


def strip(figures):
    items = "".join(
        '<div class="bw-sum-item"><dt>%s</dt><dd>%s</dd></div>'
        % (esc(k), esc(v)) for k, v in figures)
    return '<dl class="bw-summary">%s</dl>' % items


def grid_table(tid, cols, rows_html, sortable=False):
    return (bw_open(tid, cols, engine_sort=sortable)
            + "<tbody>" + rows_html + "</tbody></table>"
            + reset_btn(tid))


def tr(cells):
    return "<tr>" + "".join("<td>%s</td>" % c for c in cells) + "</tr>"


def write(relpath, title, lede, body):
    path = os.path.join(NEWS, "content", relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(frontmatter(title, lede, AS_OF))
        fh.write(body)
    return path


# ------------------------------------------------------------------ hubs
def hub_page(e):
    fam = e["family"] or e["canonical"]
    title = fam
    forms = e["swaps_forms"]
    figs = [("Bonds in the registry, this issuer", len(e["cusips"]))]
    if e["family_cusip_count"] > len(e["cusips"]):
        figs.append(("Bonds in the registry, whole family",
                     e["family_cusip_count"]))
    if e["nport"]:
        figs.append(("Bonds with fund marks, latest panel",
                     "%d of %d" % (e["nport"]["priced"],
                                   e["nport"]["total"])))
    figs.append(("CDS five-year median, Sep 2026 (bp)",
                 bp(e["bp_primary"])))
    figs.append(("Watched list",
                 (e["watched"]["tier"] if e["watched"] else "not listed")))
    body = [strip(figs)]
    body.append(
        "<p>%s appears under two name forms in two datasets: the "
        "swaps single-name CDS panel carries it as %s, and the bond "
        "registry carries it as %s. This page records that "
        "resolution and links each dataset's own pages. The data "
        "itself stays in those pages.</p>"
        % (esc(forms[0]), esc(", ".join(forms)),
           esc(", ".join(e["registry_issuers"]))))
    # name forms table
    rows = ""
    for f in forms:
        link = '<a href="/swaps/credit/names/">Single-name CDS panel</a>'
        if e["curve_slug"]:
            link += (' / <a href="/swaps/credit/name/%s/">Curve page</a>'
                     % e["curve_slug"])
        rows += tr(["Swaps, single-name CDS panel", esc(f), link])
    for iss in e["registry_issuers"]:
        link = ""
        if e["issuer_page"]:
            link = ('<a href="/leverage/issuer/%s/">Issuer page</a>'
                    % e["issuer_page"])
        rows += tr(["Bond registry", esc(iss), link])
    if e["watched"]:
        rows += tr(["FINRA watched list",
                    esc(e["watched"]["finra_name"]),
                    '<a href="/leverage/monitor/">Leverage Monitor</a>'
                    " (tier: %s)" % esc(e["watched"]["tier"])])
    if len(e["family_issuers"]) > len(e["registry_issuers"]):
        others = [i for i in e["family_issuers"]
                  if i not in e["registry_issuers"]]
        rows += tr(["Bond registry, same family (separate legal "
                    "issuers, not merged)", esc(", ".join(others)),
                    ('<a href="/leverage/issuer/%s/">Issuer page</a>'
                     % e["issuer_page"]) if e["issuer_page"] else ""])
    body.append("<h2>Names by dataset</h2>")
    body.append(grid_table("ent-names-%s" % e["slug"],
                           [("Dataset", 300, 170),
                            ("Name form", 340, 200),
                            ("Page", 320, 190)], rows))
    # bond links table
    rows = ""
    for c in e["cusips"]:
        b = BOND_BY_CUSIP.get(c, {})
        sec = b.get("security")
        if not sec:
            bits = []
            if b.get("coupon_pct"):
                bits.append("%s%%" % b["coupon_pct"])
            if b.get("maturity"):
                bits.append("due %s" % str(b["maturity"])[:4])
            sec = " ".join(bits) if bits else "Bond"
        rows += tr(['<a href="/leverage/bond/%s/">%s</a>'
                    % (c.lower(), esc(c)), esc(sec), mark_flag(c)])
    body.append("<h2>Bonds in the registry</h2>")
    body.append(grid_table("ent-bonds-%s" % e["slug"],
                           [("CUSIP", 140, 100),
                            ("Security", 560, 300),
                            ("Fund marks", 160, 110)], rows,
                           sortable=True))
    if e["nport"]:
        body.append(
            "<p>Fund marks, N-PORT 2026 Q3 panel: %d of %d of this "
            "issuer's bonds carry a priced fund position; the modal "
            "fund report date across those positions is %s. Marks "
            "themselves are on the bond pages.</p>"
            % (e["nport"]["priced"], e["nport"]["total"],
               e["nport"]["modal_period"] or "not reported"))
    body.append(
        "<p>Resolution: %s. Method: %s. Parent and subsidiary "
        "issuers are not merged: this page covers only the issuer "
        "strings named above.</p>"
        % (esc(e["evidence"]), esc(e["method"])))
    body.append(TABLE_ENGINE_JS)
    lede = ("Cross-dataset record for %s: swaps CDS panel name, bond "
            "registry issuer, watched-list entry and fund-mark "
            "coverage, with links to each dataset's pages." % fam)
    return write(os.path.join("entities", e["slug"] + ".md"),
                 title, lede, "".join(body))


# ----------------------------------------------------------------- index
def index_page():
    pa, pb = RES["pass_a"], RES["pass_b"]
    ents = pa["entities"]
    matched = [e for e in ents if e["status"] == "matched"]
    sov = sum(1 for e in ents if "sovereign" in e["reason"])
    loan = sum(1 for e in ents if "loan underlier" in e["reason"])
    corp = sum(1 for e in ents
               if e["status"] == "unmatched" and "sovereign" not in e["reason"]
               and "loan underlier" not in e["reason"])
    trusts = pb["trusts"]
    t_in = sum(1 for t in trusts if t["in_panel"])
    body = [strip([
        ("Companies in the index", len(ents)),
        ("Companies in two datasets", len(matched)),
        ("CMBS trust pages in the index", len(trusts)),
        ("Trust pages with fund marks", t_in),
    ])]
    body.append(
        "<p>This index resolves the site's entities once, across "
        "datasets that name the same company or trust in different "
        "forms. It records what exists where: which swaps panel "
        "names are bond issuers here, which are not, and which CMBS "
        "trusts carry fund marks. It holds no market data of its "
        "own; every row links to the page that owns the data.</p>")
    cov = ""
    cov += tr(["Swaps single-name panel rows, Sep 2026", pa["panel_rows"]])
    cov += tr(["Resolved companies (variant name forms merged)",
               len(ents)])
    cov += tr(["Companies matched to the bond registry", len(matched)])
    cov += tr(["Companies matched to the watched list",
               len(pa["watched_matched"])])
    cov += tr(["Panel companies not matched: sovereign reference "
               "entities", sov])
    cov += tr(["Panel companies not matched: loan underlier strings, "
               "not CDS reference entities", loan])
    cov += tr(["Panel companies not matched: no bonds in this "
               "registry", corp])
    cov += tr(["Bond registry families", pa["registry_families_total"]])
    cov += tr(["Registry families with a swaps panel name",
               len(pa["registry_families_matched"])])
    cov += tr(["Registry families with no swaps panel name",
               len(pa["registry_families_unmatched"])])
    cov += tr(["Watched issuers", pa["watched_total"]])
    cov += tr(["Watched issuers with no swaps panel name",
               len(pa["watched_unmatched"])])
    cov += tr(["CMBS trust pages", pb["trust_pages"]])
    cov += tr(["Trust pages with fund marks in the latest panel", t_in])
    cov += tr(["Trust pages with no fund marks in the latest panel",
               len(trusts) - t_in])
    cov += tr(["Classes in the CMBS fund-marks panel",
               pb["marks_classes_total"]])
    body.append("<h2>Coverage</h2>")
    body.append(grid_table("ent-coverage",
                           [("Measure", 560, 300),
                            ("Count", 140, 90, True)], cov))
    # companies table
    rows = ""
    for e in ents:
        name = esc(e["canonical"])
        swaps_cell = '<a href="/swaps/credit/names/">Panel</a>'
        if e["curve_slug"]:
            swaps_cell += (' / <a href="/swaps/credit/name/%s/">Curve</a>'
                           % e["curve_slug"])
        marks = "no bonds in registry"
        if e["nport"]:
            marks = "%d of %d" % (e["nport"]["priced"],
                                  e["nport"]["total"])
        hub = ""
        if e["status"] == "matched":
            hub = '<a href="/entities/%s/">Index page</a>' % e["slug"]
        rows += tr([name, bp(e["bp_primary"]),
                    esc(" / ".join(e["swaps_forms"])), swaps_cell,
                    len(e["cusips"]) if e["cusips"] else "0",
                    marks,
                    esc(e["watched"]["tier"] if e["watched"]
                        else "not listed"),
                    hub])
    body.append("<h2>Companies: swaps panel against the bond "
                "registry</h2>")
    body.append(
        "<p>Every company on the swaps single-name CDS panel, "
        "resolved against the bond registry and the watched list. "
        "A bond count of zero is a finding, not missing data: the "
        "registry covers the AI infrastructure stack and a big-tech "
        "benchmark set, and most panel names sit outside it.</p>")
    body.append(grid_table(
        "ent-companies",
        [("Entity", 250, 150), ("CDS 5Y median, Sep 2026 (bp)", 130, 96, True),
         ("Name forms in the panel", 260, 150), ("Swaps", 110, 76),
         ("Bonds in registry", 110, 84, True), ("Bonds with fund marks", 120, 92),
         ("Watched list", 90, 70), ("Cross-dataset page", 130, 92)],
        rows, sortable=True))
    # trusts table
    rows = ""
    for t in sorted(trusts, key=lambda x: x["name"]):
        link = '<a href="/cmbs/deal/%s/">%s</a>' % (t["slug"],
                                                    esc(t["name"]))
        if t["db_status"] != "resolved":
            classes = "outside the merged dataset"
            marks = "none"
            reports = "none"
            period = "no classes in the dataset"
        else:
            classes = t["classes_total"]
            marks = t["classes_with_marks"]
            reports = t["fund_class_reports"]
            period = (t["mark_period_modal"] or
                      "no fund marks in the 2026 Q3 panel")
        rows += tr([link, classes, marks, reports, period])
    body.append("<h2>CMBS trusts against the fund-marks panel</h2>")
    body.append(
        "<p>Every CMBS trust page on the site, resolved to its "
        "classes in the merged dataset and checked against the "
        "N-PORT fund-marks panel (2026 Q3). Fund-class reports "
        "counts one fund holding one class once; a fund holding "
        "several classes of a trust is counted once per class. "
        "The mark period is the modal fund report date across the "
        "trust's marked classes.</p>")
    body.append(grid_table(
        "ent-trusts",
        [("Trust", 420, 240), ("Classes", 90, 70, True),
         ("Classes with fund marks", 130, 100, True),
         ("Fund-class reports", 120, 96, True),
         ("Latest mark period (fund report date)", 190, 130)],
        rows, sortable=True))
    body.append(
        "<h2>How resolution works</h2>"
        "<p>Names are compared after case, punctuation and legal "
        "suffix forms are unified (Corporation with Corp, "
        "Incorporated with Inc). A company matches when its unified "
        "name, or its name with the legal suffix removed, equals a "
        "registry issuer or a watched-list name. The issuer "
        "crosswalk maintained with the leverage monitor serves as "
        "the alias layer. A name that could belong to two registry "
        "families is recorded as ambiguous and is never forced; in "
        "this build there were none. Parent and subsidiary issuers "
        "are kept separate.</p>"
        "<p>Trusts resolve by name to their classes in the merged "
        "dataset; where a page prints its CIK and segment, the "
        "resolution uses that exact unit. Four trust pages have no "
        "unit in the merged dataset: three 2026 deals that postdate "
        "it and one 1998 trust outside the dataset's universe.</p>")
    body.append(TABLE_ENGINE_JS)
    lede = ("One resolution of the companies and trusts the site "
            "covers, across the swaps panel, the bond registry and "
            "the fund filings: what exists where, and what does "
            "not resolve.")
    return write(os.path.join("entities", "_index.md"),
                 "Entity Index", lede, "".join(body))


def layouts():
    tpl = ("{{ define \"main\" }}\n"
           "<h1 class=\"page-title\">{{ .Title }}</h1>\n"
           "{{ with .Params.data_as_of }}"
           "<p class=\"data-vintage\">{{ . }}</p>{{ end }}\n"
           "{{ with .Params.lede }}<p class=\"lede\">{{ . }}</p>"
           "{{ end }}\n"
           "<article class=\"prose\">\n{{ .Content }}\n</article>\n"
           "{{ end }}\n")
    for name in ("list.html", "single.html"):
        path = os.path.join(NEWS, "layouts", "entities", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(tpl)


def main():
    layouts()
    p = index_page()
    print("index:", p)
    for e in RES["pass_a"]["entities"]:
        if e["status"] == "matched":
            print("hub:", hub_page(e))


if __name__ == "__main__":
    main()
