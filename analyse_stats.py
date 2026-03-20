"""
Analyses statistiques et graphiques de la simulation de base martienne.
Charge les donnees de simulation_data.pkl et genere 9 graphiques.
"""
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict

# --- Chargement des donnees ---
with open("simulation_data.pkl", "rb") as f:
    data = pickle.load(f)

historique_stocks = data["historique_stocks"]
historique_effectifs = data["historique_effectifs"]
historique_modules = data["historique_modules"]
log_operations = data["log_operations"]
log_expeditions = data["log_expeditions"]
log_sinistres = data["log_sinistres"]
log_recoltes = data["log_recoltes"]
log_plantations = data["log_plantations"]
log_consommation = data["log_consommation"]
log_ravitaillements = data["log_ravitaillements"]
donnees_membres = data["donnees_membres"]
donnees_serres = data["donnees_serres"]
donnees_garages = data["donnees_garages"]

# --- Dossier de sortie ---
os.makedirs("graphiques", exist_ok=True)


def save_and_show(fig, filename):
    fig.savefig(f"graphiques/{filename}", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ================================================================
# 1. LINE CHART - Evolution des stocks (avec moyenne mobile)
# ================================================================
jours = [s[0] for s in historique_stocks]
graines = [s[1] for s in historique_stocks]
nourriture = [s[2] for s in historique_stocks]
pieces = [s[3] for s in historique_stocks]

def moving_avg(data, window=30):
    arr = np.array(data, dtype=float)
    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="same")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

# Courbes brutes en fond
ax1.plot(jours, graines, alpha=0.2, color="tab:blue")
ax1.plot(jours, nourriture, alpha=0.2, color="tab:orange")
ax1.plot(jours, pieces, alpha=0.2, color="tab:green")
# Moyennes mobiles
ax1.plot(jours, moving_avg(graines), label="Graines (moy. mobile 30j)", color="tab:blue", linewidth=2)
ax1.plot(jours, moving_avg(nourriture), label="Nourriture (moy. mobile 30j)", color="tab:orange", linewidth=2)
ax1.plot(jours, moving_avg(pieces), label="Pieces module (moy. mobile 30j)", color="tab:green", linewidth=2)
ax1.axhspan(0, 20, color="red", alpha=0.08, label="Zone critique (< 20)")
ax1.set_ylabel("Quantite en stock")
ax1.set_title("1. Evolution des stocks au fil du temps")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# Sous-graphique : stock nourriture seul avec zone critique
ax2.fill_between(jours, nourriture, alpha=0.3, color="tab:orange")
ax2.plot(jours, moving_avg(nourriture), color="tab:orange", linewidth=2, label="Nourriture (moy. mobile)")
ax2.axhline(y=20, color="red", linestyle="--", alpha=0.7, label="Seuil critique")
ax2.set_xlabel("Jour de simulation")
ax2.set_ylabel("Stock nourriture")
ax2.set_title("Zoom sur le stock de nourriture")
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

fig.tight_layout()
save_and_show(fig, "01_evolution_stocks.png")

# ================================================================
# 2. BAR CHART - Balance nourriture (sans la periode initiale J0-50)
# ================================================================
periode = 50
nb_periodes = max(jours) // periode + 1

production_par_periode = [0] * nb_periodes
ravitaillement_par_periode = [0] * nb_periodes
consommation_par_periode = [0] * nb_periodes

for jour, serre_id, nb in log_recoltes:
    idx = jour // periode
    if idx < nb_periodes:
        production_par_periode[idx] += nb

for jour, g, n, p in log_ravitaillements:
    idx = jour // periode
    if idx < nb_periodes:
        ravitaillement_par_periode[idx] += n

for jour, membre_id, nb in log_consommation:
    idx = jour // periode
    if idx < nb_periodes:
        consommation_par_periode[idx] += nb

# Exclure la 1ere periode (commande initiale massive qui ecrase l'echelle)
start = 1
x = np.arange(start, nb_periodes)
labels = [f"J{i*periode}-{(i+1)*periode}" for i in range(start, nb_periodes)]

