import os
import re
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

# -----------------------------------------------------
#            CHARGEMENT VARIABLES .ENV
# -----------------------------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME_ONLINE = "llama-3.1-8b-instant"

# MODELE OFFLINE
MODEL_NAME_OFFLINE = "llama3.2:3b-instruct-q4_K_M"
OLLAMA_URL = "http://localhost:11434/api/generate"

# -----------------------------------------------------
#   STOCKAGE DES HISTORIQUES (chat et mémoire)
# -----------------------------------------------------
user_memory = {}         # {user_id: [("role", "message")]}
memory_storage = {}      # {theme: {"section": "texte"}}
user_progress = {}       # {user_id: {"theme": ..., "current_section": ...}}

# Ordre des sections pour le workflow avec la nouvelle structure détaillée
sections_order = [
    "introduction",
    "chapitre 1 - cadre théorique",
    "chapitre 1 - synthèse travaux",
    "chapitre 1 - analyse critique",
    "chapitre 2 - matériels et terrain",
    "chapitre 2 - méthodologie",
    "chapitre 3 - résultats",
    "chapitre 3 - discussion",
    "conclusion"
]

# Mapping des sections simplifiées aux sections détaillées
section_mapping = {
    "introduction": "introduction",
    "chapitre 1": "chapitre 1 - cadre théorique",
    "chapitre 2": "chapitre 2 - matériels et terrain",
    "chapitre 3": "chapitre 3 - résultats",
    "conclusion": "conclusion"
}

# -----------------------------------------------------
#     VERIFIE SI GROQ EST ACCESSIBLE (INTERNET OK)
# -----------------------------------------------------
def groq_is_available():
    try:
        client.models.list()
        return True
    except Exception:
        return False

