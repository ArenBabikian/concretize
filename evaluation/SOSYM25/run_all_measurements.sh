
# 1. Run Complete Evaluation
bash evaluation/SOSYM25/complete/run-gen-for-baseline.sh

# 2. Run Scenic Evaluation (F2L)
python evaluation/SOSYM25/scenic/scenic-evaluation.py

# 3. Run Scenic Concretization (L2C)
python evaluation/SOSYM25/scenic/scenic-concretization.py
python evaluation/SOSYM25/scenic/scenic-concretization.py --threshold 2.5

