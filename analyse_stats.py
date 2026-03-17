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
    plt.show()


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
                 + m["nb_exp_receptionnees"] + m["nb_evenements_serre"])
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

for jour, g, n, p in historique_stocks:
    idx = jour // periode_corr
    if idx < nb_p:
        series["Graines"][idx] = g
        series["Nourriture"][idx] = n
        series["Pieces"][idx] = p

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
# 9. LINE CHART - Simulation Monte Carlo (avec echelle log pour lisibilite)
# ================================================================
from Base import Base as BaseClass
import random as rng

# Scenarios avec parametres differents
scenarios = [
    {"nom": "Faible equip. (40 membres)",       "nb_membres": 40,  "freq_ravit": 20, "ravit_nourr": (60, 120)},
    {"nom": "Standard (60 membres)",             "nb_membres": 60,  "freq_ravit": 20, "ravit_nourr": (80, 200)},
    {"nom": "Grand equip. (100 membres)",        "nb_membres": 100, "freq_ravit": 20, "ravit_nourr": (80, 200)},
    {"nom": "Ravit. frequent (10j)",             "nb_membres": 60,  "freq_ravit": 10, "ravit_nourr": (80, 200)},
    {"nom": "Ravit. rare (40j)",                 "nb_membres": 60,  "freq_ravit": 40, "ravit_nourr": (80, 200)},
    {"nom": "Grosses commandes",                 "nb_membres": 60,  "freq_ravit": 20, "ravit_nourr": (200, 400)},
    {"nom": "Petites commandes",                 "nb_membres": 60,  "freq_ravit": 20, "ravit_nourr": (30, 80)},
    {"nom": "Pire cas (100 memb, ravit rare)",   "nb_membres": 100, "freq_ravit": 40, "ravit_nourr": (50, 100)},
]

NB_JOURS_MC = 500
colors_mc = plt.cm.tab10(np.linspace(0, 1, len(scenarios)))

# Collecter toutes les courbes
all_curves = []
for idx, sc in enumerate(scenarios):
    rng.seed(idx * 13 + 7)
    b = BaseClass(9000 + idx)
    b.receptionnerCommande(9000 + idx, 400, 400, 300)

    mid = 9001 + idx * 200
    techs_mc, bios_mc, cherch_mc = [], [], []
    nb_m = sc["nb_membres"]
    for role, lst, ratio in [("Technicien", techs_mc, 0.25), ("Biologiste", bios_mc, 0.25), ("Chercheur", cherch_mc, 0.48)]:
        for _ in range(int(nb_m * ratio)):
            b.ajouterMembre(9000 + idx, mid, role)
            lst.append(mid)
            mid += 1

    mod_id = 1
    serres_mc = []
    for _ in range(10):
        if techs_mc:
            b.ajouterModule(techs_mc[0], mod_id, "Serre", 5)
            serres_mc.append(mod_id)
            mod_id += 1

    nourriture_mc = []
    eid_mc = 1

    for jour in range(NB_JOURS_MC):
        if jour % sc["freq_ravit"] == 0 and jour > 0:
            lo, hi = sc["ravit_nourr"]
            b.receptionnerCommande(9000 + idx, rng.randint(30, 80), rng.randint(lo, hi), rng.randint(10, 30))

        nb_mang = max(2, sc["nb_membres"] // 10)
        for _ in range(rng.randint(nb_mang // 2, nb_mang)):
            if techs_mc + bios_mc + cherch_mc:
                b.consommerNourriture(rng.choice(techs_mc + bios_mc + cherch_mc), rng.randint(1, 3))

        if rng.random() < 0.35 and bios_mc and serres_mc:
            b.planterGraines(rng.choice(serres_mc), rng.choice(bios_mc), rng.randint(2, 10), eid_mc)
            eid_mc += 1

        if rng.random() < 0.25 and bios_mc and serres_mc:
            b.recolterPlantation(rng.choice(bios_mc), rng.choice(serres_mc), eid_mc)
            eid_mc += 1

        nourriture_mc.append(b.donneeStocks()["nourriture"])

    all_curves.append(nourriture_mc)

# 2 sous-graphiques : echelle lineaire + echelle log
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10), sharex=True)

for idx, (sc, curve) in enumerate(zip(scenarios, all_curves)):
    ax1.plot(range(NB_JOURS_MC), curve, alpha=0.8, color=colors_mc[idx],
             label=sc["nom"], linewidth=1.5)
    ax2.plot(range(NB_JOURS_MC), [max(v, 1) for v in curve], alpha=0.8,
             color=colors_mc[idx], label=sc["nom"], linewidth=1.5)

ax1.axhline(y=0, color="red", linestyle="--", alpha=0.5, linewidth=2)
ax1.set_ylabel("Stock de nourriture")
ax1.set_title("9. Simulation Monte Carlo - Scenarios de survie alimentaire")
ax1.legend(fontsize=7, loc="upper left")
ax1.grid(True, alpha=0.3)

ax2.set_yscale("log")
ax2.axhline(y=20, color="red", linestyle="--", alpha=0.5, linewidth=2, label="Seuil critique (20)")
ax2.set_xlabel("Jour de simulation")
ax2.set_ylabel("Stock de nourriture (echelle log)")
ax2.set_title("Meme donnee en echelle logarithmique (meilleure lisibilite)")
ax2.legend(fontsize=7, loc="upper left")
ax2.grid(True, alpha=0.3)

fig.tight_layout()
save_and_show(fig, "09_monte_carlo_nourriture.png")

print("\n=== Analyses terminees ===")
print(f"9 graphiques sauvegardes dans le dossier 'graphiques/'")
