from utils.sound_manager import SoundManager

'''Interface for elements in the UI. Each element need a an update and draw method.'''
class Element:
    def __init__(self,
                 display_name: str,
                 basic_ui: bool = True,
                 options: list = [],
                 key_options: list = [],
                 basic_action: callable = None,
                 basic_open: bool = True
                 ):
        self.display_name = display_name
        self.basic_ui = basic_ui
        self.options = options
        self.key_options = key_options
        self.basic_action = basic_action
        self.basic_open = basic_open

    def get_display_name(self) -> str:
        return self.display_name

    def is_basic_ui(self) -> bool:
        return self.basic_ui

    def get_options(self) -> list:
        return self.options

    def get_key_options(self) -> list:
        return self.key_options

    def launch(self, sound_manager: SoundManager=None):
        if self.is_basic_ui() and self.basic_action is not None:
            self.basic_action()

    def update(self, sound_manager: SoundManager=None):
        '''
        Method to update the actions that are happening

        Parameters:
            sound_manager (SoundManager): The sound manager to use for playing sounds.

        Returns:
            False if the element is still active, True if it should close.
        '''
        pass

    def draw(self, global_color, x, y, width, height):
        pass

    def close(self):
        pass

    def __str__(self) -> str:
        return self.get_display_name()
