import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

FILE_FORMAT = 'pdf'

THRESHOLD = 0.9
style_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']


def clean_fig(plt):
    # plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
    # plt.box(False)
    # plt.margins(0, 0.05)
    plt.tight_layout(pad=0.25)
    # plt.gca().set_aspect('equal')


def agg_attempt_collision_near_miss(data):

    d = {}
    d['attempts'] = data['num_collisions'].count()
    d['near miss'] = data['near_miss_occurance'].sum()
    d['collision'] = data['num_collisions'].sum()
    # d['preventable collision'] = data['num_collisions'].sum()
    d['preventative measure'] = (data['num_preventative_maneuvers'] > 0).sum()
    return pd.Series(d)


def create_bar_chart(df, groupby, title, xlabel, add_prev, width, height, output_path):

    # print(df)
    df_agg = df.groupby([groupby]).apply(agg_attempt_collision_near_miss)

    if groupby == 'maneuver.id':
        allowed = {'road981_lane0': 'tl_west', 'road949_lane0': 'tl_east', 'road974_lane0': 'tl_south', 'road962_lane0': 'tl_north'}
        # allowed = {}
        # allowed.update({'road2282_lane0': 'tl_west', 'road2242_lane0': 'tl_north'}) 
        # # left turn
        # allowed.update({'road2241_lane0': 'tr_east', 'road2292_lane0': 'tr_north'}) # right
        allowed.update({'road2281_lane0': 'gs_westA', 'road2280_lane0': 'gs_eastA', 'road2280_lane1': 'gs_eastB', 'road2281_lane1': 'gs_westB'}) # straight

        # fig, ax = plt.subplots(figsize=(3.33, 3))
    elif groupby == 'maneuver.type':
        allowed = {'left': 'turnLeft', 'right': 'turnRight', 'straight': 'goStraight'}
        # fig, ax = plt.subplots(figsize=(3.33, 3))
    elif groupby == 'num_actors':
        allowed = {'1': '1', '2': '2', '3': '3', '4': '4'}
        # fig, ax = plt.subplots(figsize=(5, 2.3))
        
    if add_prev:
        fig, ax = plt.subplots(figsize=(4, 3))
        bar_width = 0.45
    else:
        fig, ax = plt.subplots(figsize=(3, 3))
        bar_width = 0.8

    # print(df_agg)
    df_agg = df_agg.loc[df_agg.index.isin(allowed)]
    categories = [allowed[x] for x in df_agg.index]
    
    # Extracting data for plotting
    
    # colors = ['#A50205', '#0876B5', '#CC6400', '#E8BFC0', '#C1DDEC', '#F2D8BF']
    colors = ['#CC6400', '#0876B5', '#A50205', '#5C7B3D', '#C1DDEC', '#F2D8BF']
    attributes = ['attempts', 'near miss', 'collision']
    labels = ['Success', 'Near-miss', 'Collision']


    if add_prev:
        attributes.append('preventative measure')
        labels.append('Preventive maneuver')
    data = df_agg[attributes].values

    # STATISTICAL SIGNIFICANCE
    from scipy.stats import fisher_exact
    
    os.makedirs(f'{output_path}/statsig/', exist_ok=True)
    with open(f'{output_path}/statsig/{title}.txt', 'w') as f:

        f.write(">>>Success Rate Statistical Significance<<<\n")
        f.write(f'>>>{output_path}<<<\n')
        f.write(data.__str__()+'\n')

        thresh=0.05
        for i, dc in enumerate(data):
            f.write(f'    {categories[i]}(at={dc[0]}, nm={dc[1]}, col={dc[2]})\n')
        f.write('\n')

        combos = [(1, 1), (2, 2), (1, 2), (2, 1)] 
        names = ['at', 'nm', 'col']
        for i, dci in enumerate(data):
            at1 = dci[0]
            nm1 = dci[1]
            col1 = dci[2]
            for j, dcj in enumerate(data):
                if j == i:
                    continue
                at2 = dcj[0]
                nm2 = dcj[1]
                col2 = dcj[2]
                f.write(f'    {categories[i]}-{categories[j]}\n')
                for c in combos:
                    oddsratio, pvaluerm = fisher_exact([[at1, dci[c[0]]],[at2, dcj[c[1]]]])
                    oddsratio, pvaluerm = fisher_exact([[at2, dcj[c[1]]],[at1, dci[c[0]]]])

                    f.write(('~~~~' if pvaluerm>thresh else '    ') + f' {names[c[0]].ljust(4)} * {names[c[1]].ljust(4)} : (pvalue={pvaluerm:.3f}) (oddsrat={oddsratio:.3f})\n')
        f.write(">>>End Statistical Significance<<<\n")
    # END STATISTICAL SIGNIFICANCE

    # NORMALIZE DATA
    for i, d in enumerate(data):
        d2 = d / d.max() * 100
        data[i] = d2

    # Set the bar width
    # bar_width = 1

    # Create positions for bars
    x = range(len(categories))
    x_positions = []
    for i in range(len(attributes)):
        if i != 3:
            x_positions.append([j+bar_width for j in x])
        else:
            x_positions.append([j+2*bar_width for j in x])
            # x_positions.append([j + i * bar_width for j in x])

    # Create the bars
    for i in range(len(attributes)):
        plt.bar(x_positions[i], data[:, i], width=bar_width, label=labels[i], edgecolor='black', color=colors[i % len(colors)])
        # plt.bar(x_positions[i], data[:, i], width=bar_width, label=attributes[i], edgecolor='black', color=colors[i % len(colors)])

    # Set x-axis labels
    plt.xticks([i + (len(attributes) - 1) / 2 * bar_width for i in x], categories)
    # Add axis titles
    if add_prev:
        ax.set_ylabel('Percentage of simulation runs')

    # Add axis titles
    ax.set_xlabel(xlabel)

    # Show the plot
    # plt.tight_layout()
    

    clean_fig(plt)

    # Save the plot
    plt.savefig(f'{output_path}/{title}.{FILE_FORMAT}')
    os.makedirs(f'{output_path}/csv', exist_ok=True)
    df_agg.to_csv(f'{output_path}/csv/{title}.csv')

    os.makedirs(f'{output_path}/latex', exist_ok=True)
    with open(f'{output_path}/latex/{title}.tex', 'w') as f:
        f.write(df_agg.to_latex())

    # EXPORT LEGEND
    if not add_prev:
        return
    
    plt.close()
    
    colors = ['#A50205', '#0876B5', '#CC6400', '#5C7B3D', '#C1DDEC', '#F2D8BF']
    attributes = ['collision', 'near miss', 'attempts', 'preventative measure']
    labels = ['Collision', 'Near-miss', 'No incident', 'Preventive maneuver']
    # for i in range(len(attributes)):
    #     plt.bar(x_positions[i], data[:, i], width=bar_width, label=labels[i], edgecolor='black', color=colors[i % len(colors)])

    fig, ax = plt.subplots(figsize=(13, 13))
        # plt.bar(x_positions[i], data[:, i], width=bar_width, label=attributes[i], edgecolor='black', color=colors[i % len(colors)])
    plt.pie(data[0], labels=labels, colors=colors, wedgeprops={"edgecolor":"k"})

    
    print('EXPORTING LEGEND')
    plt.axis('off')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
                    box.width, box.height * 0.9])

    # Put a legend below current axis
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), framealpha=1, frameon=False, ncol=4)

    # legend = plt.legend(ncol=7, framealpha=1, frameon=False)
    fig  = legend.figure
    fig.canvas.draw()
    bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(f'{output_path}/legend.{FILE_FORMAT}', dpi=300, bbox_inches=bbox)

    plt.close()


