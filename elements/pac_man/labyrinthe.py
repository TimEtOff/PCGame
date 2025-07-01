import pyxel
import copy
from random import choice
from elements.pac_man.node import Node
import random

class Lab:

    powergums_coords = [(32, 0), (40, 0), (32, 8), (40, 8)]
    next_nodes = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def __init__(self, l):
        self.grille = copy.deepcopy(l["laby"])
        self.og_grille = copy.deepcopy(l["laby"])
        self.infos = l
        self.num_gum = self.get_num_gum()
        self.colors = {'mur':5, 'normal_gum':13, 'powergum':8, 'barrier':12}
        self.sprites = random.randint(0, 5)
        self.graph = []
        self.create_graph(self.infos["pac_coords"])

        self.init_gums()

    def init_gums(self):
        self.powergums = {}
        for i in range(len(self.grille)):
            for j in range(len(self.grille[0])):
                if self.grille[i][j]:
                    self.powergums[(i,j)] = choice(self.powergums_coords)

    def affiche(self, pac_man, panic_mode, panic_time, difficulty, start_x, start_y):
        r = [0,1,2,3,4]
        if panic_mode and (panic_time>30 or pyxel.frame_count%int((4*24)/10) in r):
            self.colors['mur'] = 12
        else:
            self.colors['mur'] = 5
        for i in range(len(self.grille)):
            for j in range(len(self.grille[0])):
                pyxel.rect(start_x+j*8, start_y+i*8, 8, 8, 0)

                if self.grille[i][j] == 1:
                    #pyxel.rect(j*8+1, i*8+1, 6, 6, self.colors['mur']) # mur
                    if self.colors['mur'] == 12:
                        u = 64+32
                    else:
                        u = 64
                    if pac_man.lives == 3:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, u, 0 +16*self.sprites, 8, 8, 0)
                    elif pac_man.lives == 2:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, u+8, 0 +16*self.sprites, 8, 8, 0)
                    elif pac_man.lives <= 1:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, u, 8 +16*self.sprites, 8, 8, 0)

                elif self.grille[i][j] == 2:
                    #pyxel.circ(j*8+4, i*8+4, 2, self.colors['normal_gum']) # gomme normale
                    if pac_man.lives == 2:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 72, 8 +16*self.sprites, 8, 8, 0)
                    elif pac_man.lives <= 1:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 88, 8 +16*self.sprites, 8, 8, 0)

                    if pac_man.lives == 3:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 80, 0 +16*self.sprites, 8, 8, 0)
                    elif pac_man.lives == 2:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 88, 0 +16*self.sprites, 8, 8, 0)
                    elif pac_man.lives <= 1:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 80, 8 +16*self.sprites, 8, 8, 0)

                elif self.grille[i][j] == 3:
                    if pac_man.lives == 2:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 72, 8, 8, 8, 0)
                    elif pac_man.lives <= 1:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 88, 8, 8, 8, 0)

                    if difficulty != 2:
                        #pyxel.circ(j*8+4, i*8+4, 3, self.colors['powergum']) # powergum
                        u, v = self.powergums[(i,j)]
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, u, v, 8, 8, 0)

                elif self.grille[i][j] == 4:
                    pyxel.rect(start_x+j*8+1, start_y+i*8+1, 6, 6, self.colors['barrier']) # barrier

                elif self.grille[i][j] == 0:
                    if pac_man.lives == 2:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 72, 8 +16*self.sprites, 8, 8, 0)
                    elif pac_man.lives <= 1:
                        pyxel.blt(start_x+j*8, start_y+i*8, 0, 88, 8 +16*self.sprites, 8, 8, 0)

        #for node in self.graph:
        #    u, v = node.get_id()
        #    #print(str((u*8, v*8)))
        #    pyxel.text(v*8, u*8, str(node.get_value()), 7)

    def create_graph(self, coords):
        #graphe = {}
        #for i in range(len(self.grille)):
        #    for j in range(len(self.grille[0])):
        #        if self.grille[i][j] != 1:
        #            graphe[(i, j)] = 0
        #return graphe

        i, j = coords
        node = None
        if i >= 0 and j >= 0:
            node = Node((i,j), [])
            self.graph.append(node)
            for next_node in self.next_nodes:
                p_i, p_j = next_node
                try:
                    if self.grille[i+p_i][j+p_j] != 1:
                        #print(str((i+p_i, j+p_j)))
                        next_node = self.in_graph((i+p_i, j+p_j))
                        if next_node == None:
                            add_node = self.create_graph((i+p_i, j+p_j))
                            if add_node != None:
                                node.add_to_node(add_node)
                        else:
                            node.add_to_node(next_node)
                except IndexError:
                    pass

        return node


    def in_graph(self, coords):
        res = None
        for node in self.graph:
            if node.get_id() == coords:
                res = node
        return res

    def update_graph(self, pac_coords):
        pac_node = None
        for node in self.graph:
            if node.get_id() == pac_coords:
                pac_node = node

        pac_node.set_value(0)

        for node in pac_node.get_to_list():
            node.update_depth(1)

        for node in self.graph:
            node.not_changed()

    def get_node(self, coords):
        for n in self.graph:
            if n.get_id() == coords:
                return n

    def get_num_gum(self):
        num = 0
        for i in range(len(self.grille)):
            for j in range(len(self.grille[0])):
                if self.grille[i][j] == 2:
                    num += 1
        return num

    def get_num_gum_quick(self):
        return self.num_gum

    def set_num_gum(self, n):
        self.num_gum = n

    def is_cleared(self):
        #self.colors['mur'] = 5      # OG, reset map
        #if self.get_num_gum_quick() <= 0:
        #    self.set_grille(copy.deepcopy(self.og_grille))
        #    self.num_gum = self.get_num_gum()
        #    self.colors['mur'] = 12
        #    self.init_gums()
        res = False
        if self.get_num_gum_quick() <= 0:
            res = True
        return res

    def get_grille(self):
        return self.grille

    def set_grille(self, l):
        self.grille = l

    def get_case(self, coords):
        i, j = coords
        return self.grille[i][j]

    def set_case(self, coords, val):
        i, j = coords
        self.grille[i][j] = val
