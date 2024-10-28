"""The main file used to launch the app."""

from configparser import ConfigParser

from gui.services.app_service import AppService

if __name__ == "__main__":

    _config = ConfigParser()
    _config.read("config.cfg")
    AppService(_config).initialize_app()
