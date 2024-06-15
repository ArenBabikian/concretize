import logging

class Speed_Profile:
    def __init__(self, speed_profile_id):

        if speed_profile_id == None:
            self.speed_in_junction = 0
            self.speed_on_road = 0
        elif speed_profile_id == 'transfuser':
            self.speed_in_junction = 3
            self.speed_on_road = 4
        elif speed_profile_id.isdigit():
            s = float(speed_profile_id)
            self.speed_in_junction = s
            self.speed_on_road = s
        else:
            logging.error(f"Invalid speed profile id <{speed_profile_id}>. Select among the following ids ['transfuser', <float>]")
            exit(1)

    def speed_at_position(self):
        return self.speed_profile
