from __future__ import annotations
from typing import TYPE_CHECKING
from Module import Module
if TYPE_CHECKING:
    from Base import Base
    from Sinistre import Sinistre
    from EvenementSerre import EvenementSerre
    from MembreEquipage import MembreEquipage


class Serre(Module):
    _nbPlantSerre: int
    _mesEvenements: list["EvenementSerre"]

    def __init__(self, idSerre: int, s: "Base"):
        super().__init__(idSerre, s)
        self._nbPlantSerre = 0
        self._mesEvenements = []

    def getNbPlantSerre(self) -> int:
        return self._nbPlantSerre

    def setNbPlantSerre(self, nb: int) -> bool:
        self._nbPlantSerre = nb
        return True

    def creerEvenementSerre(self, biologiste: "MembreEquipage", idEvenementSerre: int, nbGraine: int) -> None:
        from EvenementSerre import EvenementSerre
        EvenementSerre(idEvenementSerre, nbGraine, biologiste, self, self._monSystem)

    def donnee(self):
        return (self._idModule, self._nbPlantSerre, self._etat)
