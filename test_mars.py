import pytest
from Base import Base


# ---------------------------------------------------------------------------
# Fixture partagée — état construit progressivement (scope module)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def base():
    """Initialise la base avec le commandant (id=0) et les stocks de départ."""
    b = Base(0)  # commandant id=0
    b.receptionnerCommande(0, 100, 50, 200)
    return b


# ---------------------------------------------------------------------------
# UC1 — Ajouter un Membre d'équipage
# ---------------------------------------------------------------------------

def test_uc1_ajouter_technicien(base):
    assert base.ajouterMembre(0, 1, "Technicien") is True

def test_uc1_ajouter_technicien_doublon(base):
    assert base.ajouterMembre(0, 1, "Technicien") is False  # doublon

def test_uc1_ajouter_biologiste_cmdt_invalide(base):
    assert base.ajouterMembre(99, 2, "Biologiste") is False  # commandant inconnu

def test_uc1_ajouter_biologiste(base):
    assert base.ajouterMembre(0, 2, "Biologiste") is True

def test_uc1_ajouter_chercheur_3(base):
    assert base.ajouterMembre(0, 3, "Chercheur") is True

def test_uc1_ajouter_chercheur_4(base):
    assert base.ajouterMembre(0, 4, "Chercheur") is True

def test_uc1_ajouter_chercheur_5(base):
    assert base.ajouterMembre(0, 5, "Chercheur") is True


# ---------------------------------------------------------------------------
# UC2 — Créer un Module (Garage / Serre)
# ---------------------------------------------------------------------------

def test_uc2_creer_garage(base):
    assert base.ajouterModule(1, 10, "Garage", 20) is True

def test_uc2_creer_garage_doublon(base):
    assert base.ajouterModule(1, 10, "Garage", 20) is False  # doublon

def test_uc2_creer_serre(base):
    assert base.ajouterModule(1, 11, "Serre", 15) is True

def test_uc2_creer_module_type_inconnu(base):
    assert base.ajouterModule(1, 12, "Autre", 10) is False  # type invalide


# ---------------------------------------------------------------------------
# UC9 — Réceptionner une commande
# ---------------------------------------------------------------------------

def test_uc9_receptionner_commande(base):
    assert base.receptionnerCommande(0, 50, 20, 30) is True

def test_uc9_stocks_apres_commande(base):
    stocks = base.donneeStocks()
    # graines: 100 + 50 = 150  (modules ne déduisent pas les graines)
    # nourriture: 50 + 20 = 70
    # piecesModule: 200 - 20 - 15 + 30 = 195
    assert stocks["graines"] == 150
    assert stocks["nourriture"] == 70
    assert stocks["piecesModule"] == 195


# ---------------------------------------------------------------------------
# UC3 — Consommer de la nourriture
# ---------------------------------------------------------------------------

def test_uc3_consommer_nourriture(base):
    assert base.consommerNourriture(1, 10) is True

def test_uc3_consommer_nourriture_membre_invalide(base):
    assert base.consommerNourriture(99, 10) is False  # membre inconnu

def test_uc3_consommer_nourriture_stock_insuffisant(base):
    assert base.consommerNourriture(1, 9999) is False  # stock insuffisant


# ---------------------------------------------------------------------------
# UC7 — Planter des graines
# ---------------------------------------------------------------------------

def test_uc7_planter_graines(base):
    assert base.planterGraines(11, 2, 10, 500) is True

def test_uc7_planter_graines_stock_insuffisant(base):
    assert base.planterGraines(11, 2, 9999, 501) is False  # stock insuffisant

def test_uc7_planter_graines_evenement_doublon(base):
    assert base.planterGraines(11, 2, 5, 500) is False  # id événement doublon


# ---------------------------------------------------------------------------
# UC10 — Récolter des plantations
# ---------------------------------------------------------------------------

def test_uc10_recolter_plantation(base):
    assert base.recolterPlantation(2, 11, 501) is True

def test_uc10_recolter_plantation_plus_de_plantes(base):
    assert base.recolterPlantation(2, 11, 502) is False  # serre vide


