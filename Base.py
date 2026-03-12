from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MembreEquipage import MembreEquipage
    from Garage import Garage
    from Serre import Serre
    from Sinistre import Sinistre

# Constantes de recyclage
RECYCLAGE = 10
RECYCLAGE_MODULE = 5
PV_MAX_GARAGE = 100
PV_MAX_SERRE = 100

# Rôles valides
ROLES_VALIDES = {"Commandant", "Technicien", "Biologiste", "Chercheur"}
ROLE_COMMANDANT = "Commandant"
ROLE_TECHNICIEN = "Technicien"
ROLE_BIOLOGISTE = "Biologiste"
ROLE_CHERCHEUR  = "Chercheur"


class Base:
    # Stocks
    _nbGraineStock: int
    _nbNourritureStock: int
    _nbPieceModuleStock: int

    # Collections
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
        self._mesMembres.append(MembreEquipage(idCmdt, ROLE_COMMANDANT, self))

    # -------------------------------------------------------------------------
    # Méthodes de vérification d'existence (appelées en interne)
    # -------------------------------------------------------------------------

    def estIdMembreValide(self, idMembre: int) -> bool:
        for m in self._mesMembres:
            if m.getId() == idMembre and m.getEtatMembreEquipage() == 1:
                return True
        return False

    def estIdCmdtValide(self, idCmdt: int) -> bool:
        for m in self._mesMembres:
            if m.getId() == idCmdt and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_COMMANDANT:
                return True
        return False

    def estIdTechValide(self, idTech: int) -> bool:
        for m in self._mesMembres:
            if m.getId() == idTech and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_TECHNICIEN:
                return True
        return False

    def estIdBioValide(self, idBio: int) -> bool:
        for m in self._mesMembres:
            if m.getId() == idBio and m.getEtatMembreEquipage() == 1 and m.getRoleMembre() == ROLE_BIOLOGISTE:
                return True
        return False

    def estIdChercheurValide(self, idChercheur: int) -> bool:
        for m in self._mesMembres:
            if (m.getId() == idChercheur and m.getEtatMembreEquipage() == 1
                    and m.getRoleMembre() == ROLE_CHERCHEUR
                    and not m.estEnExpedition()):
                return True
        return False

    def estIdGarageValide(self, idGarage: int) -> bool:
        for g in self._mesGarages:
            if g.getId() == idGarage and g.getEtat() == 1:
                return True
        return False

    def estIdSerreValide(self, idSerre: int) -> bool:
        for s in self._mesSerres:
            if s.getId() == idSerre and s.getEtat() == 1:
                return True
        return False

    def estIdModuleValide(self, idModule: int) -> bool:
        return self.estIdGarageValide(idModule) or self.estIdSerreValide(idModule)

    def estIdExpeditionValide(self, idExpedition: int) -> bool:
        for g in self._mesGarages:
            if g.aExpedition(idExpedition):
                return True
        return False

    def estIdSinistreValide(self, idSinistre: int) -> bool:
        for s in self._mesSinistres:
            if s.getId() == idSinistre:
                return True
        return False

    # -------------------------------------------------------------------------
    # Méthodes utilitaires internes
    # -------------------------------------------------------------------------

    def estIdEvenementSerreValide(self, idEvenement: int) -> bool:
        for s in self._mesSerres:
            for e in s._mesEvenements:
                if e.getId() == idEvenement:
                    return True
        return False

    # -------------------------------------------------------------------------
    # Méthodes de recherche (trouver)
    # -------------------------------------------------------------------------

    def trouverMembreEquipage(self, idMembre: int) -> "MembreEquipage":
        for m in self._mesMembres:
            if m.getId() == idMembre:
                return m
        return None

    def trouverGarage(self, idGarage: int) -> "Garage":
        for g in self._mesGarages:
            if g.getId() == idGarage:
                return g
        return None

    def trouverSerre(self, idSerre: int) -> "Serre":
        for s in self._mesSerres:
            if s.getId() == idSerre:
                return s
        return None

    def trouverExpedition(self, idExpedition: int):
        for g in self._mesGarages:
            expedition = g.trouverExpedition(idExpedition)
            if expedition is not None:
                return expedition
        return None

    # =========================================================================
    # UC1 — Ajouter un Membre d'équipage
    # =========================================================================
    def ajouterMembre(self, idCmdt: int, idMembre: int, role: str) -> bool:
        from MembreEquipage import MembreEquipage
        reponseIdCmdtValide = self.estIdCmdtValide(idCmdt)
        reponseIdMembreValide = self.estIdMembreValide(idMembre)

        if not reponseIdCmdtValide or reponseIdMembreValide:
            return False
        if role not in ROLES_VALIDES:
            return False

        self._mesMembres.append(MembreEquipage(idMembre, role, self))
        return True

    # =========================================================================
    # UC2 — Créer un Module (Serre ou Garage)
    # =========================================================================
    def ajouterModule(self, idTech: int, idModule: int, typeModule: str, coutModule: int) -> bool:
        from Serre import Serre
        from Garage import Garage

        reponseIdTechValide = self.estIdTechValide(idTech)
        reponseIdModuleValide = self.estIdModuleValide(idModule)

        if not reponseIdTechValide or reponseIdModuleValide or self._nbPieceModuleStock < coutModule:
            return False

        if typeModule == "Serre":
            nouvelleSerre = Serre(idModule, self)
            self._mesSerres.append(nouvelleSerre)
            self._nbPieceModuleStock -= coutModule
            return True
        elif typeModule == "Garage":
            nouveauGarage = Garage(idModule, self)
            self._mesGarages.append(nouveauGarage)
            self._nbPieceModuleStock -= coutModule
            return True
        else:
            return False

    # =========================================================================
    # UC3 — Consommer une denrée alimentaire
    # =========================================================================
    def consommerNourriture(self, idMembre: int, nbNourriture: int) -> bool:
        reponseIdMembreValide = self.estIdMembreValide(idMembre)

        if not reponseIdMembreValide or self._nbNourritureStock < nbNourriture:
            return False

        self._nbNourritureStock -= nbNourriture
        return True

    # =========================================================================
    # UC4 — Déclarer un Sinistre (Garage)
    # =========================================================================
    def declarerSinistreGarage(self, idMembreAuteur: int, idSinistre: int,
                                idGarage: int, dateCreation: str, ptDeVieResultant: int) -> bool:
        from Sinistre import Sinistre

        reponseIdMembreValide = self.estIdMembreValide(idMembreAuteur)
        reponseIdGarageValide = self.estIdGarageValide(idGarage)
        reponseIdSinistreValide = self.estIdSinistreValide(idSinistre)

        if not reponseIdMembreValide or not reponseIdGarageValide or reponseIdSinistreValide:
            return False

        garage = self.trouverGarage(idGarage)
        if garage.verifSinistreEnCours():
            return False

        nouveauSinistre = Sinistre(idSinistre, dateCreation, idMembreAuteur, ptDeVieResultant, self)
        self._mesSinistres.append(nouveauSinistre)

        membre = self.trouverMembreEquipage(idMembreAuteur)
        nouveauSinistre.lierMembreEquipage(membre)
        membre.lierSinistre(nouveauSinistre)

        garage.lierSinistre(nouveauSinistre)
        nouveauSinistre.lierModule(garage)

        return True

    # =========================================================================
    # UC5 — Déclarer un Sinistre (Serre)
    # =========================================================================
    def declarerSinistreSerre(self, idMembreAuteur: int, idSinistre: int,
                               idSerre: int, dateCreation: str, ptDeVieResultant: int) -> bool:
        from Sinistre import Sinistre

        reponseIdMembreValide = self.estIdMembreValide(idMembreAuteur)
        reponseIdSerreValide = self.estIdSerreValide(idSerre)
        reponseIdSinistreValide = self.estIdSinistreValide(idSinistre)

        if not reponseIdMembreValide or not reponseIdSerreValide or reponseIdSinistreValide:
            return False

        serre = self.trouverSerre(idSerre)
        if serre.verifSinistreEnCours():
            return False

        nouveauSinistre = Sinistre(idSinistre, dateCreation, idMembreAuteur, ptDeVieResultant, self)
        self._mesSinistres.append(nouveauSinistre)

        membre = self.trouverMembreEquipage(idMembreAuteur)
        nouveauSinistre.lierMembreEquipage(membre)
        membre.lierSinistre(nouveauSinistre)

        serre.lierSinistre(nouveauSinistre)
        nouveauSinistre.lierModule(serre)

        return True

    # =========================================================================
    # UC6 — Lancer une Expédition
    # =========================================================================
    def lancerExpedition(self, idChercheurLancement: int, idParticipant1: int,
                         idParticipant2: int, idExpedition: int,
                         idGarage: int, dateLancement: str) -> bool:
        """
        Valide les ids puis délègue la création au Garage.
        Le chercheur lanceur ne participe PAS à l'expédition.
        """
        reponseIdChercheurValide = self.estIdChercheurValide(idChercheurLancement)
        reponseIdParticipant1Valide = self.estIdChercheurValide(idParticipant1)
        reponseIdParticipant2Valide = self.estIdChercheurValide(idParticipant2)
        reponseIdExpeditionValide = self.estIdExpeditionValide(idExpedition)
        reponseIdGarageValide = self.estIdGarageValide(idGarage)

        if (not reponseIdChercheurValide or not reponseIdParticipant1Valide
                or not reponseIdParticipant2Valide
                or reponseIdExpeditionValide or not reponseIdGarageValide):
            return False

        # Les 3 ids doivent être distincts
        if len({idChercheurLancement, idParticipant1, idParticipant2}) != 3:
            return False

        garage = self.trouverGarage(idGarage)
        if garage.verifExpeditionEnCours():
            return False

        # Délégation au Garage (point 5)
        garage.creerExpedition(idChercheurLancement, idParticipant1,
                               idParticipant2, idExpedition, dateLancement)

        return True

    # =========================================================================
    # UC7 — Planter des Graines
    # =========================================================================
    def planterGraines(self, idSerre: int, idBio: int, nbGraine: int, idEvenement: int) -> bool:
        reponseIdBioValide = self.estIdBioValide(idBio)
        reponseIdSerreValide = self.estIdSerreValide(idSerre)
        reponseIdEvenementValide = self.estIdEvenementSerreValide(idEvenement)

        if self._nbGraineStock < nbGraine or not reponseIdBioValide or not reponseIdSerreValide or reponseIdEvenementValide:
            return False

        serre = self.trouverSerre(idSerre)
        serre.setNbPlantSerre(serre.getNbPlantSerre() + nbGraine)
        self._nbGraineStock -= nbGraine

        serre.creerEvenementSerre(idBio, idEvenement, nbGraine)
        return True

    # =========================================================================
    # UC8 — Réceptionner une Expédition
    # =========================================================================
    def receptionnerExpedition(self, idChercheurRetour: int, idExpedition: int,
                                nbPieceModule: int, dateRetour: str, ptDeVieResultant: int) -> bool:
        reponseIdChercheurValide = self.estIdChercheurValide(idChercheurRetour)
        reponseIdExpeditionValide = self.estIdExpeditionValide(idExpedition)

        if not reponseIdChercheurValide or not reponseIdExpeditionValide:
            return False

        garage = self._trouverGarageAvecExpedition(idExpedition)
        if garage is None:
            return False

        # Point 6 : on passe idExpedition pour vérifier la bonne expédition
        if not garage.receptionnerExpedition(idExpedition, dateRetour, ptDeVieResultant):
            return False

        self._nbPieceModuleStock += nbPieceModule

        expedition = self.trouverExpedition(idExpedition)
        chercheur = self.trouverMembreEquipage(idChercheurRetour)
        expedition.lierChercheurRetour(chercheur)
        chercheur.lierExpeditionReceptionnee(expedition)

        return True

    def _trouverGarageAvecExpedition(self, idExpedition: int) -> "Garage":
        for g in self._mesGarages:
            if g.aExpedition(idExpedition):
                return g
        return None

    # =========================================================================
    # UC9 — Réceptionner une commande
    # =========================================================================
    def receptionnerCommande(self, idCmdt: int, nbGraine: int, nbNourriture: int,
                              nbPieceModule: int) -> bool:
        reponseIdCmdtValide = self.estIdCmdtValide(idCmdt)

        if not reponseIdCmdtValide:
            return False

        self._nbGraineStock += nbGraine
        self._nbNourritureStock += nbNourriture
        self._nbPieceModuleStock += nbPieceModule
        return True

    # =========================================================================
    # UC10 — Récolter des Plantations
    # =========================================================================
    def recolterPlantation(self, idBio: int, idSerre: int, idEvenement: int) -> bool:
        reponseIdBioValide = self.estIdBioValide(idBio)
        reponseIdSerreValide = self.estIdSerreValide(idSerre)
        reponseIdEvenementValide = self.estIdEvenementSerreValide(idEvenement)

        if not reponseIdBioValide or not reponseIdSerreValide or reponseIdEvenementValide:
            return False

        serre = self.trouverSerre(idSerre)
        nbPlantSerre = serre.getNbPlantSerre()

        if nbPlantSerre == 0:
            return False

        self._nbNourritureStock += nbPlantSerre
        serre.setNbPlantSerre(0)

        serre.creerEvenementSerre(idBio, idEvenement, -nbPlantSerre)
        return True

    # =========================================================================
    # UC11 — Réparer un Garage
    # =========================================================================
    def reparerGarage(self, idTech: int, idGarage: int, dateReparation: str) -> bool:
        reponseIdTechValide = self.estIdTechValide(idTech)
        reponseIdModuleValide = self.estIdGarageValide(idGarage)

        if not reponseIdTechValide or not reponseIdModuleValide:
            return False

        garage = self.trouverGarage(idGarage)
        sinistreEnCours = garage.getSinistreEnCours()

        if sinistreEnCours is None:
            return False

        coutReparation = PV_MAX_GARAGE - sinistreEnCours.getPtDeVieResultant()

        if self._nbPieceModuleStock < coutReparation:
            return False

        self._nbPieceModuleStock -= coutReparation
        sinistreEnCours.setEtat(1)
        sinistreEnCours.setDateReparation(dateReparation)

        technicien = self.trouverMembreEquipage(idTech)
        sinistreEnCours.lierTechnicien(technicien)
        technicien.lierSinistre(sinistreEnCours)

        return True

    # =========================================================================
    # UC12 — Réparer une Serre
    # =========================================================================
    def reparerSerre(self, idTech: int, idModule: int, dateReparation: str) -> bool:
        reponseIdTechValide = self.estIdTechValide(idTech)
        reponseIdModuleValide = self.estIdSerreValide(idModule)

        if not reponseIdTechValide or not reponseIdModuleValide:
            return False

        serre = self.trouverSerre(idModule)
        sinistreEnCours = serre.getSinistreEnCours()

        if sinistreEnCours is None:
            return False

        coutReparation = PV_MAX_SERRE - sinistreEnCours.getPtDeVieResultant()

        if self._nbPieceModuleStock < coutReparation:
            return False

        self._nbPieceModuleStock -= coutReparation
        sinistreEnCours.setEtat(1)
        sinistreEnCours.setDateReparation(dateReparation)

        technicien = self.trouverMembreEquipage(idTech)
        sinistreEnCours.lierTechnicien(technicien)
        technicien.lierSinistre(sinistreEnCours)

        return True

    # =========================================================================
    # UC14 — Supprimer un Membre Equipage
    # =========================================================================
    def supprimerMembre(self, idCmdt: int, idMembre: int) -> bool:
        reponseIdCmdtValide = self.estIdCmdtValide(idCmdt)
        reponseIdMembreValide = self.estIdMembreValide(idMembre)

        if not reponseIdCmdtValide or not reponseIdMembreValide:
            return False

        membre = self.trouverMembreEquipage(idMembre)
        self._nbNourritureStock += RECYCLAGE
        membre.setEtat(0)
        return True

    # =========================================================================
    # UC15 — Supprimer un Garage
    # =========================================================================
    def supprimerGarage(self, idTech: int, idGarage: int) -> bool:
        reponseIdTechValide = self.estIdTechValide(idTech)
        reponseIdGarageValide = self.estIdGarageValide(idGarage)

        if not reponseIdTechValide or not reponseIdGarageValide:
            return False

        garage = self.trouverGarage(idGarage)
        self._nbPieceModuleStock += RECYCLAGE_MODULE
        garage.setEtat(0)
        return True

    # =========================================================================
    # UC16 — Supprimer une Serre
    # =========================================================================
    def supprimerSerre(self, idTech: int, idSerre: int) -> bool:
        reponseIdTechValide = self.estIdTechValide(idTech)
        reponseIdSerreValide = self.estIdSerreValide(idSerre)

        if not reponseIdTechValide or not reponseIdSerreValide:
            return False

        serre = self.trouverSerre(idSerre)
        self._nbPieceModuleStock += RECYCLAGE_MODULE
        serre.setEtat(0)
        return True

    # =========================================================================
    # Méthodes utilitaires
    # =========================================================================

    def donneeStocks(self):
        return {
            "graines": self._nbGraineStock,
            "nourriture": self._nbNourritureStock,
            "piecesModule": self._nbPieceModuleStock,
        }