def create_box_plot(df_actor, output_path):

    # print(df_actor[(df_actor['num_collisions'] > 0) & (df_actor['ego'])])
    df_actor['prevent_vis_tot_frames'] = df_actor['prevent_vis_tot_frames'] / df_actor['num_frames']
    df_actor['prevent_lid_tot_frames'] = df_actor['prevent_lid_tot_frames'] / df_actor['num_frames']
    df_actor['prevent_both_tot_frames'] = df_actor['prevent_both_tot_frames'] / df_actor['num_frames']
    
    df_actor['prevent_vis_stretch_frames'] = df_actor['prevent_vis_stretch_frames'] / 60
    df_actor['prevent_lid_stretch_frames'] = df_actor['prevent_lid_stretch_frames'] / 60
    df_actor['prevent_both_stretch_frames'] = df_actor['prevent_both_stretch_frames'] / 60

    df_actor_with_accident_melted = pd.melt(df_actor[(df_actor['num_collisions'] > 0) & (df_actor['ego'])].rename(columns={
                'prevent_vis_tot_frames': 'revent_visual_total_frames',
                'prevent_vis_stretch_frames' : 'prevent_visual_stretch_frames',
                # 'prevent_vis_tail_frames' : 'prevent_visual_tail_frames',
                'prevent_lid_tot_frames' : 'prevent_lidar_total_frames',
                'prevent_lid_stretch_frames' : 'prevent_lidar_stretch_frames',
                # 'prevent_lid_tail_frames' : 'prevent_lidar_tail_frames',
                'prevent_both_tot_frames' : 'prevent_both_total_frames',
                'prevent_both_stretch_frames' : 'prevent_both_stretch_frames',
                # 'prevent_both_tail_frames' : 'prevent_both_tail_frames'
            }, inplace=False),
            value_vars=[
                'revent_visual_total_frames',
                'prevent_visual_stretch_frames',
                # 'prevent_visual_tail_frames',
                'prevent_lidar_total_frames',
                'prevent_lidar_stretch_frames',
                # 'prevent_lidar_tail_frames',
                'prevent_both_total_frames',
                'prevent_both_stretch_frames',
                # 'prevent_both_tail_frames',
                ],
                value_name='# of frames visible',
            )

    # df_actor_with_accident_melted['# of frames visible'] = df_actor_with_accident_melted['# of frames visible'] / df_actor_with_accident_melted['num_frames']
    
    df_actor_with_accident_melted['Sensor'] = df_actor_with_accident_melted['variable'].apply(lambda x: x.split('_')[1])
    df_actor_with_accident_melted['Aggregation'] = df_actor_with_accident_melted['variable'].apply(lambda x: x.split('_')[2])
    
    # Define a custom color palette
    custom_palette = {"visual": style_colors[0], "lidar": style_colors[1], "both": style_colors[2]}

    # Set the style of the plot (optional)

    # PREVIOUS VERSION: BOXPLOT
    # sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.boxplot(data=df_actor_with_accident_melted, x='Aggregation', y='# of frames visible', hue='Sensor', palette=custom_palette)
    plt.legend().remove()  # Remove the legend

    # Print relevant info
    aggregated_df = df_actor_with_accident_melted.groupby('variable').agg({'# of frames visible': ['count', lambda x: (x >= THRESHOLD).sum()]})
    aggregated_df.columns = ['num_iterations', 'num_rows_greater_than_threshold']
    aggregated_df.reset_index(inplace=True)
    aggregated_df.to_csv(f'{output_path}/csv/preventability.csv')

    print(output_path)
    print(aggregated_df)

    # CURRENT VERSION: 2 bucket plots

    # fig, ax = plt.subplots(figsize=(6, 3))


    def create_bar_chart(df, groupby, title, xlabel, width, height, output_path):
        # Filter the dataframe where sensor=visual
        df_visual = df[df['Sensor'] == 'visual']

        # Create 10 buckets for the values
        bins = np.linspace(0, 1, 10)
        df_visual['bucket'] = pd.cut(df_visual[groupby], bins=bins, include_lowest=True)

        # Group by the bucket and count the occurrences
        grouped = df_visual.groupby('bucket').size()

        # Plot the bar chart
        plt.figure(figsize=(width, height))
        plt.bar(grouped.index.astype(str), grouped.values)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel('Count')

        # Save the plot
        plt.savefig(f'{output_path}/preventbility-visual.{FILE_FORMAT}')
        plt.close()

    # Rest of the code...

    # create_bar_chart(df=df_actor_with_accident_melted, groupby='prevent_visual_stretch_frames', title='Visual', xlabel='Number of frames visible', width=6, height=3, output_path=output_path)

    # Set the title and labels
    plt.xlabel('Aggregation method')
    plt.ylabel('Ratio of frames visible')

    plt.tight_layout()
    plt.savefig(f'{output_path}/preventabiility.{FILE_FORMAT}')

    # EXPORT LEGEND
    plt.axis('off')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2,
                    box.width, box.height * 0.9])

    # Put a legend below current axis
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), framealpha=1, frameon=False, ncol=4)

    # legend = plt.legend(ncol=7, framealpha=1, frameon=False)
    fig  = legend.figure
    fig.canvas.draw()
    bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(f'{output_path}/preventability-legend.{FILE_FORMAT}', dpi=300, bbox_inches=bbox)

    plt.close()