fig, ax = plt.subplots(figsize=(13, 5))
width = 0.27
ax.bar(x - width, production_par_periode[start:], width, label="Production (recoltes)", color="#27ae60", alpha=0.8)
ax.bar(x, ravitaillement_par_periode[start:], width, label="Ravitaillement (commandes)", color="#3498db", alpha=0.8)
ax.bar(x + width, consommation_par_periode[start:], width, label="Consommation", color="#e74c3c", alpha=0.8)

# Solde net en ligne
solde = [p + r - c for p, r, c in zip(production_par_periode[start:],
         ravitaillement_par_periode[start:], consommation_par_periode[start:])]
ax.plot(x, solde, "ko--", label="Solde net", markersize=4, linewidth=1.5)
ax.axhline(y=0, color="black", linestyle="-", alpha=0.3)

ax.set_xlabel("Periode")
ax.set_ylabel("Quantite de nourriture")
ax.set_title("2. Balance nourriture : production + ravitaillement vs consommation (hors periode initiale)")
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3, axis="y")
save_and_show(fig, "02_balance_nourriture.png")

# ================================================================
# 3. HISTOGRAM - Distribution des durees d'expedition (avec ecart-type)
# ================================================================
if log_expeditions:
    durees = [exp[3] for exp in log_expeditions]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Histogramme
    n_bins, bins, patches = ax1.hist(durees, bins=15, color="steelblue", edgecolor="black", alpha=0.7)
    moy = np.mean(durees)
    med = np.median(durees)
    std = np.std(durees)
    ax1.axvline(moy, color="red", linestyle="--", linewidth=2, label=f"Moyenne = {moy:.1f}j")
    ax1.axvline(med, color="orange", linestyle="--", linewidth=2, label=f"Mediane = {med:.1f}j")
    # Zone ecart-type
    ax1.axvspan(moy - std, moy + std, color="red", alpha=0.08, label=f"Ecart-type = {std:.1f}j")
    ax1.set_xlabel("Duree (jours)")
    ax1.set_ylabel("Nombre d'expeditions")
    ax1.set_title(f"3. Distribution des durees d'expedition (n={len(durees)})")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3, axis="y")

    # Box plot
    bp = ax2.boxplot(durees, vert=True, patch_artist=True)
    bp["boxes"][0].set_facecolor("steelblue")
    bp["boxes"][0].set_alpha(0.5)
    ax2.set_ylabel("Duree (jours)")
    ax2.set_title("Box plot des durees")
    ax2.set_xticklabels(["Expeditions"])
    ax2.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    save_and_show(fig, "03_durees_expedition.png")

# ================================================================
# 4. PIE CHART - Repartition sinistres Garage vs Serre
# ================================================================
if log_sinistres:
    nb_sin_garage = sum(1 for s in log_sinistres if s["type"] == "Garage")
    nb_sin_serre = sum(1 for s in log_sinistres if s["type"] == "Serre")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Pie chart
    ax1.pie([nb_sin_garage, nb_sin_serre],
            labels=[f"Garage ({nb_sin_garage})", f"Serre ({nb_sin_serre})"],
            autopct="%1.1f%%", colors=["#ff9999", "#66b3ff"], startangle=90)
    ax1.set_title("4. Repartition des sinistres par type")

    # Bar chart : nb sinistres par module individuel
    sinistres_par_module = defaultdict(lambda: {"Garage": 0, "Serre": 0})
    for s in log_sinistres:
        key = f"{s['type'][0]}{s['module_id']}"
        sinistres_par_module[key][s["type"]] += 1

    modules_tries = sorted(sinistres_par_module.items(), key=lambda x: sum(x[1].values()), reverse=True)[:20]
    noms = [m[0] for m in modules_tries]
    vals = [sum(m[1].values()) for m in modules_tries]
    colors = ["#ff9999" if n.startswith("G") else "#66b3ff" for n in noms]

    ax2.bar(range(len(noms)), vals, color=colors, edgecolor="black", alpha=0.7)
    ax2.set_xticks(range(len(noms)))
    ax2.set_xticklabels(noms, rotation=45, fontsize=8)
    ax2.set_xlabel("Module")
    ax2.set_ylabel("Nombre de sinistres")
    ax2.set_title("Sinistres par module (top 20)")
    ax2.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    save_and_show(fig, "04_sinistres_repartition.png")