# -----------------------------------------------------
#               FASTAPI CONFIG
# -----------------------------------------------------
app = FastAPI(title="Memory Assistant — Hybrid AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------
#               SCHEMA REPONSE
# -----------------------------------------------------
class ResponseModel(BaseModel):
    theme: str
    section: str
    response: str

# -----------------------------------------------------
#      DETECTION AUTOMATIQUE DE L'INTENTION
# -----------------------------------------------------
def detect_intention(message: str) -> str:
    message_lower = message.lower().strip()
    greetings = ["bonjour", "salut", "hello", "hi", "coucou", "hey", "bonsoir"]

    for greeting in greetings:
        if message_lower == greeting or message_lower.startswith(f"{greeting} "):
            if len(message_lower.split()) <= 3:
                return "chat"

    memoire_keywords = [
        "rédiger", "rédige", "rédaction", "mémoire", "memoire", "thèse", "these",
        "rapport", "projet", "dissertation", "introduction", "chapitre", "conclusion",
        "section", "problématique", "méthodologie", "bibliographie", "littérature",
        "revue", "état de l'art", "méthodes", "résultats", "discussion", "analyse",
        "partie", "paragraphe", "sujet", "thème", "titre", "universitaire", "académique",
        "cadre théorique", "matériels et méthodes", "contexte d'étude", "problématique"
    ]

    memoire_phrases = [
        "aide moi à rédiger", "aide-moi à rédiger", "aide pour rédiger",
        "je dois rédiger", "je veux rédiger", "j'ai besoin de rédiger",
        "comment rédiger", "comment faire un", "structure d'un mémoire",
        "plan de mémoire", "aide pour mon mémoire", "aide pour ma thèse",
        "rédiger l'introduction", "rédiger le chapitre", "rédiger la conclusion"
    ]

    for phrase in memoire_phrases:
        if phrase in message_lower:
            return "memoire"

    keyword_count = sum(1 for keyword in memoire_keywords if keyword in message_lower)
    if keyword_count >= 2:
        return "memoire"

    if len(message_lower.split()) > 20:
        return "memoire"

    return "chat"

# -----------------------------------------------------
#      DETECTION AMÉLIORÉE DE SECTION (pour mémoire)
# -----------------------------------------------------
def detect_section(message: str) -> str:
    message_lower = message.lower()

    # Patterns détaillés selon la nouvelle méthodologie
    patterns = {
        "introduction": [
            r"(?:^|\s)introduction\s+générale?\b",
            r"commence(?:r|z)?\s+(?:par\s+)?l['']?introduction",
            r"rédige(?:r|z)?\s+(?:l['']?)?introduction",
            r"contexte\s+d['']?étude",
            r"problématique\s+(?:et|ou)\s+objectifs",
            r"début(?:er)?\s+(?:le\s+)?mémoire",
            r"1\s*\.?\s*contexte",
            r"plan\s+du\s+document"
        ],
        "chapitre 1 - cadre théorique": [
            r"chapitre\s*1\s*[\.\-]?\s*(?:cadre\s+théorique|concepts\s+clés)",
            r"cadre\s+théorique",
            r"concepts\s+clés",
            r"définitions\s+opérationnelles",
            r"1\.1\s*concepts",
            r"présentation\s+des\s+concepts"
        ],
        "chapitre 1 - synthèse travaux": [
            r"chapitre\s*1\s*[\.\-]?\s*(?:synthèse|travaux|état\s+de\s+l['']?art)",
            r"synthèse\s+des\s+travaux",
            r"travaux\s+antérieurs",
            r"travaux\s+récents",
            r"état\s+de\s+l['']?art",
            r"revue\s+de\s+la\s+littérature",
            r"1\.2\s*synthèse",
            r"cartographie\s+de\s+la\s+recherche"
        ],
        "chapitre 1 - analyse critique": [
            r"chapitre\s*1\s*[\.\-]?\s*(?:analyse\s+critique|gap)",
            r"analyse\s+critique",
            r"discussion\s+critique",
            r"identification\s+du\s+gap",
            r"lacune\s+de\s+recherche",
            r"1\.3\s*analyse",
            r"critique\s+des\s+travaux"
        ],
        "chapitre 2 - matériels et terrain": [
            r"chapitre\s*2\s*[\.\-]?\s*(?:matériels|terrain|outils)",
            r"matériels\s+(?:et|ou)\s+outils",
            r"description\s+du\s+terrain",
            r"population\s+(?:d['']?|de\s+)étude",
            r"corpus\s+d['']?étude",
            r"2\.1\s*matériels",
            r"outils\s+de\s+collecte",
            r"échantillon\s+(?:de\s+)?recherche"
        ],
        "chapitre 2 - méthodologie": [
            r"chapitre\s*2\s*[\.\-]?\s*(?:méthodologie|méthodes)",
            r"méthodologie\s+de\s+recherche",
            r"design\s+de\s+recherche",
            r"procédure\s+de\s+collecte",
            r"méthodes\s+d['']?analyse",
            r"2\.2\s*méthodes",
            r"protocole\s+de\s+recherche"
        ],
        "chapitre 3 - résultats": [
            r"chapitre\s*3\s*[\.\-]?\s*(?:résultats|présentation)",
            r"présentation\s+des\s+résultats",
            r"résultats\s+obtenus",
            r"données\s+collectées",
            r"3\.1\s*résultats",
            r"faits\s+et\s+chiffres",
            r"tableaux\s+(?:de\s+)?résultats"
        ],
        "chapitre 3 - discussion": [
            r"chapitre\s*3\s*[\.\-]?\s*(?:discussion|analyse)",
            r"discussion\s+des\s+résultats",
            r"analyse\s+(?:et\s+|des\s+)résultats",
            r"interprétation\s+des\s+résultats",
            r"3\.2\s*discussion",
            r"confrontation\s+avec\s+la\s+littérature"
        ],
        "conclusion": [
            r"(?:^|\s)conclusion\s+(?:et\s+perspectives)?\b",
            r"termine(?:r|z)?\s+(?:par\s+)?la\s+conclusion",
            r"rédige(?:r|z)?\s+(?:la\s+)?conclusion",
            r"synthèse\s+finale",
            r"bilan\s+(?:final|général)",
            r"perspectives\s+(?:de\s+recherche|d['']?avenir)",
            r"limites\s+de\s+l['']?étude"
        ]
    }

    # D'abord chercher les patterns détaillés
    for section, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, message_lower, flags=re.IGNORECASE):
                return section

    # Fallback vers les sections génériques
    if any(word in message_lower for word in ["début", "commencer", "première", "premier", "contexte", "problématique"]):
        return "introduction"
    elif any(word in message_lower for word in ["chapitre 1", "revue littérature", "état art", "littérature"]):
        return "chapitre 1 - cadre théorique"
    elif any(word in message_lower for word in ["chapitre 2", "méthodologie", "méthodes", "matériel"]):
        return "chapitre 2 - matériels et terrain"
    elif any(word in message_lower for word in ["chapitre 3", "résultats", "discussion", "analyse résultats"]):
        return "chapitre 3 - résultats"
    elif any(word in message_lower for word in ["fin", "terminer", "dernier", "bilan", "perspectives"]):
        return "conclusion"

    # Par défaut
    return "introduction"

