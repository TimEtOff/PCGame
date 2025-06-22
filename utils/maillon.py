class Maillon:
    def __init__(self, valeur, maillon_suivant=None):
        self.__valeur = valeur
        self.__m_suivant = maillon_suivant

    def get_valeur(self):
        return self.__valeur

    def set_valeur(self, valeur):
        self.__valeur = valeur

    def get_suivant(self):
        return self.__m_suivant

    def set_suivant(self, maillon):
        self.__m_suivant = maillon
