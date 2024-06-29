parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd "../"

if [ ! -d output ]; then
    mkdir output
fi

# town 04, j916 is the 4-way 1-lane junction

python concretize.py\
    -v 2\
    -n 2\
    -t 5\
    -m Town05\
    -all\
    --output-directory output-new\
    --save-statistics-file stats.json\
    --save-diagram\
    --show-maneuver\
    --view-diagram\
    --show-exact-paths\
    --color-scheme alternate\
    -z\
    complete\
    -j 332\
    scripts/specifications/dynamic.concretize