from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Base import Base
    from MembreEquipage import MembreEquipage
    from Garage import Garage


class Expedition:
    _idExpedition: int
    _dateLancement: str
    _dateRetour: str
    _ptDeVieResultant: int
    _etat: int          # 1 = en cours, 0 = terminée
    _monSystem: "Base"
    _monChercheurLancement: "MembreEquipage"
    _monChercheurRetour: "MembreEquipage"
    _monParticipant: "MembreEquipage"
    _monGarage: "Garage"

    def __init__(self, idExpedition: int, dateLancement: str,
                 chercheurLancement: "MembreEquipage", participant: "MembreEquipage",
                 garage: "Garage", s: "Base"):
        self._idExpedition = idExpedition
        self._dateLancement = dateLancement
        self._dateRetour = None
        self._ptDeVieResultant = None
        self._etat = 1
        self._monSystem = s
        self._monChercheurLancement = chercheurLancement
        self._monChercheurRetour = None
        self._monParticipant = participant
        self._monGarage = garage
        chercheurLancement.lierExpeditionLancee(self)
        participant.lierExpeditionParticipee(self)
        garage._mesExpeditions.append(self)

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

    def lierChercheurRetour(self, membre: "MembreEquipage") -> bool:
        self._monChercheurRetour = membre
        return True

    def donnee(self):
        return (self._idExpedition, self._monChercheurLancement.getId(),
                self._dateLancement, self._etat)
