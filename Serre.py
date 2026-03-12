from __future__ import annotations
from typing import TYPE_CHECKING
from Module import Module
if TYPE_CHECKING:
    from Base import Base
    from Sinistre import Sinistre
    from EvenementSerre import EvenementSerre


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

    def creerEvenementSerre(self, idBio: int, idEvenementSerre: int, nbGraine: int) -> "EvenementSerre":
        from EvenementSerre import EvenementSerre
        nouvelEvenement = EvenementSerre(idEvenementSerre, nbGraine, self._monSystem)
        biologiste = self._monSystem.trouverMembreEquipage(idBio)
        nouvelEvenement.lierMembreEquipage(biologiste)
        biologiste.lierEvenementSerre(nouvelEvenement)
        nouvelEvenement.lierSerre(self)
        self._mesEvenements.append(nouvelEvenement)
        return nouvelEvenement

    def donnee(self):
        return (self._idModule, self._nbPlantSerre, self._etat)
