import os
import pandas as pd
from pingouin import mwu
from pprint import pprint
import csv

# Read CSVs
df_complete = pd.read_csv('evaluation/SOSYM25/statistics/output/complete/f2l_times.csv')    
df_scenic = pd.read_csv('evaluation/SOSYM25/statistics/output/scenic/total_generation_times.csv')

# Group by 'junction' and 'actors'
grouped_complete = df_complete.groupby(['junction', 'actors'])['time'].apply(list)
grouped_scenic = df_scenic.groupby(['junction', 'actors'])['time'].apply(list)
results = {}

# Find common groups
common_groups = set(grouped_complete.index) & set(grouped_scenic.index)

for group in common_groups:
    times_complete = grouped_complete[group]
    times_scenic = grouped_scenic[group]
    # times_scenic = [t / 10 for t in times_scenic]  # Convert ms to seconds
    print(f"Processing group: {group}")

    df_mwu = mwu( times_scenic,times_complete, alternative='greater')
    p = df_mwu["p-val"]["MWU"]
    # u = df_mwu["U-val"]["MWU"]
    eff = df_mwu["CLES"]["MWU"]
    print(f"MWU p-value: {p}, Effect size: {eff}")
    # print(f"MWU p-value: {p}, U-value: {u}, Effect size: {eff}")

    results[group] = {
        'junction': group[0],
        'actors': group[1],
        'significant': p < 0.05,
        'mwu_p': p,
        'mwu_eff': eff,
        'complete_n': len(times_complete),
        'scenic_n': len(times_scenic)
    }

# Convert results to DataFrame
results_df = pd.DataFrame(list(results.values())).sort_values(['junction', 'actors']).reset_index(drop=True)

# Write results to CSV
output_file = 'evaluation/SOSYM25/statistics/output/stat_sig/f2l_stat_sig.csv'
os.makedirs(os.path.dirname(output_file), exist_ok=True)
results_df.to_csv(output_file, index=True)

# Print results
# pprint(results)