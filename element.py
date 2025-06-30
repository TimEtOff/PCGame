from sound_manager import SoundManager

'''Interface for elements in the UI. Each element need a an update and draw method.'''
class Element:
    def __init__(self,
                 display_name: str,
                 basic_ui: bool = True,
                 options: list = [],
                 key_options: list = []
                 ):
        self.__display_name = display_name
        self.__basic_ui = basic_ui
        self.__options = options
        self.__key_options = key_options

    def get_display_name(self) -> str:
        return self.__display_name

    def is_basic_ui(self) -> bool:
        return self.__basic_ui

    def get_options(self) -> list:
        return self.__options

    def get_key_options(self) -> list:
        return self.__key_options

    def update(self, sound_manager: SoundManager=None):
        '''
        Method to update the actions that are happening

        Parameters:
            current_global_selection (int): What option is currently selected.

        Returns:
            A tuple (int, list) of the current option selected and the options available after the update.
        '''
        pass

    def draw(self, global_color, x, y, width, height):
        pass

    def __str__(self) -> str:
        return self.get_display_name()
