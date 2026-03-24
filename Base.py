from __future__ import annotations
from typing import TYPE_CHECKING

from MembreEquipage import MembreEquipage
from Garage import Garage
from Serre import Serre
from Sinistre import Sinistre
from Expedition import Expedition
from EvenementSerre import EvenementSerre

if TYPE_CHECKING:
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
    # attributs
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
        self._mesMembres.append(MembreEquipage(idCmdt, ROLE_COMMANDANT))

    def trouverMembreParId(self, idMembre: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idMembre and m.getEtatMembreEquipage() == 1:
                return m
        return None

    def getMembre(self, idMembre: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idMembre and m.getEtatMembreEquipage() == 1 and not m.estEnExpedition():
                return m
        return None

    def getCmdt(self, idCmdt: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idCmdt and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_COMMANDANT:
                return m
        return None

    def getTech(self, idTech: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idTech and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_TECHNICIEN:
                return m
        return None

    def getBio(self, idBio: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if m.getId() == idBio and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_BIOLOGISTE:
                return m
        return None

    def getChercheur(self, idChercheur: int) -> "MembreEquipage | None":
        for m in self._mesMembres:
            if (m.getId() == idChercheur and m.getEtatMembreEquipage() == 1
                    and m.getRoleMembre() == ROLE_CHERCHEUR
                    and not m.estEnExpedition()):
                return m
        return None

    def getGarage(self, idGarage: int) -> "Garage | None":
        for g in self._mesGarages:
            if g.getId() == idGarage and g.getEtat() == 1:
                return g
        return None

    def getSerre(self, idSerre: int) -> "Serre | None":
        for s in self._mesSerres:
            if s.getId() == idSerre and s.getEtat() == 1:
                return s
        return None

    def getModule(self, idModule: int) -> "Module | None":
        return self.getGarage(idModule) or self.getSerre(idModule)

    def getExpedition(self, idExpedition: int) -> "Expedition | None":
        for g in self._mesGarages:
            expedition = g.getExpedition(idExpedition)
            if expedition:
                return expedition
        return None

    def getSinistre(self, idSinistre: int) -> "Sinistre | None":
        for s in self._mesSinistres:
            if s.getId() == idSinistre:
                return s
        return None

    def getEvenementSerre(self, idEvenementSerre: int) -> "EvenementSerre | None":
        for s in self._mesSerres:
            e = s.getIdEvenementValide(idEvenementSerre)
            if e:
                return e
        return None

    def getMembres(self) -> list["MembreEquipage"]:
        return list(self._mesMembres)

    def getGarages(self) -> list["Garage"]:
        return list(self._mesGarages)

    def getSerres(self) -> list["Serre"]:
        return list(self._mesSerres)

    def ajouterMembre(self, idCmdt: int, idMembre: int, role: str) -> bool:
        if not self.getCmdt(idCmdt) or self.trouverMembreParId(idMembre) or role not in ROLES_VALIDES:
            return False
        self._mesMembres.append(MembreEquipage(idMembre, role))
        return True

    def ajouterModule(self, idTech: int, idModule: int, typeModule: str, coutModule: int) -> bool:
        if not self.getTech(idTech) or self.getModule(idModule) or self._nbPieceModuleStock < coutModule:
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
        if not self.getMembre(idMembre) or self._nbNourritureStock < nbNourriture:
            return False
        self._nbNourritureStock -= nbNourriture
        return True

    def declarerSinistreGarage(self, idMembreAuteur: int, idSinistre: int,
                                idGarage: int, dateCreation: str, ptDeVieResultant: int) -> bool:
        membre = self.getMembre(idMembreAuteur)
        garage = self.getGarage(idGarage)
        if not membre or not garage or self.getSinistre(idSinistre) or garage.getSinistreEnCours():
            return False
        nouveauSinistre = Sinistre(idSinistre, dateCreation, ptDeVieResultant, membre, garage)
        self._mesSinistres.append(nouveauSinistre)
        return True

    def declarerSinistreSerre(self, idMembreAuteur: int, idSinistre: int,
                               idSerre: int, dateCreation: str, ptDeVieResultant: int) -> bool:
        membre = self.getMembre(idMembreAuteur)
        serre = self.getSerre(idSerre)
        if not membre or not serre or self.getSinistre(idSinistre) or serre.getSinistreEnCours():
            return False
        nouveauSinistre = Sinistre(idSinistre, dateCreation, ptDeVieResultant, membre, serre)
        self._mesSinistres.append(nouveauSinistre)
        return True

    def lancerExpedition(self, idChercheurLancement: int, idParticipant: int,
                         idExpedition: int, idGarage: int, dateLancement: str) -> bool:
        chercheur = self.getChercheur(idChercheurLancement)
        participant = self.getChercheur(idParticipant)
        garage = self.getGarage(idGarage)
        if not chercheur or not participant or not garage:
            return False
        if self.getExpedition(idExpedition) or idChercheurLancement == idParticipant:
            return False
        if garage.getExpeditionEnCours():
            return False
        Expedition(idExpedition, dateLancement, chercheur, participant, garage)
        return True

    def planterGraines(self, idSerre: int, idBio: int, nbGraine: int, idEvenementSerre: int) -> bool:
        bio = self.getBio(idBio)
        serre = self.getSerre(idSerre)
        if not bio or not serre or self._nbGraineStock < nbGraine or self.getEvenementSerre(idEvenementSerre):
            return False
        serre.setNbPlantSerre(serre.getNbPlantSerre() + nbGraine)
        self._nbGraineStock -= nbGraine
        serre.creerEvenementSerre(bio, idEvenementSerre, nbGraine)
        return True

    def receptionnerExpedition(self, idChercheurRetour: int, idExpedition: int,
                                nbPieceModule: int, dateRetour: str, ptDeVieResultant: int) -> bool:
        chercheur = self.getChercheur(idChercheurRetour)
        expedition = self.getExpedition(idExpedition)
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
        if not self.getCmdt(idCmdt):
            return False
        self._nbGraineStock += nbGraine
        self._nbNourritureStock += nbNourriture
        self._nbPieceModuleStock += nbPieceModule
        return True

    def recolterPlantation(self, idBio: int, idSerre: int, idEvenementSerre: int) -> bool:
        bio = self.getBio(idBio)
        serre = self.getSerre(idSerre)
        if not bio or not serre or self.getEvenementSerre(idEvenementSerre):
            return False
        nbPlantSerre = serre.getNbPlantSerre()
        if nbPlantSerre == 0:
            return False
        self._nbNourritureStock += nbPlantSerre
        serre.setNbPlantSerre(0)
        serre.creerEvenementSerre(bio, idEvenementSerre, -nbPlantSerre)
        return True

    def reparerGarage(self, idTech: int, idGarage: int, dateReparation: str) -> bool:
        tech = self.getTech(idTech)
        garage = self.getGarage(idGarage)
        if not tech or not garage:
            return False
        sinistreEnCours = garage.getSinistreEnCours()
        if sinistreEnCours is None:
            return False
        coutReparation = PV_MAX_GARAGE - sinistreEnCours.getPtDeVieResultant()
        if self._nbPieceModuleStock < coutReparation:
            return False
        self._nbPieceModuleStock -= coutReparation
        sinistreEnCours.setEtat(0)
        sinistreEnCours.setDateReparation(dateReparation)
        sinistreEnCours.lierTechnicien(tech)
        tech.lierSinistre(sinistreEnCours)
        return True

    def reparerSerre(self, idTech: int, idSerre: int, dateReparation: str) -> bool:
        tech = self.getTech(idTech)
        serre = self.getSerre(idSerre)
        if not tech or not serre:
            return False
        sinistreEnCours = serre.getSinistreEnCours()
        if sinistreEnCours is None:
            return False
        coutReparation = PV_MAX_SERRE - sinistreEnCours.getPtDeVieResultant()
        if self._nbPieceModuleStock < coutReparation:
            return False
        self._nbPieceModuleStock -= coutReparation
        sinistreEnCours.setEtat(0)
        sinistreEnCours.setDateReparation(dateReparation)
        sinistreEnCours.lierTechnicien(tech)
        tech.lierSinistre(sinistreEnCours)
        return True

    def supprimerMembre(self, idCmdt: int, idMembre: int) -> bool:
        if idCmdt == idMembre:
            return False
        cmdt = self.getCmdt(idCmdt)
        membre = self.getMembre(idMembre)
        if not cmdt or not membre:
            return False
        self._nbNourritureStock += RECYCLAGE
        membre.setEtat(0)
        return True

    def supprimerGarage(self, idTech: int, idGarage: int) -> bool:
        tech = self.getTech(idTech)
        garage = self.getGarage(idGarage)
        if not tech or not garage:
            return False
        if garage.getExpeditionEnCours() or garage.getSinistreEnCours():
            return False
        self._nbPieceModuleStock += RECYCLAGE_MODULE
        garage.setEtat(0)
        return True

    def supprimerSerre(self, idTech: int, idSerre: int) -> bool:
        tech = self.getTech(idTech)
        serre = self.getSerre(idSerre)
        if not tech or not serre:
            return False
        if serre.getSinistreEnCours():
            return False
        self._nbPieceModuleStock += RECYCLAGE_MODULE
        serre.setEtat(0)
        return True

    def donneeStocks(self) -> dict:
        return {
            "graines": self._nbGraineStock,
            "nourriture": self._nbNourritureStock,
            "piecesModule": self._nbPieceModuleStock,
        }
