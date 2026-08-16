# LinkedIn Business Analyst Alternance Scraper & Analyzer (France)

Ce projet est un outil d'automatisation en Python permettant de collecter, d'analyser et de consolider les offres d'alternance pour les rôles de **Business Analyst** en France publiées au cours des dernières 24 heures sur LinkedIn.

## Fonctionnalités

1. **Recherche automatique** : Recherche les offres avec les mots-clés `alternance business analyst` en France publiées dans les dernières 24 heures.
2. **Extraction intelligente & Capture d'écran** :
   - Extrait les informations clés : Titre du poste, Entreprise, Localisation, URL directe, Description complète.
   - Capture automatiquement une capture d'écran pleine page de chaque offre sous `output/screenshots/`.
   - Contourne les fenêtres contextuelles de connexion LinkedIn en injectant des styles CSS personnalisés en arrière-plan.
3. **Analyse des compétences (en Français)** :
   - Analyse la description pour extraire les outils techniques (SQL, Excel, Jira...), les méthodologies (Agile, Scrum...), les soft skills et les exigences linguistiques.
   - Normalise et déduplique les noms des compétences.
4. **Rapport Excel structuré** : Génère un fichier Excel `output/LinkedIn_BA_France_Report.xlsx` contenant :
   - Onglet **Job Listings** : Liste détaillée des offres avec liens vers les captures d'écran.
   - Onglet **Top Skills Ranking** : Classement par fréquence des compétences requises.

---

## Installation & Utilisation

### Prérequis
- Python 3.11+
- Microsoft Edge installé (le script utilise Edge headfully pour contourner les protections anti-robot de LinkedIn).

### Lancement du script
Exécutez la commande suivante depuis la racine du projet :

```powershell
.venv\Scripts\python.exe src\main.py
```

Le script va créer automatiquement un dossier `output/` contenant le fichier Excel final et les captures d'écran associées.

---

## Dashboard Web Interactif (Streamlit)

Vous pouvez lancer l'interface graphique interactive sur votre navigateur web local pour effectuer vos recherches dynamiquement, suivre vos candidatures en direct et analyser les compétences :

```powershell
.venv\Scripts\streamlit run src/app.py
```

### Fonctionnalités du Dashboard :
- **Recherche personnalisée** : Saisissez vos mots-clés (ex: `Alternance Product Owner`) et votre localisation directly dans le panneau latéral et lancez le scraper.
- **Suivi éditable en direct** : Modifiez le statut de vos candidatures, ajoutez des remarques ou des dates d'entretien directement depuis le tableau, puis sauvegardez.
- **Visualiseur d'images** : Visualisez l'image complète de l'offre d'emploi d'un simple clic.
- **Statistiques des compétences** : Graphique en barres des 15 compétences les plus demandées.
