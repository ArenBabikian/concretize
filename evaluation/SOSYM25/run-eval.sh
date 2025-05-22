# town 04, j916 is the 4-way 1-lane junction

EVAL_HOME="evaluation/SOSYM25/"

# Store junction-town pairs as "junction:town"
junctions=("916:Town04" "2240:Town05")
num_actors=(2 3 4)

if [ ! -d output ]; then
    mkdir output
fi

for jt in "${junctions[@]}"; do
    IFS=":" read -r junction town <<< "$jt"
    for num_actor in "${num_actors[@]}"; do
        suffix="_j${junction}_n${num_actor}"
        python concretize.py\
            -v 2\
            -n 10\
            -t 60\
            -m ${town}\
            --save-xml\
            --save-xml-file scenarios${suffix}.xml\
            -z\
            --color-scheme default\
            --show-maneuvers\
            --show-exact-paths\
            -all\
            --output-directory ${EVAL_HOME}/output\
            --save-statistics-file stats${suffix}.json\
            complete\
            --junction $junction\
            ${EVAL_HOME}/evaluation${num_actor}.concretize
    done
done
