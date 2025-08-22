import os
import json

def validate_dir(d):
    exit(f"The folder '{d}' does not exist.") if not os.path.exists(d) else None
    exit(f"'{d}' is not a directory.") if not os.path.isdir(d) else None
    
def validate_path(f):
    exit(f"The file '{f}' does not exist.") if not os.path.exists(f) else None
    exit(f"'{f}' is not a directory.") if not os.path.isfile(f) else None

def gen_figures(cooked_measurements_path, abs_scenario_dir, included_sizes):

    # Validate and get started
    validate_dir(abs_scenario_dir)
    validate_path(cooked_measurements_path)
    with open(cooked_measurements_path) as j:
        cooked_measurements = json.load(j)

    # SEMANTICS
    # >> ego-related measurements:
    #   semantics are the same regardless of the number of non-ego actors
    # >> non-ego-related measurements:
    #   for 2-actor scenarios:
    #     there is 1 non-ego, so the metric is whether that one is satisfying the criterion (e.g. if that one has the specified maneuver type)
    #   for 3/4-actor scenarios:
    #     if any of the non-egos is satisfying the criterion
    # >> relationship measurements:
    #   for 2-actor scenarios:
    #     if the non-ego satisfies the positional relation constraint
    #   for 3/4-actor scenarios:
    #     if any of the non-egos satisfy the positional relatio constraint WRT the EGO

    # DATA DICTIONARIES
    # EGO
    map_ego____specific_man = {}
    map_ego____type_____man = {}
    map_ego____start___lane = {}
    map_ego____end_____lane = {}

    # NON_EGO
    map_nonego_specific_man = {}
    map_nonego_type_____man = {}
    map_nonego_start___lane = {}
    map_nonego_end_____lane = {}

    # RELATIONSHIPS
    map_init__relationship = {}
    map_final_relationship = {}

    all_scenarios = cooked_measurements['scenarios']
    for num_actors in all_scenarios:
        if int(num_actors) not in included_sizes:
            continue

        # ABSTRACT
        with open(f'{abs_scenario_dir}/_{num_actors}actors-abs-scenarios.json') as j:
            abs_scenarios_json = json.load(j)

        all_scenarios_at_size = all_scenarios[num_actors]
        for scenario_spec_id in all_scenarios_at_size:
            all_reps_for_scenario_spec = all_scenarios_at_size[scenario_spec_id]

            # ABSTRACT INFO ABOUT THE REP
            scen_descs = list(filter(lambda scen : scen['scenario_id'] == int(scenario_spec_id), abs_scenarios_json['all_scenarios']))
            assert len(scen_descs) == 1
            abs_scen_info = scen_descs[0]

            for rep_id  in all_reps_for_scenario_spec:

                # GATHERED INFO ABOUT THE REP
                rep_info = all_reps_for_scenario_spec[rep_id]
                num_collisions = len(rep_info['collided with'])
                assert num_collisions < 2

                near_miss_occurance = 1 if sum(rep_info['near_miss_with']) else 0

                stats_to_add = {'collisions':num_collisions, 'near-miss':near_miss_occurance}
                

                # GATHER SPECIFIC INFO (2 actors only, for now)
                # EGO
                data_ego____specific_man = abs_scen_info['actors'][0]['maneuver']['id']
                data_ego____type_____man = abs_scen_info['actors'][0]['maneuver']['type']
                data_ego____start___lane = abs_scen_info['actors'][0]['maneuver']['start_lane_id']
                data_ego____end_____lane = abs_scen_info['actors'][0]['maneuver']['end_lane_id']

                add_data_to_map(data_ego____specific_man, map_ego____specific_man, stats_to_add)
                add_data_to_map(data_ego____type_____man, map_ego____type_____man, stats_to_add)
                add_data_to_map(data_ego____start___lane, map_ego____start___lane, stats_to_add)
                add_data_to_map(data_ego____end_____lane, map_ego____end_____lane, stats_to_add)

                # iterate through NON-EGOs
                for nonego_actor in abs_scen_info['actors'][1:]:
                    data_nonego_specific_man = nonego_actor['maneuver']['id']
                    data_nonego_type_____man = nonego_actor['maneuver']['type']
                    data_nonego_start___lane = nonego_actor['maneuver']['start_lane_id']
                    data_nonego_end_____lane = nonego_actor['maneuver']['end_lane_id']
                    add_data_to_map(data_nonego_specific_man, map_nonego_specific_man, stats_to_add)
                    add_data_to_map(data_nonego_type_____man, map_nonego_type_____man, stats_to_add)
                    add_data_to_map(data_nonego_start___lane, map_nonego_start___lane, stats_to_add)
                    add_data_to_map(data_nonego_end_____lane, map_nonego_end_____lane, stats_to_add)

                # iterate through INITIAL RELATIONS, only relative to ego
                all_initial_relations_from_ego = abs_scen_info['initial_relations']['0']
                for target in all_initial_relations_from_ego:
                    data_init__relationship = all_initial_relations_from_ego[target]
                    add_data_to_map(data_init__relationship, map_init__relationship, stats_to_add)

                # iterate through FINAL RELATIONS, only relative to ego
                all_final_relations_from_ego = abs_scen_info['final_relations']['0']
                for target in all_final_relations_from_ego:
                    data_final_relationship = all_final_relations_from_ego[target]
                    add_data_to_map(data_final_relationship, map_final_relationship, stats_to_add)


    all_relevant_maps = {'ego____specific' : map_ego____specific_man,
                         'ego________type' : map_ego____type_____man,
                         'ego_______start' : map_ego____start___lane,
                         'ego_________end' : map_ego____end_____lane,

                         'nonego_specific' : map_nonego_specific_man,
                         'nonego_____type' : map_nonego_type_____man,
                         'nonego____start' : map_nonego_start___lane,
                         'nonego______end' : map_nonego_end_____lane,

                         'rel________init' : map_init__relationship,
                         'rel_______final' : map_final_relationship
    }

    return all_relevant_maps
    

