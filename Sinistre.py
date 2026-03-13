from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from MembreEquipage import MembreEquipage
    from Module import Module


class Sinistre:
    _idSinistre: int
    _dateCreation: str
    _ptDeVieResultant: int
    _etat: int          # 0 = en cours, 1 = réparé
    _dateReparation: str
    _monMembreAuteur: "MembreEquipage"
    _monTechnicien: "MembreEquipage"
    _monModule: "Module"

    def __init__(self, idSinistre: int, dateCreation: str, ptDeVieResultant: int,
                 membre: "MembreEquipage", module: "Module"):
        self._idSinistre = idSinistre
        self._dateCreation = dateCreation
        self._ptDeVieResultant = ptDeVieResultant
        self._etat = 0
        self._dateReparation = None
        self._monMembreAuteur = membre
        self._monTechnicien = None
        self._monModule = module
        membre.lierSinistre(self)
        module.lierSinistre(self)

    def getId(self) -> int:
        return self._idSinistre

    def getPtDeVieResultant(self) -> int:
        return self._ptDeVieResultant

    def getEtat(self) -> int:
        return self._etat

    def setEtat(self, etat: int) -> bool:
        self._etat = etat
        return True

    def setDateReparation(self, dateReparation: str) -> bool:
        self._dateReparation = dateReparation
        return True

    def lierTechnicien(self, technicien: "MembreEquipage") -> bool:
        self._monTechnicien = technicien
        return True

    def donnee(self):
        return (self._idSinistre, self._dateCreation, self._monMembreAuteur.getId(),
                self._ptDeVieResultant, self._etat)
