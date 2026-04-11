"""
Analyses statistiques et graphiques de la simulation de base martienne.
Charge les donnees de simulation_data.pkl et genere 6 graphiques.
"""
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict
from matplotlib.patches import Patch

# --- Chargement des donnees ---
with open("simulation_data.pkl", "rb") as f:
    data = pickle.load(f)

historique_stocks = data["historique_stocks"]
log_operations = data["log_operations"]
log_expeditions = data["log_expeditions"]
log_sinistres = data["log_sinistres"]
log_recoltes = data["log_recoltes"]
log_consommation = data["log_consommation"]
log_ravitaillements = data["log_ravitaillements"]
log_membres = data["log_membres"]
donnees_membres = data["donnees_membres"]

# --- Dossier de sortie ---
os.makedirs("graphiques", exist_ok=True)

NB_GRAPHIQUES = 0


def save_and_show(fig, filename):
    global NB_GRAPHIQUES
    NB_GRAPHIQUES += 1
    fig.savefig(f"graphiques/{filename}", dpi=150, bbox_inches="tight")
    plt.close(fig)


def moving_avg(data, window=30):
    arr = np.array(data, dtype=float)
    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="same")


# ================================================================
# 1. LINE CHART - Evolution des stocks (avec moyenne mobile)
# ================================================================
jours = [s[0] for s in historique_stocks]
graines = [s[1] for s in historique_stocks]
nourriture = [s[2] for s in historique_stocks]
pieces = [s[3] for s in historique_stocks]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

ax1.plot(jours, graines, alpha=0.2, color="tab:blue")
ax1.plot(jours, nourriture, alpha=0.2, color="tab:orange")
ax1.plot(jours, pieces, alpha=0.2, color="tab:green")
ax1.plot(jours, moving_avg(graines), label="Graines (moy. mobile 30j)", color="tab:blue", linewidth=2)
ax1.plot(jours, moving_avg(nourriture), label="Nourriture (moy. mobile 30j)", color="tab:orange", linewidth=2)
ax1.plot(jours, moving_avg(pieces), label="Pieces module (moy. mobile 30j)", color="tab:green", linewidth=2)
ax1.axhspan(0, 20, color="red", alpha=0.08, label="Zone critique (< 20)")
ax1.set_ylabel("Quantite en stock")
ax1.set_title("1. Evolution des stocks au fil du temps")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

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
# 2. BAR CHART - Balance nourriture (hors periode initiale)
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

start = 1
x = np.arange(start, nb_periodes)
labels = [f"J{i*periode}-{(i+1)*periode}" for i in range(start, nb_periodes)]

fig, ax = plt.subplots(figsize=(13, 5))
width = 0.27
ax.bar(x - width, production_par_periode[start:], width, label="Production (recoltes)", color="#27ae60", alpha=0.8)
ax.bar(x, ravitaillement_par_periode[start:], width, label="Ravitaillement d'urgence", color="#3498db", alpha=0.8)
ax.bar(x + width, consommation_par_periode[start:], width, label="Consommation", color="#e74c3c", alpha=0.8)

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
# 3. HISTOGRAM - Distribution des durees d'expedition
# ================================================================
if log_expeditions:
    durees = [exp[3] for exp in log_expeditions]

    fig, ax = plt.subplots(figsize=(10, 5))
    n_bins, bins, patches = ax.hist(durees, bins=15, color="steelblue", edgecolor="black", alpha=0.7)
    moy = np.mean(durees)
    med = np.median(durees)
    std = np.std(durees)
    ax.axvline(moy, color="red", linestyle="--", linewidth=2, label=f"Moyenne = {moy:.1f}j")
    ax.axvline(med, color="orange", linestyle="--", linewidth=2, label=f"Mediane = {med:.1f}j")
    ax.axvspan(moy - std, moy + std, color="red", alpha=0.08, label=f"Ecart-type = {std:.1f}j")
    ax.set_xlabel("Duree (jours)")
    ax.set_ylabel("Nombre d'expeditions")
    ax.set_title(f"3. Distribution des durees d'expedition (n={len(durees)})")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    save_and_show(fig, "03_durees_expedition.png")

# ================================================================
# 4. HISTOGRAM - Duree des sinistres avant reparation
# ================================================================
sinistres_repares = [s for s in log_sinistres if s["dateReparation"] is not None]
if sinistres_repares:
    durees_sin = [s["duree"] for s in sinistres_repares]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(durees_sin, bins=15, color="mediumpurple", edgecolor="black", alpha=0.7)
    moy_sin = np.mean(durees_sin)
    med_sin = np.median(durees_sin)
    ax.axvline(moy_sin, color="red", linestyle="--", linewidth=2, label=f"Moyenne = {moy_sin:.1f}j")
    ax.axvline(med_sin, color="orange", linestyle="--", linewidth=2, label=f"Mediane = {med_sin:.1f}j")
    ax.set_xlabel("Duree avant reparation (jours)")
    ax.set_ylabel("Nombre de sinistres")
    ax.set_title("4. Duree des sinistres avant reparation")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    save_and_show(fig, "04_duree_sinistres.png")

