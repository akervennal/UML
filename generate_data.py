"""
Generateur de donnees massives pour la base martienne.
Simule ~1000 operations aleatoires et exporte les donnees collectees en pickle.
"""
import random
import math
import pickle
import csv
import os
from datetime import datetime, timedelta
from Base import Base

# --- Configuration ---
NB_GARAGES = 20
NB_SERRES = 20
NB_OPERATIONS = 1000
COUT_MODULE = 8

# Repartition des roles (hors commandant deja cree)
ROLES_DISTRIBUTION = {
    "Technicien": 25,
    "Biologiste": 25,
    "Chercheur": 48,
}

random.seed(42)

# --- Compteurs d'IDs uniques ---
next_membre_id = 2      # 1 = commandant
next_module_id = 1
next_sinistre_id = 1
next_expedition_id = 1
next_evenement_id = 1

ID_CMDT = 1


def gen_date(jour):
    """Genere une date string a partir du jour de simulation."""
    d = datetime(2040, 1, 1) + timedelta(days=jour)
    return d.strftime("%Y-%m-%d")


def rand_gauss_clamp(mu, sigma, lo, hi):
    """Genere un entier selon une loi normale tronquee."""
    val = random.gauss(mu, sigma)
    return int(max(lo, min(hi, round(val))))


def rand_expo_clamp(lam, lo, hi):
    """Genere un entier selon une loi exponentielle tronquee."""
    val = random.expovariate(1 / lam)
    return int(max(lo, min(hi, round(val))))


