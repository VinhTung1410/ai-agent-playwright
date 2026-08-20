# LinkedIn Business Analyst Alternance Scraper & Analyzer (France)

Ce projet est un outil d'automatisation en Python permettant de collecter, d'analyser et de consolider les offres d'alternance pour les rôles de **Business Analyst** en France publiées au cours des dernières 24 heures sur LinkedIn.

---

## 🌟 Fonctionnalités

1. **Recherche automatique** : Recherche les offres avec les mots-clés `alternance business analyst` en France publiées dans les dernières 24 heures.
2. **Extraction intelligente & Capture d'écran** :
   - Extrait les informations clés : Titre du poste, Entreprise, Localisation, URL directe, Description complète.
   - Capture automatiquement une capture d'écran pleine page de chaque offre sous `output/screenshots/`.
   - Contourne les fenêtres contextuelles de connexion LinkedIn en injectant des styles CSS personnalisés en arrière-plan.
3. **Analyse des compétences (en Français)** :
   - Analyse la description pour extraire les outils techniques (SQL, Excel, Jira...), les méthodologies (Agile, Scrum...), les soft skills et les exigences linguistiques.
   - Normalise et déduplique les noms des compétences.
4. **Rapport Excel structuré** : Génère un fichier Excel `output/LinkedIn_BA_France_Report.xlsx` contenant :
   - Onglet **Job Listings** : Liste détaillée des offres avec liens vers les captures d'écran et colonnes de suivi des candidatures.
   - Onglet **Top Skills Ranking** : Classement par fréquence des compétences requises.
5. **Dashboard Web Interactif (Streamlit)** : Interface graphique complète pour lancer la collecte, suivre l'avancement, éditer les candidatures en direct et visualiser les métriques.

---

## 🚀 Installation & Guide d'Exécution Local

### Prérequis
- **Python 3.11+**
- Moteur de navigateur **Chromium** (géré automatiquement via Playwright).

### 1. Installation des dépendances

```powershell
# Cloner le dépôt et naviguer dans le dossier
cd "AI Agent"

# Installation des dépendances Python dans l'environnement virtuel (.venv)
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Installation du navigateur Chromium pour Playwright
.\.venv\Scripts\python.exe -m playwright install chromium
```

---

### 2. Lancement de l'application en local

#### Option A : Lancer le Dashboard Web Streamlit (Recommandé)

Sous Windows PowerShell, utilisez l'une des commandes suivantes pour éviter les erreurs de PATH :

```powershell
# Méthode 1 : Lancement direct via le module Python de .venv (Recommandé)
.\.venv\Scripts\python.exe -m streamlit run src/app.py

# Méthode 2 : Activation préalable de l'environnement virtuel
.\.venv\Scripts\Activate.ps1
streamlit run src/app.py
```

#### Option B : Lancer le Scraper en ligne de commande (CLI)

```powershell
.\.venv\Scripts\python.exe src/main.py
```

---

## 🖥️ Dashboard Web Interactif (Streamlit)

Le dashboard permet une expérience utilisateur fluide et dynamique :

- **Recherche personnalisée** : Saisissez vos mots-clés (ex: `Alternance Product Owner`) et votre localisation directement dans le panneau latéral.
- **Suivi éditable en direct** : Modifiez le statut de vos candidatures, ajoutez des remarques ou des dates d'entretien directement depuis le tableau, puis sauvegardez.
- **Visualiseur d'images** : Visualisez l'image complète de l'offre d'emploi d'un simple clic.
- **Statistiques des compétences** : Graphique en barres des 15 compétences les plus demandées.

---

## 📜 Historique des Versions (Changelog)

### 📌 v1.0.2 (Sprint 3) - *Streamlit Cloud Deployment & Chromium Refactor*
- **Compatibilité Streamlit Cloud** : Résolution des problèmes de permissions `sudo` lors de l'installation des navigateurs Playwright dans les conteneurs.
- **Standardisation Chromium** : Remplacement de Microsoft Edge par le navigateur Chromium standard (exécution automatique en mode headless sur Linux/Cloud et headful en local).
- **Configuration packages.txt** : Ajout de toutes les bibliothèques système Linux requises (`libnss3`, `libgbm1`, `libxfixes3`...) pour exécuter Chromium de manière optimale sur le serveur.
- **Mise à jour de la documentation** : Ajout des instructions détaillées pour exécuter Streamlit en local via `.venv\Scripts\python.exe -m streamlit run src/app.py`.

### 📌 v1.0.1 (Sprint 2) - *Logging, Metadata & Application Tracking*
- **Intégration du suivi des candidatures** : Ajout des colonnes de suivi (*Statut Candidature*, *Date Candidature*, *Contact Recruteur*, *Notes & Remarques*) dans les rapports Excel.
- **Système de journalisation** : Ajout d'un système de logs structuré pour suivre l'exécution du navigateur (`logs/browser.log`).
- **Dashboard Streamlit** : Configuration initiale du tableau interactif avec `st.data_editor`.

### 📌 v1.0.0 (Sprint 1) - *Browser Automation & Core Scraper*
- **Scraper automatisé** : Développement du scraper LinkedIn avec Playwright.
- **Captures d'écran pleine page** : Intégration de la capture d'écran automatique avec masquage des modales de connexion via injection CSS.
- **Moteur d'extraction des compétences** : Développement du système d'extraction basé sur une taxonomie de compétences en français.
- **Exportation Excel** : Génération automatique du rapport Excel structuré avec liens cliquables et validations de données.
