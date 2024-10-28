"""
Service concerning all user actions in general.

The ActionService provides a list of functions corresponding
to various actions that the user can perform, such as creating
a new project, adding a layer to a sequence...
"""

from utils.singleton import Singleton


class ActionService(metaclass=Singleton):
    """Service concerning all user actions in general."""

    #####################
    # File menu actions #
    #####################

    def create_new_project():
        print("New project")

    def open_project():
        print("Open project")

    def save_project():
        print("Save project")

    def save_project_as():
        print("Save project as")

    def open_project_parameters():
        print("Project parameters")

    def close():
        print("Close window")

    #####################
    # Edit menu actions #
    #####################

    def cut():
        print("Cut")

    def copy():
        print("Copy")

    def paste():
        print("Paste")
