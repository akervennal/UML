from __future__ import annotations
from typing import TYPE_CHECKING
from Module import Module
from EvenementSerre import EvenementSerre
if TYPE_CHECKING:
    from Base import Base
    from Sinistre import Sinistre
    from MembreEquipage import MembreEquipage


class Serre(Module):
    _nbPlantSerre: int
    _mesEvenements: list["EvenementSerre"]

    def __init__(self, idSerre: int, base: "Base"):
        super().__init__(idSerre, base)
        self._nbPlantSerre = 0
        self._mesEvenements = []

    def getNbPlantSerre(self) -> int:
        return self._nbPlantSerre

    def setNbPlantSerre(self, nb: int) -> bool:
        self._nbPlantSerre = nb
        return True

    def creerEvenementSerre(self, biologiste: "MembreEquipage", idEvenementSerre: int, nbGraine: int) -> None:
        EvenementSerre(idEvenementSerre, nbGraine, biologiste, self)

    def lierEvenementSerre(self, evenement: "EvenementSerre") -> bool:
        self._mesEvenements.append(evenement)
        return True

    def getIdEvenementValide(self, idEvenement: int) -> "EvenementSerre | None":
        for e in self._mesEvenements:
            if e.getId() == idEvenement:
                return e
        return None

    def donnee(self):
        return (self._idModule, self._nbPlantSerre, self._etat)
