from typing import Any
from utils.maillon import Maillon

class PileLIFO:
    def __init__(self, premier_maillon:Maillon|None=None):
        self.__maillon1:Maillon = premier_maillon

    def empiler(self, nouvelle_valeur:Any|Maillon):
        m_pre = self.__maillon1
        if nouvelle_valeur.__class__ != Maillon:
                nouvelle_valeur = Maillon(nouvelle_valeur)

        if m_pre == None:
            self.__maillon1 = nouvelle_valeur
        else:
            while m_pre.get_suivant() != None:
                m_pre = m_pre.get_suivant()

            m_pre.set_suivant(nouvelle_valeur)

    def depiler(self) -> Maillon:
        try:
            m_pre = self.__maillon1
            while m_pre.get_suivant().get_suivant() != None:
                m_pre = m_pre.get_suivant()
            m_del = m_pre.get_suivant()
            m_pre.set_suivant(None)
        except AttributeError:
            m_del = self.__maillon1
            self.__maillon1 = None
        return m_del

    def taille(self) -> int:
        if self.__maillon1 != None:
            res = 1
            m_pre = self.__maillon1
            while m_pre.get_suivant() != None:
                res += 1
                m_pre = m_pre.get_suivant()
        else:
            res = 0

        return res

    def affiche_tete(self) -> Any:
        return self.__maillon1.get_valeur()

    def afficher_main(self) -> Any:
        try:
            m_pre = self.__maillon1
            while m_pre.get_suivant().get_suivant() != None:
                m_pre = m_pre.get_suivant()
            m_del = m_pre.get_suivant()
        except AttributeError:
            m_del = self.__maillon1
        return m_del.get_valeur()

    def affiche(self, show_last: bool = True) -> str:
        res = str(self.__maillon1.get_valeur())
        m_suiv = self.__maillon1.get_suivant()
        while m_suiv != None:
            res += " -> " + str(m_suiv.get_valeur())
            m_suiv = m_suiv.get_suivant()

        if show_last:
            res += " -> None"

        return res

#m1 = Maillon(12, None)
#m2 = Maillon(10, m1)
#liste = PileLIFO(m2)
#liste.ajoute(Maillon(17))
#print(liste.affiche())
#liste.enleve()
#print(liste.affiche())