def add_data_to_map(data, data2metric, stats_to_add):
    if data not in data2metric:
        data2metric[data] = {'attempts' : 0, 'collisions' : 0, '>0-near-miss-occured' : 0}
    data2metric[data]['attempts'] += 1
    data2metric[data]['collisions'] += stats_to_add['collisions']
    data2metric[data]['>0-near-miss-occured'] += stats_to_add['near-miss']


def to_dataframe(cooked_measurements_path, abs_scenario_dir, included_sizes):
    # Validate and get started
    validate_dir(abs_scenario_dir)
    validate_path(cooked_measurements_path)
    with open(cooked_measurements_path) as j:
        cooked_measurements = json.load(j)


    data_for_actor_df = []
    data_for_relationship_df = []
    dict_for_actor_df = {}
    dict_for_actor_df['actors'] = data_for_actor_df
    dict_for_relationship_df = {}
    dict_for_relationship_df['relationships'] = data_for_relationship_df


    
    all_scenarios = cooked_measurements['scenarios']
    for num_actors in all_scenarios:
        if int(num_actors) not in included_sizes:
            continue

        # ABSTRACT
        with open(f'{abs_scenario_dir}/_{num_actors}actors-abs-scenarios.json') as j:
            abs_scenarios_json = json.load(j)

        all_scenarios_at_size = all_scenarios[num_actors]
        for scenario_spec_id in all_scenarios_at_size:
            all_reps_for_scenario_spec = all_scenarios_at_size[scenario_spec_id]

            # ABSTRACT INFO ABOUT THE REP
            scen_descs = list(filter(lambda scen : scen['scenario_id'] == int(scenario_spec_id), abs_scenarios_json['all_scenarios']))
            assert len(scen_descs) == 1
            abs_scen_info = scen_descs[0]

            for rep_id  in all_reps_for_scenario_spec:

                # GATHERED INFO ABOUT THE REP
                rep_info = all_reps_for_scenario_spec[rep_id]
                num_collisions = len(rep_info['collided with'])
                assert num_collisions < 2

                near_miss_occurance = 1 if sum(rep_info['near_miss_with']) else 0
                num_preventative_maneuver = rep_info['num_preventative_maneuver']
                num_frames = rep_info['num_frames']
                preventability = rep_info['preventability']
                if preventability is None:
                    preventability = {
                        'vis' : {
                            'tot_frames' : 0,
                            'stretch_frames' : 0,
                            'tail_frames' : 0
                        },
                        'lid' : {
                            'tot_frames' : 0,
                            'stretch_frames' : 0,
                            'tail_frames' : 0
                        },
                        'both' : {
                            'tot_frames' : 0,
                            'stretch_frames' : 0,
                            'tail_frames' : 0
                        }
                    }
                

                # GATHER SPECIFIC INFO
                # EGO
                scen_base = {}
                scen_base['map_name'] = cooked_measurements['map_name']
                scen_base['junction_id'] = cooked_measurements['junction_id']
                scen_base['num_actors'] = num_actors
                scen_base['scenario_spec_id'] = scenario_spec_id
                scen_base['rep_id'] = rep_id
                scen_base['num_collisions'] = num_collisions
                scen_base['num_preventative_maneuvers'] = num_preventative_maneuver
                scen_base['near_miss_occurance'] = near_miss_occurance
                scen_base['num_frames'] = num_frames
                scen_base['prevent_vis_tot_frames'] = preventability['vis']['tot_frames']
                scen_base['prevent_vis_stretch_frames'] = preventability['vis']['stretch_frames']
                scen_base['prevent_vis_tail_frames'] = preventability['vis']['tail_frames']
                scen_base['prevent_lid_tot_frames'] = preventability['lid']['tot_frames']
                scen_base['prevent_lid_stretch_frames'] = preventability['lid']['stretch_frames']
                scen_base['prevent_lid_tail_frames'] = preventability['lid']['tail_frames']
                scen_base['prevent_both_tot_frames'] = preventability['both']['tot_frames']
                scen_base['prevent_both_stretch_frames'] = preventability['both']['stretch_frames']
                scen_base['prevent_both_tail_frames'] = preventability['both']['tail_frames']

                data_to_add = {}
                data_to_add.update(scen_base)
                data_to_add['ego'] = True
                data_to_add['maneuver'] = abs_scen_info['actors'][0]['maneuver']
                data_for_actor_df.append(data_to_add)

                # iterate through NON-EGOs
                for nonego_actor in abs_scen_info['actors'][1:]:
                    data_to_add = {}
                    data_to_add.update(scen_base)
                    data_to_add['ego'] = False
                    data_to_add['maneuver'] = nonego_actor['maneuver']
                    data_for_actor_df.append(data_to_add)

                # iterate through INITIAL RELATIONS, only relative to ego
                all_initial_relations_from_ego = abs_scen_info['initial_relations']['0']
                for target in all_initial_relations_from_ego:
                    relation_to_add = {}
                    relation_to_add.update(scen_base)
                    relation_to_add['relative_to'] = 0
                    relation_to_add['target'] = target
                    relation_to_add['time'] = 'initial'
                    relation_to_add['relationship'] = all_initial_relations_from_ego[target]
                    data_for_relationship_df.append(relation_to_add)

                # iterate through FINAL RELATIONS, only relative to ego
                all_final_relations_from_ego = abs_scen_info['final_relations']['0']
                for target in all_final_relations_from_ego:
                    relation_to_add = {}
                    relation_to_add.update(scen_base)
                    relation_to_add['relative_to'] = 0
                    relation_to_add['target'] = target
                    relation_to_add['time'] = 'final'
                    relation_to_add['relationship'] = all_final_relations_from_ego[target]
                    data_for_relationship_df.append(relation_to_add)
    return dict_for_actor_df, dict_for_relationship_df



