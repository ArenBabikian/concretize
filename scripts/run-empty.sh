parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd "../"

if [ ! -d output ]; then
    mkdir output
fi

python concretize.py\
    -v 2\
    -n 1\
    -t 15\
    -m Zalazone\
    --output-directory output-sept\
    --save-statistics-file stats.json\
    --hide-actors\
    --view-diagram\
    --save-diagram\
    --color-scheme alternate\
    mhs\
    scripts/specifications/empty_map.concretize