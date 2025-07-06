from random import choice
import pyxel

sprites = {"Blinky":0, "Inky":16, "Clyde":8, "Pinky":24, "Left":32, "Right":48, "Up":56, "Down":40, "":32}

class Ghost:

    def __init__(self, color, i, j, name):
        self.color = color
        self.i = i
        self.spawn_i = i
        self.j = j
        self.spawn_j = j
        self.R = False
        self.L = False
        self.U = True
        self.D = False
        self.name = name
        self.move_when = 0

    def move(self, laby, pac_man, panic_mode):
        pass

    def get_coords(self):
        return (self.i, self.j)

    def update(self, laby, pac_man, panic_mode):
        if pyxel.frame_count >= self.move_when:
            self.move(laby, pac_man, panic_mode)

            if self.R and self.j < len(laby.get_grille()[0]) and laby.get_grille()[self.i][self.j+1]!=1:
                self.j += 1
            elif self.L and self.j > 0 and laby.get_grille()[self.i][self.j-1]!=1:
                self.j -= 1
            elif self.D and self.i < len(laby.get_grille()) and laby.get_grille()[self.i+1][self.j]!=1:
                self.i += 1
            elif self.U and self.i > 0 and laby.get_grille()[self.i-1][self.j]!=1:
                self.i -= 1

    def affiche(self, pac_man, panic_mode, start_x, start_y):
        #pyxel.rect(self.j*8+1, self.i*8+1, 6, 6, self.color)
        v = 16

        r = [0,1,2,3,4]
        if pyxel.frame_count%int((4*24)/10) in r:
            v += 8
        if panic_mode:
            v += 16

        pyxel.blt(start_x+self.j*8, start_y+self.i*8, 0, sprites[self.name], v, 8, 8, 0)
        orientation = ""

        if self.U:
            orientation = "Up"
        elif self.D:
            orientation = "Down"
        elif self.R:
            orientation = "Right"
        elif self.L:
            orientation = "Left"

        if not panic_mode:
            if pac_man.lives == 2:
                v += 16
            elif pac_man.lives <= 1:
                v += 32

            pyxel.blt(start_x+self.j*8, start_y+self.i*8, 0, sprites[orientation], v, 8, 8, 0)

    def return_to_lobby(self):
        self.i = self.spawn_i
        self.j = self.spawn_j

    def get_hit(self):
        self.return_to_lobby()
        self.move_when = pyxel.frame_count + 70

    def is_straight_path(self, paths):
        res = False
        if len(paths) <= 2:
            if (0, -1, 'L') in paths and (0, 1, 'R') in paths:
                res = True
            elif (-1, 0, 'U') in paths and (1, 0, 'D') in paths:
                res = True
        return res

    def opposite_path(self, path):
        res = None
        if path == (0, -1, 'L'):
            res = (0, 1, 'R')
        elif path == (0, 1, 'R'):
            res = (0, -1, 'L')
        elif path == (-1, 0, 'U'):
            res = (1, 0, 'D')
        elif path == (1, 0, 'D'):
            res = (-1, 0, 'U')
        return res

    def check_paths(self, laby):
        possible_paths = [(0, -1, 'L'), (0, 1, 'R'), (-1, 0, 'U'), (1, 0, 'D')]
        paths = []
        for p in possible_paths:
            try:
                if laby.get_grille()[self.i + p[0]][self.j + p[1]] != 1:
                    paths.append(p)
            except IndexError:
                pass
        return paths

    def apply_dir(self, path):
        if path == 'L':
            self.R = False
            self.L = True
            self.U = False
            self.D = False
        elif path == 'R':
            self.R = True
            self.L = False
            self.U = False
            self.D = False
        elif path == 'U':
            self.R = False
            self.L = False
            self.U = True
            self.D = False
        elif path == 'D':
            self.R = False
            self.L = False
            self.U = False
            self.D = True
        elif path == '':
            self.R = False
            self.L = False
            self.U = False
            self.D = False


class Blinky(Ghost): # Plus court chemin vers Pac-Man

    def __init__(self):
        super().__init__(8, 14, 12, "Blinky")

    def move(self, laby, pac_man, panic_mode):
        x, y = self.get_coords()
        node = laby.get_node((x, y))
        path = 'U'
        for next_node in node.get_to_list():
            if next_node.get_value() < node.get_value() and not panic_mode:
                if next_node.get_id() == (x, y-1):
                    path = 'L'
                elif next_node.get_id() == (x, y+1):
                    path = 'R'
                elif next_node.get_id() == (x-1, y):
                    path = 'U'
                elif next_node.get_id() == (x+1, y):
                    path = 'D'
            elif next_node.get_value() > node.get_value() and panic_mode:
                if next_node.get_id() == (x, y-1):
                    path = 'L'
                elif next_node.get_id() == (x, y+1):
                    path = 'R'
                elif next_node.get_id() == (x-1, y):
                    path = 'U'
                elif next_node.get_id() == (x+1, y):
                    path = 'D'

        self.apply_dir(path)

class Inky(Ghost): # Change aléatoirement à chaque bifurquation

    def __init__(self):
        super().__init__(5, 14, 14, "Inky")
        self.last_paths = [(0, -1, 'L'), (0, 1, 'R'), (-1, 0, 'U'), (1, 0, 'D')]
        self.last_choice = (-1, 0, 'U')

    def move(self, laby, pac_man, panic_mode):
        paths = self.check_paths(laby)

        if self.last_paths != paths and not self.is_straight_path(paths):
            self.last_paths = paths.copy()

            opp_path = self.opposite_path(self.last_choice)
            if opp_path in paths: # Moins de chances de revenir sur ses pas
                paths += paths
                paths.remove(opp_path)

            path = choice(paths)
            self.last_choice = path

            self.apply_dir(path[2])

class Pinky(Ghost): # Se rapproche en vol d'oiseau

    def __init__(self):
        super().__init__(14, 14, 15, "Pinky")

    def move(self, laby, pac_man, panic_mode):
        g_x, g_y = self.get_coords()
        p_x, p_y = pac_man.get_coords()

        x, y = g_x-p_x, g_y-p_y

        if panic_mode:
            x, y = -x, -y

        path = ''
        paths = self.check_paths(laby)

        if x < 0 and (1, 0, 'D') in paths:
            path = 'D'
        elif x > 0 and (-1, 0, 'U') in paths:
            path = 'U'
        elif y < 0 and (0, 1, 'R') in paths:
            path = 'R'
        elif y > 0 and (0, -1, 'L') in paths:
            path = 'L'

        #if x < 0:
        #    path = 'D'
        #elif x > 0:
        #    path = 'U'
        #elif y < 0:
        #    path = 'R'
        #elif y > 0:
        #    path = 'L'

        self.apply_dir(path)

class Clyde(Ghost): # Full aléatoire

    def __init__(self):
        super().__init__(9, 14, 13, "Clyde")

    def move(self, laby, pac_man, panic_mode):
        paths = ['L', 'R', 'U', 'D']
        path = choice(paths)

        self.apply_dir(path)
