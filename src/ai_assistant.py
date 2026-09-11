import os
import re
import logging
from typing import Dict, List, Any, Optional
import dotenv

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

# Preferred models in order of priority
MODEL_CANDIDATES = [
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash"
]


def get_api_key(custom_key: Optional[str] = None) -> Optional[str]:
    """
    Récupère la clé d'API Gemini (priorité à la clé personnalisée passée en paramètre,
    puis aux fichiers .env à la racine ou dans .venv, puis aux variables d'environnement / st.secrets).
    """
    if custom_key and custom_key.strip():
        return custom_key.strip()

    # Recharger dynamiquement depuis les emplacements possibles (.env à la racine ou dans .venv)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, ".."))
    
    env_paths = [
        os.path.join(root_dir, ".env"),
        os.path.join(root_dir, ".venv", ".env"),
        os.path.join(current_dir, ".env"),
        ".env",
        ".venv/.env"
    ]
    for p in env_paths:
        if os.path.exists(p) and os.path.isfile(p):
            dotenv.load_dotenv(dotenv_path=p, override=True)
            break

    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    # Fallback pour Streamlit Cloud via st.secrets
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass

    return key.strip() if key and key.strip() else None


def call_gemini_api(prompt: str, system_instruction: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """
    Exécute un appel à l'API Gemini avec gestion des exceptions et bascule automatique de modèle.
    """
    key = get_api_key(api_key)
    if not key:
        raise ValueError("Clé API Gemini introuvable. Veuillez configurer GEMINI_API_KEY dans votre fichier .env.")

    # 1. Tentative avec le SDK moderne google-genai
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        
        last_err = None
        for model_name in MODEL_CANDIDATES:
            try:
                gen_config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7
                ) if system_instruction else types.GenerateContentConfig(temperature=0.7)
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=gen_config
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_err = e
                logger.warning(f"Modèle {model_name} indisponible: {e}. Essai du modèle suivant...")
                continue
        
        if last_err:
            raise last_err

    except ImportError:
        logger.info("google-genai non disponible, tentative avec google.generativeai...")

    # 2. Fallback avec google.generativeai si disponible
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=key)
        for model_name in ["gemini-1.5-flash", "gemini-pro"]:
            try:
                model = legacy_genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Échec de l'appel Gemini: {e}")

    raise RuntimeError("Impossible de contacter l'API Gemini avec les modèles configurés.")


def generate_cover_letter(
    cv_text: str,
    job_details: Dict[str, Any],
    matched_skills: List[str],
    missing_skills: List[str],
    candidate_name: str = "Lucas Martin",
    tone: str = "Professionnel & Dynamique",
    api_key: Optional[str] = None
) -> str:
    """
    Génère une lettre de motivation en français, sur-mesure, structurée selon les standards
    de recrutement français (Vous - Moi - Nous) et respectant les formules de politesse.
    """
    company = job_details.get("Company", "l'Entreprise")
    title = job_details.get("Job Title", job_details.get("Title", "Business Analyst"))
    location = job_details.get("Location", "France")
    contract = job_details.get("Employment Type", "Alternance")
    job_desc = job_details.get("Description", "")[:2500]  # limiter pour éviter la saturation du contexte
    
    matched_str = ", ".join(matched_skills) if matched_skills else "Business Analysis, Gestion de projet"
    missing_str = ", ".join(missing_skills) if missing_skills else "Aucune majeure"

    system_instruction = (
        "Tu es un expert senior en recrutement et coach carrière de premier plan sur le marché du travail en France. "
        "Tu rédiges des lettres de motivation percutantes, personnalisées et parfaitement rédigées en français soutenu "
        "pour des postes de Business Analyst, Product Owner et Data Analyst (Alternance, Stage, CDI). "
        "Tu appliques rigoureusement la structure 'Vous - Moi - Nous', sans phrases creuses ni clichés."
    )

    prompt = f"""
Rédige une lettre de motivation complète et ultra-personnalisée pour la candidature suivante :

### INFORMATIONS CANDIDAT :
- Nom du candidat : {candidate_name}
- Compétences validées avec l'offre (Points forts) : {matched_str}
- Compétences manquantes ou à valoriser : {missing_str}
- Extrait du CV :
\"\"\"{cv_text[:2000]}\"\"\"

### INFORMATIONS OFFRE D'EMPLOI :
- Poste visé : {title}
- Entreprise : {company}
- Localisation : {location}
- Type de contrat : {contract}
- Description du poste :
\"\"\"{job_desc}\"\"\"

### DIRECTIVES DE RÉDACTION :
1. **Ton souhaité :** {tone}.
2. **Structure obligatoire :**
   - **En-tête :** Coordonnées candidat (espace réservé), Coordonnées entreprise, Date du jour, Objet clair avec intitulé du poste et référence de l'annonce.
   - **Introduction (Accroche & 'Vous') :** Montrer une compréhension précise de l'activité de {company} et des enjeux du poste de {title}.
   - **Corps de texte ('Moi') :** Valoriser 2 ou 3 réalisations concrètes du CV qui démontrent la maîtrise de {matched_str}. Mentionner habilement l'aptitude à monter en compétence sur {missing_str}.
   - **Projection ('Nous') :** Expliquer comment le candidat va créer de la valeur concrète dès ses premières semaines dans l'équipe.
   - **Conclusion :** Demande proactive d'entretien et formule de politesse formelle et élégante (ex: "Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées").
3. **Format :** Rends le texte en Markdown soigné, prêt à être copié ou téléchargé.
"""

    return call_gemini_api(prompt, system_instruction=system_instruction, api_key=api_key)


