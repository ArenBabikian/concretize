import os
import pandas as pd
from pingouin import mwu
from pprint import pprint
import csv
from scipy.stats import fisher_exact

def get_mwu(x, y, alternative='greater'):
    df_mwu = mwu( x,y, alternative=alternative)
    p = df_mwu["p-val"]["MWU"]
    # u = df_mwu["U-val"]["MWU"]
    eff = df_mwu["CLES"]["MWU"]
    # print(f"MWU p-value: {p}, Effect size: {eff}")
    return p, eff


def get_a2l_stat_sig():
    # Read CSVs
    df_complete = pd.read_csv('evaluation/SOSYM25/all_output/statistics/complete/a2l_times.csv')    
    df_scenic = pd.read_csv('evaluation/SOSYM25/all_output/statistics/scenic/a2l_total_generation_times.csv')

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

        p, eff = get_mwu(times_scenic, times_complete, alternative='greater')

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
    output_file = 'evaluation/SOSYM25/all_output/statistics/stat_sig/a2l_stat_sig.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    results_df.to_csv(output_file, index=True)


def get_l2c_stat_sig(threshold=-1):
    # Read CSVs
    df_complete = pd.read_csv('evaluation/SOSYM25/all_output/statistics/complete/l2c_times.csv')    
    df_scenic = pd.read_csv(f'evaluation/SOSYM25/all_output/scenic/l2c/concretization_times_{threshold}.csv')

    #######
    # TIMES
    # Group by 'junction' and 'actors'
    times_grouped_complete = df_complete.groupby(['junction', 'actors'])['time'].apply(list)
    # Filter out rows where success is False only for the times analysis in the scenic dataframe
    times_grouped_scenic = df_scenic[df_scenic['success']].groupby(['junction', 'actors'])['runtime'].apply(list)
    times_results = {}

    # Find common groups
    common_groups = set(times_grouped_complete.index) & set(times_grouped_scenic.index)

    for group in common_groups:
        times_complete = times_grouped_complete[group]
        times_scenic = times_grouped_scenic[group]
        # times_scenic = [t / 10 for t in times_scenic]  # Convert ms to seconds
        print(f"Processing group: {group}")

        p, eff = get_mwu(times_scenic, times_complete, alternative='greater')

        times_results[group] = {
            'junction': group[0],
            'actors': group[1],
            'significant': p < 0.05,
            'mwu_p': p,
            'mwu_eff': eff,
            'complete_n': len(times_complete),
            'scenic_n': len(times_scenic)
        }

    # Convert results to DataFrame
    results_df = pd.DataFrame(list(times_results.values())).sort_values(['junction', 'actors']).reset_index(drop=True)

    # Write results to CSV
    output_file = f'evaluation/SOSYM25/all_output/statistics/stat_sig/l2c_time_stat_sig_{threshold}.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    results_df.to_csv(output_file, index=True)

    ##############
    # SUCCESS RATE
    # Count number of entries per group in df_complete
    successes_complete = df_complete.groupby(['junction', 'actors']).size().reset_index(name='attempts')
    successes_complete['successes'] = successes_complete['attempts']
    successes_results = {}

    # Count number of entries per group in df_scenic and number of successes (success == True)
    successes_scenic = df_scenic.groupby(['junction', 'actors']).agg(
        attempts=('success', 'size'),
        successes=('success', 'sum')
    ).reset_index()

    # Find common groups
    common_groups = set(successes_complete.set_index(['junction', 'actors']).index) & set(successes_scenic.set_index(['junction', 'actors']).index)

    for group in common_groups:
        successes_complete_group = successes_complete.set_index(['junction', 'actors']).loc[group]
        s_complete_attempts = successes_complete_group['attempts']
        s_complete_successes = successes_complete_group['successes']
        successes_scenic_group = successes_scenic.set_index(['junction', 'actors']).loc[group]
        s_scenic_attempts = successes_scenic_group['attempts']
        s_scenic_successes = successes_scenic_group['successes']

        # Note on fisher_exact. it tatkes a 2x2 contingency table
        # [[num_successes_approach_1, num_failures_approach_1], [num_successes_approach_2, num_failures_approach_2]]
        odds, p = fisher_exact([[s_complete_successes, s_complete_attempts - s_complete_successes],
                                 [s_scenic_successes, s_scenic_attempts - s_scenic_successes]])

        successes_results[group] = {
            'junction': group[0],
            'actors': group[1],
            'significant': p < 0.05,
            'p_fisher': p,
            'odds_ratio': odds,
            'complete_attempts': successes_complete_group['attempts'],
            'complete_successes': successes_complete_group['successes'],
            'scenic_attempts': successes_scenic_group['attempts'],
            'scenic_successes': successes_scenic_group['successes'],
        }


    # Convert results to DataFrame
    successes_df = pd.DataFrame(list(successes_results.values())).sort_values(['junction', 'actors']).reset_index(drop=True)

    # Write results to CSV
    output_file = f'evaluation/SOSYM25/all_output/statistics/stat_sig/l2c_success_stat_sig_{threshold}.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    successes_df.to_csv(output_file, index=True)


if __name__ == "__main__":
    get_a2l_stat_sig()
    get_l2c_stat_sig()