# -----------------------------------------------------
#               EXTRACTION DU THÈME
# -----------------------------------------------------
def extract_theme(message: str) -> str:
    message_lower = message.lower()
    theme_patterns = [
        r"(?:thème|sujet|titre|sur)\s*(?:est|:|-)\s*\"?([^\"]+?)\"?\s*(?:\.|$|pour)",
        r"rédiger\s+(?:un|une|le|la)?\s*(?:mémoire|rapport|thèse)\s+(?:sur|au sujet de|titré)\s*\"?([^\"]+?)\"?\s*(?:\.|$)",
        r"mémoire\s+(?:sur|intitulé)\s*\"?([^\"]+?)\"?\s*(?:\.|$)",
        r"(?:je\s+veux|je\s+dois|j['']aimerais)\s+rédiger\s+(?:un|une)\s*(?:mémoire|rapport)\s+(?:sur|au sujet de)\s*\"?([^\"]+?)\"?\s*(?:\.|$)"
    ]

    for pattern in theme_patterns:
        match = re.search(pattern, message_lower, flags=re.IGNORECASE)
        if match:
            theme = match.group(1).strip()
            theme = re.sub(r"^['\"]|['\"]$", "", theme)
            if len(theme.split()) <= 15:
                return theme.capitalize()

    words = message.split()
    stop_words = ["je","tu","il","elle","nous","vous","ils","elles","le","la","les",
                  "un","une","des","de","du","à","au","pour","sur","avec","sans","dans",
                  "par","est","sont","ai","as","a","avons","avez","ont","veux","dois","peux"]
    important_words = [word for word in words if word.lower() not in stop_words]
    if len(important_words) >= 2:
        return " ".join(important_words[:5])
    return "Thème non spécifié"

# -----------------------------------------------------
#        AJOUT / RECUPERATION DE LA MÉMOIRE UTILISATEUR
# -----------------------------------------------------
def get_user_context(user_id: str) -> str:
    if user_id in user_memory:
        return "\n".join([f"{role}: {msg}" for role, msg in user_memory[user_id]])
    return ""

def update_user_context(user_id: str, role: str, message: str):
    if user_id not in user_memory:
        user_memory[user_id] = []
    user_memory[user_id].append((role, message))
    # Limiter à 20 messages max pour éviter surcharge
    if len(user_memory[user_id]) > 20:
        user_memory[user_id] = user_memory[user_id][-20:]

