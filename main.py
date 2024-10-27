import configparser

config = configparser.ConfigParser()
config.read("config.cfg")

# print(config.getint("window", "min_width"))

# TODO : send the config to the editor, renderer, GUI
# TODO : create singletons editor, renderer, GUI
