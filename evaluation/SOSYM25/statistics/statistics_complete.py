import os
import json
import pandas as pd
import sys

TOWNS_DICT = {
    '916': 'Town04',
    '2240': 'Town05'
}

def collect_f2l_times(input_folder_path, output_folder_path, j_id_list, n_ac_list):
    records_f2l = []
    records_l2c = []
    # Walk through all subfolders
    for root, _, files in os.walk(input_folder_path):

        if 'times.json' in files:
            json_path = os.path.join(root, 'times.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for j_id in j_id_list:
                for n_ac in n_ac_list:
                    # F2L time extraction
                    try:
                        f2l_time = data[j_id][n_ac]['f2l-time']
                        records_f2l.append({
                            'town': TOWNS_DICT.get(j_id, 'Unknown'),
                            'junction': j_id,
                            'actors': n_ac,
                            'time': f2l_time
                        })
                    except (KeyError, TypeError):
                        continue

                    # L2C time extraction
                    try:
                        l2c_time_list = data[j_id][n_ac]['l2c-time-list']
                        for l2c_time in l2c_time_list:
                            records_l2c.append({
                                'town': TOWNS_DICT.get(j_id, 'Unknown'),
                                'junction': j_id,
                                'actors': n_ac,
                                'time': l2c_time
                            })
                    except (KeyError, TypeError):
                        continue

    # Save F2L times to CSV
    df_f2l = pd.DataFrame(records_f2l)
    output_csv = os.path.join(output_folder_path, 'a2l_times.csv')
    df_f2l.to_csv(output_csv, index=False)

    median_df_f2l = df_f2l.groupby(['town', 'junction', 'actors'])['time'].median().reset_index()
    median_csv = os.path.join(output_folder_path, 'a2l_median_time')
    median_df_f2l.to_csv(median_csv + ".csv", index=False)
    median_df_f2l.to_latex(median_csv + ".txt")

    # Save L2C times to CSV
    df_l2c = pd.DataFrame(records_l2c)
    output_l2c_csv = os.path.join(output_folder_path, 'l2c_times.csv')
    df_l2c.to_csv(output_l2c_csv, index=False)

    median_df_l2c = df_l2c.groupby(['town', 'junction', 'actors'])['time'].median().reset_index()
    median_l2c_csv = os.path.join(output_folder_path, 'l2c_median_time')
    median_df_l2c.to_csv(median_l2c_csv + ".csv", index=False)
    median_df_l2c.to_latex(median_l2c_csv + ".txt")

    print(f"Saved {len(df_f2l)} records to {output_csv}")
    print(f"Saved {len(df_l2c)} records to {output_l2c_csv}")

if __name__ == "__main__":
    # Example usage:
    # python statistics_complete.py /path/to/folder
    in_folder = 'evaluation/SOSYM25/all_output/complete'
    out_folder = 'evaluation/SOSYM25/all_output/statistics/complete'
    os.makedirs(out_folder, exist_ok=True)
    j_id = ['916', '2240']
    n_ac = ['1', '2', '3', '4']
    collect_f2l_times(in_folder, out_folder, j_id, n_ac)