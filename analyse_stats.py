"""
Analyses statistiques et graphiques de la simulation de base martienne.
Charge les donnees de simulation_data.pkl et genere 17 graphiques.
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
historique_effectifs = data["historique_effectifs"]
historique_modules = data["historique_modules"]
log_operations = data["log_operations"]
log_expeditions = data["log_expeditions"]
log_sinistres = data["log_sinistres"]
log_recoltes = data["log_recoltes"]
log_plantations = data["log_plantations"]
log_consommation = data["log_consommation"]
log_ravitaillements = data["log_ravitaillements"]
log_membres = data["log_membres"]
donnees_membres = data["donnees_membres"]
donnees_serres = data["donnees_serres"]
donnees_garages = data["donnees_garages"]

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
# 4. PIE CHART - Repartition sinistres Garage vs Serre
# ================================================================
if log_sinistres:
    nb_sin_garage = sum(1 for s in log_sinistres if s["type"] == "Garage")
    nb_sin_serre = sum(1 for s in log_sinistres if s["type"] == "Serre")

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie([nb_sin_garage, nb_sin_serre],
           labels=[f"Garage ({nb_sin_garage})", f"Serre ({nb_sin_serre})"],
           autopct="%1.1f%%", colors=["#ff9999", "#66b3ff"], startangle=90)
    ax.set_title("4. Repartition des sinistres par type")
    fig.tight_layout()
    save_and_show(fig, "04_sinistres_repartition.png")

# ================================================================
# 5. HISTOGRAM - Distribution des degats (exponentielle)
# ================================================================
if log_sinistres:
    degats_sin = [s.get("degats", 100 - s["ptDeVie"]) for s in log_sinistres]

    fig, ax = plt.subplots(figsize=(10, 5))
    n_vals, bins, patches = ax.hist(degats_sin, bins=18, color="tomato", edgecolor="black", alpha=0.7)

    for patch, left_edge in zip(patches, bins[:-1]):
        if left_edge < 30:
            patch.set_facecolor("#2ecc71")
        elif left_edge < 60:
            patch.set_facecolor("#f39c12")
        else:
            patch.set_facecolor("#e74c3c")

    ax.axvline(np.mean(degats_sin), color="blue", linestyle="--", linewidth=2)
    ax.axvline(bins[-2], color="darkred", linestyle=":", linewidth=2)
    ax.annotate("Valeurs > 85\ntronquees ici\n(artefact loi expo)",
                xy=(bins[-2], n_vals[-1]), xytext=(55, n_vals[-1] + 1),
                arrowprops=dict(arrowstyle="->", color="darkred"),
                color="darkred", fontsize=8)

    legend_elements = [
        Patch(facecolor="#2ecc71", label=f"Mineur (<30) : {sum(1 for d in degats_sin if d < 30)}"),
        Patch(facecolor="#f39c12", label=f"Modere (30-60) : {sum(1 for d in degats_sin if 30 <= d < 60)}"),
        Patch(facecolor="#e74c3c", label=f"Critique (>60) : {sum(1 for d in degats_sin if d >= 60)}"),
        plt.Line2D([0], [0], color="blue", linestyle="--", label=f"Moyenne = {np.mean(degats_sin):.1f}"),
        plt.Line2D([0], [0], color="darkred", linestyle=":", label="Seuil de troncature (hi=85)"),
    ]
    ax.legend(handles=legend_elements, fontsize=9)
    ax.set_xlabel("Points de vie perdus (degats)")
    ax.set_ylabel("Nombre de sinistres")
    ax.set_title("5. Distribution de la gravite des sinistres")
    ax.grid(True, alpha=0.3, axis="y")
    save_and_show(fig, "05_distribution_degats.png")

# ================================================================
# 6. HISTOGRAM - Duree des sinistres avant reparation
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
    ax.set_title("6. Duree des sinistres avant reparation")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    save_and_show(fig, "06_duree_sinistres.png")

# ================================================================
# 7. BAR CHART GROUPE - Effectifs vs charge de travail ponderee
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
ax.set_title("7. Effectifs vs charge de travail ponderee par role")
ax.set_xticks(x)
ax.set_xticklabels(role_order, fontsize=10)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylim(0, max(max(pct_effectifs), max(pct_charges)) + 15)
fig.tight_layout()
save_and_show(fig, "07_repartition_roles.png")

# ================================================================
# 8. HEATMAP - Matrice de correlation (periodes de 10 jours)
# ================================================================
periode_corr = 10
nb_p = max(jours) // periode_corr + 1

series = {
    "Nourriture": [0.0] * nb_p,
    "Graines": [0.0] * nb_p,
    "Pieces": [0.0] * nb_p,
    "Sinistres": [0.0] * nb_p,
    "Expeditions": [0.0] * nb_p,
    "Recoltes": [0.0] * nb_p,
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

keys = list(series.keys())
matrix = np.array([series[k] for k in keys])
corr = np.corrcoef(matrix)

fig, ax = plt.subplots(figsize=(8, 7))
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
ax.set_title(f"8. Matrice de correlation (periodes de {periode_corr}j, n={nb_p})")
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

ax1.plot(jours_eff, total_eff, color="black", linewidth=2.5, label="Total")
ax1.plot(jours_eff, tech_eff,  color="#4ecdc4", linewidth=1.5, label="Techniciens")
ax1.plot(jours_eff, bio_eff,   color="#45b7d1", linewidth=1.5, label="Biologistes")
ax1.plot(jours_eff, cher_eff,  color="#f9ca24", linewidth=1.5, label="Chercheurs")
ax1.set_ylabel("Nombre de membres actifs")
ax1.set_title("9. Evolution des effectifs au fil du temps")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

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
# 10. LINE CHART - Evolution des modules actifs
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
# 11. LINE CHART - Analyse temporelle des sinistres
# ================================================================
if log_sinistres:
    jours_sin_garage = sorted([s["jour_creation"] for s in log_sinistres if s["type"] == "Garage"])
    jours_sin_serre = sorted([s["jour_creation"] for s in log_sinistres if s["type"] == "Serre"])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

    # Cumul des sinistres
    if jours_sin_garage:
        ax1.step(jours_sin_garage, range(1, len(jours_sin_garage) + 1),
                 where="post", color="#ff9999", linewidth=2, label=f"Garages ({len(jours_sin_garage)})")
    if jours_sin_serre:
        ax1.step(jours_sin_serre, range(1, len(jours_sin_serre) + 1),
                 where="post", color="#66b3ff", linewidth=2, label=f"Serres ({len(jours_sin_serre)})")
    ax1.set_ylabel("Sinistres cumules")
    ax1.set_title("11. Evolution temporelle des sinistres")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Backlog de sinistres non repares (approche evenementielle)
    events = []
    for s in log_sinistres:
        events.append((s["jour_creation"], 1))
        if s["duree"] is not None:
            events.append((s["jour_creation"] + s["duree"], -1))
    events.sort()

    max_jour = max(jours) if jours else 0
    backlog_jours = [0]
    backlog_vals = [0]
    current = 0
    for jour_ev, delta in events:
        if jour_ev <= max_jour:
            current += delta
            backlog_jours.append(jour_ev)
            backlog_vals.append(current)
    backlog_jours.append(max_jour)
    backlog_vals.append(current)

    ax2.fill_between(backlog_jours, backlog_vals, alpha=0.4, color="tomato", step="post")
    ax2.step(backlog_jours, backlog_vals, where="post", color="tomato", linewidth=1.5,
             label="Sinistres non repares")
    ax2.set_xlabel("Jour de simulation")
    ax2.set_ylabel("Sinistres non repares", color="tomato")
    ax2.tick_params(axis="y", labelcolor="tomato")
    ax2.set_title("Backlog de sinistres vs stock de pieces module")
    ax2.grid(True, alpha=0.3)

    # Stock de pieces module (axe secondaire)
    pieces_stock = [s[3] for s in historique_stocks]
    jours_stock = [s[0] for s in historique_stocks]
    ax2_pieces = ax2.twinx()
    ax2_pieces.plot(jours_stock, moving_avg(pieces_stock), color="tab:green",
                    linewidth=2, alpha=0.8, label="Stock pieces (moy. mobile)")
    ax2_pieces.plot(jours_stock, pieces_stock, color="tab:green", alpha=0.15)
    ax2_pieces.set_ylabel("Stock pieces module", color="tab:green")
    ax2_pieces.tick_params(axis="y", labelcolor="tab:green")

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_pieces.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper left")

    fig.tight_layout()
    save_and_show(fig, "11_evolution_sinistres.png")

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
# 14. BAR CHART - Reparations par technicien (top 15)
# ================================================================
if sinistres_repares:
    reparations_par_tech = Counter(s["tech_id"] for s in sinistres_repares if s["tech_id"] is not None)
    top_techs = reparations_par_tech.most_common(15)

    if top_techs:
        labels_tech = [f"T{tid}" for tid, _ in top_techs]
        counts_tech = [c for _, c in top_techs]
        moy_rep = np.mean(list(reparations_par_tech.values()))

        fig, ax = plt.subplots(figsize=(12, 5))
        bars = ax.bar(labels_tech, counts_tech, color="#4ecdc4", edgecolor="black", alpha=0.8)
        ax.axhline(moy_rep, color="red", linestyle="--", linewidth=2,
                   label=f"Moyenne = {moy_rep:.1f} rep/tech")

        for bar, c in zip(bars, counts_tech):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    str(c), ha="center", va="bottom", fontsize=8)

        ax.set_xlabel("Technicien")
        ax.set_ylabel("Nombre de reparations")
        ax.set_title(f"14. Top 15 techniciens par nombre de reparations (total={sum(counts_tech)})")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()
        save_and_show(fig, "14_reparations_par_technicien.png")

# ================================================================
# 15. BAR CHART - Productivite par serre (rendement recolte / plantation)
# ================================================================
if donnees_serres:
    serres_productives = [s for s in donnees_serres if s["total_plante"] > 0]
    if serres_productives:
        serres_sorted = sorted(serres_productives,
                               key=lambda s: s["total_recolte"] / s["total_plante"], reverse=True)
        ids_p = [f"S{s['id']}" for s in serres_sorted]
        rendements = [s["total_recolte"] / s["total_plante"] * 100 for s in serres_sorted]
        moy_rend = np.mean(rendements)

        couleurs_rend = ["#27ae60" if r >= 80 else "#f39c12" if r >= 50 else "#e74c3c" for r in rendements]

        fig, ax = plt.subplots(figsize=(13, 6))
        bars = ax.bar(range(len(ids_p)), rendements, color=couleurs_rend, edgecolor="black", alpha=0.8)
        ax.axhline(100, color="blue", linestyle="--", alpha=0.5, label="100% rendement")
        ax.axhline(moy_rend, color="red", linestyle="--", alpha=0.7,
                   label=f"Moyenne = {moy_rend:.1f}%")

        legend_elements = [
            Patch(facecolor="#27ae60", label=f"Bon (>=80%) : {sum(1 for r in rendements if r >= 80)}"),
            Patch(facecolor="#f39c12", label=f"Moyen (50-80%) : {sum(1 for r in rendements if 50 <= r < 80)}"),
            Patch(facecolor="#e74c3c", label=f"Faible (<50%) : {sum(1 for r in rendements if r < 50)}"),
            plt.Line2D([0], [0], color="red", linestyle="--", label=f"Moyenne = {moy_rend:.1f}%"),
        ]
        ax.legend(handles=legend_elements, fontsize=9)
        ax.set_xlabel("Serre")
        ax.set_ylabel("Rendement (recolte / plantation) %")
        ax.set_title("15. Productivite par serre : rendement recolte / plantation")
        ax.set_xticks(range(len(ids_p)))
        ax.set_xticklabels(ids_p, rotation=45, fontsize=8)
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()
        save_and_show(fig, "15_productivite_serres.png")

# ================================================================
# 16. BAR CHART - Turnover par role (ajouts vs departs)
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
    ax.set_title("16. Turnover par role : ajouts vs departs par periode")
    ax.set_xticks(x + width_attr)
    ax.set_xticklabels(labels_attr, rotation=45, ha="right", fontsize=7)
    ax.legend(fontsize=7, ncol=3, loc="upper right")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    save_and_show(fig, "16_turnover_par_role.png")

# ================================================================
# 17. BAR CHART - Expeditions par garage
# ================================================================
if log_expeditions:
    garage_exp_count = Counter(exp[5] for exp in log_expeditions)
    garages_sorted = garage_exp_count.most_common(20)

    if garages_sorted:
        labels_g = [f"G{gid}" for gid, _ in garages_sorted]
        counts_g = [c for _, c in garages_sorted]
        moy_exp = np.mean(list(garage_exp_count.values()))

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.bar(labels_g, counts_g, color="steelblue", edgecolor="black", alpha=0.8)
        ax.axhline(moy_exp, color="red", linestyle="--", linewidth=2,
                   label=f"Moyenne = {moy_exp:.1f} exp/garage")

        for i, (lbl, c) in enumerate(zip(labels_g, counts_g)):
            ax.text(i, c + 0.2, str(c), ha="center", va="bottom", fontsize=8)

        ax.set_xlabel("Garage")
        ax.set_ylabel("Nombre d'expeditions terminees")
        ax.set_title(f"17. Expeditions par garage (n={sum(counts_g)} expeditions)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()
        save_and_show(fig, "17_expeditions_par_garage.png")


print(f"\n=== Analyses terminees ===")
print(f"{NB_GRAPHIQUES} graphiques sauvegardes dans le dossier 'graphiques/'")
