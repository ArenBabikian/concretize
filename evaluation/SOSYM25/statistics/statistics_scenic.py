import os
import pandas as pd

# F2L
# Input
base_dir = 'evaluation/SOSYM25'
f2l_stats_file_path = f'{base_dir}/all_output/scenic/f2l/generation_times.csv'

# output paths
output_folder_path = f'{base_dir}/statistics/output/scenic'
os.makedirs(output_folder_path, exist_ok=True)
f2l_aggregate_stats_file_path = f'{output_folder_path}/f2l_median_generation_times.csv'
f2l_total_stats_file_path = f'{output_folder_path}/f2l_total_generation_times.csv'

df_f2l = pd.read_csv(f2l_stats_file_path)

# Get total times and save
df_f2l['max_scene'] = df_f2l.groupby(['map', 'junction', 'run_id', 'actors'])['scene_number'].transform('max')
df_f2l_total_times = df_f2l[df_f2l['scene_number'] == df_f2l['max_scene']]
df_f2l_total_times.to_csv(f2l_total_stats_file_path)

# Group total times, save aggregated
# result = df_total_times.groupby(['map', 'junction', 'actors'])['time'].median().reset_index().rename(columns={'time': 'median_time'})
result_f2l = df_f2l_total_times.groupby(['map', 'junction', 'actors']).agg(
    median_time=('time', 'median'),
    num_runs=('time', 'size'),
    max_scene_number=('scene_number', 'max')
).reset_index()
result_f2l.to_csv(f2l_aggregate_stats_file_path)
result_f2l.to_latex(f2l_aggregate_stats_file_path + ".tex")


# L2C
# Input
l2c_stats_file_path = f'{base_dir}/all_output/scenic/l2c/concretization_times.csv'

# Output
l2c_aggregate_stats_file_path = f'{output_folder_path}/l2c_median_concretization_times.csv'

df_l2c = pd.read_csv(l2c_stats_file_path)

# Calculate success rate and runtime 
result_l2c = df_l2c.groupby(['map', 'junction', 'actors']).agg(
    success_ratio=('success', 'mean'),
    median_runtime=('runtime', lambda x: x[df_l2c.loc[x.index, 'success']].median())
).reset_index()
result_l2c.to_csv(l2c_aggregate_stats_file_path)
result_l2c.to_latex(l2c_aggregate_stats_file_path + ".tex")
