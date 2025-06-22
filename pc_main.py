import random
import pyxel

from utils.pile_lifo import PileLIFO
from utils.maillon import Maillon
from element import Element
from elements.quit import Quit

class PCMain:
    def __init__(self):

        #* Initialize all global variables
        self.init_globals()

        pyxel.init(self.screen_width, self.screen_height, title="PCGame", fps=self.fps, quit_key=pyxel.KEY_NONE)

        #self.toggle_fullscreen()
        pyxel.mouse(False)
        pyxel.run(self.update, self.draw)

    def init_globals(self):
        #* Pyxel variables
        self.screen_width = 512
        self.screen_height = 288
        self.fps = 24
        self.fullscreen = False
        self.global_color = 3

        #* Main variables
        self.current_selection = 0
        self.current_selection_options = [Element("Option 1"), Element("Option 2"), Element("Quit")]
        self.current_elements = PileLIFO(Maillon(Element("Main", options=[Element("Option 1"), Element("Option 2"), Quit()])))

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        pyxel.fullscreen(self.fullscreen)

    def update(self):
        if pyxel.btnp(pyxel.KEY_F11):
            self.toggle_fullscreen()

        element: Element = self.current_elements.afficher_main()
        print(element.get_display_name())
        if element.is_basic_ui():
            self.current_selection_options = element.get_options()

            if pyxel.btnp(pyxel.KEY_DOWN) and self.current_selection < len(self.current_selection_options):
                self.current_selection += 1
            elif pyxel.btnp(pyxel.KEY_UP) and self.current_selection > 0:
                self.current_selection -= 1
            elif pyxel.btnp(pyxel.KEY_SPACE):
                self.current_elements.empiler(self.current_selection_options[self.current_selection])
            elif pyxel.btnp(pyxel.KEY_BACKSPACE):
                self.current_elements.depiler()

        else:
            self.current_selection, self.current_selection_options = element.update(self.current_selection)

    def draw(self):
        pyxel.cls(0)

        if pyxel.frame_count % (self.fps*random.randint(3, 6)) == 0:
            self.global_color = 11
        else:
            self.global_color = 3


        pyxel.rectb(20, 20, self.screen_width - 40, self.screen_height - 60, self.global_color)

        pyxel.text(20, 10, self.current_elements.affiche(False), self.global_color)

        element: Element = self.current_elements.afficher_main()
        if element.is_basic_ui():
            x, y = 30, 30
            for i in range(len(self.current_selection_options)):
                if i == self.current_selection:
                    pyxel.rect(x-1, y + 10*i -1, 2 + len(self.current_selection_options[i].get_display_name())*4, 9, self.global_color)
                    pyxel.text(x, y + 10*i, self.current_selection_options[i].get_display_name(), 0)
                else:
                    pyxel.text(x, y + 10*i, self.current_selection_options[i].get_display_name(), self.global_color)
        else:
            element.draw(self.global_color)

if __name__ == "__main__":
    PCMain()