# ================================================================
# 6. BAR CHART GROUPE - Effectifs vs charge de travail ponderee
# ================================================================
POIDS_ACTIVITES = {
    "sinistre": 1,
    "exp_lancee": 5,
    "exp_participee": 8,
    "exp_receptionnee": 3,
    "evenement_serre": 2,
    "commande": 1,
    "gestion_membre": 1,
}

roles = [m["role"] for m in donnees_membres if m["etat"] == 1]
role_counts = Counter(roles)

charge_par_role = defaultdict(int)
for m in donnees_membres:
    if m["etat"] == 1:
        charge = (m["nb_sinistres"] * POIDS_ACTIVITES["sinistre"]
                  + m["nb_exp_lancees"] * POIDS_ACTIVITES["exp_lancee"]
                  + m["nb_exp_participees"] * POIDS_ACTIVITES["exp_participee"]
                  + m["nb_exp_receptionnees"] * POIDS_ACTIVITES["exp_receptionnee"]
                  + m["nb_evenements_serre"] * POIDS_ACTIVITES["evenement_serre"]
                  + m["nb_commandes_receptionnees"] * POIDS_ACTIVITES["commande"]
                  + (m["nb_membres_ajoutes"] + m["nb_membres_supprimes"]) * POIDS_ACTIVITES["gestion_membre"])
        charge_par_role[m["role"]] += charge

colors_roles = {"Commandant": "#ff6b6b", "Technicien": "#4ecdc4",
                "Biologiste": "#45b7d1", "Chercheur": "#f9ca24"}

role_order = [r for r in ["Commandant", "Technicien", "Biologiste", "Chercheur"] if r in role_counts]

effectifs = [role_counts[r] for r in role_order]
charges = [charge_par_role[r] for r in role_order]
total_eff = sum(effectifs)
total_charge = sum(charges) if sum(charges) > 0 else 1

pct_effectifs = [e / total_eff * 100 for e in effectifs]
pct_charges = [c / total_charge * 100 for c in charges]

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(role_order))
width = 0.35
colors_list = [colors_roles[r] for r in role_order]

bars1 = ax.bar(x - width/2, pct_effectifs, width, label="% des effectifs",
               color=colors_list, alpha=0.6, edgecolor="black")
bars2 = ax.bar(x + width/2, pct_charges, width, label="% de la charge ponderee",
               color=colors_list, alpha=1.0, edgecolor="black")

for bar, pct, val in zip(bars1, pct_effectifs, effectifs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{pct:.0f}%\n({val})", ha="center", va="bottom", fontsize=8)
for bar, pct, val in zip(bars2, pct_charges, charges):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{pct:.0f}%\n({val})", ha="center", va="bottom", fontsize=8)

ax.set_ylabel("Pourcentage (%)")
ax.set_title("5. Effectifs vs charge de travail ponderee par role")
ax.set_xticks(x)
ax.set_xticklabels(role_order, fontsize=10)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylim(0, max(max(pct_effectifs), max(pct_charges)) + 15)
fig.tight_layout()
save_and_show(fig, "05_repartition_roles.png")

# ================================================================
# 7. BAR CHART - Turnover par role (ajouts vs departs)
# ================================================================
if log_membres:
    roles_track = ["Technicien", "Biologiste", "Chercheur"]
    colors_attr = {"Technicien": "#4ecdc4", "Biologiste": "#45b7d1", "Chercheur": "#f9ca24"}

    periode_attr = 100
    max_jour_m = max(e[0] for e in log_membres)
    nb_p_attr = max_jour_m // periode_attr + 1

    ajouts = {r: [0] * nb_p_attr for r in roles_track}
    suppr = {r: [0] * nb_p_attr for r in roles_track}

    for jour_m, action, mid, role in log_membres:
        if role in roles_track:
            idx = min(jour_m // periode_attr, nb_p_attr - 1)
            if action == "ajout":
                ajouts[role][idx] += 1
            elif action == "suppression":
                suppr[role][idx] += 1

    x = np.arange(nb_p_attr)
    labels_attr = [f"J{i*periode_attr}-{(i+1)*periode_attr}" for i in range(nb_p_attr)]
    width_attr = 0.25

    fig, ax = plt.subplots(figsize=(13, 6))
    for i, role in enumerate(roles_track):
        ax.bar(x + i * width_attr, ajouts[role], width_attr,
               color=colors_attr[role], alpha=0.9, edgecolor="black",
               label=f"{role} (ajouts)")
        ax.bar(x + i * width_attr, [-s for s in suppr[role]], width_attr,
               color=colors_attr[role], alpha=0.4, edgecolor="black",
               label=f"{role} (departs)")

    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Periode")
    ax.set_ylabel("Nombre de membres (+ ajouts / - departs)")
    ax.set_title("6. Turnover par role : ajouts vs departs par periode")
    ax.set_xticks(x + width_attr)
    ax.set_xticklabels(labels_attr, rotation=45, ha="right", fontsize=7)
    ax.legend(fontsize=7, ncol=3, loc="upper right")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    save_and_show(fig, "06_turnover_par_role.png")


print(f"\n=== Analyses terminees ===")
print(f"{NB_GRAPHIQUES} graphiques sauvegardes dans le dossier 'graphiques/'")
