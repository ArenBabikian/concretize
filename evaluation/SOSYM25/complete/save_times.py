import json
import sys
import os
import statistics

def save_times(input_file_path, output_file_path, junction_id, num_actors):
    # Load input JSON
    with open(input_file_path, 'r') as infile:
        input_data = json.load(infile)
    # Extract the timing value
    try:
        timing_value = input_data['runs']['0']['timing']['functional-to-logical']
        l2c_list = input_data['runs']['0']['timing']['logical-to-concrete']
        l2c_median = statistics.median(l2c_list)
    except (KeyError, TypeError):
        print("Error: Could not find required timing values in input file.")
        sys.exit(1)

    # Load or initialize output JSON
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as outfile:
            try:
                output_data = json.load(outfile)
            except json.JSONDecodeError:
                output_data = {}
    else:
        output_data = {}

    # Ensure nested structure
    if junction_id not in output_data:
        output_data[junction_id] = {}
    if str(num_actors) not in output_data[junction_id]:
        output_data[junction_id][str(num_actors)] = {}

    # Update the output data with the timing values
    output_data[junction_id][str(num_actors)]['f2l-time'] = timing_value
    output_data[junction_id][str(num_actors)]['f2l-success-rate'] = 1.0
    output_data[junction_id][str(num_actors)]['l2c-time-list'] = l2c_list
    output_data[junction_id][str(num_actors)]['l2c-time-median'] = l2c_median
    output_data[junction_id][str(num_actors)]['l2c-success-rate'] = 1.0

    # Write back to output file
    with open(output_file_path, 'w') as outfile:
        json.dump(output_data, outfile, indent=2)

    print(f"Timing for junction {junction_id} with {num_actors} actors saved successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python save_times.py <input_file> <output_file> <junction_id> <num_actors>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    junction_id = sys.argv[3]
    num_actors = sys.argv[4]
    save_times(input_file, output_file, junction_id, num_actors)