# ================================================================
# 5. HISTOGRAM - Distribution des degats (exponentielle)
# ================================================================
if log_sinistres:
    degats_sin = [s.get("degats", 100 - s["ptDeVie"]) for s in log_sinistres]

    fig, ax = plt.subplots(figsize=(10, 5))
    n_vals, bins, patches = ax.hist(degats_sin, bins=18, color="tomato", edgecolor="black", alpha=0.7)

    # Colorier par zone de gravite
    for patch, left_edge in zip(patches, bins[:-1]):
        if left_edge < 30:
            patch.set_facecolor("#2ecc71")
        elif left_edge < 60:
            patch.set_facecolor("#f39c12")
        else:
            patch.set_facecolor("#e74c3c")

    ax.axvline(np.mean(degats_sin), color="blue", linestyle="--", linewidth=2)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2ecc71", label=f"Mineur (<30) : {sum(1 for d in degats_sin if d < 30)}"),
        Patch(facecolor="#f39c12", label=f"Modere (30-60) : {sum(1 for d in degats_sin if 30 <= d < 60)}"),
        Patch(facecolor="#e74c3c", label=f"Critique (>60) : {sum(1 for d in degats_sin if d >= 60)}"),
        plt.Line2D([0], [0], color="blue", linestyle="--", label=f"Moyenne = {np.mean(degats_sin):.1f}"),
    ]
    ax.legend(handles=legend_elements, fontsize=9)
    ax.set_xlabel("Points de vie perdus (degats)")
    ax.set_ylabel("Nombre de sinistres")
    ax.set_title("5. Distribution de la gravite des sinistres")
    ax.grid(True, alpha=0.3, axis="y")
    save_and_show(fig, "05_distribution_degats.png")

# ================================================================
# 6. BAR CHART - Duree des sinistres avant reparation
# ================================================================
sinistres_repares = [s for s in log_sinistres if s["dateReparation"] is not None]
if sinistres_repares:
    durees_sin = [s["duree"] for s in sinistres_repares]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Histogramme des durees de sinistre
    ax1.hist(durees_sin, bins=15, color="mediumpurple", edgecolor="black", alpha=0.7)
    moy_sin = np.mean(durees_sin)
    med_sin = np.median(durees_sin)
    ax1.axvline(moy_sin, color="red", linestyle="--", linewidth=2, label=f"Moyenne = {moy_sin:.1f}j")
    ax1.axvline(med_sin, color="orange", linestyle="--", linewidth=2, label=f"Mediane = {med_sin:.1f}j")
    ax1.set_xlabel("Duree avant reparation (jours)")
    ax1.set_ylabel("Nombre de sinistres")
    ax1.set_title("6. Duree des sinistres avant reparation")
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis="y")

    # Duree par type de module
    durees_garage = [s["duree"] for s in sinistres_repares if s["type"] == "Garage"]
    durees_serre = [s["duree"] for s in sinistres_repares if s["type"] == "Serre"]
    bp = ax2.boxplot([durees_garage, durees_serre], vert=True, patch_artist=True,
                     tick_labels=["Garage", "Serre"])
    bp["boxes"][0].set_facecolor("#ff9999")
    bp["boxes"][0].set_alpha(0.6)
    bp["boxes"][1].set_facecolor("#66b3ff")
    bp["boxes"][1].set_alpha(0.6)
    ax2.set_ylabel("Duree (jours)")
    ax2.set_title("Comparaison Garage vs Serre")
    ax2.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    save_and_show(fig, "06_duree_sinistres.png")

# ================================================================
# 7. BAR CHART GROUPE - Effectifs vs charge de travail par role
# ================================================================
roles = [m["role"] for m in donnees_membres if m["etat"] == 1]
role_counts = Counter(roles)

