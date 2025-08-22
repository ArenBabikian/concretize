
def printAggregateData(aggregate_data):
    for num_actors, data in aggregate_data.items():
        print(f"Num Actors: {num_actors} (Total Scenarios: {data['total_scenarios']})")
        print(f"Status: {data['status']}")
        print("Avoidable Collisions:")
        for key, value in data['preventability'].items():
            for key2, value2 in data['preventability'][key].items():
                print(f"    [{key}][{key2}]:{[ f'{k}:({v})' for k, v in value2.items()]}")

        print(f"Near-misses: {data['near_misses']}")
        print()


NUM_TAIL_FRAMES = 60
NUM_BUCKETS = 12
def make_empty_buckets(totalFrames):
    bucket_size = totalFrames / NUM_BUCKETS
    return {int(i*bucket_size):0 for i in range(NUM_BUCKETS)}
        

def init_aggregate_data(aggregate_data, num_actors, status, near_misses):
    if num_actors not in aggregate_data:
        aggregate_data[num_actors] = {
            'status': {
                'Completed': 0,
                'Failed': 0,
                'Failed - Agent timed out': 0
            },
            'preventability' : {
                'vis' : {
                    'tot_frames' : make_empty_buckets(100),
                    'stretch_frames' : make_empty_buckets(NUM_TAIL_FRAMES),
                    'tail_frames' : make_empty_buckets(NUM_TAIL_FRAMES)
                },
                'lid' : {
                    'tot_frames' : make_empty_buckets(100),
                    'stretch_frames' : make_empty_buckets(NUM_TAIL_FRAMES),
                    'tail_frames' : make_empty_buckets(NUM_TAIL_FRAMES)
                },
                'both' : {
                    'tot_frames' : make_empty_buckets(100),
                    'stretch_frames' : make_empty_buckets(NUM_TAIL_FRAMES),
                    'tail_frames' : make_empty_buckets(NUM_TAIL_FRAMES)
                }
            } ,
            'near_misses': {
                'scenes': 0,
                'all': 0
            },
            'total_scenarios': 0
        }

    aggregate_data[num_actors]['status'][status] += 1
    aggregate_data[num_actors]['total_scenarios'] += 1
    aggregate_data[num_actors]['near_misses']['all'] += sum(near_misses)
    if sum(near_misses) > 0:
        aggregate_data[num_actors]['near_misses']['scenes'] += 1


# Divide the tail frames into six buckets that are equally distributed over sixty
def get_bucket_index(num_active_frames, num_baseline_frames):
    bucket_size = num_baseline_frames / NUM_BUCKETS

    bucket_index = int(int(num_active_frames / bucket_size) * bucket_size)
    if bucket_index >= num_baseline_frames:
        bucket_index = int(num_baseline_frames - bucket_size)

    assert bucket_index >= 0 and bucket_index < num_baseline_frames
    return bucket_index

def fill_aggregate_data(num_actors, aggregate_data, num_frames, 
                        num_frames_tot_in_lid, num_frames_tot_in_vis, num_frames_tot_in_both,
                        num_frames_stretch_in_lid, num_frames_stretch_in_vis, num_frames_stretch_in_both,
                        num_frames_tail_in_lid, num_frames_tail_in_vis, num_frames_tail_in_both):
    aggregate_data[num_actors]['preventability']['vis']['tot_frames'][get_bucket_index(num_frames_tot_in_vis/num_frames*100, 100)] += 1
    aggregate_data[num_actors]['preventability']['vis']['stretch_frames'][get_bucket_index(num_frames_stretch_in_vis, NUM_TAIL_FRAMES)] += 1
    aggregate_data[num_actors]['preventability']['vis']['tail_frames'][get_bucket_index(num_frames_tail_in_vis, NUM_TAIL_FRAMES)] += 1

    aggregate_data[num_actors]['preventability']['lid']['tot_frames'][get_bucket_index(num_frames_tot_in_lid/num_frames*100, 100)] += 1
    aggregate_data[num_actors]['preventability']['lid']['stretch_frames'][get_bucket_index(num_frames_stretch_in_lid, NUM_TAIL_FRAMES)] += 1
    aggregate_data[num_actors]['preventability']['lid']['tail_frames'][get_bucket_index(num_frames_tail_in_lid, NUM_TAIL_FRAMES)] += 1

    aggregate_data[num_actors]['preventability']['both']['tot_frames'][get_bucket_index(num_frames_tot_in_both/num_frames*100, 100)] += 1
    aggregate_data[num_actors]['preventability']['both']['stretch_frames'][get_bucket_index(num_frames_stretch_in_both, NUM_TAIL_FRAMES)] += 1
    aggregate_data[num_actors]['preventability']['both']['tail_frames'][get_bucket_index(num_frames_tail_in_both, NUM_TAIL_FRAMES)] += 1

