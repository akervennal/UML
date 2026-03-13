from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MembreEquipage import MembreEquipage
    from Garage import Garage
    from Serre import Serre
    from Sinistre import Sinistre
    from Expedition import Expedition
    from EvenementSerre import EvenementSerre
    from Module import Module

RECYCLAGE = 10
RECYCLAGE_MODULE = 5
PV_MAX_GARAGE = 100
PV_MAX_SERRE = 100

ROLES_VALIDES = {"Commandant", "Technicien", "Biologiste", "Chercheur"}
ROLE_COMMANDANT = "Commandant"
ROLE_TECHNICIEN = "Technicien"
ROLE_BIOLOGISTE = "Biologiste"
ROLE_CHERCHEUR  = "Chercheur"


class Base:
    _nbGraineStock: int
    _nbNourritureStock: int
    _nbPieceModuleStock: int

    _mesMembres: list["MembreEquipage"]
    _mesGarages: list["Garage"]
    _mesSerres: list["Serre"]
    _mesSinistres: list["Sinistre"]

    def __init__(self, idCmdt: int):
        self._nbGraineStock = 0
        self._nbNourritureStock = 0
        self._nbPieceModuleStock = 0
        self._mesMembres = []
        self._mesGarages = []
        self._mesSerres = []
        self._mesSinistres = []
        from MembreEquipage import MembreEquipage
        self._mesMembres.append(MembreEquipage(idCmdt, ROLE_COMMANDANT))

    def estIdMembreValide(self, idMembre: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idMembre and m.getEtatMembreEquipage() == 1:
                return m
        return None

    def estIdCmdtValide(self, idCmdt: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idCmdt and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_COMMANDANT:
                return m
        return None

    def estIdTechValide(self, idTech: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idTech and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_TECHNICIEN:
                return m
        return None

    def estIdBioValide(self, idBio: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idBio and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_BIOLOGISTE:
                return m
        return None

    def estIdChercheurValide(self, idChercheur: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if (m.getId() == idChercheur and m.getEtatMembreEquipage() == 1
                    and m.getRoleMembre() == ROLE_CHERCHEUR
                    and not m.estEnExpedition()):
                return m
        return None

    def estIdGarageValide(self, idGarage: int) -> "Garage | None":
        for g in self._mesGarages:
            if g.getId() == idGarage and g.getEtat() == 1:
                return g
        return None

    def estIdSerreValide(self, idSerre: int) -> "Serre | None":
        for s in self._mesSerres:
            if s.getId() == idSerre and s.getEtat() == 1:
                return s
        return None

    def estIdModuleValide(self, idModule: int) -> "Module | None":
        return self.estIdGarageValide(idModule) or self.estIdSerreValide(idModule)

    def estIdExpeditionValide(self, idExpedition: int) -> "Expedition | None":
        for g in self._mesGarages:
            expedition = g.estIdExpeditionValide(idExpedition)
            if expedition:
                return expedition
        return None

    def estIdSinistreValide(self, idSinistre: int) -> "Sinistre | None":
        for s in self._mesSinistres:
            if s.getId() == idSinistre:
                return s
        return None

    def estIdEvenementSerreValide(self, idEvenement: int) -> "EvenementSerre | None":
        for s in self._mesSerres:
            e = s.estIdEvenementValide(idEvenement)
            if e:
                return e
        return None

    def ajouterMembre(self, idCmdt: int, idMembre: int, role: str) -> bool:
        from MembreEquipage import MembreEquipage
        if not self.estIdCmdtValide(idCmdt) or self.estIdMembreValide(idMembre) or role not in ROLES_VALIDES:
            return False
        self._mesMembres.append(MembreEquipage(idMembre, role))
        return True

    def ajouterModule(self, idTech: int, idModule: int, typeModule: str, coutModule: int) -> bool:
        from Serre import Serre
        from Garage import Garage
        if not self.estIdTechValide(idTech) or self.estIdModuleValide(idModule) or self._nbPieceModuleStock < coutModule:
            return False
        if typeModule == "Serre":
            self._mesSerres.append(Serre(idModule, self))
        elif typeModule == "Garage":
            self._mesGarages.append(Garage(idModule, self))
        else:
            return False
        self._nbPieceModuleStock -= coutModule
        return True

    def consommerNourriture(self, idMembre: int, nbNourriture: int) -> bool:
        if not self.estIdMembreValide(idMembre) or self._nbNourritureStock < nbNourriture:
            return False
        self._nbNourritureStock -= nbNourriture
        return True

    def declarerSinistreGarage(self, idMembreAuteur: int, idSinistre: int,
                                idGarage: int, dateCreation: str, ptDeVieResultant: int) -> bool:
        from Sinistre import Sinistre
        membre = self.estIdMembreValide(idMembreAuteur)
        garage = self.estIdGarageValide(idGarage)
        if not membre or not garage or self.estIdSinistreValide(idSinistre) or garage.getSinistreEnCours():
            return False
        nouveauSinistre = Sinistre(idSinistre, dateCreation, ptDeVieResultant, membre, garage, self)
        self._mesSinistres.append(nouveauSinistre)
        return True

    def declarerSinistreSerre(self, idMembreAuteur: int, idSinistre: int,
                               idSerre: int, dateCreation: str, ptDeVieResultant: int) -> bool:
        from Sinistre import Sinistre
        membre = self.estIdMembreValide(idMembreAuteur)
        serre = self.estIdSerreValide(idSerre)
        if not membre or not serre or self.estIdSinistreValide(idSinistre) or serre.getSinistreEnCours():
            return False
        nouveauSinistre = Sinistre(idSinistre, dateCreation, ptDeVieResultant, membre, serre, self)
        self._mesSinistres.append(nouveauSinistre)
        return True

    def lancerExpedition(self, idChercheurLancement: int, idParticipant: int,
                         idExpedition: int, idGarage: int, dateLancement: str) -> bool:
        from Expedition import Expedition
        chercheur = self.estIdChercheurValide(idChercheurLancement)
        participant = self.estIdChercheurValide(idParticipant)
        garage = self.estIdGarageValide(idGarage)
        if not chercheur or not participant or not garage:
            return False
        if self.estIdExpeditionValide(idExpedition) or idChercheurLancement == idParticipant:
            return False
        if garage.verifExpeditionEnCours():
            return False
        Expedition(idExpedition, dateLancement, chercheur, participant, garage)
        return True

    def planterGraines(self, idSerre: int, idBio: int, nbGraine: int, idEvenement: int) -> bool:
        bio = self.estIdBioValide(idBio)
        serre = self.estIdSerreValide(idSerre)
        if not bio or not serre or self._nbGraineStock < nbGraine or self.estIdEvenementSerreValide(idEvenement):
            return False
        serre.setNbPlantSerre(serre.getNbPlantSerre() + nbGraine)
        self._nbGraineStock -= nbGraine
        serre.creerEvenementSerre(bio, idEvenement, nbGraine)
        return True

    def receptionnerExpedition(self, idChercheurRetour: int, idExpedition: int,
                                nbPieceModule: int, dateRetour: str, ptDeVieResultant: int) -> bool:
        chercheur = self.estIdChercheurValide(idChercheurRetour)
        expedition = self.estIdExpeditionValide(idExpedition)
        if not chercheur or not expedition:
            return False
        if not expedition.getGarage().receptionnerExpedition(expedition, dateRetour, ptDeVieResultant):
            return False
        self._nbPieceModuleStock += nbPieceModule
        expedition.lierChercheurRetour(chercheur)
        chercheur.lierExpeditionReceptionnee(expedition)
        return True

    def receptionnerCommande(self, idCmdt: int, nbGraine: int, nbNourriture: int,
                              nbPieceModule: int) -> bool:
        if not self.estIdCmdtValide(idCmdt):
            return False
        self._nbGraineStock += nbGraine
        self._nbNourritureStock += nbNourriture
        self._nbPieceModuleStock += nbPieceModule
        return True

    def recolterPlantation(self, idBio: int, idSerre: int, idEvenement: int) -> bool:
        bio = self.estIdBioValide(idBio)
        serre = self.estIdSerreValide(idSerre)
        if not bio or not serre or self.estIdEvenementSerreValide(idEvenement):
            return False
        nbPlantSerre = serre.getNbPlantSerre()
        if nbPlantSerre == 0:
            return False
        self._nbNourritureStock += nbPlantSerre
        serre.setNbPlantSerre(0)
        serre.creerEvenementSerre(bio, idEvenement, -nbPlantSerre)
        return True

    def reparerGarage(self, idTech: int, idGarage: int, dateReparation: str) -> bool:
        tech = self.estIdTechValide(idTech)
        garage = self.estIdGarageValide(idGarage)
        if not tech or not garage:
            return False
        sinistreEnCours = garage.getSinistreEnCours()
        if sinistreEnCours is None:
            return False
        coutReparation = PV_MAX_GARAGE - sinistreEnCours.getPtDeVieResultant()
        if self._nbPieceModuleStock < coutReparation:
            return False
        self._nbPieceModuleStock -= coutReparation
        sinistreEnCours.setEtat(1)
        sinistreEnCours.setDateReparation(dateReparation)
        sinistreEnCours.lierTechnicien(tech)
        tech.lierSinistre(sinistreEnCours)
        return True

    def reparerSerre(self, idTech: int, idModule: int, dateReparation: str) -> bool:
        tech = self.estIdTechValide(idTech)
        serre = self.estIdSerreValide(idModule)
        if not tech or not serre:
            return False
        sinistreEnCours = serre.getSinistreEnCours()
        if sinistreEnCours is None:
            return False
        coutReparation = PV_MAX_SERRE - sinistreEnCours.getPtDeVieResultant()
        if self._nbPieceModuleStock < coutReparation:
            return False
        self._nbPieceModuleStock -= coutReparation
        sinistreEnCours.setEtat(1)
        sinistreEnCours.setDateReparation(dateReparation)
        sinistreEnCours.lierTechnicien(tech)
        tech.lierSinistre(sinistreEnCours)
        return True

    def supprimerMembre(self, idCmdt: int, idMembre: int) -> bool:
        cmdt = self.estIdCmdtValide(idCmdt)
        membre = self.estIdMembreValide(idMembre)
        if not cmdt or not membre:
            return False
        self._nbNourritureStock += RECYCLAGE
        membre.setEtat(0)
        return True

    def supprimerGarage(self, idTech: int, idGarage: int) -> bool:
        tech = self.estIdTechValide(idTech)
        garage = self.estIdGarageValide(idGarage)
        if not tech or not garage:
            return False
        self._nbPieceModuleStock += RECYCLAGE_MODULE
        garage.setEtat(0)
        return True

    def supprimerSerre(self, idTech: int, idSerre: int) -> bool:
        tech = self.estIdTechValide(idTech)
        serre = self.estIdSerreValide(idSerre)
        if not tech or not serre:
            return False
        self._nbPieceModuleStock += RECYCLAGE_MODULE
        serre.setEtat(0)
        return True

    def donneeStocks(self):
        return {
            "graines": self._nbGraineStock,
            "nourriture": self._nbNourritureStock,
            "piecesModule": self._nbPieceModuleStock,
        }