charge_par_role = defaultdict(int)
for m in donnees_membres:
    if m["etat"] == 1:
        total = (m["nb_sinistres"] + m["nb_exp_lancees"] + m["nb_exp_participees"]
                 + m["nb_exp_receptionnees"] + m["nb_evenements_serre"]
                 + m["nb_commandes_receptionnees"] + m["nb_membres_ajoutes"]
                 + m["nb_membres_supprimes"])
        charge_par_role[m["role"]] += total

colors_roles = {"Commandant": "#ff6b6b", "Technicien": "#4ecdc4",
                "Biologiste": "#45b7d1", "Chercheur": "#f9ca24"}

# Ordre coherent
role_order = ["Commandant", "Technicien", "Biologiste", "Chercheur"]
role_order = [r for r in role_order if r in role_counts]

effectifs = [role_counts[r] for r in role_order]
charges = [charge_par_role[r] for r in role_order]
total_eff = sum(effectifs)
total_charge = sum(charges)

# Normaliser en pourcentage pour comparer
pct_effectifs = [e / total_eff * 100 for e in effectifs]
pct_charges = [c / total_charge * 100 for c in charges]

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(role_order))
width = 0.35
colors_list = [colors_roles[r] for r in role_order]

bars1 = ax.bar(x - width/2, pct_effectifs, width, label="% des effectifs",
               color=colors_list, alpha=0.6, edgecolor="black")
bars2 = ax.bar(x + width/2, pct_charges, width, label="% de la charge de travail",
               color=colors_list, alpha=1.0, edgecolor="black")

# Annotations
for bar, pct, val in zip(bars1, pct_effectifs, effectifs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{pct:.0f}%\n({val})", ha="center", va="bottom", fontsize=8)
for bar, pct, val in zip(bars2, pct_charges, charges):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{pct:.0f}%\n({val})", ha="center", va="bottom", fontsize=8)

ax.set_ylabel("Pourcentage (%)")
ax.set_title("7. Effectifs vs charge de travail reelle par role")
ax.set_xticks(x)
ax.set_xticklabels(role_order, fontsize=10)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylim(0, max(max(pct_effectifs), max(pct_charges)) + 15)
fig.tight_layout()
save_and_show(fig, "07_repartition_roles.png")

# ================================================================
# 8. HEATMAP - Matrice de correlation
# ================================================================
periode_corr = 20
nb_p = max(jours) // periode_corr + 1

series = {
    "Nourriture": [0.0] * nb_p,
    "Graines": [0.0] * nb_p,
    "Pieces": [0.0] * nb_p,
    "Sinistres": [0.0] * nb_p,
    "Expeditions": [0.0] * nb_p,
    "Recoltes": [0.0] * nb_p,
    "Consommation": [0.0] * nb_p,
}

count_stocks = [0] * nb_p
for jour, g, n, p in historique_stocks:
    idx = jour // periode_corr
    if idx < nb_p:
        series["Graines"][idx] += g
        series["Nourriture"][idx] += n
        series["Pieces"][idx] += p
        count_stocks[idx] += 1
for i in range(nb_p):
    if count_stocks[i] > 0:
        series["Graines"][i] /= count_stocks[i]
        series["Nourriture"][i] /= count_stocks[i]
        series["Pieces"][i] /= count_stocks[i]

for s in log_sinistres:
    idx = s["jour_creation"] // periode_corr
    if idx < nb_p:
        series["Sinistres"][idx] += 1

for jour, type_op, ok, details in log_operations:
    if type_op == "expedition_lancement" and ok:
        idx = jour // periode_corr
        if idx < nb_p:
            series["Expeditions"][idx] += 1

for jour, serre_id, nb in log_recoltes:
    idx = jour // periode_corr
    if idx < nb_p:
        series["Recoltes"][idx] += nb

for jour, mid, nb in log_consommation:
    idx = jour // periode_corr
    if idx < nb_p:
        series["Consommation"][idx] += nb

keys = list(series.keys())
matrix = np.array([series[k] for k in keys])
corr = np.corrcoef(matrix)

fig, ax = plt.subplots(figsize=(9, 8))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(keys)))
ax.set_yticks(range(len(keys)))
ax.set_xticklabels(keys, rotation=45, ha="right")
ax.set_yticklabels(keys)
for i in range(len(keys)):
    for j in range(len(keys)):
        ax.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center",
                color="white" if abs(corr[i, j]) > 0.5 else "black", fontsize=9)
