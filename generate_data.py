import random
import pickle
import csv
import os
from datetime import datetime, timedelta
from Base import Base

NB_GARAGES = 20
NB_SERRES = 20
NB_OPERATIONS = 1000
COUT_MODULE = 8

ROLES_DISTRIBUTION = {
    "Technicien": 25,
    "Biologiste": 25,
    "Chercheur": 48,
}

random.seed(42)
ID_CMDT = 1


def gen_date(jour):
    d = datetime(2040, 1, 1) + timedelta(days=jour)
    return d.strftime("%Y-%m-%d")


def rand_gauss_clamp(mu, sigma, lo, hi):
    val = random.gauss(mu, sigma)
    return int(max(lo, min(hi, round(val))))


def rand_expo_clamp(lam, lo, hi):
    val = random.expovariate(1 / lam)
    return int(max(lo, min(hi, round(val))))


def next_id(ids, key):
    val = ids[key]
    ids[key] += 1
    return val


def main():
    ids = {"membre": 2, "module": 1, "sinistre": 1, "expedition": 1, "evenement": 1}
    base = Base(ID_CMDT)

    historique_stocks = []
    log_operations = []
    log_expeditions = []
    log_sinistres = []
    log_recoltes = []
    log_consommation = []
    log_membres = []
    log_ravitaillements = []

    techniciens = []
    biologistes = []
    chercheurs = []
    garages_ids = []
    serres_ids = []
    expeditions_en_cours = []
    degats_par_module = {}

    # ----------------------------------------------------------------

    base.receptionnerCommande(ID_CMDT, 800, 2000, 500)
    log_operations.append((0, "commande", True, "graines=800, nourriture=2000, pieces=500"))
    log_ravitaillements.append((0, 800, 2000, 500))

    for role, count in ROLES_DISTRIBUTION.items():
        for _ in range(count):
            mid = next_id(ids, "membre")
            ok = base.ajouterMembre(ID_CMDT, mid, role)
            if ok:
                if role == "Technicien":
                    techniciens.append(mid)
                elif role == "Biologiste":
                    biologistes.append(mid)
                elif role == "Chercheur":
                    chercheurs.append(mid)
                log_membres.append((0, "ajout", mid, role))

    for _ in range(NB_GARAGES):
        mid = next_id(ids, "module")
        tech = random.choice(techniciens)
        ok = base.ajouterModule(tech, mid, "Garage", COUT_MODULE)
        if ok:
            garages_ids.append(mid)

    for _ in range(NB_SERRES):
        mid = next_id(ids, "module")
        tech = random.choice(techniciens)
        ok = base.ajouterModule(tech, mid, "Serre", COUT_MODULE)
        if ok:
            serres_ids.append(mid)

    stocks = base.donneeStocks()
    historique_stocks.append((0, stocks["graines"], stocks["nourriture"], stocks["piecesModule"]))

    # ----------------------------------------------------------------

    for jour in range(1, NB_OPERATIONS + 1):
        date = gen_date(jour)

        if jour % 20 == 0:
            g = random.randint(1800, 2500)
            n = random.randint(100, 300) if random.random() < 0.10 else 0
            p = random.randint(30, 60) if random.random() < 0.08 else 0
            ok = base.receptionnerCommande(ID_CMDT, g, n, p)
            if ok:
                log_ravitaillements.append((jour, g, n, p))
            log_operations.append((jour, "commande", ok, f"graines={g}, nourriture={n}, pieces={p}"))

        all_ids = [ID_CMDT] + techniciens + biologistes + chercheurs
        for mid in all_ids:
            ok = base.consommerNourriture(mid, 1)
            if ok:
                log_consommation.append((jour, mid, 1))

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
                else:
                    log_operations.append((jour, "suppression_membre", False, f"membre={mid}"))

        if random.random() < 0.05:
            role_ajout = random.choice(["Technicien", "Biologiste", "Chercheur"])
            mid = next_id(ids, "membre")
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
            else:
                log_operations.append((jour, "ajout_membre", False, f"membre={mid}, role={role_ajout}"))

        if techniciens:
            tech = random.choice(techniciens)
            for type_module, ids_list, seuil in [
                ("Garage", garages_ids, NB_GARAGES),
                ("Serre",  serres_ids,  NB_SERRES),
            ]:
                p_build = 0.40 if len(ids_list) < seuil else 0.01
                if random.random() < p_build:
                    mid = next_id(ids, "module")
                    ok = base.ajouterModule(tech, mid, type_module, COUT_MODULE)
                    if ok:
                        ids_list.append(mid)
                        log_operations.append((jour, "ajout_module", True, f"module={mid}, type={type_module}"))
                    else:
                        log_operations.append((jour, "ajout_module", False, f"module={mid}, type={type_module}"))

        if random.random() < 0.6 and biologistes and serres_ids:
            bio = random.choice(biologistes)
            nb_serres_plant = random.randint(4, 8)
            serres_choisies = random.sample(serres_ids, min(nb_serres_plant, len(serres_ids)))
            for serre in serres_choisies:
                nb_graines = random.randint(20, 40)
                eid = next_id(ids, "evenement")
                ok = base.planterGraines(serre, bio, nb_graines, eid)
                if ok:
                    log_operations.append((jour, "plantation", True, f"serre={serre}, graines={nb_graines}"))
                else:
                    log_operations.append((jour, "plantation", False, f"serre={serre}, graines={nb_graines}"))

        if random.random() < 0.4 and biologistes and serres_ids:
            bio = random.choice(biologistes)
            nb_serres_rec = random.randint(4, 8)
            serres_choisies = random.sample(serres_ids, min(nb_serres_rec, len(serres_ids)))
            for serre in serres_choisies:
                eid = next_id(ids, "evenement")
                serre_obj = base.getSerre(serre)
                nb_avant = serre_obj.getNbPlantSerre() if serre_obj else 0
                ok = base.recolterPlantation(bio, serre, eid)
                if ok:
                    serre_obj = base.getSerre(serre)
                    nb_apres = serre_obj.getNbPlantSerre() if serre_obj else 0
                    nourriture_recoltee = nb_avant - nb_apres
                    log_recoltes.append((jour, serre, nourriture_recoltee))
                    log_operations.append((jour, "recolte", True, f"serre={serre}, nourriture={nourriture_recoltee}"))
                else:
                    log_operations.append((jour, "recolte", False, f"serre={serre}"))

        if random.random() < 0.25 and len(chercheurs) >= 2 and garages_ids:
            garage = random.choice(garages_ids)
            pair = random.sample(chercheurs, 2)
            eid = next_id(ids, "expedition")
            ok = base.lancerExpedition(pair[0], pair[1], eid, garage, date)
            if ok:
                duree = rand_gauss_clamp(20, 8, 5, 45)
                expeditions_en_cours.append((eid, garage, jour, pair[1], pair[0], duree))
                log_operations.append((jour, "expedition_lancement", True, f"exp={eid}, garage={garage}"))
            else:
                log_operations.append((jour, "expedition_lancement", False, f"exp={eid}, garage={garage}"))

        nouvelles_en_cours = []
        for exp_info in expeditions_en_cours:
            eid, garage_id, jour_lance, participant_id, launcher_id, duree = exp_info
            if jour - jour_lance >= duree:
                date_retour = gen_date(jour)
                ptVie = random.randint(30, 100)
                nb_pieces = random.randint(15, 50)
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

        if random.random() < 0.10 and garages_ids:
            garage = random.choice(garages_ids)
            all_ids_sin = [ID_CMDT] + techniciens + biologistes + chercheurs
            auteur = random.choice(all_ids_sin)
            sid = next_id(ids, "sinistre")
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
            else:
                log_operations.append((jour, "sinistre_garage", False, f"garage={garage}, pv={ptVie}"))

        if random.random() < 0.08 and serres_ids:
            serre = random.choice(serres_ids)
            all_ids_sin = [ID_CMDT] + techniciens + biologistes + chercheurs
            auteur = random.choice(all_ids_sin)
            sid = next_id(ids, "sinistre")
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
            else:
                log_operations.append((jour, "sinistre_serre", False, f"serre={serre}, pv={ptVie}"))

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
                degats_par_module[sin["module_id"]] = 0
                log_operations.append((jour, "reparation", True, f"sinistre={sin['id']}, tech={tech}"))
            else:
                log_operations.append((jour, "reparation", False, f"sinistre={sin['id']}, tech={tech}"))

        if techniciens:
            tech = random.choice(techniciens)
            for gid in garages_ids[:]:
                p = min(0.01, degats_par_module.get(gid, 0) / 8000)
                if random.random() < p:
                    ok = base.supprimerGarage(tech, gid)
                    if ok:
                        garages_ids.remove(gid)
                        log_operations.append((jour, "suppression_garage", True, f"garage={gid}, degats={degats_par_module.get(gid,0)}"))
                    else:
                        log_operations.append((jour, "suppression_garage", False, f"garage={gid}"))
            for s_id in serres_ids[:]:
                p = min(0.01, degats_par_module.get(s_id, 0) / 8000)
                if random.random() < p:
                    ok = base.supprimerSerre(tech, s_id)
                    if ok:
                        serres_ids.remove(s_id)
                        log_operations.append((jour, "suppression_serre", True, f"serre={s_id}, degats={degats_par_module.get(s_id,0)}"))
                    else:
                        log_operations.append((jour, "suppression_serre", False, f"serre={s_id}"))

        stocks = base.donneeStocks()
        historique_stocks.append((jour, stocks["graines"], stocks["nourriture"], stocks["piecesModule"]))

    # ----------------------------------------------------------------

    donnees_membres = []
    for m in base.getMembres():
        is_cmdt = (m.getId() == ID_CMDT)
        donnees_membres.append({
            "id": m.getId(),
            "role": m.getRoleMembre(),
            "etat": m.getEtatMembreEquipage(),
            "nb_sinistres": m.getNbSinistres(),
            "nb_exp_lancees": m.getNbExpeditionsLancees(),
            "nb_exp_participees": m.getNbExpeditionsParticipees(),
            "nb_exp_receptionnees": m.getNbExpeditionsReceptionnees(),
            "nb_evenements_serre": m.getNbEvenementsSerre(),
            "nb_commandes_receptionnees": len(log_ravitaillements) if is_cmdt else 0,
            "nb_membres_ajoutes": sum(1 for l in log_membres if l[1] == "ajout") if is_cmdt else 0,
            "nb_membres_supprimes": sum(1 for l in log_membres if l[1] == "suppression") if is_cmdt else 0,
        })

    # ----------------------------------------------------------------

    data = {
        "historique_stocks": historique_stocks,
        "log_operations": log_operations,
        "log_expeditions": log_expeditions,
        "log_sinistres": log_sinistres,
        "log_recoltes": log_recoltes,
        "log_consommation": log_consommation,
        "log_ravitaillements": log_ravitaillements,
        "log_membres": log_membres,
        "donnees_membres": donnees_membres,
    }

    with open("simulation_data.pkl", "wb") as f:
        pickle.dump(data, f)

    csv_dir = "csv_data"
    os.makedirs(csv_dir, exist_ok=True)

    sinistres_headers = ["id", "type_module", "module_id", "date_creation", "pt_de_vie", "degats",
                         "date_reparation", "duree_reparation_jours", "technicien_id", "jour_creation"]
    sinistres_rows = [
        [s["id"], s["type"], s["module_id"], s["dateCreation"], s["ptDeVie"],
         s["degats"], s["dateReparation"], s["duree"], s["tech_id"], s["jour_creation"]]
        for s in log_sinistres
    ]

    membres_headers = ["id", "role", "etat", "nb_sinistres", "nb_exp_lancees",
                        "nb_exp_participees", "nb_exp_receptionnees", "nb_evenements_serre",
                        "nb_commandes_receptionnees", "nb_membres_ajoutes", "nb_membres_supprimes"]
    membres_rows = [[m[k] for k in membres_headers] for m in donnees_membres]

    csv_exports = [
        ("historique_stocks",     ["jour", "graines", "nourriture", "pieces_module"],                   historique_stocks),
        ("log_operations",        ["jour", "type_operation", "succes", "details"],                      log_operations),
        ("log_expeditions",       ["id", "date_lancement", "date_retour", "duree_jours",
                                   "pt_de_vie_resultant", "garage_id"],                                 log_expeditions),
        ("log_sinistres",         sinistres_headers,                                                    sinistres_rows),
        ("log_recoltes",          ["jour", "serre_id", "nourriture_produite"],                          log_recoltes),
        ("log_consommation",      ["jour", "membre_id", "nb_nourriture"],                               log_consommation),
        ("log_ravitaillements",   ["jour", "graines", "nourriture", "pieces"],                          log_ravitaillements),
        ("log_membres",           ["jour", "action", "membre_id", "role"],                              log_membres),
        ("donnees_membres",       membres_headers,                                                      membres_rows),
    ]

    for name, headers, rows in csv_exports:
        with open(f"{csv_dir}/{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for row in rows:
                w.writerow(row)

    print(f"Simulation terminee : {NB_OPERATIONS} jours simules.")
    print(f"  Membres : {len(donnees_membres)}")
    print(f"  Expeditions terminees : {len(log_expeditions)}")
    print(f"  Sinistres : {len(log_sinistres)}")
    print(f"  Operations totales : {len(log_operations)}")
    print(f"Donnees exportees dans simulation_data.pkl + {csv_dir}/ ({len(csv_exports)} fichiers CSV)")


if __name__ == "__main__":
    main()
