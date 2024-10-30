"""The main file used to launch the app."""

from configparser import ConfigParser

from utils.config import Config
from gui.views.app import App

if __name__ == "__main__":
    _config = ConfigParser()
    _config.read("config.cfg")
    Config(_config)
    App()