# -----------------------------------------------------
#               PROMPT BUILDER (pour mémoire)
# -----------------------------------------------------
def build_prompt(theme: str, section: str, context: str = "") -> str:
    prev_context = memory_storage.get(theme, {})
    previous_text = "\n".join([f"[{sec}] {txt}" for sec, txt in prev_context.items()])

    # NOUVELLE MÉTHODOLOGIE DÉTAILLÉE
    methodology = """
MÉTHODOLOGIE ACADÉMIQUE DÉTAILLÉE POUR LA RÉDACTION DE MÉMOIRE

========================================
INTRODUCTION GÉNÉRALE
========================================
Fonction : Poser les fondations du mémoire, justifier son existence et en présenter la structure logique.

1. CONTEXTE D'ÉTUDE
   • Cadre général : Présentation du domaine scientifique, professionnel ou sociétal dans lequel s'inscrit le sujet.
   • Cadre spécifique : Délimitation précise du terrain, de l'entreprise, de la communauté ou du corpus d'étude.
   • Justification et intérêt : Pourquoi ce sujet est-il important maintenant ? (Enjeux actuels, lacunes observées, demandes institutionnelles).
   • Historique succinct : Évolution de la situation ayant conduit au besoin d'étude.

2. PROBLÉMATIQUE ET OBJECTIFS
   • Question de départ : La question large qui a initié la réflexion.
   • Problématique formulée : La question centrale, précise, argumentée et construite qui guide toute la recherche. Elle montre la "tension" ou le "problème" à résoudre.
   • Objectif général : La finalité ultime du mémoire (ex : Concevoir, Évaluer, Comprendre, Proposer un modèle).
   • Objectifs spécifiques (SMART) : La décomposition concrète et hiérarchisée des étapes à franchir pour atteindre l'objectif général.

3. PLAN DU DOCUMENT
   • Logique de la structure : Justification du choix des chapitres (approche dialectique, analytique, comparative, etc.).
   • Annonce synthétique : Présentation claire et succincte du contenu de chaque partie principale.

========================================
CHAPITRE 1 : REVUE DE LA LITTÉRATURE / ÉTAT DE L'ART
========================================
Fonction : Démontrer la maîtrise du sujet, identifier les connaissances établies et les lacunes pour justifier sa propre recherche.

1.1 PRÉSENTATION DES CONCEPTS CLÉS ET CADRE THÉORIQUE
   • Définitions opérationnelles : Définition précise des termes centraux du sujet, en citant les auteurs de référence.
   • Cadre théorique : Présentation et explication des théories, modèles ou paradigmes qui serviront de grille d'analyse.
   • Historique et évolution des idées : Comment les concepts et théories ont-ils évolué jusqu'à aujourd'hui ?

1.2 SYNTHÈSE DES TRAVAUX ANTÉRIEURS ET RÉCENTS
   • Méthodologie de la revue : Critères de sélection des sources (mots-clés, bases de données, périodes, langues).
   • Cartographie de la recherche : Classement des travaux par écoles de pensée, méthodologies, ou résultats convergents/divergents.
   • Études fondatrices et pionnières : Les recherches qui ont marqué le domaine.
   • Études les plus récentes : L'état actuel de la recherche, identifiant les fronts de science.

1.3 ANALYSE CRITIQUE ET IDENTIFICATION DU GAP
   • Discussion critique : Confrontation des points de vue, forces et faiblesses des méthodologies employées, limites des résultats.
   • Synthèse des apports : Ce qui est acquis, consensuel.
   • Identification de la niche (le "gap") : Mise en évidence claire de la lacune, de la question non résolue que votre mémoire vient combler.

========================================
CHAPITRE 2 : MATÉRIELS ET MÉTHODES
========================================
Fonction : Décrire avec une précision reproductible le "comment" de la recherche. C'est le protocole scientifique.

2.1 MATÉRIELS, OUTILS ET TERRAIN
   • Description du terrain / population / corpus :
        - Sélection et critères d'inclusion/exclusion.
        - Taille, caractéristiques principales (descriptif statistique ou qualitatif).
        - Accès au terrain et considérations éthiques (accord, consentement, anonymat).
   • Matériels (Hardware/Software) :
        - Liste et spécifications techniques des équipements.
        - Logiciels utilisés (pour l'analyse, la modélisation, les statistiques) avec version.
   • Outils de collecte :
        - Questionnaire (en annexe), guide d'entretien, grille d'observation.
        - Justification de leur élaboration (adaptation d'outils validés, création originale).

2.2 MÉTHODOLOGIE DE LA RECHERCHE
   • Choix du design de recherche : Qualitative, Quantitative ou Mixte. Justification.
   • Procédure de collecte des données : Déroulement chronologique précis (étape par étape), période, durée, conditions.
   • Méthodes d'analyse des données :
        - Pour données quantitatives : Tests statistiques utilisés (avec justification), logiciel.
        - Pour données qualitatives : Méthode d'analyse (analyse de contenu, thématique, discours), processus de codage.
   • Limites méthodologiques et biais potentiels : Anticipation et reconnaissance des limites inhérentes aux choix méthodologiques.

========================================
CHAPITRE 3 : RÉSULTATS, ANALYSE ET DISCUSSION
========================================
Fonction : Présenter, interpréter et confronter les résultats à la lumière du cadre théorique.

STRUCTURE OPTION A : RÉSULTATS ET DISCUSSION INTÉGRÉS (par thème/objectif)
   • Présentation des résultats : Faits bruts organisés (tableaux, graphiques, citations significatives).
   • Analyse et Interprétation : Que signifient ces faits ? Explication immédiate.
   • Discussion : Confrontation de ce résultat avec les travaux cités au Chapitre 1 (confirmation, infirmation, nuance).

STRUCTURE OPTION B : RÉSULTATS ET DISCUSSION SÉPARÉS
   3.1 PRÉSENTATION DES RÉSULTATS
        - Organisation stricte selon les objectifs spécifiques ou les thèmes de recherche.
        - Présentation neutre et factuelle des données, sans interprétation.
        - Utilisation efficace des visuels (graphiques, tableaux clairement titrés et commentés).
   
   3.2 ANALYSE ET DISCUSSION GÉNÉRALE
        - Interprétation globale : Donner du sens à l'ensemble des résultats.
        - Discussion argumentée : Confrontation systématique avec l'état de l'art, explication des convergences/divergences.
        - Réponse à la problématique : Montrer en quoi les résultats apportent des éléments de réponse.

========================================
CONCLUSION ET PERSPECTIVES
========================================
Fonction : Boucler la boucle logique du mémoire, résoudre la problématique et ouvrir sur l'avenir.

1. BILAN SYNTHÉTIQUE ET RÉPONSES APPORTÉES
   • Récapitulation synthétique : Rappel très concis des objectifs et de la démarche.
   • Réponse à la problématique : Formulation claire et affirmative de la réponse principale.
   • Synthèse des apports principaux : Les 3-4 contributions majeures (théoriques, méthodologiques, pratiques).
   • Limites de l'étude : Reconnaissance honnête et argumentée des limites.

2. PERSPECTIVES
   • Perspectives de recherche : Propositions concrètes pour des recherches futures.
   • Perspectives pratiques / Recommandations : Propositions d'actions concrètes.
   • Ouverture : Élargissement du sujet vers un débat plus vaste.
"""

    # Instructions spécifiques par section
    section_instructions = {
        "introduction": """
Pour l'INTRODUCTION GÉNÉRALE, développez chaque point suivant :
1. Contexte d'étude (environ 25 lignes)
   - Cadre général et spécifique
   - Justification de l'intérêt actuel du sujet
   - Historique succinct si pertinent

2. Problématique et objectifs (environ 25 lignes)
   - Formulation précise de la problématique avec justification
   - Objectif général bien défini
   - 3-5 objectifs spécifiques formulés de manière SMART

3. Plan du document (environ 10 lignes)
   - Logique de la structure choisie
   - Annonce synthétique des chapitres
""",
        "chapitre 1 - cadre théorique": """
Pour le CADRE THÉORIQUE (Chapitre 1.1), développez :
1. Définitions opérationnelles (environ 20 lignes)
   - Définitions précises des concepts clés avec auteurs
   - Clarification des termes techniques

2. Cadre théorique (environ 25 lignes)
   - Présentation des théories principales
   - Explication de leur pertinence pour votre étude
   - Articulation entre les différentes théories

3. Historique et évolution des idées (environ 15 lignes)
   - Évolution chronologique des concepts
   - Tournants théoriques importants
""",
        "chapitre 1 - synthèse travaux": """
Pour la SYNTHÈSE DES TRAVAUX (Chapitre 1.2), développez :
1. Méthodologie de la revue (environ 15 lignes)
   - Critères de sélection des sources
   - Bases de données consultées
   - Période couverte

2. Cartographie de la recherche (environ 20 lignes)
   - Classification des travaux par approches
   - Tableau synthétique des principales études
   - Tendances dominantes dans la littérature

3. Études clés (environ 25 lignes)
   - Présentation des études fondatrices
   - Analyse des travaux récents les plus pertinents
   - Synthèse des principaux résultats existants
""",
        "chapitre 1 - analyse critique": """
Pour l'ANALYSE CRITIQUE (Chapitre 1.3), développez :
1. Discussion critique (environ 25 lignes)
   - Forces et faiblesses des méthodologies rencontrées
   - Limites des résultats des études existantes
   - Controverses ou débats dans la littérature

2. Synthèse des apports (environ 15 lignes)
   - Consensus établis dans le domaine
   - Connaissances acquises et validées

3. Identification du gap (environ 20 lignes)
   - Lacunes de recherche clairement identifiées
   - Questions non résolues
   - Justification de l'originalité de votre approche
""",
        "chapitre 2 - matériels et terrain": """
Pour les MATÉRIELS ET TERRAIN (Chapitre 2.1), développez :
1. Description du terrain/corpus (environ 25 lignes)
   - Critères de sélection détaillés
   - Caractéristiques principales (tableau descriptif si pertinent)
   - Procédures d'accès et considérations éthiques

2. Matériels et outils (environ 20 lignes)
   - Liste complète avec spécifications techniques
   - Justification des choix techniques
   - Conditions d'utilisation et calibration

3. Outils de collecte (environ 15 lignes)
   - Présentation des instruments utilisés
   - Procédure de validation/adaptation
   - Fiabilité et validité des outils
""",
        "chapitre 2 - méthodologie": """
Pour la MÉTHODOLOGIE (Chapitre 2.2), développez :
1. Design de recherche (environ 20 lignes)
   - Justification du choix qualitatif/quantitatif/mixte
   - Schéma de la recherche
   - Variables étudiées (si applicable)

2. Procédure de collecte (environ 25 lignes)
   - Déroulement chronologique étape par étape
   - Conditions expérimentales ou d'observation
   - Durée et planning de la collecte

3. Méthodes d'analyse (environ 20 lignes)
   - Techniques statistiques ou d'analyse qualitative
   - Justification des choix méthodologiques
   - Procédures de traitement des données

4. Limites méthodologiques (environ 15 lignes)
   - Biais potentiels identifiés
   - Contraintes pratiques rencontrées
   - Stratégies de contrôle mises en place
""",
        "chapitre 3 - résultats": """
Pour les RÉSULTATS (Chapitre 3.1), développez :
1. Organisation des résultats (environ 15 lignes)
   - Structure selon les objectifs spécifiques
   - Logique de présentation

2. Présentation factuelle (environ 30 lignes)
   - Données brutes organisées clairement
   - Tableaux et graphiques pertinents avec légendes explicatives
   - Citations significatives (pour études qualitatives)

3. Neutralité scientifique (environ 10 lignes)
   - Présentation sans interprétation
   - Objectivité des données présentées
""",
        "chapitre 3 - discussion": """
Pour la DISCUSSION (Chapitre 3.2), développez :
1. Interprétation des résultats (environ 25 lignes)
   - Signification des principaux résultats
   - Explications possibles des observations

2. Confrontation avec la littérature (environ 30 lignes)
   - Comparaison avec les études du chapitre 1
   - Explication des convergences et divergences
   - Positionnement par rapport au cadre théorique

3. Réponse à la problématique (environ 15 lignes)
   - Articulation entre résultats et question de recherche
   - Éléments de réponse apportés
   - Nouvelles questions soulevées
""",
        "conclusion": """
Pour la CONCLUSION, développez :
1. Bilan synthétique (environ 20 lignes)
   - Récapitulation concise de la démarche
   - Synthèse des principaux résultats

2. Réponse globale (environ 15 lignes)
   - Formulation claire de la réponse à la problématique
   - Apports principaux de la recherche

3. Limites de l'étude (environ 15 lignes)
   - Reconnaissance honnête des limites
   - Impact potentiel sur les résultats

4. Perspectives (environ 20 lignes)
   - Pistes de recherche futures concrètes
   - Recommandations pratiques si applicables
   - Ouverture sur des questions plus larges
"""
    }

    brainstorming = """
BRAINSTORMING ACADÉMIQUE REQUIS :
Avant de rédiger, effectuez un brainstorming interne pour organiser TOUTES les informations pertinentes.
Pensez à :
1. Les concepts clés et leurs interrelations
2. Les auteurs majeurs et leurs contributions
3. Les méthodologies alternatives possibles
4. Les résultats attendus et inattendus
5. Les implications théoriques et pratiques

EXIGENCES DE RÉDACTION :
• Chaque sous-point doit faire au minimum 15-20 lignes
• Style académique rigoureux avec citations appropriées
• Structure hiérarchique claire (1., 1.1, 1.1.1, etc.)
• Explications didactiques accessibles à un débutant
• Éviter les répétitions et les généralités
• Proposer des exemples concrets et des tableaux synthétiques
• Inclure une synthèse à la fin de chaque section
"""

    instruction = section_instructions.get(section, f"Développez la section '{section}' de manière structurée et détaillée.")

    return f"""
THÈME DU MÉMOIRE : **{theme}**
SECTION À RÉDIGER : **{section}**
CONTEXTE FOURNI : {context if context else "Aucun contexte spécifique fourni."}

HISTORIQUE DES SECTIONS DÉJÀ RÉDIGÉES :
{previous_text if previous_text else "C'est la première section du mémoire."}

{methodology}

INSTRUCTIONS SPÉCIFIQUES POUR CETTE SECTION :
{instruction}

{brainstorming}

CONSIGNES FINALES :
1. Rédigez UNIQUEMENT la section demandée : {section}
2. Suivez scrupuleusement la méthodologie académique présentée
3. Structurez avec des titres et sous-titres hiérarchiques
4. Chaque paragraphe doit être développé et argumenté
5. Inclure des exemples concrets liés au thème "{theme}"
6. Terminer par une synthèse des points abordés
7. Proposer naturellement la section suivante dans le flux logique

COMMENCEZ LA RÉDACTION MAINTENANT :
"""

