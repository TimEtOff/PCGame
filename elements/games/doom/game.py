import pyxel
from utils.element import Element
from utils.engine.engine import Engine

# TODO Doom-like game
class Doom(Element):
    def __init__(self):
        super().__init__("DOOM.exe", False, key_options=[["[SPACE]", "Shoot"], ["[Z]", "Move forward"], ["[A]", "Turn left"], ["[D]", "turn right"], ["[ESCAPE]", "Exit"]])

    def launch(self, sound_manager):
        res = super().launch()

        pyxel.load("elements/games/doom/assets/doom.pyxres")
        sound_manager.stop_all()

        self.lives = 3
        self.shoot = False
        self.reloading = 0
        self.place = [[1,1,1,1,1,1,1],
                      [1,0,0,1,0,1,1],
                      [1,1,0,0,0,0,1],
                      [1,0,0,1,1,0,1],
                      [1,0,1,0,0,0,1],
                      [1,1,1,1,1,1,1]]
        self.engine = Engine()

        return res

    def update(self, sound_manager = None):
        res = super().update(sound_manager)

        if self.shoot:
            self.shoot = False
            self.reloading = 36

        if self.reloading > 0:
            self.reloading -= 1

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            res = True

        if pyxel.btnp(pyxel.KEY_SPACE) and self.reloading <= 0:
            self.shoot = True
            sound_manager.play_sound(1, 0, reset=True)

        if pyxel.btn(pyxel.KEY_Z):
            self.engine.move_forward(1)
        if pyxel.btn(pyxel.KEY_S):
            self.engine.move_forward(-1)

        turn = 0
        if pyxel.btn(pyxel.KEY_Q):
            turn -= 10
        if pyxel.btn(pyxel.KEY_D):
            turn += 10
        self.engine.turn(turn)

        return res

    def draw_3d(self):
        pass

    def draw(self, global_color, x, y, width, height):
        res = super().draw(global_color, x, y, width, height)

        pyxel.pal(3, global_color)

        if self.reloading > 0:
            pyxel.blt(x + width//2 - 16, y + 50, 0, 32, 24, 32, 32, 0, scale=4)
        else:
            pyxel.blt(x + width//2 - 16, y + 50, 0, 0, 24, 32, 32, 0, scale=4)

        gun_sprite_coords = (x + (width//2 - 16), y + height - 72)

        if self.reloading > 0:
            pyxel.blt(gun_sprite_coords[0], gun_sprite_coords[1], 0, 32, 0, 32, 24, 0, scale=5)
        else:
            pyxel.blt(gun_sprite_coords[0], gun_sprite_coords[1], 0, 0, 0, 32, 24, 0, scale=5)

        pyxel.text(x, y, str(self.engine.player_coords) + ", " + str(self.engine.player_angle), global_color)

        return res
