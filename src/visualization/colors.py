import matplotlib.colors as colors
import random

car_red = '#A8001B' # 140,61,54
car_blue = '#2663E6' # 45,77,111
white = '#FFFFFF'
gray = '#808080'

class color:
    def __init__(self, name, hex_def, hex_light, hex_dark):
        self.name = name
        self.default = hex_def
        self.light = hex_light
        self.dark = hex_dark

# COLOR_SEQ = ['#CC6400', '#0876B5', '#A50205', '#5C7B3D', '#C1DDEC', '#F2D8BF']

def get_color_object(name):
    if name in STR2COLOR:
        return STR2COLOR[name]
    else:
        return color(name, name, name, name)

def get_random_color():
    r = random.randint(0, 256)
    b = random.randint(0, 256)
    g = random.randint(0, 256)
    col = f"#{r:02x}{g:02x}{b:02x}"
    return color('random', col, col, col)

# TODO generalize this...
STR2COLOR = {
    'red': color('red', '#c25c55', '#D99B96', '#9B2721'),
    'blue': color('blue', '#4b779d', '#83A5C3', '#283F52'),
    'orange': color('orange', '#EB9419', '#F0B056', '#83510B'),
    'green': color('green', '#5EA667', '#96C59C', '#335C38'),
    'purple': color('purple', '#A47BD1', '#CBB4E4', '#5D4479'),
    'random': get_random_color()
    }