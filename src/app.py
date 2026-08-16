import os
import subprocess
import pandas as pd
import streamlit as st

from scraper import scrape_linkedin, process_and_export

# Page configuration
st.set_page_config(
    page_title="LinkedIn Job Search & Application Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Premium Aesthetics
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        color: #1F4E78;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F2F4F7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #1F4E78;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# File Paths
EXCEL_PATH = "output/LinkedIn_BA_France_Report.xlsx"
SCREENSHOTS_DIR = "output/screenshots"

def load_data():
    if os.path.exists(EXCEL_PATH):
        try:
            df_jobs = pd.read_excel(EXCEL_PATH, sheet_name="Job Listings")
            
            # Cast application tracking columns to string and fill NaNs to prevent Streamlit type mismatches
            tracking_cols = ["Statut Candidature", "Date Candidature", "Contact Recruteur", "Notes & Remarques"]
            for col in tracking_cols:
                if col in df_jobs.columns:
                    df_jobs[col] = df_jobs[col].fillna("").astype(str)
                else:
                    df_jobs[col] = ""
                    
            df_ranking = pd.read_excel(EXCEL_PATH, sheet_name="Top Skills Ranking")
            return df_jobs, df_ranking
        except Exception as e:
            st.error(f"Error loading Excel file: {e}")
    return None, None

def save_data(df_jobs):
    try:
        # Re-read rankings to preserve them
        _, df_ranking = load_data()
        
        # Save back to Excel
        with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
            df_jobs.to_excel(writer, sheet_name="Job Listings", index=False)
            if df_ranking is not None:
                df_ranking.to_excel(writer, sheet_name="Top Skills Ranking", index=False)
        st.success("Changes saved successfully to Excel report!")
    except Exception as e:
        st.error(f"Error saving data: {e}")

# App Title
st.markdown('<div class="main-title">💼 LinkedIn Job Scraper & Application Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Recherchez des opportunités d\'alternance, analysez les compétences clés requises et gérez vos candidatures en temps réel. (v1.0.1)</div>', unsafe_allow_html=True)

# Load existing data
df_jobs, df_ranking = load_data()

# Sidebar: Controls & Scraper trigger
with st.sidebar:
    st.header("🔍 Critères de Recherche")
    keywords_input = st.text_input("Mots-clés de l'emploi", value="alternance business analyst")
    location_input = st.text_input("Localisation", value="France")
    
    st.markdown("---")
    st.subheader("🚀 Lancer une nouvelle recherche")
    st.write("Le scraper va lancer Microsoft Edge localement, récupérer jusqu'à 30 offres récentes publiées dans les dernières 24h, et extraire les compétences.")
    
    if st.button("Lancer la collecte", type="primary"):
        with st.status("Collecte des offres en cours...", expanded=True) as status:
            try:
                    import glob
                    cache_dir = os.path.expanduser("~/.cache/ms-playwright")
                    # Check if any chromium folder exists physically in the cache directory
                    has_chromium = len(glob.glob(os.path.join(cache_dir, "chromium_headless_shell-*"))) > 0 or len(glob.glob(os.path.join(cache_dir, "chromium-*"))) > 0
                    
                    if not has_chromium:
                        status.write("Chromium introuvable. Téléchargement du navigateur (environ 30-60s)...")
                        import sys
                        # Install chromium browser binary
                        res = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True, text=True)
                        if res.returncode != 0:
                            st.error(f"Playwright installation failed: {res.stderr}\n{res.stdout}")
                            
                    status.write("Lancement du navigateur...")
                    jobs_data = scrape_linkedin(keywords_input, location_input)
                    
                    status.write(f"Analyse des compétences et export Excel ({len(jobs_data)} offres trouvées)...")
                    process_and_export(jobs_data)
                    
                    status.update(label="Collecte terminée avec succès !", state="complete")
                    st.rerun()
            except Exception as e:
                status.update(label=f"Erreur lors de la collecte : {e}", state="error")
                st.error(e)