def main():
    map_junction = 'rural'
    # map_junction = 'urban'
    data_path = f"evaluation/SOSYM25/data-sim/{map_junction}"
    cooked_measurements_path = f'{data_path}/measurements.json'
    abs_scenario_dir = f'{data_path}/abs_scenarios'
    included_sizes = [2, 3, 4]
    out_path = f"evaluation/SOSYM25/data-sim/{map_junction}"
    
    # Get the list of file contents
    data = gen_figures(cooked_measurements_path, abs_scenario_dir, included_sizes)
    data_actor, data_relationship = to_dataframe(cooked_measurements_path, abs_scenario_dir, included_sizes)

    os.makedirs(out_path, exist_ok=True)
    json.dump(data_actor, open(f'{out_path}/data_actor.json', 'w'), indent=4)
    json.dump(data_relationship, open(f'{out_path}/data_relationship.json', 'w'), indent=4)

    # PRINT DATA
    print('_______________________________________')
    print(F'AGGREGATE RESULTS FOR {included_sizes}')

    for map_id in data:
        print('---------------------')
        print(f'<<<{map_id}>>>')
        for x in data[map_id]:
            print(f'{x} : {data[map_id][x]}')

    # Save the list as a JSON file
    # with open(out_path, "w") as json_file:
    #     json.dump(file_contents_list, json_file, indent=4)
    # print(f'Saved cooked measurments at     {out_path}')

if __name__ == "__main__":
    main()