def main():
    global next_membre_id, next_module_id, next_sinistre_id
    global next_expedition_id, next_evenement_id

    base = Base(ID_CMDT)

    # --- Listes pour collecter les donnees ---
    historique_stocks = []       # (jour, graines, nourriture, pieces)
    historique_effectifs = []    # (jour, total, techniciens, biologistes, chercheurs)
    historique_modules = []      # (jour, nb_garages_actifs, nb_serres_actifs)
    log_operations = []          # (jour, type_op, succes, details)
    log_expeditions = []         # (id, dateLancement, dateRetour, duree_jours, ptDeVie, garage_id)
    log_sinistres = []           # dict avec id, type, module_id, dates, ptDeVie, duree, tech_id
    log_recoltes = []            # (jour, serre_id, nb_nourriture_produite)
    log_plantations = []         # (jour, serre_id, nb_graines)
    log_consommation = []        # (jour, membre_id, nb_nourriture)
    log_membres = []             # (jour, action, id, role)
    log_ravitaillements = []     # (jour, graines, nourriture, pieces)

    # Listes de suivi interne
    techniciens = []
    biologistes = []
    chercheurs = []
    garages_ids = []
    serres_ids = []
    expeditions_en_cours = []
    degats_par_module = {}   # module_id -> degats cumules (pour loi de suppression)

    # ================================================================
    # PHASE 1 : Initialisation (commande + membres + modules)
    # ================================================================
    # Grosse commande initiale
    base.receptionnerCommande(ID_CMDT, 800, 2000, 500)
    log_operations.append((0, "commande", True, "graines=800, nourriture=2000, pieces=500"))
    log_ravitaillements.append((0, 800, 2000, 500))

    # Ajout des membres
    for role, count in ROLES_DISTRIBUTION.items():
        for _ in range(count):
            mid = next_membre_id
            next_membre_id += 1
            ok = base.ajouterMembre(ID_CMDT, mid, role)
            if ok:
                if role == "Technicien":
                    techniciens.append(mid)
                elif role == "Biologiste":
                    biologistes.append(mid)
                elif role == "Chercheur":
                    chercheurs.append(mid)
                log_membres.append((0, "ajout", mid, role))

    # Creation des modules
    for _ in range(NB_GARAGES):
        mid = next_module_id
        next_module_id += 1
        tech = random.choice(techniciens)
        ok = base.ajouterModule(tech, mid, "Garage", COUT_MODULE)
        if ok:
            garages_ids.append(mid)

    for _ in range(NB_SERRES):
        mid = next_module_id
        next_module_id += 1
        tech = random.choice(techniciens)
        ok = base.ajouterModule(tech, mid, "Serre", COUT_MODULE)
        if ok:
            serres_ids.append(mid)

    # Snapshot initial
    stocks = base.donneeStocks()
    historique_stocks.append((0, stocks["graines"], stocks["nourriture"], stocks["piecesModule"]))

    # ================================================================
    # PHASE 2 : Simulation des operations
    # ================================================================
    for jour in range(1, NB_OPERATIONS + 1):
        date = gen_date(jour)

        # --- Commande de ravitaillement periodique (tous les 20 jours) ---
        # La nourriture provient exclusivement des serres (hors init). Le ravitaillement
        # fournit uniquement des graines (pour le cycle agricole) et des pieces.
        if jour % 20 == 0:
            g = random.randint(1800, 2500)
            n = 0
            p = random.randint(30, 80)
            ok = base.receptionnerCommande(ID_CMDT, g, n, p)
            if ok:
                log_ravitaillements.append((jour, g, n, p))
            log_operations.append((jour, "commande", ok, f"graines={g}, nourriture={n}, pieces={p}"))

        # --- Consommation quotidienne : chaque membre consomme 1 nourriture par jour ---
        all_ids = [ID_CMDT] + techniciens + biologistes + chercheurs
        for mid in all_ids:
            ok = base.consommerNourriture(mid, 1)
            if ok:
                log_consommation.append((jour, mid, 1))

        # --- Suppression de membre (probabilite 3%) ---
        if random.random() < 0.03:
            all_non_cmdt = techniciens + biologistes + chercheurs
            if all_non_cmdt:
                mid = random.choice(all_non_cmdt)
                ok = base.supprimerMembre(ID_CMDT, mid)
                if ok:
                    if mid in techniciens:
                        techniciens.remove(mid)
                        role_supp = "Technicien"
                    elif mid in biologistes:
                        biologistes.remove(mid)
                        role_supp = "Biologiste"
                    else:
                        chercheurs.remove(mid)
                        role_supp = "Chercheur"
                    log_membres.append((jour, "suppression", mid, role_supp))
                    log_operations.append((jour, "suppression_membre", True, f"membre={mid}, role={role_supp}"))

        # --- Ajout de membre (probabilite 5%) ---
        if random.random() < 0.05:
            role_ajout = random.choice(["Technicien", "Biologiste", "Chercheur"])
            mid = next_membre_id
            next_membre_id += 1
            ok = base.ajouterMembre(ID_CMDT, mid, role_ajout)
            if ok:
                if role_ajout == "Technicien":
                    techniciens.append(mid)
                elif role_ajout == "Biologiste":
                    biologistes.append(mid)
                else:
                    chercheurs.append(mid)
                log_membres.append((jour, "ajout", mid, role_ajout))
                log_operations.append((jour, "ajout_membre", True, f"membre={mid}, role={role_ajout}"))

        # --- Ajout de module : mode maintenance si sous le seuil initial ---
        if techniciens:
            tech = random.choice(techniciens)
            for type_module, ids_list, seuil in [
                ("Garage", garages_ids, NB_GARAGES),
                ("Serre",  serres_ids,  NB_SERRES),
            ]:
                p_build = 0.40 if len(ids_list) < seuil else 0.01
                if random.random() < p_build:
                    mid = next_module_id
                    next_module_id += 1
                    ok = base.ajouterModule(tech, mid, type_module, COUT_MODULE)
                    if ok:
                        ids_list.append(mid)
                        log_operations.append((jour, "ajout_module", True, f"module={mid}, type={type_module}"))

        # --- Plantation (probabilite 60%, plusieurs serres par event) ---
        if random.random() < 0.6 and biologistes and serres_ids:
            bio = random.choice(biologistes)
            nb_serres_plant = random.randint(4, 8)
            serres_choisies = random.sample(serres_ids, min(nb_serres_plant, len(serres_ids)))
            for serre in serres_choisies:
                nb_graines = random.randint(20, 40)
                eid = next_evenement_id
                next_evenement_id += 1
                ok = base.planterGraines(serre, bio, nb_graines, eid)
                if ok:
                    log_plantations.append((jour, serre, nb_graines))
                    log_operations.append((jour, "plantation", True, f"serre={serre}, graines={nb_graines}"))

        # --- Recolte (probabilite 40%, plusieurs serres par event) ---
        if random.random() < 0.4 and biologistes and serres_ids:
            bio = random.choice(biologistes)
            nb_serres_rec = random.randint(4, 8)
            serres_choisies = random.sample(serres_ids, min(nb_serres_rec, len(serres_ids)))
            for serre in serres_choisies:
                eid = next_evenement_id
                next_evenement_id += 1
                serre_obj = base.getIdSerreValide(serre)
                nb_avant = serre_obj.getNbPlantSerre() if serre_obj else 0
                ok = base.recolterPlantation(bio, serre, eid)
                if ok:
                    serre_obj = base.getIdSerreValide(serre)
                    nb_apres = serre_obj.getNbPlantSerre() if serre_obj else 0
                    nourriture_recoltee = nb_avant - nb_apres
                    log_recoltes.append((jour, serre, nourriture_recoltee))
                    log_operations.append((jour, "recolte", True, f"serre={serre}, nourriture={nourriture_recoltee}"))

        # --- Lancer expedition (probabilite 25%) ---
        if random.random() < 0.25 and len(chercheurs) >= 2 and garages_ids:
            garage = random.choice(garages_ids)
            pair = random.sample(chercheurs, 2)
            eid = next_expedition_id
            next_expedition_id += 1
            ok = base.lancerExpedition(pair[0], pair[1], eid, garage, date)
            if ok:
                duree = rand_gauss_clamp(20, 8, 5, 45)
                expeditions_en_cours.append((eid, garage, jour, pair[1], pair[0], duree))
                log_operations.append((jour, "expedition_lancement", True, f"exp={eid}, garage={garage}"))

        # --- Receptionner expeditions terminees ---
        nouvelles_en_cours = []
        for exp_info in expeditions_en_cours:
            eid, garage_id, jour_lance, participant_id, launcher_id, duree = exp_info
            if jour - jour_lance >= duree:
                date_retour = gen_date(jour)
                ptVie = random.randint(30, 100)
                nb_pieces = random.randint(2, 15)
                receptionneurs = [c for c in chercheurs if c != participant_id and c != launcher_id]
                if not receptionneurs:
                    receptionneurs = [c for c in chercheurs if c != participant_id]
                if receptionneurs:
                    recep = random.choice(receptionneurs)
                    ok = base.receptionnerExpedition(recep, eid, nb_pieces, date_retour, ptVie)
                    if ok:
                        duree_reelle = jour - jour_lance
                        log_expeditions.append((eid, gen_date(jour_lance), date_retour, duree_reelle, ptVie, garage_id))
                        log_operations.append((jour, "expedition_retour", True, f"exp={eid}, pieces={nb_pieces}"))
                    else:
                        nouvelles_en_cours.append(exp_info)
                else:
                    nouvelles_en_cours.append(exp_info)
            else:
                nouvelles_en_cours.append(exp_info)
        expeditions_en_cours = nouvelles_en_cours

        # --- Sinistre garage (probabilite 10%) ---
        if random.random() < 0.10 and garages_ids:
            garage = random.choice(garages_ids)
            all_ids = [ID_CMDT] + techniciens + biologistes + chercheurs
            auteur = random.choice(all_ids)
            sid = next_sinistre_id
            next_sinistre_id += 1
            # Distribution exponentielle : beaucoup de petits degats, peu de gros
            degats = rand_expo_clamp(30, 5, 85)
            ptVie = 100 - degats
            ok = base.declarerSinistreGarage(auteur, sid, garage, date, ptVie)
            if ok:
                degats_par_module[garage] = degats_par_module.get(garage, 0) + degats
                log_sinistres.append({
                    "id": sid, "type": "Garage", "module_id": garage,
                    "dateCreation": date, "ptDeVie": ptVie, "degats": degats,
                    "dateReparation": None, "duree": None, "tech_id": None,
                    "jour_creation": jour
                })
                log_operations.append((jour, "sinistre_garage", True, f"garage={garage}, pv={ptVie}"))

        # --- Sinistre serre (probabilite 8%) ---
        if random.random() < 0.08 and serres_ids:
            serre = random.choice(serres_ids)
            all_ids = [ID_CMDT] + techniciens + biologistes + chercheurs
            auteur = random.choice(all_ids)
            sid = next_sinistre_id
            next_sinistre_id += 1
            degats = rand_expo_clamp(30, 5, 85)
            ptVie = 100 - degats
            ok = base.declarerSinistreSerre(auteur, sid, serre, date, ptVie)
            if ok:
                degats_par_module[serre] = degats_par_module.get(serre, 0) + degats
                log_sinistres.append({
                    "id": sid, "type": "Serre", "module_id": serre,
                    "dateCreation": date, "ptDeVie": ptVie, "degats": degats,
                    "dateReparation": None, "duree": None, "tech_id": None,
                    "jour_creation": jour
                })
                log_operations.append((jour, "sinistre_serre", True, f"serre={serre}, pv={ptVie}"))

        # --- Reparation (probabilite 40% si sinistres en cours) ---
        sinistres_non_repares = [s for s in log_sinistres if s["dateReparation"] is None]
        if random.random() < 0.40 and sinistres_non_repares and techniciens:
            sin = random.choice(sinistres_non_repares)
            tech = random.choice(techniciens)
            if sin["type"] == "Garage":
                ok = base.reparerGarage(tech, sin["module_id"], date)
            else:
                ok = base.reparerSerre(tech, sin["module_id"], date)
            if ok:
                sin["dateReparation"] = date
                sin["duree"] = jour - sin["jour_creation"]
                sin["tech_id"] = tech
                degats_par_module[sin["module_id"]] = 0  # module repare : degats remis a zero
                log_operations.append((jour, "reparation", True, f"sinistre={sin['id']}, tech={tech}"))

        # --- Suppression de modules (Bernoulli conditionnelle aux degats cumules) ---
        if techniciens:
            tech = random.choice(techniciens)
            for gid in garages_ids[:]:
                p = min(0.01, degats_par_module.get(gid, 0) / 8000)
                if random.random() < p:
                    ok = base.supprimerGarage(tech, gid)
                    if ok:
                        garages_ids.remove(gid)
                        log_operations.append((jour, "suppression_garage", True, f"garage={gid}, degats={degats_par_module.get(gid,0)}"))
            for sid in serres_ids[:]:
                p = min(0.01, degats_par_module.get(sid, 0) / 8000)
                if random.random() < p:
                    ok = base.supprimerSerre(tech, sid)
                    if ok:
                        serres_ids.remove(sid)
                        log_operations.append((jour, "suppression_serre", True, f"serre={sid}, degats={degats_par_module.get(sid,0)}"))

        # --- Snapshot des stocks et des effectifs ---
        stocks = base.donneeStocks()
        historique_stocks.append((jour, stocks["graines"], stocks["nourriture"], stocks["piecesModule"]))
        historique_effectifs.append((
            jour,
            1 + len(techniciens) + len(biologistes) + len(chercheurs),
            len(techniciens),
            len(biologistes),
            len(chercheurs),
        ))
        historique_modules.append((jour, len(garages_ids), len(serres_ids)))

    # ================================================================
    # PHASE 3 : Collecte des donnees finales depuis les objets
    # ================================================================
    donnees_membres = []
    for m in base._mesMembres:
        is_cmdt = (m.getId() == ID_CMDT)
        donnees_membres.append({
            "id": m.getId(),
            "role": m.getRoleMembre(),
            "etat": m.getEtatMembreEquipage(),
            "nb_sinistres": len(m._mesSinistres),
            "nb_exp_lancees": len(m._mesExpeditionsLancees),
            "nb_exp_participees": len(m._mesExpeditionsParticipees),
            "nb_exp_receptionnees": len(m._mesExpeditionsReceptionnees),
            "nb_evenements_serre": len(m._mesEvenementsSerre),
            "nb_commandes_receptionnees": len(log_ravitaillements) if is_cmdt else 0,
            "nb_membres_ajoutes": sum(1 for l in log_membres if l[1] == "ajout") if is_cmdt else 0,
            "nb_membres_supprimes": sum(1 for l in log_membres if l[1] == "suppression") if is_cmdt else 0,
        })

    donnees_serres = []
    for s in base._mesSerres:
        total_plante = sum(e.getNbGraine() for e in s._mesEvenements if e.getNbGraine() > 0)
        total_recolte = sum(-e.getNbGraine() for e in s._mesEvenements if e.getNbGraine() < 0)
        donnees_serres.append({
            "id": s.getId(),
            "etat": s.getEtat(),
            "plantes_actuelles": s.getNbPlantSerre(),
            "total_plante": total_plante,
            "total_recolte": total_recolte,
            "nb_evenements": len(s._mesEvenements),
            "nb_sinistres": len(s._mesSinistres),
        })

    donnees_garages = []
    for g in base._mesGarages:
        nb_exp = len(g._mesExpeditions)
        degats_cumules = sum(100 - sin.getPtDeVieResultant() for sin in g._mesSinistres)
        donnees_garages.append({
            "id": g.getId(),
            "etat": g.getEtat(),
            "nb_expeditions": nb_exp,
            "nb_sinistres": len(g._mesSinistres),
            "degats_cumules": degats_cumules,
        })

    # ================================================================
    # Export pickle (pour analyse_stats.py)
    # ================================================================
    data = {
        "historique_stocks": historique_stocks,
        "historique_effectifs": historique_effectifs,
        "historique_modules": historique_modules,
        "log_operations": log_operations,
        "log_expeditions": log_expeditions,
        "log_sinistres": log_sinistres,
        "log_recoltes": log_recoltes,
        "log_plantations": log_plantations,
        "log_consommation": log_consommation,
        "log_ravitaillements": log_ravitaillements,
        "log_membres": log_membres,
        "donnees_membres": donnees_membres,
        "donnees_serres": donnees_serres,
        "donnees_garages": donnees_garages,
    }

    with open("simulation_data.pkl", "wb") as f:
        pickle.dump(data, f)

    # ================================================================
    # Export CSV
    # ================================================================
    csv_dir = "csv_data"
    os.makedirs(csv_dir, exist_ok=True)

    # 0b. historique_modules.csv
    with open(f"{csv_dir}/historique_modules.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "garages_actifs", "serres_actives"])
        for row in historique_modules:
            w.writerow(row)

    # 0. historique_effectifs.csv
    with open(f"{csv_dir}/historique_effectifs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "total", "techniciens", "biologistes", "chercheurs"])
        for row in historique_effectifs:
            w.writerow(row)

    # 1. historique_stocks.csv
    with open(f"{csv_dir}/historique_stocks.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "graines", "nourriture", "pieces_module"])
        for row in historique_stocks:
            w.writerow(row)

    # 2. log_operations.csv
    with open(f"{csv_dir}/log_operations.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "type_operation", "succes", "details"])
        for row in log_operations:
            w.writerow(row)

    # 3. log_expeditions.csv
    with open(f"{csv_dir}/log_expeditions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "date_lancement", "date_retour", "duree_jours", "pt_de_vie_resultant", "garage_id"])
        for row in log_expeditions:
            w.writerow(row)

    # 4. log_sinistres.csv
    with open(f"{csv_dir}/log_sinistres.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "type_module", "module_id", "date_creation", "pt_de_vie", "degats",
                     "date_reparation", "duree_reparation_jours", "technicien_id", "jour_creation"])
        for s in log_sinistres:
            w.writerow([s["id"], s["type"], s["module_id"], s["dateCreation"], s["ptDeVie"],
                        s["degats"], s["dateReparation"], s["duree"], s["tech_id"], s["jour_creation"]])

    # 5. log_recoltes.csv
    with open(f"{csv_dir}/log_recoltes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "serre_id", "nourriture_produite"])
        for row in log_recoltes:
            w.writerow(row)

    # 6. log_plantations.csv
    with open(f"{csv_dir}/log_plantations.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "serre_id", "nb_graines"])
        for row in log_plantations:
            w.writerow(row)

    # 7. log_consommation.csv
    with open(f"{csv_dir}/log_consommation.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "membre_id", "nb_nourriture"])
        for row in log_consommation:
            w.writerow(row)

    # 8. log_ravitaillements.csv
    with open(f"{csv_dir}/log_ravitaillements.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "graines", "nourriture", "pieces"])
        for row in log_ravitaillements:
            w.writerow(row)

    # 9. log_membres.csv
    with open(f"{csv_dir}/log_membres.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["jour", "action", "membre_id", "role"])
        for row in log_membres:
            w.writerow(row)

    # 10. donnees_membres.csv
    with open(f"{csv_dir}/donnees_membres.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "role", "etat", "nb_sinistres", "nb_exp_lancees",
                     "nb_exp_participees", "nb_exp_receptionnees", "nb_evenements_serre",
                     "nb_commandes_receptionnees", "nb_membres_ajoutes", "nb_membres_supprimes"])
        for m in donnees_membres:
            w.writerow([m["id"], m["role"], m["etat"], m["nb_sinistres"], m["nb_exp_lancees"],
                        m["nb_exp_participees"], m["nb_exp_receptionnees"], m["nb_evenements_serre"],
                        m["nb_commandes_receptionnees"], m["nb_membres_ajoutes"], m["nb_membres_supprimes"]])

    # 11. donnees_serres.csv
    with open(f"{csv_dir}/donnees_serres.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "etat", "plantes_actuelles", "total_plante", "total_recolte",
                     "nb_evenements", "nb_sinistres"])
        for s in donnees_serres:
            w.writerow([s["id"], s["etat"], s["plantes_actuelles"], s["total_plante"],
                        s["total_recolte"], s["nb_evenements"], s["nb_sinistres"]])

    # 12. donnees_garages.csv
    with open(f"{csv_dir}/donnees_garages.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "etat", "nb_expeditions", "nb_sinistres", "degats_cumules"])
        for g in donnees_garages:
            w.writerow([g["id"], g["etat"], g["nb_expeditions"], g["nb_sinistres"], g["degats_cumules"]])

    print(f"Simulation terminee : {NB_OPERATIONS} jours simules.")
    print(f"  Membres : {len(donnees_membres)}")
    print(f"  Garages : {len(donnees_garages)}")
    print(f"  Serres  : {len(donnees_serres)}")
    print(f"  Expeditions terminees : {len(log_expeditions)}")
    print(f"  Sinistres : {len(log_sinistres)}")
    print(f"  Operations totales : {len(log_operations)}")
    print(f"Donnees exportees dans simulation_data.pkl + {csv_dir}/ (12 fichiers CSV)")


if __name__ == "__main__":
    main()
