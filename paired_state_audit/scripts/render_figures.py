from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from templates.denominator_sankey import continue_covered_flow, draw_sankey
from templates.allocation_waterfall import draw_allocation
from templates.charls_joint_states import draw_joint_states


PACKAGE = Path(__file__).resolve().parents[1]
DATA = PACKAGE / "data" / "derived"
OUT = PACKAGE / "outputs"
FIG = OUT / "figures"
SUP = OUT / "supplementary_figures"

BLUE = "#1f5a94"
CORAL = "#c44e52"
TEAL = "#2a9d8f"
GOLD = "#d98f39"
INK = "#1f2933"
GREY = "#5b6573"
LIGHT = "#e8eef4"
MID = "#b5c1cc"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#7c8792",
    "axes.linewidth": 0.8,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})


def save(fig, name, supplementary=False):
    target = SUP if supplementary else FIG
    for ext in ("png", "tif", "pdf"):
        fig.savefig(target / f"{name}.{ext}", dpi=400, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def configure_output(path):
    """Select a new output directory without changing the bundled inputs."""
    global OUT, FIG, SUP
    OUT = Path(path).resolve()
    FIG = OUT / "figures"
    SUP = OUT / "supplementary_figures"
    FIG.mkdir(parents=True, exist_ok=True)
    SUP.mkdir(parents=True, exist_ok=True)


def clean(ax):
    ax.grid(axis="x", color="#d9e1e8", linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=3, color="#7c8792")


def label_panels(fig, axes):
    y = max(ax.get_position().y1 for ax in axes) + .025
    for label, ax in zip(("A", "B"), axes):
        fig.text(ax.get_position().x0, y, label, ha="left", va="bottom",
                 fontsize=12, fontweight="bold", color=INK)


def load_inputs():
    names = ["direction_reversal", "simulation", "charls_states", "charls_bridge",
             "cvai_or", "cvai_contrasts", "sample_flow", "failures", "charls_estimates"]
    loaded = {name: pd.read_csv(DATA / f"{name}.csv") for name in names}
    hrs = pd.read_csv(DATA / "hrs_application.csv")
    return (loaded["direction_reversal"], loaded["simulation"], loaded["charls_states"],
            loaded["charls_bridge"], loaded["cvai_or"], loaded["cvai_contrasts"],
            loaded["sample_flow"], loaded["failures"], loaded["charls_estimates"], hrs)


def fig1(reversal):
    d = reversal[reversal.point_estimate_reversal].copy().reset_index(drop=True)
    d["sig"] = d.ci_excludes_zero.astype(bool)
    d["label"] = d.dataset + " (" + d.country + ")"
    d["m"] = np.log(d.or_measured)
    d["s"] = np.log(d.or_selfreport)
    y = np.arange(len(d))[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 5.1))
    for yi, row in zip(y, d.itertuples()):
        line = INK if row.sig else MID
        ax.plot([row.m, row.s], [yi+0.075, yi-0.075], color=line, lw=2.4 if row.sig else 1.7, ls="-" if row.sig else "--", zorder=2)
        fc_m = BLUE if row.sig else "white"
        fc_s = CORAL if row.sig else "white"
        ax.scatter(row.m, yi + 0.075, s=48, c=fc_m, edgecolors=BLUE, linewidths=1.2, zorder=3, label="M" if yi == y[0] else None)
        ax.scatter(row.s, yi - 0.075, s=48, c=fc_s, edgecolors=CORAL, linewidths=1.2, zorder=3, label="S" if yi == y[0] else None)
    ax.axvline(0, color=INK, lw=1.4, zorder=1)
    ax.set_yticks(y)
    ax.set_yticklabels(d.label)
    ax.set_xlabel("log odds ratio for current versus noncurrent smoking")
    ax.set_xlim(-0.62, 0.38)
    ax.set_xticks(np.arange(-0.6, 0.41, 0.2))
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE, markeredgecolor=BLUE, markersize=7, label="M"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=CORAL, markeredgecolor=CORAL, markersize=7, label="S"),
    ], frameon=False, loc="lower right", ncol=2, fontsize=8)
    clean(ax)
    fig.tight_layout()
    save(fig, "Figure1_direction_reversals")


