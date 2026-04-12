from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Base import Base
    from Sinistre import Sinistre


class Module:
    _idModule: int
    _etat: int
    _monSystem: "Base"
    _mesSinistres: list["Sinistre"]

    def __init__(self, idModule: int, base: "Base"):
        self._idModule = idModule
        self._etat = 1
        self._monSystem = base
        self._mesSinistres = []

    def getId(self) -> int:
        return self._idModule

    def getEtat(self) -> int:
        return self._etat

    def setEtat(self, etat: int) -> bool:
        if etat not in (0, 1):
            return False
        self._etat = etat
        return True

    def getSinistreEnCours(self) -> "Sinistre | None":
        for s in self._mesSinistres:
            if s.getEtat() == 1:
                return s
        return None

    def getNbSinistres(self) -> int:
        return len(self._mesSinistres)

    def getDegatsCumules(self) -> int:
        return sum(100 - s.getPtDeVieResultant() for s in self._mesSinistres)

    def lierSinistre(self, sinistre: "Sinistre") -> bool:
        self._mesSinistres.append(sinistre)
        return True
