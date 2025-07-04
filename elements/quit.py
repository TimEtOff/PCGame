from utils.element import Element

class Quit(Element):
    def __init__(self):
        super().__init__("Quit", True, basic_open=False)

    def launch(self):
        super().launch()
        exit(0)