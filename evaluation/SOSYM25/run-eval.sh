# town 04, j916 is the 4-way 1-lane junction

EVAL_HOME="evaluation/SOSYM25/"
OUTPUT_FOLDER="${EVAL_HOME}/output3"

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
        python concretize.py\
            -v 2\
            -n 10\
            -t 60\
            -m ${town}\
            --save-xml-json\
            --save-xml-file ${xml_save_file}\
            --save-json-file ${json_save_file}\
            -z\
            --color-scheme default\
            --show-maneuvers\
            --show-exact-paths\
            -all\
            --output-directory ${OUTPUT_FOLDER}\
            --save-statistics-file stats${suffix}.json\
            --project SOSYM\
            complete\
            --junction $junction\
            ${EVAL_HOME}/evaluation${num_actor}.concretize
        # Check if the command was successful
        if [ $? -ne 0 ]; then
            echo "Error: concretize.py failed for junction $junction, town $town, actors $num_actor"
            exit 1
        fi
    done

    # Combine all output files for this junction-town pair
    combined_file="${OUTPUT_FOLDER}/combined_j${junction}.xml"
    > "$combined_file"
    for i in "${!num_actors[@]}"; do
        num_actor="${num_actors[$i]}"
        xml_file="${OUTPUT_FOLDER}/scenarios_j${junction}_n${num_actor}.xml"
        if [ -f "$xml_file" ]; then
            if [ "$i" -eq 0 ]; then
            # First entry: remove last line
            head -n -1 "$xml_file" >> "$combined_file"
            echo "" >> "$combined_file"
            elif [ "$i" -eq $((${#num_actors[@]}-1)) ]; then
            # Last entry: remove first 2 lines
            tail -n +3 "$xml_file" >> "$combined_file"
            echo "" >> "$combined_file"
            else
            # Middle entries: remove first 2 lines and last line
            tail -n +3 "$xml_file" | head -n -1 >> "$combined_file"
            echo "" >> "$combined_file"
            fi
        fi
    done

done
