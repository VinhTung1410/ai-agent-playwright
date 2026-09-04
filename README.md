# LinkedIn Business Analyst Alternance Scraper & Analyzer (France)

Ce projet est un outil d'automatisation haute performance en Python permettant de collecter, d'analyser et de consolider les offres d'alternance pour les rôles de **Business Analyst** en France publiées au cours des dernières 24 heures sur LinkedIn.

---

## 🌟 Fonctionnalités Principales

1. **Recherche automatique ciblée** : Recherche les offres avec les mots-clés configurables (par défaut : `alternance business analyst`) en France publiées dans les dernières 24 heures (`f_TPR=r86400`).
2. **Moteur d'extraction ultra-rapide (Scraper Haute Performance)** :
   - Temps d'extraction considérablement optimisé : **10 offres traitées en ~15 à 30 secondes** (contre plus de 150 secondes auparavant).
   - Interception intelligente des requêtes réseau : blocage des médias, images, balises de télémétrie et polices superflues tout en conservant les feuilles de style CSS.
   - Cycle de vie de page optimisé avec `domcontentloaded` et sélecteurs synchronisés.
   - Contournement automatique des fenêtres contextuelles de connexion LinkedIn (authwall/modal) par injection dynamique de CSS dans le DOM.
3. **Fiche détaillée du poste & de l'entreprise (Native Job & Company Viewer)** :
   - Remplacement complet des anciennes captures d'écran (souvent sujettes aux bannières de cookies ou aux problèmes de police) par une fiche textuelle structurée et moderne directement dans Streamlit.
   - Extraction des sections clés : **About the job** (description intégrale du poste), **About the company** (présentation de l'entreprise), Type de contrat (*Employment type*), Niveau hiérarchique (*Seniority level*), Secteur d'activité (*Industries*), Liens directs LinkedIn et entreprise.
4. **Analyse avancée des compétences (Taxonomie Française)** :
   - Détection et normalisation bilingue (Français/Anglais) des compétences requises : Outils techniques (SQL, Power BI, Python, Jira...), Méthodologies (Agile, Scrum, Cycle en V...), Compétences professionnelles (Recueil des besoins, User stories...) et Langues.
5. **Tableaux de bord visuels interactifs (Plotly)** :
   - Affichage direct des ratios et pourcentages sous la forme `X/Total (Y%)` sur chaque barre horizontale.
   - Suppression des infobulles noires superflues (`hoverinfo='skip'`) et masquage de la barre d'outils flottante pour une interface épurée et sans chevauchement.
   - Graphiques de répartition par catégorie, top entreprises qui recrutent et localisation géographique.
6. **Rapport Excel structuré & Suivi des candidatures** :
   - Fichier généré automatiquement : `output/LinkedIn_BA_France_Report.xlsx`.
   - Onglet **Job Listings** : Tableau complet avec listes déroulantes de validation (*À postuler, Postulé, Entretien, Refusé, Offre reçue*), champs de suivi (date, contact, remarques) et hyperliens directs.
   - Onglet **Top Skills Ranking** : Classement par ordre de fréquence et taux d'apparition de chaque compétence.
7. **Dashboard Web Interactif (Streamlit)** :
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

# Installation des dépendances Python
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Installation du navigateur Chromium pour Playwright
.\.venv\Scripts\python.exe -m playwright install chromium
```

---

### 2. Lancement de l'application en local

#### Option A : Lancer le Dashboard Web Streamlit (Recommandé)

Sous Windows PowerShell, lancez directement l'interface web :

```powershell
.\.venv\Scripts\python.exe -m streamlit run src/app.py
```
*(Le navigateur s'ouvrira automatiquement à l'adresse `http://localhost:8501`)*

#### Option B : Lancer le Scraper en ligne de commande (CLI)

```powershell
.\.venv\Scripts\python.exe src/main.py
```

---

## 🖥️ Organisation du Dashboard Web (Streamlit)

Le dashboard est articulé autour de 3 onglets thématiques :

- **Onglet 1 : 📊 Tableaux de Bord & Visualisations (Plotly)** :
  - *Top 15 Compétences* avec étiquettes claires de proportion (ex: `5/6 (83.3%)`).
  - Répartition circulaire par famille de compétences.
  - Classement des entreprises et répartition géographique.
- **Onglet 2 : 📋 Suivi des Candidatures (Application Tracker)** :
  - Modification directe du statut des candidatures, des notes et contacts.
  - Bouton de sauvegarde vers le fichier Excel.
  - Bouton de téléchargement immédiat du fichier `.xlsx`.
- **Onglet 3 : 🏢 Détails du Poste & Entreprise (Job & Company Details)** :
  - Sélection de l'offre pour consultation directe des sections *About the job*, *About the company*, critères de séniorité et types d'emploi.

---

## 📜 Historique des Versions (Changelog)

### 📌 v1.0.3 (Sprint 4) - *UX/UI Enhancement, Visual Analytics & Search Performance Optimization*
- **Accélération majeure du scraper** : Réduction du temps de collecte de ~150s à **~15-30s pour 10 offres** grâce au filtrage réseau (blocage des traqueurs/images/balises) et à l'exploitation de l'événement `domcontentloaded`.
- **Fiche native du poste & de l'entreprise** : Remplacement du visualiseur de captures d'écran par un composant d'affichage textuel complet et stylisé (About the job, About the company, Employment type, Seniority level, Industries).
- **Perfectionnement des graphiques Plotly** :
  - Affichage direct du format `X/Total (Y%)` sur chaque barre.
  - Suppression de l'infobulle noire au survol (`hoverinfo='skip'`).
  - Masquage de la barre d'outils superposée aux titres (`displayModeBar: False`).
- **Curseur de sélection du volume & ETA dynamique** : Contrôle du nombre d'offres ciblées (6 à 30 offres) avec estimation précise du temps de complétion.
- **Export direct Excel** : Téléchargement du fichier de rapport en un clic depuis l'interface utilisateur.

### 📌 v1.0.2 (Sprint 3) - *Streamlit Cloud Deployment & Chromium Refactor*
- **Compatibilité Streamlit Cloud** : Résolution des dépendances système via `packages.txt` (Debian Linux).
- **Standardisation Chromium** : Exécution automatique en mode headless ou headful selon l'environnement.
- **Auto-installation Playwright** : Détection et installation transparente du binaire Chromium si absent.

### 📌 v1.0.1 (Sprint 2) - *Logging, Metadata & Application Tracking*
- **Suivi des candidatures** : Ajout des colonnes de gestion d'avancement des candidatures dans Excel et dans l'interface.
- **Journalisation structurée** : Enregistrement des événements de navigation dans `logs/browser.log`.
- **Éditeur de données en direct** : Intégration de `st.data_editor` pour la mise à jour des statuts.

### 📌 v1.0.0 (Sprint 1) - *Browser Automation & Core Scraper*
- **Scraper initial Playwright** : Collecte des offres LinkedIn et contournement des modales de connexion.
- **Moteur d'extraction de compétences** : Dictionnaire de mots-clés BA en français.
- **Export Excel automatisé** : Mise en forme avancée avec en-têtes корпораatifs et validation des données.
