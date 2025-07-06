import random
import pyxel

from utils.pile_lifo import PileLIFO
from utils.maillon import Maillon
from utils.sound_manager import SoundManager
from utils.element import Element
from utils.popup import Popup
from utils.settings import Settings
from elements.quit import Quit
from elements.games.pac_man.jeu import JeuPacMan
from elements.games.doom.game import Doom

class PCMain:
    def __init__(self):

        #* Initialize all global variables
        self.init_globals()
        pyxel.init(self.settings.screen_width, self.settings.screen_height, title="PCGame", fps=self.settings.fps, quit_key=pyxel.KEY_NONE)

        self.settings.toggle_fullscreen()
        self.settings.toggle_screen_mode(2)
        pyxel.mouse(False)
        pyxel.load("assets/main.pyxres")
        pyxel.run(self.update, self.draw)

    def init_globals(self):
        #* Pyxel variables
        self.settings = Settings()

        #* Basic UI variables
        self.current_selection = 0
        self.current_selection_options = []

        #* For tests
        def close_popup_action():
            self.current_popup = None

        def close_popup_action2():
            self.current_popup = None
            self.close_element()

        def open_test_popup():
            self.current_popup = Popup("Test Popup", "This is a test popup message.\nIt can span multiple lines.", "OK", "Cancel", option1_action=close_popup_action, option2_action=close_popup_action2)

        options=[Element("Games", options=[JeuPacMan(), Doom()]), Element("Documents", options=[Element("Ideas.docx"), Element("Tests.docx")]), Element("Trojan.exe")]
        #*

        self.current_elements = PileLIFO(Maillon(Element("Main", options=[Element("Files", basic_action=open_test_popup, options=options), self.settings, Quit()])))
        self.current_key_options = []
        self.current_popup = None

        self.__basic_ui_key_options = [("[UP]", "Move up"), ("[DOWN]", "Move down"), ("[SPACE]", "Select option"), ("[BACKSPACE]", "Go back")]

        #* Draw variables
        self.global_color = 3
        self.draw_x = 20
        self.draw_y = 20
        self.draw_width = self.settings.screen_width - (2 * self.draw_x)
        self.draw_height = self.settings.screen_height - (3 * self.draw_y)

# TODO When basic_ui, make the selection smarter (depends on the number of elements available and if opening or closing)
    def update(self):
        if pyxel.btnp(pyxel.KEY_F11):
            self.settings.toggle_fullscreen()

        self.settings.sdm.update_channels()

        element: Element = self.current_elements.afficher_main()
        if self.current_popup is None:
            if element.is_basic_ui():
                self.settings.sdm.play_sound(0, 2, loop=True, priority=False)

                self.current_selection_options = element.get_options()
                self.current_key_options = self.__basic_ui_key_options

                if pyxel.btnp(pyxel.KEY_DOWN) and self.current_selection < len(self.current_selection_options)-1:
                    self.current_selection += 1
                    self.settings.sdm.play_sound(1, 3, reset=True)
                elif pyxel.btnp(pyxel.KEY_UP) and self.current_selection > 0:
                    self.current_selection -= 1
                    self.settings.sdm.play_sound(1, 3, reset=True)
                elif pyxel.btnp(pyxel.KEY_SPACE) and self.current_selection < len(self.current_selection_options):
                    self.open_element(self.current_selection_options[self.current_selection])
                elif pyxel.btnp(pyxel.KEY_BACKSPACE) and self.current_elements.taille() > 1:
                    self.close_element()

                element.update(sound_manager=self.settings.sdm)

            else:
                self.current_selection = 0
                self.current_selection_options = []
                self.current_key_options = element.get_key_options()
                element_quit = element.update(sound_manager=self.settings.sdm)
                if element_quit:
                    self.close_element()

    def draw(self):
        pyxel.pal()
        pyxel.cls(0)

        if pyxel.frame_count % (self.settings.fps*random.randint(2, 5)) == 0:
            self.global_color = 11
        else:
            self.global_color = 3


        pyxel.rectb(self.draw_x, self.draw_y, self.draw_width, self.draw_height, self.global_color)

        pyxel.text(self.draw_x, self.draw_y - 10, self.current_elements.affiche(False), self.global_color)

        self.draw_key_options()

        element: Element = self.current_elements.afficher_main()
        if element.is_basic_ui():
            x, y = self.draw_x + 10, self.draw_y + 10
            for i in range(len(self.current_selection_options)):
                if i == self.current_selection:
                    pyxel.rect(x-1, y + 10*i -1, 2 + len(self.current_selection_options[i].get_display_name())*4, 9, self.global_color)
                    pyxel.text(x, y + 10*i, self.current_selection_options[i].get_display_name(), 0)
                else:
                    pyxel.text(x, y + 10*i, self.current_selection_options[i].get_display_name(), self.global_color)
        else:
            element.draw(self.global_color, self.draw_x, self.draw_y, self.draw_width, self.draw_height)

        if self.current_popup is not None:
            self.current_popup.draw(self.global_color, self.draw_x, self.draw_y, self.draw_width, self.draw_height)

    def draw_key_options(self):
        x, y = self.draw_x, self.draw_y + self.draw_height + 5
        lines = 1
        for key, description in self.current_key_options:
            text = f"{key} {description} | "

            if x + len(text) * 4 > self.draw_x + self.draw_width:
                x = self.draw_x
                y += 8
                lines += 1

            if lines <= 4:
                pyxel.text(x, y, text, self.global_color)
                x += len(text) * 4

        pyxel.text(x, y, "[F11] Toggle Fullscreen", self.global_color)

    def open_element(self, element: Element):
        self.settings.sdm.play_sound(1, 0, reset=True)
        self.settings.sdm.stop_sound(0)
        self.current_elements.empiler(element)
        self.current_elements.afficher_main().launch(self.settings.sdm)
        if not self.current_elements.afficher_main().basic_open:
            self.close_element(no_sound=True)

    def close_element(self, no_sound=False):
        self.current_elements.afficher_main().close()
        self.current_elements.depiler()
        pyxel.load("assets/main.pyxres")
        if not no_sound:
            self.settings.sdm.play_sound(1, 1, reset=True)

if __name__ == "__main__":
    PCMain()