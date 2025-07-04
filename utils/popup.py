import pyxel

class Popup:
    def __init__(self, title: str, message: str, option1: str = "OK", option2: str = "Cancel", option1_action=None, option2_action=None):
        """
        Parameters:
            title (str): The title of the popup.
            message (str): The message to display in the popup.
            option1 (str): The text for the first option (default is "OK").
            option2 (str): The text for the second option (default is "Cancel").
            option1_action (callable): The action to perform when the first option is selected (default is None).
            option2_action (callable): The action to perform when the second option is selected (default is None).
        """
        self.title = title
        self.message = [""]
        i = 0
        j = 0
        for c in message:
            if c == "\n":
                i += 1
                j = 0
                self.message.append("")
            else:
                if j < 30:
                    self.message[i] += c
                    j += 1
                else:
                    i += 1
                    j = 0
                    self.message.append(c)

        self.option1 = option1
        self.option2 = option2
        self.option1_action = option1_action
        self.option2_action = option2_action
        self.selection = 0  # 0 when opened, 1 for option1, 2 for option2

    def draw(self, global_color, x, y, width, height):
        """ Draws the popup dialog to the screen.
        Returns:
            None if nothing happened, True if the first option was selected, False if the second option was selected. If an action is defined, it will be executed.
        """
        res = None
        x_leftucorner = x + width//2 - 65
        y_leftucorner = y + height//2 - 35

        pyxel.rectb(x_leftucorner, y_leftucorner, 130, 70, global_color)
        pyxel.rect(x_leftucorner, y_leftucorner, 130, 8, global_color)

        pyxel.text(x_leftucorner + 1, y_leftucorner + 1, self.title, 0)
        for i, line in enumerate(self.message):
            if i < 4:
                pyxel.text(x_leftucorner + 4, y_leftucorner + 12 + i * 8, line, global_color)

        mouse = (pyxel.mouse_x, pyxel.mouse_y)
        coords_option1 = (x_leftucorner + 4, y_leftucorner + 54, 55, 10, len(self.option1)*4)
        coords_option2 = (x_leftucorner + 4 + 65, y_leftucorner + 54, 55, 10, len(self.option1)*4)

        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_RIGHT):
            if self.selection == 1:
                self.selection = 2
            else:
                self.selection = 1

        if self.selection == 1:
            pyxel.rect(coords_option1[0], coords_option1[1], coords_option1[2], coords_option1[3], global_color)
            pyxel.text(coords_option1[0] + 2, coords_option1[1] + 2, self.option1, 0)

            if pyxel.btnp(pyxel.KEY_SPACE):
                res = True
                if self.option1_action != None:
                    self.option1_action()
        else:
            pyxel.rectb(coords_option1[0], coords_option1[1], coords_option1[2], coords_option1[3], global_color)
            pyxel.text(coords_option1[0] + 2, coords_option1[1] + 2, self.option1, global_color)

        if self.selection == 2:
            pyxel.rect(coords_option2[0], coords_option2[1], coords_option2[2], coords_option2[3], global_color)
            pyxel.text(coords_option2[0] + 2, coords_option2[1] + 2, self.option2, 0)

            if pyxel.btnp(pyxel.KEY_SPACE):
                res = False
                if self.option2_action != None:
                    self.option2_action()
        else:
            pyxel.rectb(coords_option2[0], coords_option2[1], coords_option2[2], coords_option2[3], global_color)
            pyxel.text(coords_option2[0] + 2, coords_option2[1] + 2, self.option2, global_color)

        return res
