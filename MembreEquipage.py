from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Sinistre import Sinistre
    from Expedition import Expedition
    from EvenementSerre import EvenementSerre


class MembreEquipage:
    _idMembre: int
    _roleMembre: str
    _etat: int
    _mesSinistres: list["Sinistre"]
    _mesExpeditionsLancees: list["Expedition"]
    _mesExpeditionsParticipees: list["Expedition"]
    _mesExpeditionsReceptionnees: list["Expedition"]
    _mesEvenementsSerre: list["EvenementSerre"]

    def __init__(self, idMembre: int, roleMembre: str):
        self._idMembre = idMembre
        self._roleMembre = roleMembre
        self._etat = 1
        self._mesSinistres = []
        self._mesExpeditionsLancees = []
        self._mesExpeditionsParticipees = []
        self._mesExpeditionsReceptionnees = []
        self._mesEvenementsSerre = []

    def getId(self) -> int:
        return self._idMembre

    def getRoleMembre(self) -> str:
        return self._roleMembre

    def getEtatMembreEquipage(self) -> int:
        return self._etat

    def setEtat(self, etat: int) -> bool:
        if etat not in (0, 1):
            return False
        self._etat = etat
        return True

    def estEnExpedition(self) -> bool:
        for e in self._mesExpeditionsParticipees:
            if e.getEtat() == 1:
                return True
        return False

    def lierSinistre(self, sinistre: "Sinistre") -> bool:
        self._mesSinistres.append(sinistre)
        return True

    def lierExpeditionLancee(self, expedition: "Expedition") -> bool:
        self._mesExpeditionsLancees.append(expedition)
        return True

    def lierExpeditionParticipee(self, expedition: "Expedition") -> bool:
        self._mesExpeditionsParticipees.append(expedition)
        return True

    def lierExpeditionReceptionnee(self, expedition: "Expedition") -> bool:
        self._mesExpeditionsReceptionnees.append(expedition)
        return True

    def lierEvenementSerre(self, evenement: "EvenementSerre") -> bool:
        self._mesEvenementsSerre.append(evenement)
        return True

    def getNbSinistres(self) -> int:
        return len(self._mesSinistres)

    def getNbExpeditionsLancees(self) -> int:
        return len(self._mesExpeditionsLancees)

    def getNbExpeditionsParticipees(self) -> int:
        return len(self._mesExpeditionsParticipees)

    def getNbExpeditionsReceptionnees(self) -> int:
        return len(self._mesExpeditionsReceptionnees)

    def getNbEvenementsSerre(self) -> int:
        return len(self._mesEvenementsSerre)

    def donnee(self) -> tuple:
        return (self._idMembre, self._roleMembre, self._etat)
