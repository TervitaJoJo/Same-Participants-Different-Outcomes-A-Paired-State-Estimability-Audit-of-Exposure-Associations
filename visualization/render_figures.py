"""Independent Matplotlib visualizations from existing aggregate results.

No Vivid source, templates or helpers are used. These alternative layouts retain
supplied values and intervals; they do not recreate the manuscript's exact artwork.
Input: external JCE 'data and analysis' directory. Output: new PNG/TIF/PDF files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INPUTS = {
    'simulation': 'aggregate_tables/simulation_full.csv',
    'states': 'aggregate_tables/CHARLS_state_support.csv',
    'joint': 'aggregate_tables/S5_CHARLS_estimates.csv',
    'scan': 'aggregate_tables/S1_scan.csv',
    'cvai': 'aggregate_tables/CVAI_common_OR.csv',
    'flow': 'aggregate_tables/FigureS1_flow.csv',
    'failures': 'aggregate_tables/S3_failures.csv',
    'hrs': 'hrs_external_application/results/marginal_estimates.csv',
    'nhanes_adjustment': 'breadth_exports/aggregate_sources/FigureS14.csv',
    'nhanes_selection': 'breadth_exports/aggregate_sources/FigureS16.csv',
}
LABELS = {'delta': r'$\Delta_m$', 'unreported_component': r'$C_U$',
          'history_normal_component': r'$C_V$', 'CU': r'$C_U$', 'CV': r'$C_V$',
          'delta_m': r'$\Delta_m$', 'C_U': r'$C_U$', 'C_V': r'$C_V$'}
COLORS = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00',
          '#56B4E9', '#777777', '#6F4C9B', '#332288']


def forest(ax, df, labels, *, value='estimate', lower='lo', upper='hi', null=0,
           xlabel='', log=False):
    vals = df[[value, lower, upper]].to_numpy(float)
    if not len(vals) or not np.isfinite(vals).all():
        raise ValueError('Forest inputs must have finite supplied estimates and intervals')
    if np.any(vals[:, 1] > vals[:, 2]):
        raise ValueError('Lower endpoint exceeds upper endpoint')
    if log and np.any(vals <= 0):
        raise ValueError('Log-axis inputs must be positive ratios, not log ratios')
    y = np.arange(len(df))
    ax.hlines(y, vals[:, 1], vals[:, 2], color=COLORS[0], linewidth=1.5)
    ax.scatter(vals[:, 0], y, c=COLORS[0], s=23, zorder=3)
    ax.axvline(null, color='0.5', linestyle='--', linewidth=.8)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    if log:
        ax.set_xscale('log')
    ax.set_xlabel(xlabel)
    ax.grid(axis='x', alpha=.15)


def build(data):
    figures = []
    sim = data['simulation']
    primary = sim[sim.method.eq('primary') & sim.estimand.eq('delta')]
    fig, axs = plt.subplots(1, 3, figsize=(10.8, 4.5), layout='constrained')
    for i, (scenario, sub) in enumerate(primary.groupby('scenario', sort=True)):
        sub = sub.sort_values('n')
        for ax, metric in zip(axs, ['estimable_rate', 'coverage_conditional', 'rmse']):
            scale = 100 if metric != 'rmse' else 1
            ax.plot(sub.n, scale * sub[metric], marker='o', markersize=3,
                    color=COLORS[i], label=scenario.replace('_', ' '), linewidth=1.2)
    for ax, title in zip(axs, ['Estimability (%)', 'Conditional coverage (%)', r'$\Delta_m$ RMSE']):
        ax.set_xlabel('Simulated sample size'); ax.set_ylabel(title)
    axs[0].set_ylim(0, 103); axs[1].set_ylim(0, 103)
    axs[1].axhline(95, color='0.45', linestyle='--', linewidth=.8)
    fig.legend(*axs[0].get_legend_handles_labels(), loc='outside lower center', ncols=3, fontsize=8)
    figures.append(('Figure1_simulation', fig,
        'Primary simulation specification. Coverage is conditional on estimability; RMSE is on the log-odds-ratio difference scale.'))

    states = data['states']
    scopes = ['current', 'never', 'former']
    state_order = ['M0S0', 'M0S1', 'M1S0', 'M1S1']
    counts = states[states.scope.isin(scopes)].pivot(index='scope', columns='state', values='n').loc[scopes, state_order]
    if counts.isna().any().any():
        raise ValueError('Incomplete CHARLS exposure-by-state table')
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2), layout='constrained', width_ratios=[1, 1.3])
    base = np.zeros(len(scopes))
    for i, state in enumerate(state_order):
        vals = 100 * counts[state].to_numpy() / counts.sum(axis=1).to_numpy()
        axs[0].bar(scopes, vals, bottom=base, label=state, color=COLORS[i]); base += vals
    axs[0].set_ylabel('Unweighted state proportion (%)')
    axs[0].legend(fontsize=7, loc='lower left')
    joint = data['joint']
    metrics = ['delta', 'unreported_component', 'history_normal_component']
    j = joint[joint.contrast.eq('current_vs_noncurrent')].set_index('metric').loc[metrics].reset_index()
    forest(axs[1], j, [LABELS[k] for k in j.metric], xlabel='Marginal contrast / allocation (log OR)')
    axs[1].set_title('Current versus noncurrent smoking', fontsize=10)
    figures.append(('Figure2_CHARLS', fig,
        'CHARLS unweighted state proportions by smoking status and marginal allocation for current versus noncurrent smoking. Intervals are supplied 95% confidence intervals.'))

    scan = data['scan']
    fig, ax = plt.subplots(figsize=(8.5, max(5, len(scan) * .28)), layout='constrained')
    forest(ax, scan, [f'{d} (n={int(n):,})' for d, n in zip(scan.dataset, scan.n)],
           value='delta', xlabel=r'Conditional paired contrast $\Delta_c$ (log OR)')
    figures.append(('Figure3_programme_scan', fig,
        'Programme-specific conditional paired contrasts with supplied 95% confidence intervals. These heterogeneous programme estimates are not pooled.'))

    cv = data['cvai']
    fig, ax = plt.subplots(figsize=(7.5, 3.3), layout='constrained')
    forest(ax, cv, cv.outcome.tolist(), value='point', null=1, log=True,
           xlabel='Odds ratio per 10-unit increase in CVAI')
    figures.append(('Figure4_CVAI', fig,
        'CVAI reconstruction on the supplied common sample. S: reported diagnosis; M: measured definition; MT: measured or treatment; SMT: union of reported, measured and treatment definitions.'))

    flow = data['flow']
    fig, ax = plt.subplots(figsize=(9, max(5, .29 * len(flow))), layout='constrained')
    left = np.zeros(len(flow)); y = np.arange(len(flow))
    for i, col in enumerate(['complete_n', 'excluded_covariates', 'excluded_smoking', 'excluded_outcomes', 'excluded_age']):
        ax.barh(y, flow[col], left=left, color=COLORS[i], label=col.replace('_', ' ')); left += flow[col].to_numpy()
    if not np.allclose(left, flow.start_n):
        raise ValueError('Flow categories do not sum to the reported entry denominator')
    ax.set_yticks(y, flow.dataset); ax.invert_yaxis(); ax.set_xlabel('Records within each programme-specific entry frame')
    fig.legend(*ax.get_legend_handles_labels(), loc='outside lower center', ncols=3, fontsize=8)
    figures.append(('FigureS1_sample_flow', fig,
        'Sample accounting within heterogeneous entry frames. Complete records and sequential exclusions sum to each supplied start_n; entry frames do not share one recruitment denominator.'))

    c = sim.copy()
    c['label'] = c.scenario + ' | ' + c.n.astype(str) + ' | ' + c.method
    matrix = c.pivot(index='label', columns='estimand', values='coverage_conditional')[['delta', 'CU', 'CV']]
    fig, ax = plt.subplots(figsize=(8.5, max(5, .26 * len(matrix))), layout='constrained')
    im = ax.imshow(100 * matrix.to_numpy(), vmin=0, vmax=100, aspect='auto', cmap='cividis')
    ax.set_yticks(np.arange(len(matrix)), matrix.index, fontsize=7)
    ax.set_xticks(range(3), [LABELS[k] for k in matrix.columns])
    for (i, j), val in np.ndenumerate(matrix.to_numpy()):
        ax.text(j, i, f'{val * 100:.1f}' if np.isfinite(val) else 'NA', ha='center', va='center',
                fontsize=7, color='black' if val > .55 else 'white')
    fig.colorbar(im, ax=ax, label='Coverage conditional on estimability (%)', shrink=.55)
    figures.append(('FigureS2_simulation_coverage', fig,
        'Conditional coverage for all three quantities and all supplied simulation specifications. Values are percentages; failed fits are excluded from this conditional denominator.'))

    fail = data['failures'].copy()
    keys = ['scenario', 'n', 'method']
    den = sim[keys + ['repetitions']].drop_duplicates()
    fail = fail.merge(den, on=keys, validate='many_to_one')
    fail['label'] = fail.scenario + ' | n=' + fail.n.astype(str) + ' | ' + fail.method
    f = fail.pivot_table(index='label', columns='status', values='count', aggfunc='sum', fill_value=0)
    denominators = fail.groupby('label').repetitions.first().reindex(f.index)
    fig, ax = plt.subplots(figsize=(9, max(3.5, .35 * len(f))), layout='constrained')
    left = np.zeros(len(f))
    for i, col in enumerate(f.columns):
        val = 100 * f[col].to_numpy() / denominators.to_numpy()
        ax.barh(np.arange(len(f)), val, left=left, label=col.replace('_', ' '), color=COLORS[i]); left += val
    ax.set_yticks(np.arange(len(f)), [f'{label} (R={int(n)})' for label, n in zip(f.index, denominators)])
    ax.invert_yaxis(); ax.set_xlabel('Failed estimator rows / attempted replicates (%)')
    fig.legend(*ax.get_legend_handles_labels(), loc='outside lower center', fontsize=7)
    figures.append(('FigureS3_simulation_failures', fig,
        'Failure reasons among simulation specifications with at least one failure. R is the attempted replicate denominator for that estimator; zero-failure specifications are absent.'))

    hrs = data['hrs']
    h = hrs[hrs.metric.isin(['delta_m', 'C_U', 'C_V'])].copy()
    fig, ax = plt.subplots(figsize=(8.6, 6.4), layout='constrained')
    forest(ax, h, [f'{case}: {LABELS[metric]}' for case, metric in zip(h.case, h.metric)],
           xlabel='HRS marginal contrast / allocation (log OR)')
    figures.append(('FigureS4_HRS', fig,
        'HRS external application. full_unweighted uses current versus noncurrent smoking; full_never uses current versus never. Eligible specifications cross fitting/target weights: UU unit/unit, WU weighted/unit, UW unit/weighted, WW weighted/weighted. The populations and targets must be read separately.'))

    d = data['nhanes_adjustment']
    fig, ax = plt.subplots(figsize=(8.4, max(3.8, .32 * len(d))), layout='constrained')
    # This historical plotting source stores already exponentiated ORs despite metric='logOR'.
    forest(ax, d, d.label, null=1, log=True, xlabel='Odds ratio (supplied plotting values)')
    figures.append(('FigureS5_NHANES_adjustment', fig,
        'NHANES adjustment specifications. The plotting source already contains exponentiated odds ratios and endpoints; no second exponentiation is applied.'))

    d = data['nhanes_selection']
    fig, ax = plt.subplots(figsize=(8.4, max(3.4, .36 * len(d))), layout='constrained')
    forest(ax, d, d.label, xlabel='Change in log odds ratio between supplied specifications')
    figures.append(('FigureS6_NHANES_selection', fig,
        'NHANES nested eligibility and weighting contrasts. Values are changes in log odds ratios with supplied confidence intervals, not causal selection effects.'))
    return figures


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--dpi', type=int, default=300)
    args = p.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        p.error('Use a new or empty output directory')
    missing = [str(args.inputs / v) for v in INPUTS.values() if not (args.inputs / v).is_file()]
    if missing:
        p.error('Missing aggregate inputs:\n' + '\n'.join(missing))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'pdf.fonttype': 42,
                         'axes.spines.top': False, 'axes.spines.right': False})
    data = {k: pd.read_csv(args.inputs / v) for k, v in INPUTS.items()}
    hashes = {v: hashlib.sha256((args.inputs / v).read_bytes()).hexdigest() for v in INPUTS.values()}
    figures = build(data)
    args.output.mkdir(parents=True, exist_ok=True)
    captions = ['# Alternative aggregate-result visualizations', '',
                'Independent Matplotlib layouts. Values and intervals are read from the supplied aggregates.', '']
    for name, fig, caption in figures:
        for ext in ['png', 'tif', 'pdf']:
            kw = {'pil_kwargs': {'compression': 'tiff_lzw'}} if ext == 'tif' else {}
            fig.savefig(args.output / f'{name}.{ext}', dpi=args.dpi, **kw)
        plt.close(fig)
        captions.extend([f'## {name}', '', caption, ''])
        print(name, flush=True)
    (args.output / 'captions.md').write_text('\n'.join(captions), encoding='utf-8')
    if any(hashlib.sha256((args.inputs / path).read_bytes()).hexdigest() != digest for path, digest in hashes.items()):
        raise RuntimeError('Aggregate input changed during rendering')
    (args.output / 'render_manifest.json').write_text(json.dumps({
        'renderer': 'Independent Matplotlib alternative; not original Vivid artwork',
        'input_sha256': hashes, 'input_rows': {k: len(v) for k, v in data.items()},
        'figures': [name for name, _, _ in figures], 'formats': ['png', 'tif', 'pdf'],
        'matplotlib': matplotlib.__version__, 'inputs_unchanged': True,
    }, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
