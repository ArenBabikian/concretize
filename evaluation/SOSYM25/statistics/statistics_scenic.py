import pandas as pd

# Input
base_dir = 'evaluation/SOSYM25'
stats_file_path = f'{base_dir}/scenic/output/generation_times.csv'

# output paths
output_folder_path = f'{base_dir}/statistics/output/scenic'
aggregate_stats_file_path = f'{output_folder_path}/median_generation_times.csv'
total_stats_file_path = f'{output_folder_path}/total_generation_times.csv'

df = pd.read_csv(stats_file_path)

# Get total times and save
df['max_scene'] = df.groupby(['map', 'junction', 'run_id', 'actors'])['scene_number'].transform('max')
df_total_times = df[df['scene_number'] == df['max_scene']]
df_total_times.to_csv(total_stats_file_path)

# Group total times, save aggregated
# result = df_total_times.groupby(['map', 'junction', 'actors'])['time'].median().reset_index().rename(columns={'time': 'median_time'})
result = df_total_times.groupby(['map', 'junction', 'actors']).agg(
    median_time=('time', 'median'),
    num_runs=('time', 'size'),
    max_scene_number=('scene_number', 'max')
).reset_index()
result.to_csv(aggregate_stats_file_path)
result.to_latex(aggregate_stats_file_path + ".txt")