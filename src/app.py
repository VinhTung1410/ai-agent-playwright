import os
import time
import subprocess
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from scraper import scrape_linkedin, process_and_export, format_job_description

# Page configuration
st.set_page_config(
    page_title="LinkedIn Job Search & Application Tracker",
    page_icon="💼",
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
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        padding: 1.1rem 1.2rem;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #1F4E78;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .eta-box {
        background-color: #F1F5F9;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.88rem;
        color: #334155;
        margin-top: 5px;
        margin-bottom: 12px;
        border-left: 3px solid #3B82F6;
    }
    .job-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 0.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .job-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.4rem;
    }
    .job-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #F1F5F9;
    }
    .job-meta-item {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: #F8FAFC;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
        font-weight: 500;
    }
    .skill-pill {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .job-desc-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.2rem;
        font-size: 0.92rem;
        line-height: 1.65;
        color: #1E293B;
        max-height: 420px;
        overflow-y: auto;
        white-space: pre-line;
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
                    
            meta_defaults = {
                "Employment Type": "Alternance / CDI",
                "Seniority Level": "Non spécifié",
                "Industries": "Non spécifié",
                "Job Function": "Non spécifié",
                "Company URL": ""
            }
            for col, default_val in meta_defaults.items():
                if col in df_jobs.columns:
                    df_jobs[col] = df_jobs[col].fillna(default_val).astype(str)
                else:
                    df_jobs[col] = default_val
                    
            df_ranking = pd.read_excel(EXCEL_PATH, sheet_name="Top Skills Ranking")
            return df_jobs, df_ranking
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier Excel : {e}")
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
        st.success("✅ Modifications enregistrées avec succès dans le rapport Excel !")
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")

# App Title & Header
st.markdown('<div class="main-title">💼 LinkedIn Job Scraper & Application Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Collectez et analysez les opportunités d\'alternance, visualisez les compétences clés et pilotez vos candidatures en temps réel. (Sprint 4)</div>', unsafe_allow_html=True)

# Load existing data
df_jobs, df_ranking = load_data()

# Sidebar: Controls & Search Parameters
with st.sidebar:
    st.header("⚙️ Paramètres de Recherche")
    keywords_input = st.text_input("Mots-clés de l'emploi", value="alternance business analyst")
    location_input = st.text_input("Localisation", value="France")
    
    st.markdown("---")
    st.subheader("🎯 Contrôle de la Collecte")
    
    max_jobs_input = st.slider(
        "Nombre max d'offres à collecter",
        min_value=6,
        max_value=30,
        value=10,
        step=2,
        help="Recommandation : 10 à 14 offres pour une analyse rapide en moins de 30 secondes."
    )
    
    # Estimated time calculation
    est_seconds = int(max_jobs_input * 2.3 + 6)
    st.markdown(f"""
        <div class="eta-box">
            ⏱️ <b>Temps estimé :</b> ~{est_seconds} secondes<br>
            💡 <i>Pour éviter d'être bloqué par LinkedIn, la limite est fixée à 30 offres max.</i>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Lancer la collecte", type="primary", use_container_width=True):
        progress_placeholder = st.empty()
        status_text = st.empty()
        detail_text = st.empty()
        
        with st.status("🔄 Collecte des offres en cours...", expanded=True) as status_box:
            try:
                start_time = time.time()
                
                # Check / install Playwright Chromium if missing
                import glob
                cache_dir = os.path.expanduser("~/.cache/ms-playwright")
                has_chromium = len(glob.glob(os.path.join(cache_dir, "chromium_headless_shell-*"))) > 0 or len(glob.glob(os.path.join(cache_dir, "chromium-*"))) > 0
                
                if not has_chromium:
                    status_text.text("📦 Téléchargement de Chromium (environ 30-60s)...")
                    import sys
                    res = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True, text=True)
                    if res.returncode != 0:
                        st.warning(f"Avertissement installation Playwright: {res.stderr}\n{res.stdout}")

                def progress_callback(current, total, message):
                    elapsed = time.time() - start_time
                    ratio = min(1.0, current / max(1, total)) if total > 0 else 0.0
                    progress_placeholder.progress(ratio)
                    status_text.markdown(f"**Progression :** `{int(ratio * 100)}%` ({current}/{total} offres) — ⏱️ Écoulé : `{elapsed:.1f}s`")
                    detail_text.text(f"📍 {message}")

                jobs_data = scrape_linkedin(
                    keywords=keywords_input,
                    location=location_input,
                    max_jobs=max_jobs_input,
                    progress_callback=progress_callback
                )
                
                status_text.text(f"📊 Analyse des compétences et génération du rapport ({len(jobs_data)} offres)...")
                process_and_export(jobs_data)
                
                total_duration = time.time() - start_time
                progress_placeholder.progress(1.0)
                status_box.update(label=f"✅ Collecte terminée với succès en {total_duration:.1f}s !", state="complete")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                status_box.update(label=f"❌ Erreur lors de la collecte : {e}", state="error")
                st.error(e)

# Main Section Layout
if df_jobs is not None and not df_jobs.empty:
    # 1. Metric Overview Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Offres</div>
                <div class="metric-value">{len(df_jobs)}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        top_skill = df_ranking.iloc[0]["Skill Name"] if df_ranking is not None and not df_ranking.empty else "N/A"
        top_rate = df_ranking.iloc[0]["Occurrence Rate (%)"] if df_ranking is not None and not df_ranking.empty else "0%"
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #2E7D32;">
                <div class="metric-label">Compétence N°1</div>
                <div class="metric-value" style="color: #2E7D32;" title="{top_skill}">{top_skill} <span style="font-size: 1rem; color: #64748B;">({top_rate})</span></div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        top_comp = df_jobs["Company"].value_counts().index[0] if "Company" in df_jobs.columns and not df_jobs.empty else "N/A"
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #D97706;">
                <div class="metric-label">Top Recruteur</div>
                <div class="metric-value" style="color: #D97706;" title="{top_comp}">{top_comp}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        # Count distinct locations
        top_loc = df_jobs["Location"].value_counts().index[0] if "Location" in df_jobs.columns and not df_jobs.empty else "France"
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #8B5CF6;">
                <div class="metric-label">Zone Principale</div>
                <div class="metric-value" style="color: #8B5CF6;" title="{top_loc}">{top_loc}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs for Rich Dashboard Navigation
    tab1, tab2, tab3 = st.tabs([
        "📊 Tableaux de Bord & Visualisations",
        "📋 Suivi des Candidatures",
        "📑 Fiche de Poste & Captures d'Écran"
    ])

    # TAB 1: VISUAL ANALYTICS
    with tab1:
        st.subheader("📈 Analyse Visuelle des Offres & Compétences")
        
        row1_col1, row1_col2 = st.columns([3, 2])
        
        # Common hover styling for all charts
        common_hoverlabel = dict(
            bgcolor="#1E293B",
            font_size=12,
            font_color="#FFFFFF",
            font_family="sans-serif",
            bordercolor="#334155"
        )

        with row1_col1:
            if df_ranking is not None and not df_ranking.empty:
                chart_df = df_ranking.head(15).copy()
                chart_df["Taux (%)"] = chart_df["Occurrence Rate (%)"].astype(str).str.replace("%", "").astype(float)
                # Sort ascending for better horizontal bar rendering
                chart_df = chart_df.sort_values(by="Taux (%)", ascending=True)

                total_jobs = len(df_jobs)
                # Format directly as 'X/Y (Z%)' for instant clarity without needing hover popups
                chart_df["Label"] = chart_df.apply(
                    lambda r: f"{int(r['Job Count'])}/{total_jobs} ({r['Taux (%)']:.1f}%)", axis=1
                )

                fig_skills = px.bar(
                    chart_df,
                    x="Taux (%)",
                    y="Skill Name",
                    color="Category",
                    orientation="h",
                    title="<b>Top 15 des Compétences les Plus Demandées</b>",
                    labels={"Taux (%)": "Taux de mention dans les offres (%)", "Skill Name": "Compétence", "Category": "Catégorie"},
                    color_discrete_map={
                        "Outil Technique / Logiciel": "#1F4E78",
                        "Méthodologie / Framework": "#0284C7",
                        "Compétence Professionnelle / Soft Skill": "#10B981",
                        "Langue": "#F59E0B"
                    },
                    text="Label"
                )
                max_rate = chart_df["Taux (%)"].max() if not chart_df.empty else 100
                fig_skills.update_traces(
                    textposition='outside',
                    cliponaxis=False,
                    hoverinfo='skip',
                    hovertemplate=None
                )
                fig_skills.update_xaxes(range=[0, max(max_rate * 1.25, 10)])
                fig_skills.update_layout(
                    height=490,
                    margin=dict(l=10, r=90, t=50, b=60),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        title=None
                    )
                )
                st.plotly_chart(fig_skills, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Aucune donnée de compétence disponible.")

        with row1_col2:
            if df_ranking is not None and not df_ranking.empty and "Category" in df_ranking.columns:
                cat_counts = df_ranking.groupby("Category")["Job Count"].sum().reset_index()
                fig_cat = px.pie(
                    cat_counts,
                    values="Job Count",
                    names="Category",
                    hole=0.45,
                    title="<b>Répartition par Catégorie de Compétences</b>",
                    color="Category",
                    color_discrete_map={
                        "Outil Technique / Logiciel": "#1F4E78",
                        "Méthodologie / Framework": "#0284C7",
                        "Compétence Professionnelle / Soft Skill": "#10B981",
                        "Langue": "#F59E0B"
                    }
                )
                fig_cat.update_traces(
                    hovertemplate="<b>%{label}</b><br>Occurrences : <b>%{value}</b> (%{percent})<extra></extra>"
                )
                fig_cat.update_layout(
                    height=480,
                    margin=dict(l=10, r=10, t=50, b=60),
                    hoverlabel=common_hoverlabel,
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, title=None)
                )
                st.plotly_chart(fig_cat, use_container_width=True, config={'displayModeBar': False})

        st.markdown("---")
        
        row2_col1, row2_col2 = st.columns([1, 1])
        
        with row2_col1:
            # Top Companies
            comp_series = df_jobs["Company"].value_counts().head(8).reset_index()
            comp_series.columns = ["Entreprise", "Nombre d'offres"]
            comp_series = comp_series.sort_values(by="Nombre d'offres", ascending=True)
            
            total_jobs = len(df_jobs)
            comp_col = "Nombre d'offres"
            comp_series["Label"] = comp_series[comp_col].apply(
                lambda count: f"{int(count)}/{total_jobs} ({int(count)/max(1, total_jobs)*100:.0f}%)"
            )

            fig_comp = px.bar(
                comp_series,
                x="Nombre d'offres",
                y="Entreprise",
                orientation="h",
                title="<b>Top Entreprises qui Recrutent</b>",
                color="Nombre d'offres",
                color_continuous_scale="Blues",
                text="Label"
            )
            max_comp_count = comp_series["Nombre d'offres"].max() if not comp_series.empty else 5
            fig_comp.update_traces(
                textposition='outside',
                cliponaxis=False,
                hoverinfo='skip',
                hovertemplate=None
            )
            fig_comp.update_xaxes(range=[0, max(max_comp_count * 1.35, 3)])
            fig_comp.update_layout(
                height=360,
                margin=dict(l=10, r=80, t=50, b=30),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})

        with row2_col2:
            # Location Distribution
            loc_series = df_jobs["Location"].value_counts().head(8).reset_index()
            loc_series.columns = ["Localisation", "Nombre d'offres"]
            
            fig_loc = px.pie(
                loc_series,
                values="Nombre d'offres",
                names="Localisation",
                title="<b>Répartition Géographique des Postes</b>",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_loc.update_traces(
                hovertemplate="<b>%{label}</b><br>Nombre d'offres : <b>%{value}</b> (%{percent})<extra></extra>"
            )
            fig_loc.update_layout(
                height=360,
                margin=dict(l=10, r=10, t=50, b=30),
                hoverlabel=common_hoverlabel
            )
            st.plotly_chart(fig_loc, use_container_width=True, config={'displayModeBar': False})

    # TAB 2: APPLICATION TRACKER & EXCEL EXPORT
    with tab2:
        st.subheader("📋 Tableau de Bord de Suivi des Candidatures")
        st.caption("Modifiez directement vos statuts de candidature, dates et notes dans le tableau ci-dessous.")

        col_act1, col_act2, _ = st.columns([2, 2, 4])
        with col_act1:
            save_clicked = st.button("💾 Sauvegarder les modifications", type="primary", use_container_width=True)
            
        with col_act2:
            # Direct Excel Download button
            if os.path.exists(EXCEL_PATH):
                with open(EXCEL_PATH, "rb") as f:
                    excel_data = f.read()
                st.download_button(
                    label="📥 Télécharger le Rapport Excel",
                    data=excel_data,
                    file_name="LinkedIn_Job_Tracker_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        # Render Data Editor
        edited_df = st.data_editor(
            df_jobs,
            column_config={
                "ID": st.column_config.NumberColumn("ID", disabled=True, width="small"),
                "Job Title": st.column_config.TextColumn("Titre du Poste", disabled=True, width="medium"),
                "Company": st.column_config.TextColumn("Entreprise", disabled=True, width="small"),
                "Location": st.column_config.TextColumn("Localisation", disabled=True, width="small"),
                "Employment Type": st.column_config.TextColumn("Contrat", disabled=True, width="small"),
                "Seniority Level": st.column_config.TextColumn("Niveau", disabled=True, width="small"),
                "Industries": st.column_config.TextColumn("Secteur", disabled=True, width="small"),
                "Job URL": st.column_config.LinkColumn("Lien LinkedIn", disabled=True, width="small"),
                "Key Skills Required": st.column_config.TextColumn("Compétences Clés", disabled=True, width="medium"),
                "Statut Candidature": st.column_config.SelectboxColumn(
                    "Statut Candidature",
                    options=["À postuler", "Postulé", "Entretien", "Refusé", "Offre reçue"],
                    required=True,
                    width="medium"
                ),
                "Date Candidature": st.column_config.TextColumn("Date Candidature", width="small"),
                "Contact Recruteur": st.column_config.TextColumn("Contact Recruteur", width="medium"),
                "Notes & Remarques": st.column_config.TextColumn("Notes & Remarques", width="large")
            },
            width="stretch",
            hide_index=True
        )

        if save_clicked:
            save_data(edited_df)

    # TAB 3: NATIVE ABOUT THE JOB & ABOUT THE COMPANY VIEWER
    with tab3:
        st.subheader("📑 Fiche Détaillée : About the Job & About the Company")
        st.caption("Consultez la fiche structurée du poste, les responsabilités, les compétences requises et le profil de l'entreprise (100% propre, sans bannières rác).")
        
        job_options = {f"#{row['ID']} - {row['Company']} ({row['Job Title']})": row["ID"] for _, row in df_jobs.iterrows()}
        selected_job_label = st.selectbox("Sélectionnez une offre à afficher", list(job_options.keys()))
        
        if selected_job_label:
            selected_id = job_options[selected_job_label]
            selected_job = df_jobs[df_jobs["ID"] == selected_id].iloc[0]
            
            # 1. Header Card with Titles and Direct Action Links
            col_info, col_btn = st.columns([3, 2])
            with col_info:
                st.markdown(f"""
                    <div class="job-title">{selected_job['Job Title']}</div>
                    <div class="job-meta">
                        <span class="job-meta-item">🏢 <b>Entreprise :</b> {selected_job['Company']}</span>
                        <span class="job-meta-item">📍 <b>Lieu :</b> {selected_job['Location']}</span>
                        <span class="job-meta-item">📌 <b>Statut :</b> {selected_job.get('Statut Candidature', 'À postuler')}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                with b1:
                    job_url = str(selected_job.get('Job URL', ''))
                    if job_url and job_url.startswith("http"):
                        st.link_button("🔗 Postuler sur LinkedIn", job_url, use_container_width=True)
                with b2:
                    comp_url = str(selected_job.get('Company URL', ''))
                    if comp_url and comp_url.startswith("http"):
                        st.link_button("🏢 Page Entreprise", comp_url, use_container_width=True)

            # 2. Key Criteria Metrics
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("💼 Type de contrat", str(selected_job.get("Employment Type", "Alternance / CDI")))
            with c2:
                st.metric("🎯 Niveau d'expérience", str(selected_job.get("Seniority Level", "Non spécifié")))
            with c3:
                st.metric("🏭 Secteur d'activité", str(selected_job.get("Industries", "Non spécifié")))
            with c4:
                st.metric("📌 Statut suivi", str(selected_job.get("Statut Candidature", "À postuler")))

            st.markdown("---")

            # 3. Key Skills Badges
            skills_raw = str(selected_job.get("Key Skills Required", ""))
            if skills_raw and skills_raw != "nan":
                skills_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
                skills_html = "".join([f'<span class="skill-pill">⚡ {s}</span>' for s in skills_list])
                st.markdown(f"**Compétences Clés Requises ({len(skills_list)}) :**<br>{skills_html}", unsafe_allow_html=True)
            else:
                st.info("ℹ️ Aucune compétence spécifique détectée dans cette offre.")

            st.markdown("<br>", unsafe_allow_html=True)

            # 4. About the Job (Clean Full Description)
            st.markdown("### 📄 About the job")
            desc_text = str(selected_job.get("Description", "")).strip()
            if desc_text and desc_text != "nan":
                formatted_desc = format_job_description(desc_text)
                with st.container(height=380):
                    st.markdown(formatted_desc)
            else:
                st.info("ℹ️ Aucune description textuelle disponible pour cette offre.")

            st.markdown("<br>", unsafe_allow_html=True)

            # 5. About the Company
            st.markdown("### 🏢 About the company")
            comp_url_display = str(selected_job.get('Company URL', ''))
            comp_link_html = f'<a href="{comp_url_display}" target="_blank" style="color:#0284C7; font-weight:600; text-decoration:none;">🔗 Voir le profil de l\'entreprise sur LinkedIn</a>' if comp_url_display and comp_url_display.startswith("http") else ""
            st.markdown(f"""
                <div class="metric-card" style="border-left-color: #0284C7; background: #F8FAFC;">
                    <h4 style="margin-top:0; color: #0F172A; font-size: 1.25rem;">🏢 {selected_job['Company']}</h4>
                    <p style="margin-bottom: 6px; color: #475569;"><b>📍 Siège / Localisation :</b> {selected_job['Location']}</p>
                    <p style="margin-bottom: 6px; color: #475569;"><b>🏭 Secteur d'activité :</b> {selected_job.get('Industries', 'Non spécifié')}</p>
                    <p style="margin-bottom: 8px; color: #475569;"><b>💼 Type de recrutement :</b> {selected_job.get('Employment Type', 'Alternance / CDI')}</p>
                    {comp_link_html}
                </div>
            """, unsafe_allow_html=True)

else:
    st.info("💡 Aucune donnée disponible pour le moment. Veuillez configurer vos mots-clés dans la barre latérale và cliquer sur **'Lancer la collecte'**.")