# Main Section Layout
if df_jobs is not None:
    # 1. Metric Overview
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <span style="font-size: 0.9rem; color: #666;">Offres collectées</span><br>
                <span style="font-size: 1.8rem; font-weight: bold; color: #1F4E78;">{len(df_jobs)}</span>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        top_skill = df_ranking.iloc[0]["Skill Name"] if df_ranking is not None and not df_ranking.empty else "N/A"
        top_rate = df_ranking.iloc[0]["Occurrence Rate (%)"] if df_ranking is not None and not df_ranking.empty else "0%"
        st.markdown(f"""
            <div class="metric-card">
                <span style="font-size: 0.9rem; color: #666;">Compétence la plus demandée</span><br>
                <span style="font-size: 1.8rem; font-weight: bold; color: #2E7D32;">{top_skill} ({top_rate})</span>
            </div>
        """, unsafe_allow_html=True)

    # 2. Main Job Listings Tracker (Editable Table!)
    st.subheader("📋 Liste des offres d'emploi et suivi des candidatures")
    st.info("💡 Astuce : Vous pouvez modifier les colonnes de suivi (Statut, Date, Contact, Notes) directement dans le tableau ci-dessous, puis cliquer sur le bouton Sauvegarder pour mettre à jour le fichier Excel !")
    
    # Render with Streamlit Data Editor
    edited_df = st.data_editor(
        df_jobs,
        column_config={
            "ID": st.column_config.NumberColumn(disabled=True),
            "Job Title": st.column_config.TextColumn("Titre du Poste", disabled=True),
            "Company": st.column_config.TextColumn("Entreprise", disabled=True),
            "Location": st.column_config.TextColumn("Localisation", disabled=True),
            "Job URL": st.column_config.LinkColumn("Lien de l'Offre", disabled=True),
            "Key Skills Required": st.column_config.TextColumn("Compétences Clés", disabled=True),
            "Screenshot File": st.column_config.TextColumn("Fichier Screenshot", disabled=True),
            "Statut Candidature": st.column_config.SelectboxColumn(
                "Statut Candidature",
                options=["À postuler", "Postulé", "Entretien", "Refusé", "Offre reçue"],
                required=True
            ),
            "Date Candidature": st.column_config.TextColumn("Date de Candidature"),
            "Contact Recruteur": st.column_config.TextColumn("Contact Recruteur"),
            "Notes & Remarques": st.column_config.TextColumn("Notes & Remarques")
        },
        width="stretch",
        hide_index=True
    )
    
    # Save button for modifications
    if st.button("Sauvegarder les modifications"):
        save_data(edited_df)

    # 3. Two columns for Visualizations and Screenshot Viewer
    st.markdown("---")
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📊 Compétences les plus recherchées")
        if df_ranking is not None and not df_ranking.empty:
            # Simple bar chart using Streamlit native charts
            chart_df = df_ranking.head(15).copy()
            # Clean occurrence rate to float for plotting
            chart_df["Taux de demande (%)"] = chart_df["Occurrence Rate (%)"].str.replace("%", "").astype(float)
            st.bar_chart(
                chart_df,
                x="Skill Name",
                y="Taux de demande (%)",
                color="#1F4E78",
                horizontal=True
            )
        else:
            st.write("Aucune compétence extraite pour le moment.")
            
    with col_right:
        st.subheader("🖼️ Visualiseur de Captures d'Écran")
        # Dropdown to select a job to display its screenshot
        job_options = {f"{row['ID']}. {row['Company']} - {row['Job Title']}": row["Screenshot File"] for _, row in df_jobs.iterrows()}
        selected_job = st.selectbox("Sélectionnez une offre pour voir sa capture d'écran", list(job_options.keys()))
        
        if selected_job:
            screenshot_path = job_options[selected_job]
            if pd.notna(screenshot_path) and os.path.exists(screenshot_path):
                st.image(screenshot_path, caption=selected_job, width="stretch")
            else:
                st.warning("Aucune capture d'écran disponible ou fichier manquant.")
else:
    st.warning("Aucune donnée disponible. Veuillez saisir vos mots-clés dans la barre latérale gauche et cliquer sur 'Lancer la collecte'.")