fig.colorbar(im, shrink=0.8)
ax.set_title("8. Matrice de correlation entre variables cles")
fig.tight_layout()
save_and_show(fig, "08_heatmap_correlation.png")

# ================================================================
# 9. LINE CHART - Evolution des effectifs par role
# ================================================================
jours_eff = [e[0] for e in historique_effectifs]
total_eff  = [e[1] for e in historique_effectifs]
tech_eff   = [e[2] for e in historique_effectifs]
bio_eff    = [e[3] for e in historique_effectifs]
cher_eff   = [e[4] for e in historique_effectifs]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

# Haut : lignes par role + total
ax1.plot(jours_eff, total_eff, color="black", linewidth=2.5, label="Total")
ax1.plot(jours_eff, tech_eff,  color="#4ecdc4", linewidth=1.5, label="Techniciens")
ax1.plot(jours_eff, bio_eff,   color="#45b7d1", linewidth=1.5, label="Biologistes")
ax1.plot(jours_eff, cher_eff,  color="#f9ca24", linewidth=1.5, label="Chercheurs")
ax1.set_ylabel("Nombre de membres actifs")
ax1.set_title("9. Evolution des effectifs au fil du temps")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# Bas : aires empilees pour voir la composition
ax2.stackplot(jours_eff, tech_eff, bio_eff, cher_eff,
              labels=["Techniciens", "Biologistes", "Chercheurs"],
              colors=["#4ecdc4", "#45b7d1", "#f9ca24"], alpha=0.8)
ax2.set_xlabel("Jour de simulation")
ax2.set_ylabel("Composition de l'equipe")
ax2.set_title("Composition par role (aires empilees)")
ax2.legend(fontsize=9, loc="upper left")
ax2.grid(True, alpha=0.3)

fig.tight_layout()
save_and_show(fig, "09_evolution_effectifs.png")

# ================================================================
# 10. LINE CHART - Evolution des modules actifs (Bernoulli conditionnelle)
# ================================================================
jours_mod   = [m[0] for m in historique_modules]
garages_act = [m[1] for m in historique_modules]
serres_act  = [m[2] for m in historique_modules]

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(jours_mod, garages_act, color="#ff9999", linewidth=2, label="Garages actifs")
ax.plot(jours_mod, serres_act,  color="#66b3ff", linewidth=2, label="Serres actives")
ax.fill_between(jours_mod, garages_act, alpha=0.2, color="#ff9999")
ax.fill_between(jours_mod, serres_act,  alpha=0.2, color="#66b3ff")
ax.set_xlabel("Jour de simulation")
ax.set_ylabel("Nombre de modules actifs")
ax.set_title("10. Evolution des modules actifs\n(suppressions selon loi de Bernoulli conditionnelle aux degats cumules)")
ax.legend(fontsize=9)
ax.set_ylim(0, max(max(garages_act), max(serres_act)) + 2)
ax.grid(True, alpha=0.3)
fig.tight_layout()
save_and_show(fig, "10_evolution_modules.png")

