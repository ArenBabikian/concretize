
# town 04, j916 is the 4-way 1-lane junction

python concretize.py\
    -v 2\
    -n -1\
    -t 60\
    -m Town02\
    --view-diagram\
    --save-diagram\
    -z\
    --color-scheme default\
    --show-maneuvers\
    --show-exact-paths\
    -z\
    -all\
    --output-directory output\
    --save-statistics-file stats.json\
    complete\
    scripts/specifications/gm.concretize