# town 04, j916 is the 4-way 1-lane junction

EVAL_HOME="evaluation/SOSYM25/"
OUTPUT_FOLDER="${EVAL_HOME}/output-rq0"

# Store junction-town pairs as "junction:town"
junctions=("916:Town04" "2240:Town05")
num_actors=(1 2 3 4)

if [ ! -d output ]; then
    mkdir output
fi

for jt in "${junctions[@]}"; do
    IFS=":" read -r junction town <<< "$jt"
    for num_actor in "${num_actors[@]}"; do
        suffix="_j${junction}_n${num_actor}"
        xml_save_file="scenarios${suffix}.xml"
        json_save_file="scenarios${suffix}.json"
        stats_save_file="stats${suffix}.json"

        # Run scenario generation
        python concretize.py\
            -v 2\
            -n 10\
            -t 60\
            -m ${town}\
            -z\
            --color-scheme default\
            --show-maneuvers\
            --show-exact-paths\
            -all\
            --output-directory ${OUTPUT_FOLDER}\
            --save-statistics-file ${stats_save_file}\
            --project SOSYM\
            complete\
            --junction $junction\
            ${EVAL_HOME}/evaluation${num_actor}.concretize
        # Check if the command was successful
        if [ $? -ne 0 ]; then
            echo "Error: concretize.py failed for junction $junction, town $town, actors $num_actor"
            exit 1
        fi

        # Collect the timing information and save it to a file
        python ${EVAL_HOME}/save_times.py\
            ${OUTPUT_FOLDER}/${stats_save_file}\
            ${OUTPUT_FOLDER}/times.json\
            ${junction}\
            ${num_actor}
        echo ""
    done

done
