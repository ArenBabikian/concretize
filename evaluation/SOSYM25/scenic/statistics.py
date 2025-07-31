import pandas as pd

base_dir = 'evaluation/SOSYM25/scenic'
stats_file_path = f'{base_dir}/output/generation_times.csv'
aggregate_stats_file_path = f'{base_dir}/output/median_generation_times.csv'

df = pd.read_csv(stats_file_path)
df['max_scene'] = df.groupby(['map', 'junction', 'run_id', 'actors'])['scene_number'].transform('max')
df_total_times = df[df['scene_number'] == df['max_scene']]
result = df_total_times.groupby(['map', 'junction', 'actors'])['time'].median().reset_index().rename(columns={'time': 'median_time'})
result.to_csv(aggregate_stats_file_path)
result.to_latex(aggregate_stats_file_path + ".txt")