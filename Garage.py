from __future__ import annotations
from typing import TYPE_CHECKING
from Module import Module
if TYPE_CHECKING:
    from Base import Base
    from Sinistre import Sinistre
    from Expedition import Expedition


class Garage(Module):
    _mesExpeditions: list["Expedition"]

    def __init__(self, idGarage: int, base: "Base"):
        super().__init__(idGarage, base)
        self._mesExpeditions = []

    def verifExpeditionEnCours(self) -> bool:
        for e in self._mesExpeditions:
            if e.getEtat() == 1:
                return True
        return False

    def estIdExpeditionValide(self, idExpedition: int) -> "Expedition | None":
        for e in self._mesExpeditions:
            if e.getId() == idExpedition:
                return e
        return None

    def receptionnerExpedition(self, expedition: "Expedition", dateRetour: str, ptDeVieResultant: int) -> bool:
        if expedition.getEtat() != 1:
            return False
        expedition.setEtat(0)
        expedition.setDateRetour(dateRetour)
        expedition.setPtDeVie(ptDeVieResultant)
        return True

    def _getExpeditionEnCours(self) -> "Expedition":
        for e in self._mesExpeditions:
            if e.getEtat() == 1:
                return e
        return None

    def lierExpedition(self, expedition: "Expedition") -> bool:
        self._mesExpeditions.append(expedition)
        return True

    def donnee(self):
        return (self._idModule, self._etat)
