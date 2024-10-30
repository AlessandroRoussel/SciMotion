"""The main file used to launch the app."""

from configparser import ConfigParser

from utils.config import Config
from gui.services.app_service import AppService

if __name__ == "__main__":

    _config = ConfigParser()
    _config.read("config.cfg")
    Config(_config)
    AppService().initialize_app()
