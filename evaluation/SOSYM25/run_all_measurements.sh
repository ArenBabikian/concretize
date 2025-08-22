
base_dir="evaluation/SOSYM25"
output_dir="evaluation/SOSYM25/all_output"

# RUN MEASUREMENTS

## 1.1 Run Complete Evaluation
### saves generation stats at `$output_dir/complete/`
bash $base_dir/complete/run-gen-for-baseline.sh

## 1.2 Run Scenic Evaluation - Abstract-to-Logical (A2L)
### saves generation stats in `$output_dir/scenic/a2l/`
### saves generated logical scenarios at `$output_dir/scenic/logical-scenarios/`
python $base_dir/scenic/scenic-evaluation.py

## 1.3 Run Scenic Concretization - Logical-to-Concrete (L2C)
### saves generation stats in `$output_dir/scenic/l2c/`
python $base_dir/scenic/scenic-concretization.py

# PROCESS DATA

## 1. Get stats for Complete Evaluation
### saves the statistics at `$output_dir/statistics/complete`
python $base_dir/statistics/statistics_complete.py

## 2. Get stats for Scenic Evaluation (A2L and L2C)
### saves the statistics at `$output_dir/statistics/scenic`
python $base_dir/statistics/statistics_scenic.py

## 3. Get statistical significance analysis
### saves the statistics at `$output_dir/statistics/stat_sig`
python $base_dir/statistics/statistical_significance.py
