
base_dir="evaluation/SOSYM25/figures"

## 1 Process the raw data.
### transforms the raw data into an intermediate format that is suitable for analysis, while also being human-digestible.
python $base_dir/process_raw_data.py

## 2. Generate the figure-ready data from the intermediate format
python $base_dir/gen_from_intermediate_data.py

## 3. Derive figures from the data
### saves figures in `$base_dir/output/`
python $base_dir/create_figures.py
