import pyxel
import csv
import random

from utils.element import Element

from elements.pac_man.ghost import *
from elements.pac_man.pac_man import *
from elements.pac_man.labyrinthe import *

#* Sounds doc
# Ch 0: Music
# Ch 1: Waka waka
# Ch 2: SFX
#
# Sd 0: Music intro
# Sd 1: Konami code
# Sd 2: Waka
# Sd 3: Up
# Sd 4: Damage
# Sd 5: Level Up

#fullscreen = True

death_anim_coords = {"Blinky": (0, 32), "Inky": (0, 64), "Clyde": (0, 128), "Pinky": (0, 96), "PacMan0": (0, 0), "PacMan1": (32, 0), "PacMan2": (64, 0)}
konami_code = [pyxel.KEY_UP, pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_B, pyxel.KEY_A]
konami_code_index = 0


class Jeu:

    def __init__(self, labys):

        #pyxel.init(224, 258, title="Pac-man", fps = 10)
        #pyxel.fullscreen(fullscreen)

        self.levels_laby = labys
        self.level = 0
        self.game = False
        self.game_over = False
        self.menu = True
        self.menu_sel = 0
        self.leaderboard_menu = False
        self.difficulty = 1

        self.leaderboard = []
        with open("elements/pac_man/assets/leaderboard.csv", "r", newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    self.leaderboard.append({"name":row[0], "score":int(row[1]), "level":row[2], "diff":row[3]})

        # Lancement du jeu
        pyxel.load("elements/pac_man/assets/sprites.pyxres")
        #pyxel.run(self.update, self.draw)

    def launch_game(self, laby, init=False):
        # création du labyrinthe
        self.L = Lab(laby)

        if init:
            pyxel.play(0, 0, loop=False)

            self.pac_man = Pac_man(self.L.infos["pac_coords"])

            self.ghosts = [Blinky(), Inky(), Clyde(), Pinky()]

            self.start_frame = pyxel.frame_count + 45
        else:
            self.start_frame = pyxel.frame_count + 15

        self.pac_man.set_coords(self.L.infos["pac_coords"])
        for g in self.ghosts:
            g.return_to_lobby()

        self.pac_man.set_R(True)
        self.pac_man.set_L(False)
        self.pac_man.set_U(False)
        self.pac_man.set_D(False)

        if init:
            self.score = 0
            self.level = 0
            self.panic_mode = False
            self.panic_time = 100
            self.game_over = False
            self.menu = False
            self.leaderboard_menu = False
            self.murderer = None
            self.death_frame = 0
            self.save_sel = 0
            self.name = "___"
            self.saved = False
            self.check = []
            self.debug = False

    def get_ghosts_coords(self):
        res = []
        ghosts = []
        for g in self.ghosts:
            res.append((g.i, g.j))
            ghosts.append(g)
        return res, ghosts

    def check_hit(self):
        check = self.check.copy()
        self.check = []

        pac_coords = self.pac_man.get_coords()
        other_coords = None
        if pyxel.frame_count > self.start_frame:
            pac_coords, other_coords = self.pac_man.move(self.L)

        self.L.update_graph(pac_coords)

        ghosts_coords, ghosts = self.get_ghosts_coords()

        for checking_coords in [pac_coords] + check:
            if ghosts_coords != None and checking_coords in ghosts_coords:
                if self.panic_mode:
                    pyxel.play(2, 3, loop=False)
                    ghosts[ghosts_coords.index(checking_coords)].get_hit()
                    self.score += 1000
                else:
                    if not self.pac_man.immunity:
                        pyxel.play(2, 4, loop=False)
                    lives = self.pac_man.get_hit()
                    if self.difficulty == 3 or lives <= 0:
                        self.murderer = ghosts[ghosts_coords.index(checking_coords)]
                        self.game = False
                        self.game_over = True
                        self.death_frame = pyxel.frame_count

        may_check = [
            [(pac_coords[0]-1, pac_coords[1]), (pac_coords[0]-2, pac_coords[1])],
            [(pac_coords[0]+1, pac_coords[1]), (pac_coords[0]+2, pac_coords[1])],
            [(pac_coords[0], pac_coords[1]-1), (pac_coords[0], pac_coords[1]-2)],
            [(pac_coords[0], pac_coords[1]+1), (pac_coords[0], pac_coords[1]+2)]
        ]
        i = 0
        for coords in [
            (pac_coords[0]-1, pac_coords[1]),
            (pac_coords[0]+1, pac_coords[1]),
            (pac_coords[0], pac_coords[1]-1),
            (pac_coords[0], pac_coords[1]+1)
            ]:
            if ghosts_coords != None and coords in ghosts_coords: # FIXME Marche pas forcément tout le temps ^^'
                if i != 0:
                    for ch_coords in may_check[0]:
                        if ch_coords not in self.check:
                            self.check.append(ch_coords)
                elif i != 1:
                    for ch_coords in may_check[1]:
                        if ch_coords not in self.check:
                            self.check.append(ch_coords)
                elif i != 2:
                    for ch_coords in may_check[2]:
                        if ch_coords not in self.check:
                            self.check.append(ch_coords)
                elif i != 3:
                    for ch_coords in may_check[3]:
                        if ch_coords not in self.check:
                            self.check.append(ch_coords)
            i += 1


        for coords in [pac_coords, other_coords]:
            if coords != None:
                value = self.L.get_case(coords)
                match value:
                    case 2:
                        if pyxel.frame_count%3 == 0:
                            pyxel.play(1, 2, loop=False)
                        self.score += 10
                        self.L.set_num_gum(self.L.get_num_gum_quick() - 1)
                    case 3:
                        pyxel.play(2, 3, loop=False)
                        if self.difficulty != 2:
                            self.panic_mode = True
                            self.panic_time = 100

                self.L.set_case(coords, 0)

    def update(self):
        global fullscreen

        #if pyxel.btnp(pyxel.KEY_F11):
        #    fullscreen = not fullscreen
        #    pyxel.fullscreen(fullscreen)

        if self.game:
            ghost_move=[3,2,2,1]
            if pyxel.frame_count > self.start_frame + 25 and pyxel.frame_count%int((ghost_move[self.difficulty]*24)/10) == 0:
                for g in self.ghosts:
                    g.update(self.L, self.pac_man, self.panic_mode)
            self.check_hit()

            if self.panic_mode:
                if self.panic_time == 0:
                    self.panic_mode = False
                    self.panic_time = 100
                else:
                    self.panic_time -= 1

            if pyxel.btnp(pyxel.KEY_M):
                self.debug = True

            if self.debug:
                if pyxel.btnp(pyxel.KEY_L): # Reset la map -> Niveau suivant
                    self.L.set_num_gum(0)
                if pyxel.btnp(pyxel.KEY_P):
                    self.panic_mode = not self.panic_mode
                    self.panic_time = 10000 if self.panic_mode else 0
                if pyxel.btnp(pyxel.KEY_K):
                    self.L.sprites = self.L.sprites + 1 if self.L.sprites < 5 else 0
                if pyxel.btnp(pyxel.KEY_O):
                    self.pac_man.lives = self.pac_man.lives - 1 if self.pac_man.lives > 1 else 3

            if pyxel.btnp(pyxel.KEY_BACKSPACE):
                self.goto_menu()

            if self.L.is_cleared():
                pyxel.play(2, 5, loop=False)
                self.level += 1
                self.launch_game(self.levels_laby[self.level%len(self.levels_laby)])

        elif konami_code_index == len(konami_code):
            if pyxel.frame_count > self.start_frame and pyxel.frame_count < self.start_frame + 50:
                self.pac_man.move(self.L)

    def draw(self, start_x, start_y, base_x):
        #pyxel.cls(0)

        self.show_leaderboard(20, base_x+15, start_y+10)
        if not self.leaderboard_menu:
            self.show_leaderboard(20, base_x+360, start_y+10, start=20, label=False)

        if self.game:
            self.L.affiche(self.pac_man, self.panic_mode, self.panic_time, self.difficulty, start_x, start_y)

            self.pac_man.affiche(start_x, start_y)

            for g in self.ghosts:
                g.affiche(self.pac_man, self.panic_mode, start_x, start_y)

            pyxel.text(start_x+4, start_y+250, f"High score : {self.leaderboard[0]['score']}", 13)
            pyxel.text(start_x+90, start_y+250, f"Score : {self.score}", 7)
            pyxel.text(start_x+150, start_y+250, f"Level : {self.level}", 13)

            if self.debug:
                pyxel.rect(start_x+0, start_y+238, 25, 9, 11)
                pyxel.text(start_x+3, start_y+240, "DEBUG", 0)

                pyxel.rect(start_x+25, start_y+240, 200, 7, 11)
                pyxel.line(start_x+0, start_y+247, start_x+224, start_y+247, 3)
                pyxel.text(start_x+28, start_y+241, "[L]:Level Up", 0)
                pyxel.text(start_x+82, start_y+241, "[K]:Colors", 0)
                pyxel.text(start_x+130, start_y+241, "[P]:Panic", 0)
                pyxel.text(start_x+175, start_y+241, "[O]:Life", 0)

            if pyxel.frame_count <= self.start_frame+25:
                pyxel.text(start_x+12*8, start_y+13*8, "LEVEL " + str(self.level), 10)
                pyxel.text(start_x+11*8, start_y+15*8, "SCORE " + str(self.score), 10)

            x = 225
            n = self.pac_man.lives
            if self.difficulty == 3:
                n = 1
            for i in range(n):
                x = x-10
                #pyxel.circ(x, 252, 3, 10)
                pyxel.blt(start_x+x, start_y+249, 0, 0, 0, 8, 8, 0)
            self.color = 10

        elif self.game_over:
            self.death_anim(start_x, start_y)

        elif self.menu:
            self.menu_screen(start_x, start_y)

        elif self.leaderboard_menu:
            self.show_leaderboard(20, base_x+120, start_y+10, start=20, label=False)
            self.show_leaderboard(20, base_x+240, start_y+10, start=40, label=False)
            pyxel.text(start_x+57, start_y+230, "Press [SPACE] to go back", 13)
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.leaderboard_menu = False
                self.menu = True

        else:
            self.L.affiche(self.pac_man, self.panic_mode, self.panic_time, self.difficulty)
            self.L.sprites = random.randint(0, 5)

            self.pac_man.affiche()

            if pyxel.frame_count >= self.start_frame + 40:
                pyxel.text(start_x+69, start_y+170, "YOU SHOULDN'T BE THERE", pyxel.frame_count%2+1)
            if pyxel.frame_count >= self.start_frame + 50:
                pyxel.blt(start_x+90, start_y+90, 1, 0, 168, 16, 16, 0)
                pyxel.blt(start_x+115, start_y+90, 1, 16, 168, 16, 16, 0)
            if pyxel.frame_count >= self.start_frame + 51:
                pyxel.blt(start_x+80, start_y+130, 1, 0, 184, 16, 16, 0)
                pyxel.blt(start_x+125, start_y+130, 1, 16, 184, 16, 16, 0)
            if pyxel.frame_count >= self.start_frame + 52:
                pyxel.cls(7)
            if pyxel.frame_count >= self.start_frame + 53:
                exit(0)

    def death_anim(self, start_x, start_y):
        ghost_coords = (start_y+96, start_x+10+(pyxel.frame_count - self.death_frame)*12)
        pac_coords = (start_y+96, start_x+161)

        pyxel.blt(ghost_coords[1], ghost_coords[0], 1, death_anim_coords[self.murderer.name][0], death_anim_coords[self.murderer.name][1], 32, 32, 0)

        pac_man_sprite = ""
        if pyxel.frame_count - self.death_frame <= 10:
            pac_man_sprite = "PacMan0"
        elif pyxel.frame_count - self.death_frame <= 20:
            pac_man_sprite = "PacMan1"
        else:
            pac_man_sprite = "PacMan2"

        pyxel.blt(pac_coords[1], pac_coords[0], 1, death_anim_coords[pac_man_sprite][0], death_anim_coords[pac_man_sprite][1], 32, 32, 0)

        self.score_save_screen(start_x, start_y)

    def name_entering(self):
        for i in range(97, 123): # 97: KEY_A | 122: KEY_Z
                if pyxel.btn(i):
                    if self.name == "___":
                        self.name = chr(i-32) + "__"
                    elif self.name.endswith("__"):
                        self.name = self.name.rstrip("__") + chr(i-32) + "_"
                    elif self.name.endswith("_"):
                        self.name = self.name.rstrip("_") + chr(i-32)

        if pyxel.btn(pyxel.KEY_BACKSPACE):
            if self.name == "___":
                pass
            elif self.name.endswith("__"):
                self.name = "___"
            elif self.name.endswith("_"):
                self.name = self.name[0] + "__"
            else:
                self.name = self.name[0] + self.name[1] + "_"

    def menu_screen(self, start_x, start_y):
        global konami_code, konami_code_index

        sel = ["nothing", "launch", "difficulty", "leaderboard"]
        colors = {"launch": 7, "difficulty": 7, "leaderboard": 7}
        r = [0,1,2,3,4,5,6,7,8,9]
        if pyxel.frame_count%int((8*24)/10) in r:
            colors[sel[self.menu_sel]] = 10
        else:
            colors[sel[self.menu_sel]] = 0

        if pyxel.btnr(konami_code[konami_code_index]):
            konami_code_index += 1
            if konami_code_index == len(konami_code):
                pyxel.play(2, 1, loop=True)
                self.menu = False
                self.start_frame = pyxel.frame_count
                self.launch_game(laby_wth, True)

        if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            if self.menu_sel < 3:
                self.menu_sel += 1
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_Z):
            if self.menu_sel > 0:
                self.menu_sel -= 1

        if sel[self.menu_sel] == "launch":
            if pyxel.btnp(pyxel.KEY_SPACE):
                konami_code_index = 0
                self.game = True
                self.launch_game(self.levels_laby[0], True)

        elif sel[self.menu_sel] == "difficulty":
            if pyxel.btnp(pyxel.KEY_SPACE):
                konami_code_index = 0
                if self.difficulty == 3:
                    self.difficulty = 0
                else:
                    self.difficulty += 1

        elif sel[self.menu_sel] == "leaderboard":
            if pyxel.btnp(pyxel.KEY_SPACE):
                konami_code_index = 0
                self.menu = False
                self.leaderboard_menu = True

        pyxel.text(start_x+90, start_y+50, "PAC-MAN", 10)
        pyxel.text(start_x+90, start_y+60, "by Tim&O", 10)

        difficulties = ["EASY", "MEDIUM", "HARD (No SupGum)", "INSANE (1PV)"]
        pyxel.text(start_x+95, start_y+135, "Launch", colors["launch"])
        pyxel.text(start_x+87, start_y+155, "Difficulty", colors["difficulty"])
        pyxel.text(start_x+95, start_y+165, difficulties[self.difficulty], colors["difficulty"])
        pyxel.text(start_x+87, start_y+185, "Leaderboard", colors["leaderboard"])

        pyxel.text(start_x+60, start_y+230, "Press [SPACE] to continue", 13)
        pyxel.text(start_x+35, start_y+240, "Press [ARROW KEYS] to change selection", 13)
        pyxel.text(start_x+50, start_y+250, "Press [ESCAPE] to quit anytime", 13)

    def goto_menu(self):
        self.menu = True
        self.game = False
        self.game_over = False
        self.leaderboard_menu = False
        pyxel.stop(0)
        pyxel.stop(1)

    def score_save_screen(self, start_x, start_y):
        sel = ["name", "save", "menu"]
        colors = {"name": 7, "save": 7, "menu": 7}
        r = [0,1,2,3]
        if pyxel.frame_count%8 in r:
            colors[sel[self.save_sel]] = 10
        else:
            colors[sel[self.save_sel]] = 0
        if self.saved or self.debug:
            colors["save"] = 13

        if pyxel.btnp(pyxel.KEY_DOWN) or (pyxel.btnp(pyxel.KEY_S) and not self.save_sel == 0):
            if self.save_sel < 2:
                self.save_sel += 1
        if pyxel.btnp(pyxel.KEY_UP) or (pyxel.btnp(pyxel.KEY_Z) and not self.save_sel == 0):
            if self.save_sel > 0:
                self.save_sel -= 1

        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.goto_menu()

        if sel[self.save_sel] == "name":
            self.name_entering()
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.save_sel += 1

        elif sel[self.save_sel] == "save":
            if pyxel.btnp(pyxel.KEY_SPACE) and not self.saved and not self.debug:
                self.save_csv()

        elif sel[self.save_sel] == "menu":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.game_over = False
                self.menu = True

        pyxel.text(start_x+103, start_y+155, self.name, colors["name"])
        pyxel.text(start_x+103-2*(len(str(self.score))/2)+1, start_y+165, str(self.score), colors["name"])
        pyxel.text(start_x+100, start_y+185, "Save", colors["save"])
        pyxel.text(start_x+100, start_y+205, "Menu", colors["menu"])

        self.show_leaderboard(5, start_x+65, start_y+15)

        pyxel.text(start_x+60, start_y+230, "Press [SPACE] to continue", 13)
        pyxel.text(start_x+35, start_y+240, "Press [ARROW KEYS] to change selection", 13)

    def show_leaderboard(self, n_items, x, y, start=0, label=True):
        if label:
            pyxel.text(x+5, y, "LEADERBOARD", 9)
        for i in range(start, start+n_items):
            if not (i > len(self.leaderboard)-1):
                place = str(i+1)
                if len(place) == 1:
                    place = "0" + place
                #pyxel.text(x, y+10 +10*i - 10*start, place + " " +
                #           self.leaderboard[i]["name"] + "  " +
                #           str(self.leaderboard[i]["score"]) + "  " +
                #           self.leaderboard[i]["level"] + "  " +
                #           self.leaderboard[i]["diff"],
                #           9)
                pyxel.text(x, y+10 +10*i - 10*start,
                           "{place:<2} {name:<3}  {score:>6}  {level:<5} {diff:>1}".format(
                               place = place,
                               name  = self.leaderboard[i]["name"],
                               score = str(self.leaderboard[i]["score"]),
                               level = self.leaderboard[i]["level"],
                               diff  = self.leaderboard[i]["diff"]
                               ), 9)

    def sort_leaderboard(self):
        n=len(self.leaderboard)
        for i in range(n):
            indMin=i
            for j in range(indMin, n):
                if self.leaderboard[j]["score"]>self.leaderboard[indMin]["score"]:
                    indMin=j
            temp=self.leaderboard[indMin]
            self.leaderboard[indMin]=self.leaderboard[i]
            self.leaderboard[i]=temp
        return self.leaderboard

    def save_csv(self):
        diffs = ["E","M","H","I"]
        self.leaderboard.append({"name":self.name, "score":self.score, "level":"LVL"+str(self.level), "diff":diffs[self.difficulty]})
        self.sort_leaderboard()
        with open("assets/leaderboard.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in self.leaderboard:
                writer.writerow([row["name"], row["score"], row["level"], row["diff"]])
        self.saved = True

# Initialisation des niveaux, voir 'labys.docx'
laby_pacman = {"laby":[
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
[1,3,1,0,0,1,2,1,0,0,0,1,2,1,1,2,1,0,0,0,1,2,1,0,0,1,3,1],
[1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
[1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
[1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
[0,0,0,0,0,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,0,0,0,0,0],
[0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
[0,0,0,0,0,1,2,1,1,0,1,1,4,4,4,4,1,1,0,1,1,2,1,0,0,0,0,0],
[1,1,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,1,1],
[0,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,1,0,0,0,2,0,0,0,0,0,0],
[1,1,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,1,1],
[0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
[0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
[0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
[1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
[1,3,2,2,1,1,2,2,2,2,2,2,2,0,0,2,2,2,2,2,2,2,1,1,2,2,3,1],
[1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
[1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
[1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
[1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
[1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],
"pac_coords":(14, 3), "tps":[((14, 0), (14, 27))]}

laby_ms_pacman_1 = {"laby":[
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,1],
[1,3,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1,1,1,3,1],
[1,2,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1,1,1,2,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,1,1,1,2,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,2,1,1,1,1],
[0,0,0,1,2,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,2,1,0,0,0],
[1,1,1,1,2,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,2,1,1,1,1],
[0,0,0,0,2,1,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,1,2,0,0,0,0],
[1,1,1,1,2,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,2,1,1,1,1],
[0,0,0,1,2,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,2,1,0,0,0],
[0,0,0,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,0,0,0],
[0,0,0,1,2,1,1,1,1,0,1,1,4,4,4,4,1,1,0,1,1,1,1,2,1,0,0,0],
[0,0,0,1,2,1,1,1,1,0,1,0,0,0,0,0,0,1,0,1,1,1,1,2,1,0,0,0],
[0,0,0,1,2,1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,2,1,0,0,0],
[0,0,0,1,2,1,0,1,1,0,1,0,0,0,0,0,0,1,0,1,1,0,1,2,1,0,0,0],
[1,1,1,1,2,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,2,1,1,1,1],
[0,0,0,0,2,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,2,0,0,0,0],
[1,1,1,1,2,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,2,1,1,1,1],
[0,0,0,1,2,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,2,1,0,0,0],
[0,0,0,1,2,2,2,2,2,2,0,0,1,1,1,1,0,0,2,2,2,2,2,2,1,0,0,0],
[1,1,1,1,2,1,1,1,1,2,1,1,1,1,1,1,1,1,2,1,1,1,1,2,1,1,1,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
[1,3,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,3,1],
[1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],
"pac_coords":(17, 2), "tps":[((8, 0), (8, 27)), ((17, 0), (17, 27))]}

laby_ms_pacman_2 = {"laby":[
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[0,0,0,0,0,0,2,1,2,2,2,2,2,2,2,2,2,2,2,2,1,2,0,0,0,0,0,0],
[1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1],
[1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,2,1],
[1,3,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,3,1],
[1,2,1,1,2,2,2,2,2,2,1,1,2,1,1,2,1,1,2,2,2,2,2,2,1,1,2,1],
[1,2,1,1,2,1,1,1,1,0,1,1,2,2,2,2,1,1,0,1,1,1,1,2,1,1,2,1],
[1,2,1,1,2,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,2,1,1,2,1],
[1,2,2,2,2,2,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,2,2,2,2,2,1],
[1,1,1,1,1,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,1,1,1,1],
[1,1,1,1,1,1,2,1,1,0,1,1,4,4,4,4,1,1,0,1,1,2,1,1,1,1,1,1],
[1,2,2,2,2,2,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,2,2,2,2,2,1],
[1,2,1,1,1,1,2,0,0,0,1,0,0,0,0,0,0,1,0,0,0,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,2,1],
[1,2,2,2,2,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,2,2,2,2,1],
[1,1,1,1,2,1,2,1,1,1,1,0,1,1,1,1,0,1,1,1,1,2,1,2,1,1,1,1],
[0,0,0,1,2,1,2,1,1,1,1,0,1,1,1,1,0,1,1,1,1,2,1,2,1,0,0,0],
[0,0,0,1,2,2,2,2,2,2,2,2,1,1,1,1,2,2,2,2,2,2,2,2,1,0,0,0],
[1,1,1,1,2,1,1,1,1,1,1,2,1,1,1,1,2,1,1,1,1,1,1,2,1,1,1,1],
[0,0,0,0,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1,1,2,2,2,2,0,0,0,0],
[1,1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1,1],
[1,1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1,1],
[1,2,2,2,2,1,1,2,2,2,2,2,2,1,1,2,2,2,2,2,2,1,1,2,2,2,2,1],
[1,2,1,1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,1,1,1,2,1],
[1,3,1,1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,1,1,1,3,1],
[1,2,1,1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,1,1,1,2,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],
"pac_coords":(1, 2), "tps":[((1, 0), (1, 27)), ((22, 0), (22, 27))]}

laby_ms_pacman_3 = {"laby":[
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,2,1],
[1,3,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,3,1],
[1,2,1,1,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,1,1,2,1],
[1,2,1,1,2,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,2,1,1,2,1],
[1,2,2,2,2,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,2,2,2,2,1],
[1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1],
[1,1,1,1,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,1,1,1,1],
[0,2,2,2,2,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,2,2,2,2,0],
[1,2,1,1,2,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,2,1,1,2,1],
[1,2,1,1,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,1,1,2,1],
[1,2,1,1,1,1,2,1,1,0,1,1,4,4,4,4,1,1,0,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,2,1],
[1,2,2,2,2,2,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,2,2,2,2,2,1],
[1,2,1,1,2,1,1,1,1,0,1,0,0,0,0,0,0,1,0,1,1,1,1,2,1,1,2,1],
[1,2,1,1,2,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,2,1,1,2,1],
[1,2,1,1,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,1,1,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,2,1],
[1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
[1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
[1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
[1,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
[1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
[1,2,2,3,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,3,2,2,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],
"pac_coords":(14,2), "tps":[((9, 0), (9, 27))]}

laby_ms_pacman_4 = {"laby":[
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,2,1,1,1,1,2,1,1,1,1,1,1,1,1,2,1,1,1,1,2,1,1,2,1],
[1,2,1,1,2,1,1,1,1,2,1,1,1,1,1,1,1,1,2,1,1,1,1,2,1,1,2,1],
[1,3,1,1,2,1,1,1,1,2,1,1,2,2,2,2,1,1,2,1,1,1,1,2,1,1,3,1],
[1,2,1,1,2,2,2,2,2,2,1,1,2,1,1,2,1,1,2,2,2,2,2,2,1,1,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,1,2,1],
[1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
[1,1,1,2,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,2,1,1,1],
[0,0,1,2,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,2,1,0,0],
[0,0,1,2,2,2,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,2,2,2,1,0,0],
[1,1,1,2,1,1,2,1,1,0,1,1,4,4,4,4,1,1,0,1,1,2,1,1,2,1,1,1],
[0,0,0,2,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,2,0,0,0],
[1,1,1,1,1,1,2,0,0,0,1,0,0,0,0,0,0,1,0,0,0,2,1,1,1,1,1,1],
[1,1,1,1,1,1,2,1,1,0,1,0,0,0,0,0,0,1,0,1,1,2,1,1,1,1,1,1],
[0,0,0,2,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,2,0,0,0],
[1,1,1,2,1,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,1,2,1,1,1],
[0,0,1,2,2,2,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,2,2,2,1,0,0],
[0,0,1,2,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,2,1,0,0],
[0,0,1,2,1,1,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,1,1,2,1,0,0],
[0,0,1,2,1,1,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,1,1,2,1,0,0],
[1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1],
[1,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
[1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
[1,3,1,1,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,1,1,3,1],
[1,2,1,1,2,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,2,1,1,2,1],
[1,2,1,1,2,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,2,1,1,2,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],
"pac_coords":(13,1), "tps":[((13, 0), (13, 27)), ((16, 0), (16, 27))]}

laby_prototype = {"laby":[
[0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
[0,0,0,0,0,0,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,0,0,0,0,0,0],
[0,0,0,0,0,0,1,2,1,1,2,1,1,1,1,1,1,2,1,1,2,1,0,0,0,0,0,0],
[0,0,0,0,0,0,1,2,1,1,2,2,2,1,1,2,2,2,1,1,2,1,0,0,0,0,0,0],
[1,1,1,1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,1,1,1,1,1],
[0,0,2,2,3,2,2,2,1,1,2,2,2,2,2,2,2,2,1,1,2,2,2,3,2,2,0,0],
[1,1,2,1,1,1,1,1,1,1,2,1,1,1,1,1,1,2,1,1,1,1,1,1,1,2,1,1],
[1,1,2,1,1,1,1,1,1,1,2,1,1,1,1,1,1,2,1,1,1,1,1,1,1,2,1,1],
[1,2,2,2,2,2,2,2,1,1,2,2,2,1,1,2,2,2,1,1,2,2,2,2,2,2,2,1],
[1,2,1,1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,1,1,1,2,1],
[1,2,1,1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,1,1,2,1,1,1,1,1,2,1],
[1,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0,2,2,1,1,2,2,2,2,1],
[1,1,1,1,2,1,1,1,1,0,1,1,4,4,4,4,1,1,0,1,1,1,1,2,1,1,1,1],
[1,1,1,1,2,1,1,1,1,0,1,0,0,0,0,0,0,1,0,1,1,1,1,2,1,1,1,1],
[0,0,1,1,2,2,2,2,2,0,1,0,0,0,0,0,0,1,0,2,2,2,2,2,1,1,0,0],
[1,0,1,1,2,1,1,1,1,0,1,0,0,0,0,0,0,1,0,1,1,1,1,2,1,1,0,1],
[1,0,0,0,2,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,2,0,0,0,1],
[1,0,1,1,2,1,1,2,2,0,0,0,0,0,0,0,0,0,0,2,2,1,1,2,1,1,0,1],
[1,0,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,0,1],
[1,0,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,0,1],
[0,0,1,1,2,1,1,2,2,2,2,2,2,1,1,2,2,2,2,2,2,1,1,2,1,1,0,0],
[1,1,1,1,2,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,2,1,1,1,1],
[1,1,1,1,2,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,2,1,1,1,1],
[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
[1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1],
[1,2,1,1,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,1,1,2,1],
[1,3,1,1,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,1,1,3,1],
[1,2,1,1,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,1,1,2,1],
[1,2,2,2,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,2,2,2,1],
[1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
"pac_coords":(16,2), "tps":[((5, 0), (5, 27)), ((14, 0), (14, 27)), ((20, 0), (20, 27))]}

laby_wth = {"laby":[
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]],
"pac_coords":(15,2), "tps":[((i, 0), (i, 27)) for i in range(30)]}

class JeuPacMan(Element):
    def __init__(self):
        super().__init__("Pac-man.pyxapp", basic_ui=False)
        self.fps = 10

    def launch(self):
        self.game = Jeu([laby_pacman, laby_ms_pacman_1, laby_ms_pacman_2, laby_ms_pacman_3, laby_ms_pacman_4, laby_prototype])

    def update(self, sound_manager):
        quit = False

        if pyxel.btn(pyxel.KEY_ESCAPE):
            quit = True

        if (pyxel.frame_count % 24)%2 == 0:
            self.game.update()

        return quit

    def draw(self, global_color, x, y, width, height):
        start_x = x + width//2 - 224//2
        self.game.draw(start_x, y, x)

    def close(self):
        pass