def generate_inmail_message(
    cv_text: str,
    job_details: Dict[str, Any],
    matched_skills: List[str],
    candidate_name: str = "Lucas Martin",
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Génère deux formats de messages d'approche LinkedIn :
    1. Message de demande de connexion (strictement < 300 caractères).
    2. Message InMail direct complet (~100-150 mots).
    """
    company = job_details.get("Company", "l'Entreprise")
    title = job_details.get("Job Title", job_details.get("Title", "Business Analyst"))
    matched_str = ", ".join(matched_skills[:3]) if matched_skills else "Business Analysis"

    system_instruction = (
        "Tu es un spécialiste du réseautage professionnel sur LinkedIn en France. "
        "Tu écris des messages d'approche qui captent immédiatement l'attention des recruteurs et managers, "
        "avec un ton courtois, direct et sans lourdeur."
    )

    prompt = f"""
Rédige 2 messages d'approche LinkedIn en français pour contacter le recruteur ou manager du poste de **{title}** chez **{company}** :

- Nom du candidat : {candidate_name}
- Compétences clés alignées : {matched_str}

Retourne STRICTEMENT le format suivant avec les balises indiquées :

[CONNEXION_NOTE]
(Ici une note d'invitation percutante de MOINS DE 280 CARACTÈRES espaces compris pour la demande de connexion LinkedIn).
[/CONNEXION_NOTE]

[INMAIL_MESSAGE]
(Ici un message InMail complet de 100 à 150 mots : Salutations, accroche sur l'offre de {title}, 2 arguments percutants liant le profil à {company}, appel à l'action pour un bref échange de 10 minutes, formule de politesse).
[/INMAIL_MESSAGE]
"""

    response_text = call_gemini_api(prompt, system_instruction=system_instruction, api_key=api_key)

    # Extraction des sections
    conn_match = re.search(r'\[CONNEXION_NOTE\](.*?)\[/CONNEXION_NOTE\]', response_text, re.DOTALL)
    inmail_match = re.search(r'\[INMAIL_MESSAGE\](.*?)\[/INMAIL_MESSAGE\]', response_text, re.DOTALL)

    note = conn_match.group(1).strip() if conn_match else response_text[:280]
    inmail = inmail_match.group(1).strip() if inmail_match else response_text

    return {
        "connection_note": note,
        "inmail_message": inmail
    }


def suggest_ats_bullets(
    cv_text: str,
    job_details: Dict[str, Any],
    missing_skills: List[str],
    api_key: Optional[str] = None
) -> str:
    """
    Propose 3 gạch đầu dòng (bullet points) hành động theo phương pháp STAR/XYZ
    để tích hợp vào CV nhằm bù đắp các từ khóa ATS còn thiếu.
    """
    if not missing_skills:
        return "🎉 Votre profil couvre déjà l'intégralité des compétences clés de l'offre !"

    company = job_details.get("Company", "l'Entreprise")
    title = job_details.get("Job Title", job_details.get("Title", "Business Analyst"))
    missing_str = ", ".join(missing_skills)

    prompt = f"""
En tant qu'expert en recrutement et optimisation ATS pour le marché français, analyse les compétences manquantes suivantes :
**{missing_str}** pour le poste de **{title}** chez **{company}**.

Propose 3 puces de réalisations (bullet points) percutantes en français, rédigées au format STAR/XYZ (Verbe d'action + Contexte/Outil + Résultat chiffré), que le candidat peut adapter et intégrer dans ses expériences de CV pour franchir le filtre ATS :

Donne des exemples réalistes et concrets.
"""
    return call_gemini_api(prompt, api_key=api_key)
