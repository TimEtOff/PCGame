from element import Element

class Quit(Element):
    def __init__(self):
        super().__init__("Quit", False)

    def update(self, sound_manager=None):
        exit(0)