def fig2(sim, failure):
    d = sim[(sim.scenario == "very_sparse") & (sim.method == "primary")].copy()
    terms = ["delta", "CU", "CV"]
    d500 = d[d.n == 500].set_index("estimand").loc[terms]
    f = failure[(failure.scenario == "very_sparse") & (failure.n == 500) & (failure.method == "primary")].iloc[0]
    attempted = int(f[["valid", "zero_required_state_cell", "fit_or_check_failure", "ill_conditioned_hessian"]].sum())
    valid = int(f.valid)
    covered = int(round(valid*d500.loc["delta", "coverage_conditional"]))
    assert (attempted, valid, covered) == (400, 12, 12)
    assert d500.coverage_conditional.eq(1).all() and d500.coverage_all.eq(.03).all()
    # At 174 mm, a 9 pt source label remains about 8.5 pt on the page.
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.4), gridspec_kw={"width_ratios": [1.55, 1.0]})
    _, ranges = draw_sankey(ax1, [("Attempted",attempted)], [("Valid",valid),("Failed",attempted-valid)],
                           [{"source_idx":0,"target_idx":0,"value":valid,"color":TEAL},
                            {"source_idx":0,"target_idx":1,"value":attempted-valid,"color":MID}],
                           [BLUE], [TEAL,GREY], left_x=.10, right_x=.50)
    continue_covered_flow(ax1, ranges[0], .50, .90, TEAL)
    ax1.set_xticks([.10,.50,.90], ["Attempts","Estimation","Coverage"])
    ax1.set_yticks([])
    for spine in ax1.spines.values():
        spine.set_visible(False)
    ax1.tick_params(axis="x", length=0)
    ax1.legend(handles=[Patch(facecolor=BLUE,label="Attempted"),
                        Patch(facecolor=TEAL,label="Valid / covering"),
                        Patch(facecolor=GREY,label="Failed")],
               frameon=False,ncol=2,fontsize=8,loc="upper center",bbox_to_anchor=(.5,-.10))
    ax2.barh([1,0], [100*covered/valid,100*covered/attempted], height=.42,
             color=[BLUE,TEAL], edgecolor="white")
    ax2.set_yticks([1,0], ["Conditional\ncoverage","Success +\ncoverage"])
    ax2.set_xlim(0,105)
    ax2.set_xticks([0,25,50,75,100])
    ax2.set_xlabel("Percentage")
    ax2.set_ylim(-.55,1.55)
    clean(ax2)
    fig.tight_layout(w_pad=2.4)
    label_panels(fig, (ax1, ax2))
    save(fig, "Figure2_simulation_denominator_trap")


def fig3(states, charls):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 4.0), gridspec_kw={"width_ratios": [1.08, 1.0]})
    records = draw_joint_states(ax1, states)
    b = charls[charls.contrast == "current_vs_noncurrent"].set_index("metric")
    total = b.loc["delta"]
    draw_allocation(ax2, b.loc["unreported_component","estimate"],
                    b.loc["history_normal_component","estimate"],total.estimate,total.lo,total.hi,
                    [INK,BLUE,CORAL,TEAL])
    fig.tight_layout(w_pad=2.2)
    label_panels(fig, (ax1, ax2))
    save(fig, "Figure3_CHARLS_state_allocation")


def fig4(cvai, hrs_data):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 4.1), gridspec_kw={"width_ratios": [1.0, 1.25]})
    hrs = hrs_data.copy()
    yy = np.arange(3)[::-1]
    ax1.axvline(0, color=INK, lw=1.2)
    for yv, row in zip(yy, hrs.itertuples()):
        c = BLUE if row.term == "delta_m" else CORAL if row.term == "C_U" else TEAL
        ax1.errorbar(row.estimate, yv,
                     xerr=[[row.estimate-row.lo], [row.hi-row.estimate]],
                     fmt="o", color=c, mec="white", mew=0.7, ms=7, capsize=3, lw=2)
    ax1.set_yticks(yy, [r"$\Delta m$", r"$C_U$", r"$C_V$"])
    ax1.set_xlabel("log odds ratio difference (95% CI)")
    ax1.set_xlim(-0.38, 0.29)
    clean(ax1)
    d = cvai[cvai.scope == "common_definitions_plausible"].copy()
    order = ["S", "M", "MT", "SMT"]
    d["outcome"] = pd.Categorical(d.outcome, categories=order, ordered=True)
    d = d.sort_values("outcome")
    y2 = np.arange(len(d))[::-1]
    ax2.axvline(1, color=INK, lw=1.2)
    for yv, row in zip(y2, d.itertuples()):
        ax2.errorbar(row.point, yv, xerr=[[row.point-row.lo], [row.hi-row.point]], fmt="o", color=CORAL if row.outcome == "S" else BLUE, mec="white", mew=0.7, ms=7, capsize=3, lw=2)
    ax2.set_yticks(y2, ["S", "M", "MT", "SMT"])
    ax2.set_xlabel("OR per 10 CVAI units (95% CI)")
    ax2.set_xlim(1.0, 1.17)
    clean(ax2)
    fig.tight_layout()
    label_panels(fig, (ax1, ax2))
    save(fig, "Figure4_external_evidence")


def supp_s1(reversal):
    d = reversal.copy().sort_values(["point_estimate_reversal", "dataset"], ascending=[False, True]).reset_index(drop=True)
    d["label"] = d.dataset + " (" + d.country + ")"
    d["sig"] = d.ci_excludes_zero.astype(bool)
    fig, ax = plt.subplots(figsize=(7.4, 7.8))
    y = np.arange(len(d))[::-1]
    for yi, row in zip(y, d.itertuples()):
        c = CORAL if row.point_estimate_reversal else GREY
        ax.errorbar(row.delta, yi, xerr=[[row.delta-row.lo], [row.hi-row.delta]], fmt="o", ms=5, color=c, mec="white", mew=0.6, capsize=2.5, lw=1.4, alpha=1 if row.ci_excludes_zero else 0.65)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(y, d.label)
    ax.set_xlabel(r"$\Delta_c$ = log OR(S) - log OR(M), 95% CI")
    clean(ax)
    fig.tight_layout()
    save(fig, "SupplementaryFigureS1_all_scan", supplementary=True)


