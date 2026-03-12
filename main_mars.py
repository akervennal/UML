from Base import Base

print("=== Initialisation de la Base ===")
base = Base(0)  # commandant id=0

base._nbGraineStock = 100
base._nbNourritureStock = 50
base._nbPieceModuleStock = 200

print("\n=== UC1 — Ajouter un Membre d'équipage ===")
print(base.ajouterMembre(0, 1, "Technicien"))   # True
print(base.ajouterMembre(0, 1, "Technicien"))   # False (doublon)
print(base.ajouterMembre(99, 2, "Biologiste"))  # False (cmdt invalide)
print(base.ajouterMembre(0, 2, "Biologiste"))   # True
print(base.ajouterMembre(0, 3, "Chercheur"))    # True
print(base.ajouterMembre(0, 4, "Chercheur"))    # True
print(base.ajouterMembre(0, 5, "Chercheur"))    # True

print("\n=== UC2 — Créer un Module ===")
print(base.ajouterModule(1, 10, "Garage", 20))  # True
print(base.ajouterModule(1, 10, "Garage", 20))  # False (doublon)
print(base.ajouterModule(1, 11, "Serre", 15))   # True
print(base.ajouterModule(1, 12, "Autre", 10))   # False (type inconnu)

print("\n=== UC9 — Réceptionner une commande ===")
print(base.receptionnerCommande(0, 50, 20, 30))  # True
print(base.donneeStocks())

print("\n=== UC3 — Consommer de la nourriture ===")
print(base.consommerNourriture(1, 10))    # True
print(base.consommerNourriture(99, 10))   # False (membre invalide)
print(base.consommerNourriture(1, 9999))  # False (stock insuffisant)

print("\n=== UC7 — Planter des graines ===")
print(base.planterGraines(11, 2, 10, 500))   # True
print(base.planterGraines(11, 2, 9999, 501)) # False (stock insuffisant)
print(base.planterGraines(11, 2, 5, 500))    # False (id doublon)

print("\n=== UC10 — Récolter des plantations ===")
print(base.recolterPlantation(2, 11, 501))   # True
print(base.recolterPlantation(2, 11, 502))   # False (plus de plantes)

print("\n=== UC4 — Déclarer un sinistre Garage ===")
print(base.declarerSinistreGarage(1, 200, 10, "2025-01-01", 40))  # True
print(base.declarerSinistreGarage(1, 201, 10, "2025-01-02", 30))  # False (sinistre en cours)
print(base.declarerSinistreGarage(1, 200, 10, "2025-01-01", 40))  # False (id sinistre doublon)

print("\n=== UC5 — Déclarer un sinistre Serre ===")
print(base.declarerSinistreSerre(2, 300, 11, "2025-01-01", 50))   # True
print(base.declarerSinistreSerre(2, 301, 11, "2025-01-02", 20))   # False (sinistre en cours)

print("\n=== UC11 — Réparer un Garage ===")
print(base.reparerGarage(1, 10, "2025-02-01"))  # True

print("\n=== UC12 — Réparer une Serre ===")
print(base.reparerSerre(1, 11, "2025-02-01"))   # True

print("\n=== UC6 — Lancer une expédition ===")
print(base.lancerExpedition(3, 4, 5, 400, 10, "2025-03-01"))   # True (lanceur=3, p1=4, p2=5)
print(base.lancerExpedition(3, 4, 5, 401, 10, "2025-03-02"))   # False (4,5 en expédition)
print(base.lancerExpedition(3, 4, 4, 401, 10, "2025-03-02"))   # False (ids non distincts)

print("\n=== UC8 — Réceptionner une expédition ===")
# 3 est le lanceur (pas participant), donc il est libre pour réceptionner
print(base.receptionnerExpedition(3, 400, 5, "2025-03-10", 80))  # True (3 est libre)
# 4 est participant en expédition, donc invalide pour réceptionner
print(base.receptionnerExpedition(4, 400, 5, "2025-03-10", 80))  # False (déjà réceptionnée + 4 en expédition)

print("\n=== UC14 — Supprimer un Membre Equipage ===")
print(base.supprimerMembre(0, 2))   # True
print(base.supprimerMembre(0, 2))   # False (déjà supprimé)

print("\n=== UC15 — Supprimer un Garage ===")
print(base.supprimerGarage(1, 10))  # True
print(base.supprimerGarage(1, 10))  # False (déjà supprimé)

print("\n=== UC16 — Supprimer une Serre ===")
print(base.supprimerSerre(1, 11))   # True
print(base.supprimerSerre(1, 11))   # False (déjà supprimée)

print("\n=== Stocks finaux ===")
print(base.donneeStocks())
