from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Base import Base
    from MembreEquipage import MembreEquipage
    from Garage import Garage


class Expedition:
    _idExpedition: int
    _idChercheurLancement: int
    _dateLancement: str
    _dateRetour: str
    _ptDeVieResultant: int
    _etat: int          # 1 = en cours, 0 = terminée
    _monSystem: "Base"
    _monChercheurLancement: "MembreEquipage"
    _monChercheurRetour: "MembreEquipage"
    _monParticipant1: "MembreEquipage"
    _monParticipant2: "MembreEquipage"
    _monGarage: "Garage"

    def __init__(self, idExpedition: int, idChercheurLancement: int, dateLancement: str, s: "Base"):
        self._idExpedition = idExpedition
        self._idChercheurLancement = idChercheurLancement
        self._dateLancement = dateLancement
        self._dateRetour = None
        self._ptDeVieResultant = None
        self._etat = 1
        self._monSystem = s
        self._monChercheurLancement = None
        self._monChercheurRetour = None
        self._monParticipant1 = None
        self._monParticipant2 = None
        self._monGarage = None

    def getId(self) -> int:
        return self._idExpedition

    def getEtat(self) -> int:
        return self._etat

    def setEtat(self, etat: int) -> bool:
        self._etat = etat
        return True

    def setDateRetour(self, dateRetour: str) -> bool:
        self._dateRetour = dateRetour
        return True

    def setPtDeVie(self, ptDeVieResultant: int) -> bool:
        self._ptDeVieResultant = ptDeVieResultant
        return True

    def lierGarage(self, garage: "Garage") -> bool:
        self._monGarage = garage
        return True

    def lierChercheurLancement(self, membre: "MembreEquipage") -> bool:
        self._monChercheurLancement = membre
        return True

    def lierChercheurRetour(self, membre: "MembreEquipage") -> bool:
        self._monChercheurRetour = membre
        return True

    def lierParticipant1(self, membre: "MembreEquipage") -> bool:
        self._monParticipant1 = membre
        return True

    def lierParticipant2(self, membre: "MembreEquipage") -> bool:
        self._monParticipant2 = membre
        return True

    def donnee(self):
        return (self._idExpedition, self._idChercheurLancement,
                self._dateLancement, self._etat)
