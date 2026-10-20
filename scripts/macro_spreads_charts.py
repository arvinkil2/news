#!/usr/bin/env python3
"""Regenerate sovereign-spread history charts for the news site macro pages.
Uses the institutional chart style. Output: ~/workspace/news-site/static/macro/
Source data: ~/workspace/sovereign-spreads/data/ (static vintage, Aug 2026).
"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
import sys, os
sys.path.insert(0, '/home/hatch/workspace/research-site')
import chart_style
chart_style.apply()

DATA = '/home/hatch/workspace/sovereign-spreads/data'
OUT = '/home/hatch/workspace/news-site/static/macro'
os.makedirs(OUT, exist_ok=True)

sp = pd.read_csv(f'{DATA}/spreads_bp_monthly.csv', index_col=0, parse_dates=True)
panel = pd.read_csv(f'{DATA}/panel_10y_monthly.csv', index_col=0, parse_dates=True)

def finalize(fig, path):
    chart_style.qa_check(fig)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("saved", path)

years = mdates.YearLocator(2); yfmt = mdates.DateFormatter('%Y')

# 1: Europe spreads vs Bund
fig, ax = plt.subplots(figsize=(7.5, 4.2))
for c, lbl in [('FR','France'),('IT','Italy'),('ES','Spain'),('GB','United Kingdom'),('BE','Belgium'),('PL','Poland')]:
    ax.plot(sp.index, sp[c], label=lbl, lw=1.4)
ax.axhline(0, color='black', lw=0.8)
ax.set_ylabel('Spread vs German 10Y (bp)')
ax.set_title('Sovereign 10-year spreads vs Germany, 2006-2026')
ax.xaxis.set_major_locator(years); ax.xaxis.set_major_formatter(yfmt)
ax.set_xlabel('Date')
ax.legend(frameon=False, fontsize=8, loc='upper left', bbox_to_anchor=(1.01, 1.0), ncols=1)
finalize(fig, f'{OUT}/spreads_europe.png')

# 2: Benchmark yield levels
fig, ax = plt.subplots(figsize=(7.5, 4.2))
for c, lbl in [('US','United States'),('DE','Germany'),('JP','Japan')]:
    ax.plot(panel.index, panel[c], label=lbl, lw=1.4)
ax.set_ylabel('10-year yield (%)')
ax.set_title('Regional benchmark 10-year yields, 2006-2026')
ax.xaxis.set_major_locator(years); ax.xaxis.set_major_formatter(yfmt)
ax.set_xlabel('Date')
ax.legend(frameon=False, fontsize=8, loc='upper left', bbox_to_anchor=(1.01, 1.0))
finalize(fig, f'{OUT}/benchmark_yields.png')

# 3: Then vs now bars
order = ['FR','BE','ES','IT','GB','PL','CH','CA','MX','CL','KR','AU']
s2006 = sp.loc['2006-01-01':'2006-12-01', order].mean()
s2026 = sp.loc['2026-08-01', order]
y = np.arange(len(order)); h = 0.38
fig, ax = plt.subplots(figsize=(7.5, 5.2))
ax.barh(y+h/2, s2006.values, h, label='2006 avg')
ax.barh(y-h/2, s2026.values, h, label='Aug 2026')
ax.set_yticks(y); ax.set_yticklabels(order)
ax.set_xlabel('Spread vs regional benchmark (bp)')
ax.set_ylabel('Country')
ax.set_title('10-year spreads: 2006 average vs August 2026')
ax.legend(frameon=False, fontsize=8, loc='upper left', bbox_to_anchor=(1.01, 1.0))
ax.axvline(0, color='black', lw=0.8)
finalize(fig, f'{OUT}/spreads_then_now.png')
