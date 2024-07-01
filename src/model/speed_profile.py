import logging

class Speed_Profile:
    def __init__(self, speed_profile_id):

        if speed_profile_id == None:
            self.speed_in_junction = 5 # default changed from 0 to 5
            self.speed_on_road = 5 # default changed from 0 to 5
        elif speed_profile_id == 'transfuser':
            self.speed_in_junction = 3
            self.speed_on_road = 4
        elif isinstance(speed_profile_id, (int, float)):
            s = float(speed_profile_id)
            self.speed_in_junction = s
            self.speed_on_road = s
        else:
            raise Exception(f"Invalid speed profile id <{speed_profile_id}>. Select among the following ids ['transfuser', <float>]")

    def speed_at_position(self):
        return self.speed_profile