def create_collision_near_miss_preventative_matrix_table(df, output_path):
    # print(len(df))
    # return

    for allowed_actors in [['2'], ['3'], ['4'], ['2', '3', '4']]:

        cond_preventative = (df['num_preventative_maneuvers'] > 0) & (df['num_actors'].isin(allowed_actors))
        cond_no_preventative = (df['num_preventative_maneuvers'] == 0) & (df['num_actors'].isin(allowed_actors))
        # exit()

        if allowed_actors == ['2', '3', '4']:
            with open(f'{output_path}/csv/dataframe.csv', 'w') as f:
                df[cond_no_preventative & (df['near_miss_occurance'] == 0)].to_csv(f)

        d = {}
        d['attempts_preventative'] = df[cond_preventative]['num_collisions'].count()
        d['collision_preventative'] = df[cond_preventative]['num_collisions'].sum()
        d['near_miss_preventative'] = (df[cond_preventative]['near_miss_occurance'].sum() - d['collision_preventative'])
        d['nothing_preventative'] = df[cond_preventative & (df['near_miss_occurance'] == 0)]['num_collisions'].count()
        assert d['attempts_preventative'] == d['collision_preventative'] + d['near_miss_preventative'] + d['nothing_preventative']

        d['attempts_no_preventative'] = df[cond_no_preventative]['num_collisions'].count()
        d['collision_no_preventative'] = df[cond_no_preventative]['num_collisions'].sum()
        d['near_miss_no_preventative'] = (df[cond_no_preventative]['near_miss_occurance'].sum() - d['collision_no_preventative'])
        d['nothing_no_preventative'] = df[cond_no_preventative & (df['near_miss_occurance'] == 0)]['num_collisions'].count()
        assert d['attempts_no_preventative'] == d['collision_no_preventative'] + d['near_miss_no_preventative'] + d['nothing_no_preventative']

        import matplotlib.pyplot as plt
            
        # Create a pie chart
        labels = ['Collision (Preventative)', 'Near Miss (Preventative)', 'Nothing (Preventative)', 'Collision (No Preventative)', 'Near Miss (No Preventative)', 'Nothing (No Preventative)']
        values = [d['collision_preventative'], d['near_miss_preventative'], d['nothing_preventative'], d['collision_no_preventative'], d['near_miss_no_preventative'], d['nothing_no_preventative']]
        print(values)
        # exit()
        colors = ['red', 'yellow', 'green', 'blue', 'purple', 'orange']

        
        colors = ['#A50205', '#0876B5', '#CC6400', '#E8BFC0', '#C1DDEC', '#F2D8BF']
        text_colors = ['white', 'white', 'white', 'black', 'black', 'black']


        # PIE PLOTS        
        # plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
        fig, ax = plt.subplots(figsize=(3, 3))
        # plt.pie(values, labels=values, colors=colors)
        explode = (0, 0, 0, 0.15, 0.15, 0.15)  # Add explosion

        # wedges, texts, pcts = plt.pie(values, labels=values, colors=colors, explode=explode, labeldistance=0.5)
        # wedges, texts, pcts = plt.pie(values, colors=colors, explode=explode, autopct=lambda x: None if x == 0 else int(np.round(x*sum(values)/100, 0)))
        wedges, texts, pcts = plt.pie(values, colors=colors, explode=explode, autopct='%1.1f%%', textprops={'fontsize': 12, 'weight': 'bold'})
        
        for text, color in zip(pcts, text_colors):
            text.set_color(color)
        # plt.legend(labels, loc='best')
        # plt.title('Preventative Measures')
        
        
        plt.tight_layout(pad=-2)

        file_suffix = ''.join(allowed_actors)

        # Save the plot
        plt.savefig(f'{output_path}/pie{file_suffix}.{FILE_FORMAT}')
        plt.close()

        # EXPORT LEGEND
        fig, ax = plt.subplots(figsize=(13, 13))
        plt.pie(values, labels=labels, colors=colors, explode=explode)
        plt.axis('off')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.2,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), framealpha=1, frameon=False, ncol=6)

        # legend = plt.legend(ncol=7, framealpha=1, frameon=False)
        fig  = legend.figure
        fig.canvas.draw()
        bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(f'{output_path}/pie-legend.{FILE_FORMAT}', dpi=300, bbox_inches=bbox)

        plt.close()

        ####################
        # SEPERATE PIE PLOTS
        ####################

        file_suffix = ''.join(allowed_actors)
        labels1 = ['Collision', 'Near-miss', 'No incident']
        values1 = [d['collision_preventative'], d['near_miss_preventative'], d['nothing_preventative']]
        values2 = [d['collision_no_preventative'], d['near_miss_no_preventative'], d['nothing_no_preventative']]

        colors = ['#A50205', '#0876B5', '#CC6400']
        text_colors = ['white', 'white', 'white']


        # PLOTR-BOTH-BAR
        fig, ax = plt.subplots(figsize=(5, 1.67))

        valuessums = [sum(values2), sum(values1)]

        hvalsAll = []
        for i in range(len(values2)):
            hvalsAll.append([values2[i], values1[i]])

        # normalize
        hvals = []
        for i in range(len(hvalsAll)):
            hvals.append([x / valuessums[j] * 100 for j, x in enumerate(hvalsAll[i])])

        bar_width = 0.9
        index = np.arange(len(hvals[0]))
        allrects = []
        for i in range(len(hvals)):
            allrects.append(ax.barh(index, hvals[i], bar_width, color=colors[i], left=None if i == 0 else np.sum(hvals[:i], axis=0)))

        for a, rects in enumerate(allrects):
            for b, rect in enumerate(rects):
                width = rect.get_width()
                ax.annotate(f'{hvalsAll[a][b]}\n({width:.1f}%)', 
                             xy=(rect.get_x() + width / 2, rect.get_y() + rect.get_height() / 2), 
                             xytext=(0, 0) if a==1 and b==0 else (0, 0), 
                             textcoords="offset points", 
                             ha='right' if a==1 and b==0 else 'center', 
                             va='center', 
                             color='white', 
                             weight='bold', 
                             fontsize=10)

        ax.set_xlabel('Percentage of simulation runs')
        # ax.set_ylabel('Categories')
        ax.set_yticks(index)
        ax.set_yticklabels(['w/o PM', 'w/ PM'])

        plt.tight_layout(pad=0.5)
        plt.savefig(f'{output_path}/bars{file_suffix}.{FILE_FORMAT}')
        plt.close()

        # PLOTR-PREV
        fig, ax = plt.subplots(figsize=(3, 3))
        wedges, texts, pcts = plt.pie(values1, colors=colors, autopct=lambda x: None if x == 0 else f'{int(np.round(x*sum(values1)/100, 0))}\n({x:.1f}%)', textprops={'fontsize': 14, 'weight': 'bold'}, pctdistance=0.65)
        for text in pcts:
            text.set_color('white')
        plt.tight_layout(pad=-2)
        plt.savefig(f'{output_path}/pie{file_suffix}-prev.{FILE_FORMAT}')
        plt.close()

        # PLOTR-NOPR
        fig, ax = plt.subplots(figsize=(3, 3))
        wedges, texts, pcts = plt.pie(values2, colors=colors, autopct=lambda x: None if x == 0 else f'{int(np.round(x*sum(values2)/100, 0))}\n({x:.1f}%)', textprops={'fontsize': 14, 'weight': 'bold'}, pctdistance=0.65)
        for text in pcts:
            text.set_color('white')
        # plt.tight_layout(pad=0)
        plt.tight_layout(pad=-2)
        plt.savefig(f'{output_path}/pie{file_suffix}-nopr.{FILE_FORMAT}')
        plt.close()

        # EXPORT LEGEND
        fig, ax = plt.subplots(figsize=(13, 13))
        plt.pie(values1, labels=labels1, colors=colors)
        plt.axis('off')
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.2,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), framealpha=1, frameon=False, ncol=6)

        # legend = plt.legend(ncol=7, framealpha=1, frameon=False)
        fig  = legend.figure
        fig.canvas.draw()
        bbox  = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(f'{output_path}/pie-split-legend.{FILE_FORMAT}', dpi=300, bbox_inches=bbox)

        plt.close()
        
        df_matrix = pd.DataFrame.from_dict({
            'Preventative measure': [True, False],
            'Collision': [d['collision_preventative'], d['collision_no_preventative']],
            'Near miss': [d['near_miss_preventative'], d['near_miss_no_preventative']],
            'Nothing': [d['nothing_preventative'], d['nothing_no_preventative']]
        })

        os.makedirs(f'{output_path}/latex/', exist_ok=True)
        with open(f'{output_path}/latex/pie{file_suffix}.tex', 'w') as f:
            f.write(df_matrix.to_latex())

    return


