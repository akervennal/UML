from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Base import Base
    from MembreEquipage import MembreEquipage
    from Serre import Serre


class EvenementSerre:
    _idEvenementSerre: int
    _nbGraine: int      # positif = plantation, négatif = récolte
    _monSystem: "Base"
    _monBiologiste: "MembreEquipage"
    _maSerre: "Serre"

    def __init__(self, idEvenementSerre: int, nbGraine: int, s: "Base"):
        self._idEvenementSerre = idEvenementSerre
        self._nbGraine = nbGraine
        self._monSystem = s
        self._monBiologiste = None
        self._maSerre = None

    def getId(self) -> int:
        return self._idEvenementSerre

    def getNbGraine(self) -> int:
        return self._nbGraine

    def lierMembreEquipage(self, membre: "MembreEquipage") -> bool:
        self._monBiologiste = membre
        return True

    def lierSerre(self, serre: "Serre") -> bool:
        self._maSerre = serre
        return True

    def donnee(self):
        return (self._idEvenementSerre, self._nbGraine)
