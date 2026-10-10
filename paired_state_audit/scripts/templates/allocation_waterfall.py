import matplotlib.colors as mcolors


def draw_allocation(ax, cu, cv, delta, lo, hi, colors):
    """Adapted from vivid competition.waterfall with paired uncertainty on the total."""
    categories = ['0', r'$C_U$', r'$C_V$', r'$\Delta m$']
    values = [0,cu,cv,delta]
    cumulative = [0]
    for value in values[1:-1]:
        cumulative.append(cumulative[-1]+value)
    cumulative.append(cumulative[-1])
    if abs(cumulative[-1]-delta) > 1e-12:
        raise ValueError('State allocations do not sum to the paired contrast')
    ax.grid(axis='y',color='#d9e1e8',linewidth=0.6)
    ax.set_axisbelow(True)
    bottoms = []
    for i in range(len(categories)):
        if i == 0 or i == len(categories)-1:
            bottoms.append(0)
        else:
            bottoms.append(min(cumulative[i-1],cumulative[i]))
    for i in range(len(categories)):
        color = colors[i]
        height = cumulative[i] if i in (0,len(categories)-1) else abs(values[i])
        fill = tuple(0.3+0.7*x for x in mcolors.to_rgb(color))
        ax.bar(i,height,bottom=bottoms[i],width=0.6,
               color=fill,edgecolor=color,linewidth=1.3,zorder=3)
        if i < len(categories)-1:
            ax.plot([i+0.3,i+0.7],[cumulative[i],cumulative[i]],
                    color='#5b6573',linewidth=0.8,linestyle='--',alpha=0.7)
    # Component intervals cannot be added to obtain the interval on the total.
    ax.errorbar(3,delta,yerr=[[delta-lo],[hi-delta]],fmt='none',
                color='#1f2933',capsize=3,linewidth=1.4,zorder=4)
    ax.axhline(0,color='#1f2933',linewidth=1.1)
    ax.set_xticks(range(len(categories)),categories)
    ax.set_ylim(-0.52,0.025)
    ax.set_yticks([-0.5,-0.4,-0.3,-0.2,-0.1,0])
    ax.set_ylabel('Cumulative log odds ratio difference')
