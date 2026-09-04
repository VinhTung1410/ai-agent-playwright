# LinkedIn Business Analyst Alternance Scraper & Analyzer (France)

Ce projet est un outil d'automatisation et d'aide à la candidature haute performance en Python permettant de collecter, d'analyser, d'évaluer les compétences d'un CV et de consolider les offres d'alternance pour les rôles de **Business Analyst** en France publiées au cours des dernières 24 heures sur LinkedIn.

---

## 🌟 Fonctionnalités Principales

1. **Recherche automatique ciblée** : Recherche les offres avec les mots-clés configurables (par défaut : `alternance business analyst`) en France publiées dans les dernières 24 heures (`f_TPR=r86400`).
2. **Moteur d'extraction ultra-rapide (Scraper Haute Performance)** :
   - Temps d'extraction optimisé : **10 offres traitées en ~15 à 30 secondes** (contre plus de 150 secondes auparavant).
   - Interception intelligente des requêtes réseau : blocage des médias, images, balises de télémétrie et polices superflues tout en conservant les feuilles de style CSS.
   - Cycle de vie de page optimisé avec `domcontentloaded` et sélecteurs synchronisés.
   - Contournement automatique des fenêtres contextuelles de connexion LinkedIn (authwall/modal) par injection dynamique de CSS dans le DOM.
