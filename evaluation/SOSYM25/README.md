
## Experiments

### RQ1
To run the experiments comparing our approach (named `Complete`) to `Scenic`, run the following command:
```
bash evalution/SOSYM25/run_all_measurements.sh
```
For further details, please refer to the `run_all_measurements.sh` file, which contains many helpful comments.

Note that data processing for RQ1 is also performed in this stage. 

### RQ2-4

To generate the scenarios that are runnable in simulation, run the following command:
```
bash evaluation/SOSYM25/complete/run-eval.sh
```
This generates simulation-ready scenarios in the `evaluation/SOSYM25/output-scenarios/` folder.

To run the generated cenarios in simulation, please refer to the documentation of our [Transfuser fork](https://github.com/ArenBabikian/transfuser/tree/complete-gen) repository.

## Data analysis

Once the Scenarios are simulated, to process the data and generate figures, you should:

1. Move the scenario generation data to the `evaluation/SOSYM25/data-sim/` folder:
    - `evaluation/SOSYM25/data-sim/0-generated-scenarios`
    - `evaluation/SOSYM25/data-sim/1-simulation-results`
<!-- 2. To process the raw data and output them in a more digestable format, run the following command: 
    ```
    python evaluation/SOSYM25/figures/runmetrics.py
    ``` -->
2. To extract the useful information from the processed data and save it in separate files, run the following command:
    ```
    python evaluation/SOSYM25/figures/gen_figures_from_cooked.py
    ```
    
3. Generate the final figures using the processed data by running the following command:
    ```
    python evaluation/SOSYM25/figures/create_figures_SOSYM.py
    ```
    The figures will be saved in the `evaluation/SOSYM25/figures/output` folder.