# ---------------------------------------------------------------------------
# UC4 — Déclarer un sinistre Garage
# ---------------------------------------------------------------------------

def test_uc4_declarer_sinistre_garage(base):
    assert base.declarerSinistreGarage(1, 200, 10, "2025-01-01", 40) is True

def test_uc4_declarer_sinistre_garage_sinistre_en_cours(base):
    assert base.declarerSinistreGarage(1, 201, 10, "2025-01-02", 30) is False  # sinistre déjà en cours

def test_uc4_declarer_sinistre_garage_id_doublon(base):
    assert base.declarerSinistreGarage(1, 200, 10, "2025-01-01", 40) is False  # id sinistre doublon


# ---------------------------------------------------------------------------
# UC5 — Déclarer un sinistre Serre
# ---------------------------------------------------------------------------

def test_uc5_declarer_sinistre_serre(base):
    assert base.declarerSinistreSerre(2, 300, 11, "2025-01-01", 50) is True

def test_uc5_declarer_sinistre_serre_en_cours(base):
    assert base.declarerSinistreSerre(2, 301, 11, "2025-01-02", 20) is False  # sinistre déjà en cours


# ---------------------------------------------------------------------------
# UC11 — Réparer un Garage
# ---------------------------------------------------------------------------

def test_uc11_reparer_garage(base):
    assert base.reparerGarage(1, 10, "2025-02-01") is True


# ---------------------------------------------------------------------------
# UC12 — Réparer une Serre
# ---------------------------------------------------------------------------

def test_uc12_reparer_serre(base):
    assert base.reparerSerre(1, 11, "2025-02-01") is True


# ---------------------------------------------------------------------------
# UC6 — Lancer une expédition
# ---------------------------------------------------------------------------

def test_uc6_lancer_expedition(base):
    # lanceur=3, participant=4, garage=10
    assert base.lancerExpedition(3, 4, 400, 10, "2025-03-01") is True

def test_uc6_lancer_expedition_participant_en_expedition(base):
    assert base.lancerExpedition(3, 4, 401, 10, "2025-03-02") is False  # 4 déjà en expédition

def test_uc6_lancer_expedition_ids_non_distincts(base):
    assert base.lancerExpedition(3, 3, 401, 10, "2025-03-02") is False  # lanceur == participant


# ---------------------------------------------------------------------------
# UC8 — Réceptionner une expédition
# ---------------------------------------------------------------------------

def test_uc8_receptionner_expedition(base):
    # chercheur 3 est le lanceur (libre), peut réceptionner
    assert base.receptionnerExpedition(3, 400, 5, "2025-03-10", 80) is True

def test_uc8_receptionner_expedition_deja_receptionnee(base):
    # expédition 400 déjà réceptionnée (etat=0) — invalide
    assert base.receptionnerExpedition(3, 400, 5, "2025-03-10", 80) is False


# ---------------------------------------------------------------------------
# UC14 — Supprimer un Membre Equipage
# ---------------------------------------------------------------------------

def test_uc14_supprimer_membre(base):
    assert base.supprimerMembre(0, 2) is True

def test_uc14_supprimer_membre_deja_supprime(base):
    assert base.supprimerMembre(0, 2) is False  # déjà supprimé


# ---------------------------------------------------------------------------
# UC15 — Supprimer un Garage
# ---------------------------------------------------------------------------

def test_uc15_supprimer_garage(base):
    assert base.supprimerGarage(1, 10) is True

def test_uc15_supprimer_garage_deja_supprime(base):
    assert base.supprimerGarage(1, 10) is False  # déjà supprimé


# ---------------------------------------------------------------------------
# UC16 — Supprimer une Serre
# ---------------------------------------------------------------------------

def test_uc16_supprimer_serre(base):
    assert base.supprimerSerre(1, 11) is True

def test_uc16_supprimer_serre_deja_supprimee(base):
    assert base.supprimerSerre(1, 11) is False  # déjà supprimée