def supp_s2(flow):
    d = flow.sort_values("complete_n").copy()
    fig, ax = plt.subplots(figsize=(7.4, 7.0))
    y = np.arange(len(d))
    ax.barh(y, d.start_n, color=LIGHT, edgecolor="white", label="Starting records")
    ax.barh(y, d.complete_n, color=BLUE, edgecolor="white", label="Final analytical sample")
    ax.set_yticks(y, d.dataset)
    ax.set_xlabel("Records")
    ax.legend(frameon=False, loc="lower right")
    clean(ax)
    fig.tight_layout()
    save(fig, "SupplementaryFigureS2_sample_flow", supplementary=True)


def supp_s3(sim):
    d = sim[(sim.method == "primary") & (sim.estimand == "delta")].copy()
    d["row"] = d.scenario + " / n=" + d.n.astype(str)
    p = d.pivot(index="scenario", columns="n", values="coverage_all").sort_index()
    fig, ax = plt.subplots(figsize=(5.7, 4.8))
    im = ax.imshow(100 * p.values, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(np.arange(len(p.columns)), [f"n={n:,}" for n in p.columns])
    ax.set_yticks(np.arange(len(p.index)), p.index.str.replace("_", " "))
    ax.set_xlabel("Generated sample size")
    ax.set_ylabel("Scenario")
    fig.colorbar(im, ax=ax, label="Percentage of all attempts")
    fig.tight_layout()
    save(fig, "SupplementaryFigureS3_simulation_coverage", supplementary=True)


def supp_s4(failure):
    d = failure.copy()
    d = d[d.valid < 400].copy().sort_values(["scenario", "n"])
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    y = np.arange(len(d))
    left = np.zeros(len(d))
    cols = [("valid", BLUE), ("zero_required_state_cell", CORAL), ("fit_or_check_failure", GOLD), ("ill_conditioned_hessian", TEAL)]
    for col, color in cols:
        ax.barh(y, d[col], left=left, color=color, label=col.replace("_", " "))
        left += d[col].to_numpy()
    ax.set_yticks(y, [f"{r.scenario} / n={r.n:,} / {r.method}" for r in d.itertuples()])
    ax.set_xlabel("Repetitions (of 400)")
    ax.legend(frameon=False, ncol=2, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    clean(ax)
    fig.tight_layout()
    save(fig, "SupplementaryFigureS4_simulation_failures", supplementary=True)


def supp_s5(states):
    d = states[states.scope.isin(["current", "never", "former"])].copy()
    order = ["current", "never", "former"]
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    bottom = np.zeros(3)
    colors = {"M0S0": "#c8d2dc", "M0S1": CORAL, "M1S0": BLUE, "M1S1": TEAL}
    for st in ["M0S0", "M0S1", "M1S0", "M1S1"]:
        vals = [float(d[(d.scope == s) & (d.state == st)].proportion.iloc[0]) for s in order]
        ax.bar(order, vals, bottom=bottom, color=colors[st], label=st)
        bottom += np.asarray(vals)
    ax.set_ylabel("Within-group proportion")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    clean(ax)
    fig.tight_layout()
    save(fig, "SupplementaryFigureS5_CHARLS_states", supplementary=True)


def supp_s6(contrasts):
    d = contrasts[contrasts.scope == "common_definitions_plausible"].copy()
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    y = np.arange(len(d))[::-1]
    for yi, row in zip(y, d.itertuples()):
        ax.errorbar(row.delta_log_OR_per10, yi, xerr=[[row.delta_log_OR_per10-row.ci_low], [row.ci_high-row.delta_log_OR_per10]], fmt="o", color=BLUE, capsize=3, lw=1.8)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(y, d.contrast.str.replace("_", " "))
    ax.set_xlabel("Paired difference in log OR per 10 CVAI units (95% CI)")
    clean(ax)
    fig.tight_layout()
    save(fig, "SupplementaryFigureS6_CVAI_contrasts", supplementary=True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-only", action="store_true")
    parser.add_argument("--output", type=Path, default=PACKAGE / "outputs",
                        help="Output directory; it will contain figures and supplementary_figures")
    args = parser.parse_args()
    configure_output(args.output)
    reversal, sim, states, bridge, cvai, contrasts, flow, failure, charls, hrs = load_inputs()
    fig1(reversal)
    fig2(sim, failure)
    fig3(states, charls)
    fig4(cvai, hrs)
    if args.main_only:
        print("Rendered main figures 1-4")
        return
    supp_s1(reversal)
    supp_s2(flow)
    supp_s3(sim)
    supp_s4(failure)
    supp_s5(states)
    supp_s6(contrasts)
    print("Rendered main figures 1-4 and supplementary figures S1-S6")


if __name__ == "__main__":
    main()
