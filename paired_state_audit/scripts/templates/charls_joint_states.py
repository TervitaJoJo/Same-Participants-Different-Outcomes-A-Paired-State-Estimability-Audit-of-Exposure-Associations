"""Count matrix adapted from vivid advanced.method_heatmap's imshow/text layers."""
import matplotlib.colors as mcolors
import numpy as np


def draw_joint_states(ax, states):
    all_states = states[states.scope.eq('all_smoking_statuses')].set_index('state')
    current = states[states.scope.eq('current')].set_index('state')
    noncurrent = states[states.scope.isin(['never','former'])].groupby('state')['n'].sum()
    state_order = [['M0S0','M0S1'],['M1S0','M1S1']]
    labels = {'M0S0':'00','M0S1':'V','M1S0':'U','M1S1':'11'}
    counts = np.array([[int(all_states.loc[state,'n']) for state in row] for row in state_order])
    total = int(counts.sum())
    assert total == 10367
    assert int(current.n.sum()) == 3309 and int(noncurrent.sum()) == 7058
    # Fixed joint-state order and one count scale replace method ranking and clustering.
    cmap = mcolors.LinearSegmentedColormap.from_list('joint_counts',['#eef0f2','#164e80'])
    im = ax.imshow(counts,cmap=cmap,aspect='equal',vmin=0,vmax=counts.max(),interpolation='nearest')
    ax.set_xticks([0,1],['Negative (0)','Positive (1)'])
    ax.set_yticks([0,1],['Negative (0)','Positive (1)'])
    ax.set_xlabel('Reported diagnosis (S)')
    ax.set_ylabel('Measured hypertension (M)')
    ax.set_xticks([-.5,.5,1.5],minor=True)
    ax.set_yticks([-.5,.5,1.5],minor=True)
    ax.grid(which='minor',color='white',linewidth=2)
    ax.tick_params(which='both',length=0,pad=5)
    ax.spines[:].set_visible(False)
    records = []
    for i in range(2):
        for j in range(2):
            state = state_order[i][j]
            count = int(counts[i,j])
            current_count = int(current.loc[state,'n'])
            noncurrent_count = int(noncurrent.loc[state])
            assert current_count+noncurrent_count == count
            rgb = im.cmap(im.norm(count))[:3]
            color = 'white' if np.dot(rgb,[.2126,.7152,.0722]) < .5 else '#182632'
            ax.text(j,i-.28,labels[state],ha='center',va='center',fontsize=10.5,fontweight='bold',color=color)
            ax.text(j,i-.08,f'{count:,} ({100*count/total:.1f}%)',ha='center',va='center',fontsize=9,fontweight='bold',color=color)
            ax.text(j,i+.15,f'Current: {current_count:,}\nNoncurrent: {noncurrent_count:,}',
                    ha='center',va='center',fontsize=8.5,linespacing=1.6,color=color)
            records.append({'state':state,'label':labels[state],'M':i,'S':j,'total_n':count,
                            'percent_total':100*count/total,'current_n':current_count,
                            'noncurrent_n':noncurrent_count,'denominator':total})
    return records
