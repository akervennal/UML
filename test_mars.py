import pytest
from Base import Base


@pytest.fixture(scope="module")
def base():
    b = Base(0)
    b.receptionnerCommande(0, 100, 50, 200)
    return b

# ----------------------------------------------------------------

def test_uc1_ajouter_technicien(base):
    assert base.ajouterMembre(0, 1, "Technicien") is True

def test_uc1_ajouter_technicien_doublon(base):
    assert base.ajouterMembre(0, 1, "Technicien") is False

def test_uc1_ajouter_biologiste_cmdt_invalide(base):
    assert base.ajouterMembre(99, 2, "Biologiste") is False

def test_uc1_ajouter_biologiste(base):
    assert base.ajouterMembre(0, 2, "Biologiste") is True

def test_uc1_ajouter_chercheur_3(base):
    assert base.ajouterMembre(0, 3, "Chercheur") is True

def test_uc1_ajouter_chercheur_4(base):
    assert base.ajouterMembre(0, 4, "Chercheur") is True

def test_uc1_ajouter_chercheur_5(base):
    assert base.ajouterMembre(0, 5, "Chercheur") is True

# ----------------------------------------------------------------

def test_uc2_creer_garage(base):
    assert base.ajouterModule(1, 10, "Garage", 20) is True

def test_uc2_creer_garage_doublon(base):
    assert base.ajouterModule(1, 10, "Garage", 20) is False

def test_uc2_creer_serre(base):
    assert base.ajouterModule(1, 11, "Serre", 15) is True

def test_uc2_creer_module_type_inconnu(base):
    assert base.ajouterModule(1, 12, "Autre", 10) is False

# ----------------------------------------------------------------

def test_uc9_receptionner_commande(base):
    assert base.receptionnerCommande(0, 50, 20, 30) is True

def test_uc9_stocks_apres_commande(base):
    stocks = base.donneeStocks()
    assert stocks["graines"] == 150
    assert stocks["nourriture"] == 70
    assert stocks["piecesModule"] == 195

# ----------------------------------------------------------------

def test_uc3_consommer_nourriture(base):
    assert base.consommerNourriture(1, 10) is True

def test_uc3_consommer_nourriture_membre_invalide(base):
    assert base.consommerNourriture(99, 10) is False

def test_uc3_consommer_nourriture_stock_insuffisant(base):
    assert base.consommerNourriture(1, 9999) is False

# ----------------------------------------------------------------

def test_uc7_planter_graines(base):
    assert base.planterGraines(11, 2, 10, 500) is True

def test_uc7_planter_graines_stock_insuffisant(base):
    assert base.planterGraines(11, 2, 9999, 501) is False

def test_uc7_planter_graines_evenement_doublon(base):
    assert base.planterGraines(11, 2, 5, 500) is False

# ----------------------------------------------------------------

def test_uc10_recolter_plantation(base):
    assert base.recolterPlantation(2, 11, 501) is True

def test_uc10_recolter_plantation_plus_de_plantes(base):
    assert base.recolterPlantation(2, 11, 502) is False

# ----------------------------------------------------------------

def test_uc4_declarer_sinistre_garage(base):
    assert base.declarerSinistreGarage(1, 200, 10, "2025-01-01", 40) is True

def test_uc4_declarer_sinistre_garage_sinistre_en_cours(base):
    assert base.declarerSinistreGarage(1, 201, 10, "2025-01-02", 30) is False

def test_uc4_declarer_sinistre_garage_id_doublon(base):
    assert base.declarerSinistreGarage(1, 200, 10, "2025-01-01", 40) is False

def test_supprimer_garage_sinistre_en_cours(base):
    assert base.supprimerGarage(1, 10) is False

# ----------------------------------------------------------------

def test_uc5_declarer_sinistre_serre(base):
    assert base.declarerSinistreSerre(2, 300, 11, "2025-01-01", 50) is True

def test_uc5_declarer_sinistre_serre_en_cours(base):
    assert base.declarerSinistreSerre(2, 301, 11, "2025-01-02", 20) is False

def test_supprimer_serre_sinistre_en_cours(base):
    assert base.supprimerSerre(1, 11) is False

# ----------------------------------------------------------------

def test_uc11_reparer_garage(base):
    assert base.reparerGarage(1, 10, "2025-02-01") is True

def test_uc12_reparer_serre(base):
    assert base.reparerSerre(1, 11, "2025-02-01") is True

# ----------------------------------------------------------------

def test_uc6_lancer_expedition(base):
    assert base.lancerExpedition(3, 4, 400, 10, "2025-03-01") is True

def test_uc6_lancer_expedition_participant_en_expedition(base):
    assert base.lancerExpedition(3, 4, 401, 10, "2025-03-02") is False

def test_uc6_lancer_expedition_ids_non_distincts(base):
    assert base.lancerExpedition(3, 3, 401, 10, "2025-03-02") is False

def test_ajouter_membre_doublon_en_expedition(base):
    assert base.ajouterMembre(0, 4, "Chercheur") is False

def test_supprimer_garage_expedition_en_cours(base):
    assert base.supprimerGarage(1, 10) is False

# ----------------------------------------------------------------

def test_uc8_receptionner_expedition(base):
    assert base.receptionnerExpedition(3, 400, 5, "2025-03-10", 80) is True

def test_uc8_receptionner_expedition_deja_receptionnee(base):
    assert base.receptionnerExpedition(3, 400, 5, "2025-03-10", 80) is False

# ----------------------------------------------------------------

def test_uc14_supprimer_membre(base):
    assert base.supprimerMembre(0, 2) is True

def test_uc14_supprimer_membre_deja_supprime(base):
    assert base.supprimerMembre(0, 2) is False

def test_uc14_supprimer_commandant_lui_meme(base):
    assert base.supprimerMembre(0, 0) is False

# ----------------------------------------------------------------

def test_uc15_supprimer_garage(base):
    assert base.supprimerGarage(1, 10) is True

def test_uc15_supprimer_garage_deja_supprime(base):
    assert base.supprimerGarage(1, 10) is False

# ----------------------------------------------------------------

def test_uc16_supprimer_serre(base):
    assert base.supprimerSerre(1, 11) is True

def test_uc16_supprimer_serre_deja_supprimee(base):
    assert base.supprimerSerre(1, 11) is False
