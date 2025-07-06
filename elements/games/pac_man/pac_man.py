import pyxel

class Pac_man:

    def __init__(self, launch_coords):
        self.i = launch_coords[0]
        self.j = launch_coords[1]
        self.R = True
        self.L = False
        self.U = False
        self.D = False
        self.angle = 0
        self.last_angle = None
        self.lives = 3
        self.color = 10
        self.immunity = False
        self.immunity_time = 0
        #pyxel.image[0].rect(16, 16, 8, 8, 0)

    def affiche(self, start_x, start_y):
        if self.angle == 0:
            u = 0
            w, h = 8, 8
        elif self.angle == 90:
            u = 16
            w, h = 8, 8
        elif self.angle == 180:
            u = 0
            w, h = -8, -8
        elif self.angle == -90:
            u = 16
            w, h = -8, -8

        r = [0, 1]
        if pyxel.frame_count%int((2*24)/10) not in r:
            u += 8

        v = 0
        r += [2,3,4]
        if self.immunity and pyxel.frame_count%int((3*24)/10) in r:
            v = 8
        elif self.lives == 2:
            v = 48
        elif self.lives <= 1:
            v = 56

        pyxel.blt(start_x+self.j*8, start_y+self.i*8, 0, u, v, w, h, 0)

        #pyxel.circ(self.j*8+4, self.i*8+4, 3, self.color)
        #pyxel.text(180, 250, f"Lives : {self.lives}", 7)

    def move(self, laby):
        if self.immunity_time > 0:
            self.immunity_time -= 1
            if self.immunity_time%2 == 0:
                self.color = 10
            else:
                self.color = 7

        if self.immunity_time == 0:
            self.immunity = False
            self.color = 10

        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.set_R(True)
            self.set_L(False)
            self.set_D(False)
            self.set_U(False)
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_Q):
            self.set_R(False)
            self.set_L(True)
            self.set_D(False)
            self.set_U(False)
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_Z):
            self.set_R(False)
            self.set_L(False)
            self.set_D(False)
            self.set_U(True)
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            self.set_R(False)
            self.set_L(False)
            self.set_D(True)
            self.set_U(False)

        dont_go = [1, 4]
        tped = False
        other_coords = None

        if self.R:
            for tp in laby.infos["tps"]:
                if self.i == tp[1][0] and self.j == tp[1][1]:
                    self.j = tp[0][1]
                    tped = True

            if not tped and self.j < len(laby.get_grille()[0]):
                if laby.get_case((self.i,self.j+1)) not in dont_go:
                    self.j += 1
                elif laby.get_case((self.i-1,self.j+1)) not in dont_go: # -90
                    other_coords = (self.i-1, self.j)
                    self.i -= 1
                    self.j += 1
                elif laby.get_case((self.i+1,self.j+1)) not in dont_go: # 90
                    other_coords = (self.i+1, self.j)
                    self.i += 1
                    self.j += 1

        elif self.L:
            for tp in laby.infos["tps"]:
                if self.i == tp[0][0] and self.j == tp[0][1]:
                    self.j = tp[1][1]

            if not tped and self.j > 0:
                if laby.get_case((self.i,self.j-1)) not in dont_go:
                    self.j -= 1
                elif laby.get_case((self.i-1,self.j-1)) not in dont_go: # -90
                    other_coords = (self.i-1, self.j)
                    self.i -= 1
                    self.j -= 1
                elif laby.get_case((self.i+1,self.j-1)) not in dont_go: # 90
                    other_coords = (self.i+1, self.j)
                    self.i += 1
                    self.j -= 1

        elif self.D and self.i < len(laby.get_grille()):
            if laby.get_case((self.i+1,self.j)) not in dont_go:
                self.i += 1
            elif laby.get_case((self.i+1,self.j+1)) not in dont_go: # 0
                other_coords = (self.i, self.j+1)
                self.i += 1
                self.j += 1
            elif laby.get_case((self.i+1,self.j-1)) not in dont_go: # 180
                other_coords = (self.i, self.j-1)
                self.i += 1
                self.j -= 1

        elif self.U and self.i > 0:
            if laby.get_case((self.i-1,self.j)) not in dont_go:
                self.i -= 1
            elif laby.get_case((self.i-1,self.j+1)) not in dont_go: # 0
                other_coords = (self.i, self.j+1)
                self.i -= 1
                self.j += 1
            elif laby.get_case((self.i-1,self.j-1)) not in dont_go: # 180
                other_coords = (self.i, self.j-1)
                self.i -= 1
                self.j -= 1

        return (self.get_coords(), other_coords)

    def get_hit(self):
        if not self.immunity:
            self.lives -= 1
            self.color = 7
            self.immunity = True
            self.immunity_time = 30
        return self.lives

    def set_U(self, U):
        self.U = U
        if U:
            self.change_angle(-90)

    def set_L(self, L):
        self.L = L
        if L:
            self.change_angle(180)

    def set_R(self, R):
        self.R = R
        if R:
            self.change_angle(0)

    def set_D(self, D):
        self.D = D
        if D:
            self.change_angle(90)

    def change_angle(self, angle):
        if self.angle != angle:
            self.last_angle = self.angle
            self.angle = angle

    def set_coords(self, coords):
        self.i = coords[0]
        self.j = coords[1]

    def get_coords(self):
        return (self.i, self.j)