# ================================================================
# 12. BAR CHART GROUPE - Activite par serre (plante / recolte / sinistres)
# ================================================================
if donnees_serres:
    serres_tries = sorted(donnees_serres, key=lambda s: s["total_plante"], reverse=True)
    ids_s  = [f"S{s['id']}" for s in serres_tries]
    tp     = [s["total_plante"]  for s in serres_tries]
    tr     = [s["total_recolte"] for s in serres_tries]
    ns     = [s["nb_sinistres"]  for s in serres_tries]
    x      = np.arange(len(ids_s))
    width  = 0.3

    fig, ax1 = plt.subplots(figsize=(13, 6))
    ax1.bar(x - width, tp, width, label="Total plante",  color="#27ae60", alpha=0.8, edgecolor="black")
    ax1.bar(x,         tr, width, label="Total recolte", color="#e67e22", alpha=0.8, edgecolor="black")
    ax1.set_xlabel("Serre")
    ax1.set_ylabel("Quantite (graines / nourriture)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(ids_s, rotation=45, fontsize=8)
    ax1.grid(True, alpha=0.3, axis="y")

    ax2 = ax1.twinx()
    ax2.bar(x + width, ns, width, label="Nb sinistres", color="#e74c3c", alpha=0.7, edgecolor="black")
    ax2.set_ylabel("Nombre de sinistres", color="#e74c3c")
    ax2.tick_params(axis="y", labelcolor="#e74c3c")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper right")
    ax1.set_title("12. Activite par serre : plantations, recoltes et sinistres")
    fig.tight_layout()
    save_and_show(fig, "12_performance_serres.png")

# ================================================================
# 13. BAR CHART - Taux de reussite par type d'operation
# ================================================================
succes_par_type  = defaultdict(int)
echecs_par_type  = defaultdict(int)
for jour, type_op, ok, details in log_operations:
    if ok:
        succes_par_type[type_op] += 1
    else:
        echecs_par_type[type_op] += 1

types_ops = sorted(succes_par_type.keys() | echecs_par_type.keys(),
                   key=lambda t: succes_par_type[t] + echecs_par_type[t], reverse=True)
totaux    = [succes_par_type[t] + echecs_par_type[t] for t in types_ops]
taux      = [100 * succes_par_type[t] / tot if tot > 0 else 0
             for t, tot in zip(types_ops, totaux)]

couleurs = ["#27ae60" if tx >= 95 else "#f39c12" if tx >= 75 else "#e74c3c" for tx in taux]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(types_ops, taux, color=couleurs, edgecolor="black", alpha=0.85)
ax.axvline(100, color="gray", linestyle="--", alpha=0.4)

for bar, tx, tot in zip(bars, taux, totaux):
    ax.text(min(tx + 1, 98), bar.get_y() + bar.get_height() / 2,
            f"{tx:.1f}%  (n={tot})", va="center", fontsize=8)

ax.set_xlabel("Taux de reussite (%)")
ax.set_title("13. Taux de reussite par type d'operation")
ax.set_xlim(0, 115)
ax.grid(True, alpha=0.3, axis="x")
fig.tight_layout()
save_and_show(fig, "13_taux_reussite_operations.png")

# ================================================================
# 14. BOX PLOT - Duree de reparation par technicien (top actifs)
# ================================================================
sinistres_repares_tech = [s for s in log_sinistres
                          if s["dateReparation"] is not None and s["tech_id"] is not None]
if sinistres_repares_tech:
    durees_par_tech = defaultdict(list)
    for s in sinistres_repares_tech:
        durees_par_tech[s["tech_id"]].append(s["duree"])

    # Garder les 15 techniciens les plus actifs
    top_techs = sorted(durees_par_tech.items(), key=lambda x: len(x[1]), reverse=True)[:15]
    labels_tech = [f"T{tid}\n(n={len(d)})" for tid, d in top_techs]
    data_tech   = [d for _, d in top_techs]

    fig, ax = plt.subplots(figsize=(13, 6))
    bp = ax.boxplot(data_tech, patch_artist=True, tick_labels=labels_tech)
    for patch in bp["boxes"]:
        patch.set_facecolor("#4ecdc4")
        patch.set_alpha(0.6)

    moy_glob = np.mean([s["duree"] for s in sinistres_repares_tech])
    ax.axhline(moy_glob, color="red", linestyle="--", linewidth=1.5,
               label=f"Moyenne globale = {moy_glob:.1f}j")

    ax.set_xlabel("Technicien (n = nb reparations)")
    ax.set_ylabel("Duree de reparation (jours)")
    ax.set_title("14. Duree de reparation par technicien (top 15 les plus actifs)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    save_and_show(fig, "14_reparations_par_technicien.png")

print("\n=== Analyses terminees ===")
print(f"13 graphiques sauvegardes dans le dossier 'graphiques/'")
