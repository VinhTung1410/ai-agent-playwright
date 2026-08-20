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
5. **Dashboard Web Interactif (Streamlit)** : Interface graphique complète pour lancer la collecte, suivre l'avancement, éditer les candidatures en direct và visualiser les métriques.

---

## 🚀 Installation & Guide d'Exécution Local

### Prérequis
- **Python 3.11+**
- Moteur de navigateur **Chromium** (géré automatiquement via Playwright).

### 1. Installation des dépendances

```powershell
# Cloner le dépôt et naviguer dans le dossier
cd "AI Agent"

# Cài đặt thư viện Python trong môi trường ảo (.venv)
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Cài đặt trình duyệt Chromium cho Playwright
.\.venv\Scripts\python.exe -m playwright install chromium
```

---

### 2. Chạy ứng dụng dưới Local

#### Option A: Lancer le Dashboard Web Streamlit (Recommandé)

Dưới Windows PowerShell, sử dụng một trong các câu lệnh sau để tránh lỗi PATH:

```powershell
# Cách 1: Chạy trực tiếp qua Python module của .venv (Khuyên dùng)
.\.venv\Scripts\python.exe -m streamlit run src/app.py

# Cách 2: Kích hoạt môi trường ảo trước rồi chạy
.\.venv\Scripts\Activate.ps1
streamlit run src/app.py
```

#### Option B: Lancer le Scraper en ligne de commande (CLI)

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
- **Compatibilité Streamlit Cloud** : Résolution des problèmes de phân quyền `sudo` khi cài đặt trình duyệt Playwright trên môi trường container.
- **Standardisation Chromium** : Remplacement de Microsoft Edge par trình duyệt Chromium tiêu chuẩn (tự động chạy headless trên Linux/Cloud và headful trên Local).
- **Cấu hình packages.txt** : Bổ sung đầy đủ các thư viện hệ thống Linux (`libnss3`, `libgbm1`, `libxfixes3`,...) phục vụ chạy Chromium mượt mà trên server.
- **Cập nhật tài liệu README** : Hướng dẫn chi tiết cách chạy Streamlit local qua `.venv\Scripts\python.exe -m streamlit run src/app.py`.

### 📌 v1.0.1 (Sprint 2) - *Logging, Metadata & Application Tracking*
- Integrated application tracker columns (*Statut Candidature*, *Date Candidature*, *Contact Recruteur*, *Notes & Remarques*) into Excel reports.
- Added structured logging system for browser execution trace (`logs/browser.log`).
- Interactive Streamlit Web App initial setup with `st.data_editor`.

### 📌 v1.0.0 (Sprint 1) - *Browser Automation & Core Scraper*
- Built LinkedIn automated scraper using Playwright.
- Implemented full-page screenshot capturing with custom CSS overlay injection.
- Developed skill extraction engine based on standard skill taxonomy.
- Excel exporter with custom formatting, hyperlinks, and data validations.
