
'''Interface for elements in the UI. Each element need a an update and draw method.'''
class Element:
    def __init__(self, display_name: str, basic_ui: bool = True, options: list = []):
        self.__display_name = display_name
        self.__basic_ui = basic_ui
        self.__options = options

    def get_display_name(self) -> str:
        return self.__display_name

    def is_basic_ui(self) -> bool:
        return self.__basic_ui

    def get_options(self) -> list:
        return self.__options

    '''
    Method to update the actions that are happening

    Parameters:
        current_global_selection (int): What option is currently selected.

    Returns:
        A tuple (int, list) of the current option selected and the options available after the update.
    '''
    def update(self, current_global_selection) -> tuple:
        return (current_global_selection, [])

    def draw(self, global_color):
        pass

    def __str__(self) -> str:
        return self.get_display_name()
