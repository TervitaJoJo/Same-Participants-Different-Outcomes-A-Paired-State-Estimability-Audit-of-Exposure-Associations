from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle


def draw_sankey(ax, source_nodes, target_nodes, flows,
                source_colors, target_colors, left_x=0.10, right_x=0.90,
                node_width=0.035, node_gap=0.06):
    """Adapted from vivid advanced.sankey; no in-image annotations."""
    total_src = sum(v for _, v in source_nodes)
    total_tgt = sum(v for _, v in target_nodes)
    if abs(total_src-total_tgt) > 1e-9:
        raise ValueError('Flow totals do not match')
    y_margin = 0.08
    # Equal scales preserve count-proportional heights across node gaps.
    available = 1-2*y_margin-node_gap*max(len(source_nodes)-1,len(target_nodes)-1)
    src_ranges, tgt_ranges = [], []
    for nodes, ranges in ((source_nodes,src_ranges),(target_nodes,tgt_ranges)):
        y = 1-y_margin
        for _, value in nodes:
            h = value/total_src*available
            ranges.append((y-h,y))
            y = y-h-node_gap

    for nodes, ranges, colors, x in ((source_nodes,src_ranges,source_colors,left_x),
                                     (target_nodes,tgt_ranges,target_colors,right_x)):
        for (_, value), (y0,y1), color in zip(nodes,ranges,colors):
            ax.add_patch(Rectangle((x-node_width/2,y0),node_width,y1-y0,
                                   facecolor=color,edgecolor='none',alpha=0.92,zorder=3))

    src_top_used = [r[1] for r in src_ranges]
    tgt_top_used = [r[1] for r in tgt_ranges]
    for flow in flows:
        si, ti, value = flow['source_idx'],flow['target_idx'],flow['value']
        height = value/total_src*available
        s_top, t_top = src_top_used[si],tgt_top_used[ti]
        s_bot, t_bot = s_top-height,t_top-height
        src_top_used[si],tgt_top_used[ti] = s_bot,t_bot
        mid_x = (left_x+right_x)/2
        path_data = [
            (Path.MOVETO,(left_x+node_width/2,s_top)),
            (Path.CURVE4,(mid_x,s_top)),
            (Path.CURVE4,(mid_x,t_top)),
            (Path.CURVE4,(right_x-node_width/2,t_top)),
            (Path.LINETO,(right_x-node_width/2,t_bot)),
            (Path.CURVE4,(mid_x,t_bot)),
            (Path.CURVE4,(mid_x,s_bot)),
            (Path.CURVE4,(left_x+node_width/2,s_bot)),
            (Path.CLOSEPOLY,(left_x+node_width/2,s_top)),
        ]
        codes, verts = zip(*path_data)
        ax.add_patch(PathPatch(Path(verts,codes),facecolor=flow.get('color',source_colors[si]),
                               edgecolor='none',alpha=0.42,zorder=2))
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.set_aspect('auto')
    return src_ranges,tgt_ranges


def continue_covered_flow(ax, y_range, left_x, right_x, color, node_width=0.035):
    """Continue successful fits at their original height, without renormalizing."""
    y0,y1 = y_range
    x0,x1 = left_x+node_width/2,right_x-node_width/2
    mid_x = (x0+x1)/2
    verts = [(x0,y1),(mid_x,y1),(mid_x,y1),(x1,y1),
             (x1,y0),(mid_x,y0),(mid_x,y0),(x0,y0),(x0,y1)]
    codes = [Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,
             Path.LINETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts,codes),facecolor=color,edgecolor='none',alpha=0.42,zorder=2))
    ax.add_patch(Rectangle((right_x-node_width/2,y0),node_width,y1-y0,
                           facecolor=color,edgecolor='none',alpha=0.92,zorder=3))
