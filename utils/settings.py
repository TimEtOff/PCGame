import pyxel

from utils.element import Element
from utils.sound_manager import SoundManager

class Settings(Element):
    def __init__(self):
        super().__init__("Settings")
        self.__init_variables()
        self.update_options()

    def update_options(self):
        options = []
        #*
        screen_mode_str = ""
        match self.screen_mode:
            case 0:
                screen_mode_str = "Normal"
            case 1:
                screen_mode_str = "Antialisaing"
            case 2:
                screen_mode_str = "Cathod VHS (Default)"
        options.append(Element("Screen mode: " + screen_mode_str, basic_action=self.toggle_screen_mode, basic_open=False))

        self.options = options

    def __init_variables(self):
        self.screen_width = 512
        self.screen_height = 288
        self.fps = 24
        self.fullscreen = False
        self.sdm = SoundManager()
        self.screen_mode = 2

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        pyxel.fullscreen(self.fullscreen)

    def toggle_screen_mode(self, mode=None):
        if mode == None:
            if self.screen_mode == 2:
                mode = 0
            else:
                mode = self.screen_mode + 1
        self.screen_mode = mode
        pyxel.screen_mode(self.screen_mode)

    def update(self, sound_manager = None):
        res = super().update(sound_manager)
        self.update_options()
        return res
