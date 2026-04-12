from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from MembreEquipage import MembreEquipage
    from Serre import Serre


class EvenementSerre:
    _idEvenementSerre: int
    _nbGraine: int
    _monBiologiste: "MembreEquipage"
    _maSerre: "Serre"

    def __init__(self, idEvenementSerre: int, nbGraine: int,
                 biologiste: "MembreEquipage", serre: "Serre"):
        self._idEvenementSerre = idEvenementSerre
        self._nbGraine = nbGraine
        self._monBiologiste = biologiste
        self._maSerre = serre
        biologiste.lierEvenementSerre(self)
        serre.lierEvenementSerre(self)

    def getId(self) -> int:
        return self._idEvenementSerre

    def getNbGraine(self) -> int:
        return self._nbGraine

    def donnee(self) -> tuple:
        return (self._idEvenementSerre, self._nbGraine)