3. **Fiche détaillée du poste & de l'entreprise (Native Job & Company Viewer)** :
   - Remplacement complet des captures d'écran par une fiche textuelle structurée et moderne directement dans Streamlit.
   - Extraction des sections clés : **About the job** (description intégrale du poste), **About the company** (présentation de l'entreprise), Type de contrat (*Employment type*), Niveau hiérarchique (*Seniority level*), Secteur d'activité (*Industries*), Liens directs LinkedIn et entreprise.
4. **Évaluation du CV & Matching Intelligent (AI Matcher - Sprint 5)** :
   - **Upload de CV en format PDF** via `pypdf` : extraction automatique du texte et détection des compétences clés du candidat selon la taxonomie française.
   - **Calcul du score de compatibilité (Fit Score %)** pour chaque offre collectée.
   - **Classement dynamique (Leaderboard)** de toutes les offres par ordre de pertinence décroissant.
   - **Analyse d'écart & Points forts** : comparaison directe entre compétences validées (*Forces*) et compétences requises non détectées (*Manquants*).
   - **Plan d'action & Conseils d'optimisation personnalisés** : recommandations concrètes pour adapter le CV, franchir les filtres ATS et réussir l'entretien.
5. **Analyse avancée des compétences (Taxonomie Française)** :
   - Détection et normalisation bilingue (Français/Anglais) des compétences requises : Outils techniques (SQL, Power BI, Python, Jira...), Méthodologies (Agile, Scrum, Cycle en V...), Compétences professionnelles (Recueil des besoins, User stories...) et Langues.
6. **Tableaux de bord visuels interactifs (Plotly)** :
   - Affichage direct des ratios et pourcentages sous la forme `X/Total (Y%)` sur chaque barre horizontale.
   - Suppression des infobulles noires superflues (`hoverinfo='skip'`) et masquage de la barre d'outils flottante.
7. **Rapport Excel structuré & Suivi des candidatures** :
   - Fichier généré automatiquement : `output/LinkedIn_BA_France_Report.xlsx`.
   - Onglet **Job Listings** : Tableau complet avec listes déroulantes de validation (*À postuler, Postulé, Entretien, Refusé, Offre reçue*), champs de suivi et hyperliens directs.
   - Onglet **Top Skills Ranking** : Classement par ordre de fréquence et taux d'apparition de chaque compétence.
8. **Dashboard Web Interactif (Streamlit)** :
   - 4 Onglets thématiques de navigation fluide.
   - Barre de progression en temps réel avec calcul précis du temps restant estimé (ETA).
   - Éditeur interactif en direct (`st.data_editor`) avec sauvegarde instantanée dans le fichier Excel.
   - Bouton de téléchargement direct du rapport Excel sans quitter le navigateur.

---

## 🚀 Installation & Guide d'Exécution Local

### Prérequis
- **Python 3.11+**
- Moteur de navigateur **Chromium** (installé et géré automatiquement via Playwright).

### 1. Installation des dépendances

```powershell
# Cloner le dépôt et se placer dans le dossier
cd "Linkedin app"

# Créer un environnement virtuel (si ce n'est pas déjà fait)
python -m venv .venv

# Installation des dépendances Python (inclut pypdf pour l'analyse des CV)
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Installation du navigateur Chromium pour Playwright
.\.venv\Scripts\python.exe -m playwright install chromium
```

---

### 2. Lancement de l'application en local

#### Option A : Lancer le Dashboard Web Streamlit (Recommandé)

```powershell
.\.venv\Scripts\python.exe -m streamlit run src/app.py
```
*(Le navigateur s'ouvrira automatiquement à l'adresse `http://localhost:8501`)*

#### Option B : Lancer le Scraper en ligne de commande (CLI)

```powershell
.\.venv\Scripts\python.exe src/main.py
```

---

## 🖥️ Organisation du Dashboard Web (Streamlit - 4 Onglets)

- **Onglet 1 : 📊 Tableaux de Bord & Visualisations (Plotly)** :
  - *Top 15 Compétences* avec étiquettes claires de proportion (ex: `5/6 (83.3%)`).
  - Répartition circulaire par famille de compétences.
  - Classement des entreprises et répartition géographique.
- **Onglet 2 : 📋 Suivi des Candidatures (Application Tracker)** :
  - Modification directe du statut des candidatures, des notes et contacts.
  - Bouton de sauvegarde vers le fichier Excel et téléchargement immédiat.
- **Onglet 3 : 📑 Fiche de Poste & Détails (Job & Company Details)** :
  - Consultation directe des sections *About the job*, *About the company*, critères de séniorité et types d'emploi.
- **Onglet 4 : 🎯 Évaluation du CV & Matching (AI Matcher)** :
  - Dépôt de CV PDF (`st.file_uploader`), extraction des compétences du candidat.
  - Leaderboard de compatibilité des offres.
  - Diagnostic comparatif des points forts et des compétences manquantes.
  - Conseils et plan d'action personnalisés par offre.

---

## 📜 Historique des Versions (Changelog)

### 📌 v1.0.4 (Sprint 5) - *CV PDF Matching, Fit Scoring & Personalized Recommendations*
- **Module d'évaluation de CV (`src/cv_matcher.py`)** : Décodage de CV au format PDF via `pypdf`, extraction des compétences via la taxonomie bilingue existante.
- **Ajout de l'Onglet 4 (Évaluation du CV & Matching)** :
  - Téléversement direct du fichier CV en PDF.
  - Résumé du profil candidat avec métriques par catégorie (Outils, Méthodes, Langues).
  - Tableau de classement de toutes les offres selon le score d'adéquation (Fit Score %).
  - Carte de score avec badges de couleur (🟢 $\ge 75\%$, 🟡 $50-74\%$, 🔴 $< 50\%$).
  - Recommandations concrètes en français pour ajuster le CV pour chaque offre spécifique.
- **Mise à jour des dépendances** : Ajout de `pypdf>=4.0.0` dans `requirements.txt`.

### 📌 v1.0.3 (Sprint 4) - *UX/UI Enhancement, Visual Analytics & Search Performance Optimization*
- **Accélération majeure du scraper** : Réduction du temps de collecte de ~150s à **~15-30s pour 10 offres** grâce au filtrage réseau et à l'événement `domcontentloaded`.
- **Fiche native du poste & de l'entreprise** : Remplacement des captures d'écran par un composant textuel propre (About the job, About the company).
- **Perfectionnement des graphiques Plotly** : Affichage direct du format `X/Total (Y%)`, suppression des infobulles noires superflues.

### 📌 v1.0.2 (Sprint 3) - *Streamlit Cloud Deployment & Chromium Refactor*
- **Compatibilité Streamlit Cloud** : Résolution des dépendances système via `packages.txt`.
- **Standardisation Chromium** : Exécution automatique en mode headless ou headful.

### 📌 v1.0.1 (Sprint 2) - *Logging, Metadata & Application Tracking*
- **Suivi des candidatures** : Ajout des colonnes de gestion d'avancement des candidatures.
- **Journalisation structurée** : Enregistrement des événements dans `logs/browser.log`.

### 📌 v1.0.0 (Sprint 1) - *Browser Automation & Core Scraper*
- **Scraper initial Playwright** : Collecte des offres LinkedIn et contournement des modales.
- **Moteur d'extraction de compétences** : Dictionnaire de compétences BA en français.