# -----------------------------------------------------
#       APPEL MODELE ONLINE (GROQ)
# -----------------------------------------------------
def call_online_model(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME_ONLINE,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ONLINE ERROR] Impossible d'utiliser Groq : {str(e)}"

# -----------------------------------------------------
#       APPEL MODELE OFFLINE (OLLAMA)
# -----------------------------------------------------
def call_offline_model(prompt):
    payload = {
        "model": MODEL_NAME_OFFLINE,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 3000
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        data = response.json()
        if "response" in data:
            return data["response"]
        if "error" in data and "CUDA error" in data["error"]:
            os.environ["OLLAMA_NUM_GPU"] = "0"
            response = requests.post(OLLAMA_URL, json=payload, timeout=90)
            data_cpu = response.json()
            if "response" in data_cpu:
                return data_cpu["response"]
            return f"[OFFLINE ERROR CPU] {data_cpu}"
        if "error" in data:
            return f"[OFFLINE ERROR] {data['error']}"
        return "[OFFLINE ERROR] Réponse inconnue du modèle."
    except Exception as e:
        return f"[OFFLINE FATAL ERROR] {str(e)}"

# -----------------------------------------------------
#       APPEL MODELE POUR CONVERSATION
# -----------------------------------------------------
def call_chat_model(user_id: str, prompt: str):
    update_user_context(user_id, "Utilisateur", prompt)
    full_prompt = get_user_context(user_id) + "\nAI:"
    if groq_is_available():
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME_ONLINE,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"[Erreur technique] {str(e)}"
    else:
        answer = call_offline_model(full_prompt)
    update_user_context(user_id, "AI", answer)
    return answer

# -----------------------------------------------------
#   UTILITAIRE POUR LE WORKFLOW
# -----------------------------------------------------
def get_next_section(current: str):
    try:
        idx = sections_order.index(current.lower())
        if idx + 1 < len(sections_order):
            return sections_order[idx + 1]
    except ValueError:
        pass
    return None

# -----------------------------------------------------
#                ROUTE PRINCIPALE
# -----------------------------------------------------
@app.get("/ask", response_model=ResponseModel)
def ask(prompt: str = Query(...), context: str = Query("", description="Contexte optionnel"), user_id: str = Query("default")):
    intention = detect_intention(prompt)

    if intention == "chat":
        response = call_chat_model(user_id, prompt)
        return ResponseModel(theme="Conversation", section="chat", response=response)

    # Détection du thème
    theme = extract_theme(prompt)

    # Détection de la section demandée
    detected_section = detect_section(prompt)

    # Gestion du workflow utilisateur
    if user_id not in user_progress or user_progress[user_id].get("theme") != theme:
        user_progress[user_id] = {"theme": theme, "current_section": detected_section}
        section = detected_section
        response_text = f"Nous allons commencer par rédiger la section **{section}** du thème '{theme}'."
    else:
        # Si l'utilisateur demande une section spécifique, l'utiliser
        if detected_section != user_progress[user_id]["current_section"]:
            section = detected_section
            user_progress[user_id]["current_section"] = section
            response_text = f"Je vais maintenant rédiger la section **{section}**."
        else:
            section = user_progress[user_id]["current_section"]
            response_text = f"Je continue avec la section **{section}**."

    # Construction du prompt avec la nouvelle méthodologie
    final_prompt = build_prompt(theme, section, context)

    # Appel du modèle
    if groq_is_available():
        output = call_online_model(final_prompt)
    else:
        output = call_offline_model(final_prompt)

    # Sauvegarde mémoire
    if theme not in memory_storage:
        memory_storage[theme] = {}
    memory_storage[theme][section] = output

    # Mise à jour progression et suggestion section suivante
    next_sec = get_next_section(section)
    if next_sec:
        user_progress[user_id]["current_section"] = next_sec
        output += f"\n\n{'='*60}\n SECTION SUIVANTE SUGGÉRÉE : **{next_sec.upper()}**\n{'='*60}\n\nSouhaitez-vous que je rédige cette section maintenant ?"
    else:
        output += f"\n\n{'='*60}\nFÉLICITATIONS ! Toutes les sections ont été rédigées pour ce thème.\n{'='*60}\n\nVous pouvez maintenant :\n1. Relire et peaufiner chaque section\n2. Ajouter une bibliographie complète\n3. Rédiger un résumé/abstract\n4. Préparer la soutenance"

    return ResponseModel(theme=theme, section=section, response=response_text + "\n\n" + output)

# -----------------------------------------------------
#         ROUTE DE TEST
# -----------------------------------------------------
@app.get("/test-intention")
def test_intention(prompt: str = Query(...)):
    intention = detect_intention(prompt)
    section = detect_section(prompt) if intention == "memoire" else "N/A"
    theme = extract_theme(prompt) if intention == "memoire" else "N/A"

    # Info sur la méthodologie
    methodology_info = "NOUVELLE MÉTHODOLOGIE DÉTAILLÉE INTÉGRÉE"
    section_description = {
        "introduction": "Introduction Générale (Contexte, Problématique, Plan)",
        "chapitre 1 - cadre théorique": "Chapitre 1.1 - Concepts clés et cadre théorique",
        "chapitre 1 - synthèse travaux": "Chapitre 1.2 - Synthèse des travaux antérieurs",
        "chapitre 1 - analyse critique": "Chapitre 1.3 - Analyse critique et identification du gap",
        "chapitre 2 - matériels et terrain": "Chapitre 2.1 - Matériels, outils et terrain",
        "chapitre 2 - méthodologie": "Chapitre 2.2 - Méthodologie de recherche",
        "chapitre 3 - résultats": "Chapitre 3.1 - Présentation des résultats",
        "chapitre 3 - discussion": "Chapitre 3.2 - Analyse et discussion",
        "conclusion": "Conclusion et Perspectives"
    }

    return {
        "prompt": prompt,
        "intention_detectee": intention,
        "section_detectee": section,
        "section_description": section_description.get(section, "Section standard"),
        "theme_extrait": theme,
        "methode_utilisee": methodology_info,
        "explication": f"chat = conversation simple | memoire = rédaction académique avec la nouvelle méthodologie"
    }

# -----------------------------------------------------
#         ROUTE POUR VOIR LA STRUCTURE
# -----------------------------------------------------
@app.get("/structure")
def get_structure():
    return {
        "methodologie_utilisee": "Nouvelle méthodologie académique détaillée",
        "sections_disponibles": sections_order,
        "description_sections": {
            "introduction": "Introduction Générale - Contexte, Problématique, Plan",
            "chapitre 1 - cadre théorique": "Chapitre 1.1 - Concepts clés et cadre théorique",
            "chapitre 1 - synthèse travaux": "Chapitre 1.2 - Synthèse des travaux antérieurs et récents",
            "chapitre 1 - analyse critique": "Chapitre 1.3 - Analyse critique et identification du gap",
            "chapitre 2 - matériels et terrain": "Chapitre 2.1 - Matériels, outils et description du terrain",
            "chapitre 2 - méthodologie": "Chapitre 2.2 - Méthodologie de recherche complète",
            "chapitre 3 - résultats": "Chapitre 3.1 - Présentation des résultats (option A ou B)",
            "chapitre 3 - discussion": "Chapitre 3.2 - Analyse et discussion des résultats",
            "conclusion": "Conclusion - Bilan, Limites et Perspectives"
        },
        "workflow_recommandé": "Suivre l'ordre des sections pour une rédaction cohérente"
    }

# -----------------------------------------------------
#         ROUTE EXEMPLES
# -----------------------------------------------------
@app.get("/exemples")
def get_exemples():
    return {
        "conversations_simples": [
            "Bonjour",
            "Comment ça va ?",
            "Quelle heure est-il ?",
            "Merci pour ton aide",
            "Au revoir"
        ],
        "demandes_memoire_nouvelle_methode": [
            "Bonjour, je dois rédiger un mémoire sur l'intelligence artificielle",
            "Rédige le contexte d'étude de mon mémoire sur le changement climatique",
            "Je veux écrire le cadre théorique sur les méthodes de recherche qualitative",
            "Aide-moi à rédiger la synthèse des travaux sur les réseaux neuronaux",
            "Thème: L'impact des réseaux sociaux sur les adolescents. Rédige la problématique",
            "J'ai besoin de décrire la méthodologie de ma recherche en sociologie",
            "Rédige la présentation des résultats de mon étude sur la pollution marine",
            "Je veux faire l'analyse critique de la littérature sur l'économie circulaire",
            "Aide-moi à rédiger la conclusion de mon mémoire de biologie moléculaire"
        ],
        "sections_specifiques": [
            "1.1 Concepts clés du machine learning",
            "1.2 Synthèse des travaux sur les énergies renouvelables",
            "1.3 Analyse critique des études sur le e-learning",
            "2.1 Description du terrain d'étude en Amazonie",
            "2.2 Méthodologie d'analyse de contenu qualitative",
            "3.1 Présentation des résultats statistiques",
            "3.2 Discussion des résultats sur la vaccination",
            "Conclusion avec perspectives de recherche"
        ]
    }

# -----------------------------------------------------
#               MAIN
# -----------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("SERVER STARTING - NOUVELLE MÉTHODOLOGIE ACADÉMIQUE")
    print("="*60)
    print("\nEndpoints disponibles:")
    print("- GET /ask?prompt=...&context=...&user_id=... (Rédaction mémoire)")
    print("- GET /test-intention?prompt=... (Test de détection)")
    print("- GET /structure (Voir la structure détaillée)")
    print("- GET /exemples (Exemples de prompts)")
    print("\nMéthodologie intégrée: Structure académique complète avec 9 sections détaillées")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)