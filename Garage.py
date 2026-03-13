from __future__ import annotations
from typing import TYPE_CHECKING
from Module import Module
if TYPE_CHECKING:
    from Base import Base
    from Sinistre import Sinistre
    from Expedition import Expedition


class Garage(Module):
    _mesExpeditions: list["Expedition"]

    def __init__(self, idGarage: int, s: "Base"):
        super().__init__(idGarage, s)
        self._mesExpeditions = []

    def lierExpedition(self, expedition: "Expedition") -> bool:
        self._mesExpeditions.append(expedition)
        return True

    def lancerExpedition(self, idChercheurLancement: int, idParticipant: int,
                        idExpedition: int,
                        dateLancement: str) -> "Expedition":
        """
        Crée une Expedition, lie le garage, le chercheur lanceur et le participant.
        Le chercheur lanceur ne participe PAS à l'expédition.
        Retourne l'Expedition créée.
        """
        from Expedition import Expedition

        nouvelleExpedition = Expedition(idExpedition, dateLancement, self._monSystem)

        chercheur = self._monSystem.trouverMembreEquipage(idChercheurLancement)
        participant = self._monSystem.trouverMembreEquipage(idParticipant)

        # Liaison chercheur lancement (lance mais ne participe PAS)
        nouvelleExpedition.lierChercheurLancement(chercheur)
        chercheur.lierExpeditionLancee(nouvelleExpedition)

        # Liaison participant
        nouvelleExpedition.lierParticipant(participant)
        participant.lierExpeditionParticipee(nouvelleExpedition)

        # Liaison garage
        nouvelleExpedition.lierGarage(self)
        self._mesExpeditions.append(nouvelleExpedition)

        return nouvelleExpedition

    def verifExpeditionEnCours(self) -> bool:
        for e in self._mesExpeditions:
            if e.getEtat() == 1:
                return True
        return False

    def estIdExpeditionValide(self, idExpedition: int) -> bool:
        for e in self._mesExpeditions:
            if e.getId() == idExpedition:
                return True
        return False

    def trouverExpedition(self, idExpedition: int) -> "Expedition":
        for e in self._mesExpeditions:
            if e.getId() == idExpedition:
                return e
        return None

    def receptionnerExpedition(self, idExpedition: int, dateRetour: str, ptDeVieResultant: int) -> bool:
        """
        Réceptionne l'expédition identifiée par idExpedition.
        Vérifie que l'expédition existe et est en cours (etat == 1).
        """
        expedition = self.trouverExpedition(idExpedition)
        if expedition is None or expedition.getEtat() != 1:
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

    def donnee(self):
        return (self._idModule, self._etat)