def main():
    input_path = 'evaluation/SOSYM25/data-sim'
    output_path_meta = 'evaluation/SOSYM25/figures/figures'
    # os.makedirs(output_path, exist_ok=True)

    map_junction_names = ['Town04_916', 'Town05_2240', 'both']
    for map_junction_name in map_junction_names:
        
        actor_df_list = []
        relationship_list = []
        coordinatess_list = []

        output_path = f'{output_path_meta}/{map_junction_name}'
        os.makedirs(output_path, exist_ok=True)
        
        def add_data(folder):
            json_data_actor = json.load(open(f'{input_path}/{folder}/data_actor.json', 'rb'))
            df_act = pd.json_normalize(json_data_actor, record_path=['actors'])
            actor_df_list.append(df_act)

            json_data_relationship = json.load(open(f'{input_path}/{folder}/data_relationship.json', 'rb'))
            df_rel = pd.json_normalize(json_data_relationship, record_path=['relationships'])
            relationship_list.append(df_rel)

            # dc_coord = pd.read_csv(f'{input_path}/{map_junction_name}/path_coords.csv')
            # coordinatess_list.append(dc_coord)

        if map_junction_name == 'both':
            add_data('Town04_916')
            add_data('Town05_2240')
        else:
            add_data(map_junction_name)

        df_actor = pd.concat(actor_df_list)

        # INFO - IMPORTANT
        # FILTER UNPREVENTABLE COLISIONS
        df_actor = df_actor[(df_actor['prevent_both_stretch_frames'] >= 0.9 * 60) | (df_actor['num_collisions'] == 0)]

        plot_types = [
            (df_actor[df_actor['ego']], 'num_actors',    'size-res'      , 'Number of Actors', True),
            (df_actor[df_actor['ego']], 'maneuver.id',   'log-res'      , 'Logical Maneuver', True),
            (df_actor[df_actor['ego']], 'maneuver.type', 'fun-res' , 'Functional maneuver', True)
        ]

        for df, groupby, title, xlabel, add_prev in plot_types:
            create_bar_chart(df=df, groupby=groupby, title=title, xlabel=xlabel, add_prev=add_prev, width=8, height=4, output_path=output_path)

        
        # create_box_plot(df_actor, output_path)
        create_collision_near_miss_preventative_matrix_table(df_actor[df_actor['ego']], output_path=output_path)



if __name__ == "__main__":
    main()
