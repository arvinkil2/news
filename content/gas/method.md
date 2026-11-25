---
title: "EU Gas: Method and Data Notes"
date: "2026-11-23"
lede: "How the EU Gas figures are computed, where the data comes from, and what is missing."
data_as_of: "Gas day 2026-11-23. Storage: GIE AGSI+. Flows: ENTSOG Transparency Platform, to 2026-11-25. Weather: national meteorological services, banked."
---

<h2>Sources</h2>
<p>Storage: GIE AGSI+, daily stock, injection, withdrawal and
working gas volume by country, banked in full from the source.
Flows: ENTSOG Transparency Platform zone aggregates, physical flow
and nominations by neighbouring system and by class. Weather:
daily mean temperature from the national meteorological services
of the five hub countries, population-weighted to a national mean
and converted to heating degree days on the Eurostat formula: on
days with a mean temperature at or below 15 degrees, heating
degree days equal 18 minus the mean temperature; otherwise
zero.</p>
<h2>The measures</h2>
<p>Fill is stock divided by working gas volume, as published by
AGSI+. Fill is always printed with stock and capacity in TWh.</p>
<p>Flow balance is injection divided by withdrawal, seven-day
mean. Below 1, storage is draining.</p>
<p>Days of cover, plain: stock divided by the mean daily net
withdrawal for the rest of the season, where the mean is taken
over the same calendar span in the last five winters.</p>
<p>Days of cover, normalized: stock divided by the mean fitted
daily net withdrawal for the rest of the season at normal
weather. The fit is a per-hub regression of daily net withdrawal
on heating degree days over the banked heating seasons. Normal
weather is the climatological heating degree day path: for each
calendar day, the mean heating degree days across the last five
winters that have weather data, lightly smoothed.</p>
<p>Projected March 31 fill: the stock is walked forward from the
latest gas day to March 31. The plain walk subtracts the
five-winter average net withdrawal for each calendar day. The
normalized walk subtracts the fitted drain at normal weather.
Both are storage paths at stated drain rates: neither models a
supply response, a price response or imports beyond what the
drain history already contains. If the walk reaches zero, the
date is printed and the path stops.</p>
<p>The European Union normalized figures use a fit of the EU
aggregate drain on a storage-weighted heating degree day index
of the five hub countries. The five-hub normalized figures walk
the summed stock with the summed hub fitted drains.</p>
<h2>The projection revision chart</h2>
<p>Each point is the March 31 projection as computed on that
date. Past winters are shown on the plain method. This winter is
shown on the plain method up to 2026-11-24, and on the
weather-normalized method from that date, which is when the
normalized method went live on these pages.</p>
<h2>Flows</h2>
<p>Hub totals are the sum of the generic transmission rows and
the per-neighbour rows in the ENTSOG zone aggregates. The two
sets cover disjoint entry and exit points. Austria publishes
only per-neighbour rows. Entry is presented by source class and
exit by destination class, as published. The two are never
netted into a forced balance: in the zone aggregates, the
published entry and exit figures for the Netherlands and Germany
do not sum to a closed balance against storage and demand, so a
closed balance would invent precision the source does not
carry. The generic transmission entry row combines several
entry points; the hub pages name the points it combines, and it
is not split further.</p>
<h2>What is not shown</h2>
<p>Cold-winter stress paths are computed in the background
analysis and are not displayed in this section. This section
shows the live supply picture and the normal-weather outlook.</p>
<h2>Named gaps</h2>
<p>Flow history: the ENTSOG backfill is still running. Recent
windows are complete; earlier seasons deepen as windows land,
and the pages rebuild from the banked files on every refresh,
so the history fills in without any change to the pages.</p>
<p>Weather, Austria: the banked Austrian series ends on
September 1, 2024, the publication boundary of its source
dataset. Austria has a fit on its earlier winters and
normalized figures, but no weather-expected line this winter.</p>
<p>Weather, Italy: the banked Italian series ends on August 24,
2025, a stall in its source feed. Italy has a fit on its earlier
winters and normalized figures, but no weather-expected line
this winter.</p>
<p>Storage history: the AGSI+ backfill is still running for some
hubs. Seasonal bands and revision history use the banked
windows and deepen as the backfill lands.</p>
<h2>Updates</h2>
<p>One refresh command recomputes every measure from the newest
banked files, rebuilds these pages and republishes only what
changed. It runs hourly. The collectors pull at each source's
own cadence, so a refresh with no new banked data changes
nothing and publishes nothing.</p>