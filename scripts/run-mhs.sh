parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd "../"

if [ ! -d output ]; then
    mkdir output
fi

python concretize.py\
    -v 2\
    -n -1\
    -t 5\
    -m maps/town05.xodr\
    -all\
    -s-stat output/stats.json\
    -v-diag\
    -s-diag output/diagram.png\
    -z\
    mhs\
    --num-of-mhs-runs 2\
    scripts/specifications/static.concretize