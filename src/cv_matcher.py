import io
from typing import List, Dict, Tuple, Any, Optional
import pypdf
try:
    from scraper import SKILL_MAP, extract_skills_from_text
except ImportError:
    from src.scraper import SKILL_MAP, extract_skills_from_text


def extract_text_from_pdf(pdf_source: Any) -> str:
    """
    Extrait le texte intégral d'un fichier PDF (chemin de fichier ou objet binaire/BytesIO).
    """
    text_content = []
    try:
        if isinstance(pdf_source, (str, bytes)):
            stream = io.BytesIO(pdf_source) if isinstance(pdf_source, bytes) else pdf_source
            reader = pypdf.PdfReader(stream)
        else:
            # Pour Streamlit UploadedFile ou objet similaire
            reader = pypdf.PdfReader(pdf_source)
            
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
    except Exception as e:
        print(f"Erreur lors de la lecture du PDF : {e}")
        return ""

    return "\n".join(text_content).strip()


def analyze_cv_skills(cv_text: str) -> Dict[str, Any]:
    """
    Analyse le texte du CV pour extraire et catégoriser les compétences clés.
    """
    if not cv_text:
        return {"skills": [], "categories": {}, "word_count": 0}

    skills = extract_skills_from_text(cv_text)
    
    # Regrouper par catégorie
    categories: Dict[str, List[str]] = {}
    skill_category_map: Dict[str, str] = {}
    for skill in skills:
        cat = SKILL_MAP.get(skill, ([], "Autre"))[1]
        categories.setdefault(cat, []).append(skill)
        skill_category_map[skill] = cat

    return {
        "skills": skills,
        "categories": categories,
        "skill_category_map": skill_category_map,
        "word_count": len(cv_text.split())
    }


def compute_job_match(cv_skills: List[str], job_skills: List[str], job_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Calcule la correspondance entre les compétences du CV et les exigences de l'offre d'emploi.
    Génère un score de pertinence (%) et des recommandations personnalisées.
    """
    cv_set = set(cv_skills)
    job_set = set(job_skills)

    matched = sorted(list(cv_set.intersection(job_set)))
    missing = sorted(list(job_set - cv_set))
    extra = sorted(list(cv_set - job_set))

    if not job_skills:
        score = 80 if cv_skills else 50
    else:
        score = min(100, round((len(matched) / len(job_skills)) * 100))

    # Évaluation du niveau de correspondance
    if score >= 75:
        match_level = "Excellent Match (Prêt à postuler)"
        level_color = "green"
    elif score >= 50:
        match_level = "Bon Match (Quelques ajustements recommandés)"
        level_color = "orange"
    else:
        match_level = "Écart important (Profil à renforcer)"
        level_color = "red"

    # Recommandations d'optimisation
    recommendations = []
    
    # 1. Mise en valeur des points forts
    if matched:
        top_strengths = ", ".join(matched[:4])
        recommendations.append(
            f"**Mettre en avant vos atouts majeurs :** Vos compétences en **{top_strengths}** correspondent parfaitement à l'offre. Placez-les en tête de votre profil ou dans l'accroche de votre lettre de motivation."
        )

    # 2. Conseils sur les compétences manquantes
    if missing:
        missing_str = ", ".join(missing)
        recommendations.append(
            f"**Combler les mots-clés manquants :** L'offre recherche explicitement **{missing_str}**. Si vous avez déjà utilisé ces outils/méthodes en projet académique ou personnel, intégrez ces termes exacts pour franchir les filtres ATS."
        )
        
        # Conseils ciblés par type de compétence
        missing_tech = [s for s in missing if SKILL_MAP.get(s, ([], ""))[1] == "Outil Technique / Logiciel"]
        missing_methods = [s for s in missing if SKILL_MAP.get(s, ([], ""))[1] == "Méthodologie / Framework"]
        
        if missing_tech:
            recommendations.append(
                f"**Outils techniques à valoriser :** Si vous débutez sur **{', '.join(missing_tech)}**, mentionnez votre adaptabilité en citant des outils similaires maîtrisés (ex: Power BI vs Tableau, SQL vs Excel avancé)."
            )
        if missing_methods:
            recommendations.append(
                f"**Cadre méthodologique :** L'équipe applique **{', '.join(missing_methods)}**. Mentionnez votre capacité à travailler en sprints, participer aux daily standups ou rédiger des User Stories."
            )
    else:
        recommendations.append(
            "**Alignement parfait :** Votre profil couvre 100% des compétences clés mentionnées dans l'annonce ! Soignez la présentation de vos réalisations chiffrées."
        )

    # 3. Conseil contextuel selon le poste
    if job_details:
        emp_type = str(job_details.get("Employment Type", "")).lower()
        if "alternance" in emp_type or "stage" in emp_type or "apprenti" in emp_type:
            recommendations.append(
                "**Conseil Alternance/Stage :** Les recruteurs privilégient le potentiel d'apprentissage et la curiosité. Mettez en avant vos projets d'école et votre rigueur méthodologique."
            )

    return {
        "score": score,
        "match_level": match_level,
        "level_color": level_color,
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "recommendations": recommendations
    }


def rank_all_jobs_for_cv(cv_skills: List[str], jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Classe l'ensemble des offres collectées par score de compatibilité décroissant avec le CV.
    """
    ranked_jobs = []
    for job in jobs_data:
        # Extraire les compétences requises
        raw_skills = job.get("Key Skills Required", job.get("Extracted Skills", ""))
        if isinstance(raw_skills, list):
            job_skills = raw_skills
        elif isinstance(raw_skills, str) and raw_skills.strip():
            job_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
        else:
            job_skills = []

        match_result = compute_job_match(cv_skills, job_skills, job)
        ranked_jobs.append({
            "Job ID": job.get("ID", job.get("Job ID", "")),
            "Title": job.get("Job Title", job.get("Title", "")),
            "Company": job.get("Company", ""),
            "Location": job.get("Location", ""),
            "Score": match_result["score"],
            "Match Level": match_result["match_level"],
            "Level Color": match_result["level_color"],
            "Matched Count": len(match_result["matched_skills"]),
            "Missing Count": len(match_result["missing_skills"]),
            "Matched Skills": ", ".join(match_result["matched_skills"]),
            "Missing Skills": ", ".join(match_result["missing_skills"]),
            "Job URL": job.get("Job URL", ""),
            "raw_job": job
        })

    # Trier par score décroissant
    ranked_jobs.sort(key=lambda x: x["Score"], reverse=True)
    return ranked_jobs
