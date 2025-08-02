## Scenario Generation for RQ1, RQ2, RQ3
```
bash evaluation/SOSYM25/complete/run-eval.sh
```

## RQ0

### For COMPLETE

1. generate the scenarios
```
bash evaluation/SOSYM25/complete/run-gen-for-baseline.sh
```
saves everything at `evaluation/SOSYM25/all_output/complete`

2. generate the stats (mdeians)
```
python evaluation/SOSYM25/statistics/statistics_complete.py
```
saves results in `evaluation\SOSYM25\statistics\output\complete`



### For SCENIC

1. Run f2l
```
python evaluation\SOSYM25\scenic\scenic-evaluation.py
```
generates all the times (including intermediate times) at `evaluation\SOSYM25\all_output\scenic\f2l\generation_times.csv`
<br>
also generates all logcal scenarios at `evaluation\SOSYM25\all_output\scenic\logical-scenarios`

2. get statistics for f2l
```
python evaluation\SOSYM25\statistics\statistics_scenic.py
```
saves results in `evaluation\SOSYM25\statistics\output\scenic`

3. Run L2C
```
python evaluation\SOSYM25\scenic\scenic-concretization.py
```
generates all the times at `evaluation\SOSYM25\all_output\scenic\l2c\concretization_times.csv`

4. get stats for L2C
```
python evaluation\SOSYM25\statistics\statistics_scenic.py
```
saves results in `evaluation\SOSYM25\statistics\output\scenic`


### For STAT SIG

1. for F2L
```
python evaluation\SOSYM25\statistics\statistical_significance.py
```
Saves resluts at `evaluation\SOSYM25\statistics\output\stat_sig`

2. for L2C (TODO)