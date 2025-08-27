# 1. Primero las importaciones
import streamlit as st
import unicodedata
import re
from datetime import datetime
import random
import json, base64, requests, time
import sys
import logging

# 2. Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 3. Definir TODAS las funciones ANTES de usarlas
def init_session_state():
    """Inicializa el estado de la sesión"""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False  # Por defecto tema CLARO
    if "historial" not in st.session_state:
        st.session_state.historial = []
    if "quiz" not in st.session_state:
        st.session_state.quiz = None
    if "quiz_n" not in st.session_state:
        st.session_state.quiz_n = 10
    if "scores" not in st.session_state:
        st.session_state.scores = []
    if "quiz_corrected" not in st.session_state:
        st.session_state.quiz_corrected = False
    if "last_score" not in st.session_state:
        st.session_state.last_score = {}
    # Inicializar menú por defecto si no existe
    if "menu" not in st.session_state:
        st.session_state["menu"] = "🔍 Cerca un monosíl·lab"

def inject_custom_css():
    """CSS personalizado con soporte para tema oscuro y claro (contraste garantizado)."""
    dark = st.session_state.get("dark_mode", False)
    if dark:
        # ===== MODO OSCURO =====
        st.markdown("""
        <style>
        :root {
            --bg: #1e1e1e;
            --bg-2: #2a2a2a;
            --bg-3: #2d2d2d;
            --fg: #f5f7fa;
            --muted: #cbd5e1;
            --border: #404040;
            --accent: #4a9eff;
            --btn: #2d2d2d;
            --btn-hover: #404040;
            --code-bg: #1a1a1a;
            --code-fg: #e0e0e0;
        }
        /* Base */
        html, body, .stApp, [data-testid="stAppViewContainer"], .block-container {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
        }
        /* Texto común y encabezados */
        .stMarkdown, .stText, .stCaption, .stMetric, .stAlert, .stCodeBlock,
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: var(--fg) !important;
        }
        /* Sidebar */
        [data-testid="stSidebar"], .sidebar .sidebar-content {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
        }
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stRadio > div,
        .stTextArea textarea {
            background-color: var(--bg-3) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }
        /* Botones */
        .stButton > button {
            background-color: var(--btn) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }
        .stButton > button:hover {
            background-color: var(--btn-hover) !important;
        }
        /* Botón primario (Streamlit >=1.25) */
        button[data-testid="baseButton-primary"] {
            background-color: var(--accent) !important;
            border-color: var(--accent) !important;
            color: #ffffff !important;
        }
        /* Bloques del quiz */
        .quiz-progress {
            background-color: #333333 !important;
            border-radius: 10px; padding: 10px; margin: 10px 0;
            border-left: 4px solid var(--accent);
        }
        .quiz-question {
            border-left: 4px solid var(--accent);
            padding-left: 1rem; margin: 1rem 0;
            background-color: var(--bg-2);
            border-radius: 5px; padding: 1rem;
            border: 1px solid var(--border);
        }
        .success-score {
            background-color: #1a472a; border: 1px solid #2d5a3d;
            border-radius: 5px; padding: 1rem; margin: 1rem 0;
            color: var(--fg) !important;
        }
        /* DataFrame - ARREGLADO COMPLETO */
        .stDataFrame, .stDataFrame div, .stDataFrame table, 
        .stDataFrame th, .stDataFrame td, 
        [data-testid="dataframe"], [data-testid="dataframe"] *,
        [data-testid="dataframe"] table, [data-testid="dataframe"] tbody,
        [data-testid="dataframe"] th, [data-testid="dataframe"] td,
        [data-testid="stDataFrame"], [data-testid="stDataFrame"] *,
        div[data-testid="dataframe"] table tbody tr td,
        div[data-testid="dataframe"] table thead tr th {
            background-color: var(--bg-2) !important;
            color: var(--fg) !important;
            border-color: #e9ecef !important;
        }
        
        /* Sidebar toggle button - MODO OSCURO */
        [data-testid="collapsedControl"] {
            color: #ffffff !important;
            background-color: var(--bg-2) !important;
        }
        
        [data-testid="collapsedControl"] svg {
            fill: #ffffff !important;
        }
        
        /* Tooltip/help text */
        .stTooltipIcon, [data-testid="stTooltipHoverTarget"],
        [role="tooltip"], div[data-baseweb="tooltip"] {
            background-color: var(--bg-3) !important;
            color: var(--fg) !important;
            border: 1px solid #e9ecef !important;
        }
        
        /* Code blocks - ARREGLADO para que se vean en modo oscuro */
        .stCode, .stCodeBlock, 
        .stCode > div, .stCodeBlock > div, 
        .stCode pre, .stCodeBlock pre, 
        .stCode code, .stCodeBlock code,
        [data-testid="stCodeBlock"],
        [data-testid="stCodeBlock"] *,
        pre, code {
            background-color: var(--code-bg) !important;
            color: var(--code-fg) !important;
            border: 1px solid var(--border) !important;
        }
        
        /* Monosílabs acentuats en blau per a 'Definició' */
        .accented {
            color: #1e90ff !important;
            font-weight: 600;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # ===== MODO CLARO =====
        st.markdown("""
        <style>
        :root {
            --bg: #ffffff;
            --bg-2: #ffffff;
            --bg-3: #ffffff;
            --fg: #111827;        /* gris muy oscuro (mejor que negro puro) */
            --muted: #374151;
            --border: #d1d5db;
            --accent: #0066cc;
            --btn: #f8f9fa;
            --btn-hover: #e9ecef;
            --code-bg: #f8f9fa;
            --code-fg: #333333;
        }
        /* Base */
        html, body, .stApp, [data-testid="stAppViewContainer"], .block-container {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
        }
        /* Texto común y encabezados */
        .stMarkdown, .stText, .stCaption, .stMetric, .stAlert, .stCodeBlock,
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: var(--fg) !important;
        }
        /* Sidebar */
        [data-testid="stSidebar"], .sidebar .sidebar-content {
            background-color: #f8f9fa !important;
            color: var(--fg) !important;
        }
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stRadio > div,
        .stTextArea textarea {
            background-color: var(--bg-3) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }
        /* Botones */
        .stButton > button {
            background-color: var(--btn) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }
        .stButton > button:hover {
            background-color: var(--btn-hover) !important;
            border: 1px solid #adb5bd !important;
        }
        /* Botón primario (Streamlit >=1.25) */
        button[data-testid="baseButton-primary"] {
            background-color: var(--accent) !important;
            border-color: var(--accent) !important;
            color: #ffffff !important;
        }
        /* Bloques del quiz */
        .quiz-progress {
            background-color: #f8f9fa;
            border-radius: 10px; padding: 10px; margin: 10px 0;
            border-left: 4px solid var(--accent);
            border: 1px solid #e9ecef;
        }
        .quiz-question {
            border-left: 4px solid var(--accent);
            padding-left: 1rem; margin: 1rem 0;
            background-color: var(--bg-2);
            border-radius: 5px; padding: 1rem;
            border: 1px solid #e9ecef;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .success-score {
            background-color: #d4edda; border: 1px solid #c3e6cb;
            border-radius: 5px; padding: 1rem; margin: 1rem 0;
            color: #0f5132 !important;
        }
        /* DataFrame - ARREGLADO */
        .stDataFrame, .stDataFrame div, .stDataFrame table, 
        .stDataFrame th, .stDataFrame td,
        [data-testid="dataframe"] *, 
        [data-testid="dataframe"] table,
        [data-testid="dataframe"] th,
        [data-testid="dataframe"] td {
            background-color: var(--bg-2) !important;
            color: var(--fg) !important;
        }
        
        /* Code blocks - ARREGLADO para que se vean en modo claro */
        .stCode, .stCodeBlock, 
        .stCode > div, .stCodeBlock > div, 
        .stCode pre, .stCodeBlock pre, 
        .stCode code, .stCodeBlock code,
        [data-testid="stCodeBlock"],
        [data-testid="stCodeBlock"] *,
        pre, code {
            background-color: var(--code-bg) !important;
            color: var(--code-fg) !important;
            border: 1px solid #e9ecef !important;
        }
        
        /* Monosílabs acentuats en blau per a 'Definició' */
        .accented {
            color: #1e90ff !important;
            font-weight: 600;
        }
        </style>
        """, unsafe_allow_html=True)


def show_quiz_progress(current_question: int, total_questions: int, answered_count: int = None):
    """Muestra progreso del quiz"""
    if answered_count is not None:
        progress = answered_count / total_questions
        st.progress(progress)
        st.caption(f"Respondidas {answered_count} de {total_questions} preguntas")
    else:
        progress = current_question / total_questions
        st.progress(progress)
        st.caption(f"Pregunta {current_question} de {total_questions}")

def _is_accented(word: str) -> bool:
    # True si la palabra tiene marca diacrítica (á, é, í, ó, ú, à, è, ò, ï, ü, etc.)
    nfd = unicodedata.normalize("NFD", word or "")
    return any(unicodedata.category(ch) == "Mn" for ch in nfd)

def color_word(word: str) -> str:
    # Devuelve la palabra sin color
    return word


def highlight_accented(text: str) -> str:
    """Ya no resalta los monosílabs acentuados"""
    return text

def search_suggestions(prefix: str):
     """Sugerencias por inicial (sin quitar acentos)."""
     inicial = prefix.strip().lower()[:1]
     return sorted([w for w in monosilabos if w.lower().startswith(inicial)])

def display_word_info(paraula: str):
    info = monosilabos[paraula]

    # — Títol de la paraula en color —
    st.markdown(f"### — {color_word(paraula)} —")
    st.write("**Categoria:**", info.get("categoria", "—"))
    st.write("**Definició:**", info["definicion"])

    # Generar key único para ejemplos basado en session_state
    if f"examples_{paraula}" not in st.session_state:
        st.session_state[f"examples_{paraula}"] = random.sample(info["ejemplos"], k=min(2, len(info["ejemplos"])))
    
    ej = st.session_state[f"examples_{paraula}"]
    
    # Exemples
    st.write("**Exemples:**")
    for ex in ej:
        st.markdown("- " + ex)

    # Bloc per copiar: definició + exemples mostrats
    bloc = f"{paraula.capitalize()}\n{info['definicion']}\n" + "\n".join(f"- {e}" for e in ej)
    st.code(bloc)
    
    # Botones en columnas
    col1, col2 = st.columns(2)
    with col1:
        st.button("Copia", help="Selecciona el bloc i copia'l", key=f"copy_btn_{paraula}")
    with col2:
        if st.button("Generar nous exemples", key=f"new_examples_{paraula}"):
            st.session_state[f"examples_{paraula}"] = random.sample(info["ejemplos"], k=min(2, len(info["ejemplos"])))
            st.rerun()

    # — Contrast (si existeix) —
    if paraula in parelles:
        altra = parelles[paraula]
        if altra in monosilabos:
            info2 = monosilabos[altra]
            st.markdown(f"### — {color_word(altra)} — *_(contrast)_*")
            st.write("**Categoria:**", info2.get("categoria", "—"))
            st.write("**Definició:**", info2["definicion"])

            # Generar key único para ejemplos de la pareja
            if f"examples_{altra}" not in st.session_state:
                st.session_state[f"examples_{altra}"] = random.sample(info2["ejemplos"], k=min(2, len(info2["ejemplos"])))
            
            ej2 = st.session_state[f"examples_{altra}"]

            # Exemples de la parella
            st.write("**Exemples:**")
            for ex in ej2:
                st.markdown("- " + ex)

            # Bloc per copiar de la paraula contrast
            bloc2 = f"{altra.capitalize()}\n{info2['definicion']}\n" + "\n".join(f"- {e}" for e in ej2)
            st.code(bloc2)
            
            # Botones en columnas para la pareja
            col3, col4 = st.columns(2)
            with col3:
                st.button("Copia", help="Selecciona el bloc i copia'l", key=f"copy_btn_{altra}")
            with col4:
                if st.button("Generar nous exemples", key=f"new_examples_{altra}"):
                    st.session_state[f"examples_{altra}"] = random.sample(info2["ejemplos"], k=min(2, len(info2["ejemplos"])))
                    st.rerun()

def rerun_safe():
    """Forza un rerun compatible amb versiones nuevas/antiguas de Streamlit."""
    try:
        st.rerun()              # versiones nuevas
    except Exception:
        try:
            st.experimental_rerun()  # versiones antiguas
        except Exception:
            pass

def make_cloze(sentence: str, word: str) -> str:
    """Devuelve la frase con la PRIMERA aparición exacta de 'word' sustituida por _____"""
    return re.sub(rf"\b{re.escape(word)}\b", "_____", sentence, count=1)

def generar_preguntas(n=10):
    """Genera hasta n preguntas (enunciado cloze + 2 opciones: correcta y su parella)."""
    preguntas = []
    bolsa = []
    for w, info in monosilabos.items():
        if w in parelles and parelles[w] in monosilabos:
            for ex in info["ejemplos"]:
                # Usar solo ejemplos que contengan la palabra tal cual (con acentos)
                if re.search(rf"\b{re.escape(w)}\b", ex):
                    bolsa.append((w, ex))
    random.shuffle(bolsa)

    for w, ex in bolsa:
        pareja = parelles[w]
        preguntas.append({
            "enunciado": make_cloze(ex, w),
            "correcta": w,
            "opciones": random.sample([w, pareja], k=2),  # baraja orden
            "pareja": pareja,
        })
        if len(preguntas) >= n:
            break
    return preguntas
    
def generar_quiz(n=10):
    """Adapta generar_preguntas() al formato que espera el Mini-quiz."""
    preguntas = generar_preguntas(n)
    return {
        "preguntas": preguntas,
        "respuestas": [None] * len(preguntas)
    }

# ==== GitHub helpers: guardar/leer ranking en scores.jsonl ====
def _gh_headers():
    return {
        "Authorization": f"Bearer {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def _gh_file_url():
    owner_repo = st.secrets["GITHUB_REPO"]
    branch = st.secrets.get("GITHUB_BRANCH", "main")
    path = st.secrets.get("GITHUB_SCORES_PATH", "scores.jsonl")
    return f"https://api.github.com/repos/{owner_repo}/contents/{path}?ref={branch}"

def _gh_put_url():
    owner_repo = st.secrets["GITHUB_REPO"]
    path = st.secrets.get("GITHUB_SCORES_PATH", "scores.jsonl")
    return f"https://api.github.com/repos/{owner_repo}/contents/{path}"

@st.cache_data(ttl=60)  # 👈 Cachea la lectura 60s (ajusta el ttl si quieres)
def load_scores_from_github():
    """
    Lee el JSONL del repo.
    Devuelve (scores:list, sha:str|None). Si no existe, ([], None).
    """
    try:
        r = requests.get(_gh_file_url(), headers=_gh_headers(), timeout=10)
        if r.status_code == 404:
            return [], None  # fichero aún no creado
        r.raise_for_status()
        data = r.json()
        content_b64 = data["content"]
        sha = data["sha"]
        content = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
        scores = []
        for line in content.splitlines():
            if line.strip():
                scores.append(json.loads(line))
        return scores, sha
    except Exception as e:
        st.error(f"Error leyendo ránking de GitHub: {e}")
        return [], None

def append_score_to_github(record: dict, max_retries=3):
    """
    Añade un registro al JSONL en GitHub con control de conflictos.
    Flujo:
      - GET: leer contenido y sha
      - APPEND: añadir línea
      - PUT: subir con sha (si existe)
    """
    for attempt in range(max_retries):
        scores, sha = load_scores_from_github()
        lines = [json.dumps(s, ensure_ascii=False) for s in scores]
        lines.append(json.dumps(record, ensure_ascii=False))
        new_content = "\n".join(lines) + "\n"

        payload = {
            "message": f"Add score: {record.get('nom','???')} {record.get('puntuacio','?')}/{record.get('total','?')}",
            "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
            "branch": st.secrets.get("GITHUB_BRANCH", "main"),
        }
        if sha:
            payload["sha"] = sha

        try:
            r = requests.put(_gh_put_url(), headers=_gh_headers(), json=payload, timeout=15)
            if r.status_code in (200, 201):
                # ✅ Guardado correcto → vaciamos la caché de lectura para ver el cambio al instante
                st.cache_data.clear()
                return True
            if r.status_code == 409:  # conflicto: el fichero ha cambiado; reintentar
                time.sleep(0.8)
                continue
            r.raise_for_status()
            # si llega aquí sin excepción, lo consideramos OK por seguridad
            st.cache_data.clear()
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                st.error(f"No se ha podido guardar en el ránking (GitHub): {e}")
                return False
            time.sleep(0.8)
    return False

# ===========================
# Dades (els 15 monosílabs)
# ===========================
monosilabos = {
    "sí": {"categoria": "adverbi d'afirmació",
           "definicion": "Adverbi d'afirmació.",
           "ejemplos": [
               "Sí, vindré demà.",
               "Va dir que sí a la proposta.",
               "Sí que ho sabia.",
               "I tant que sí!",
               "Sí, estic d'acord amb tu.",
               "Sí, és veritat."
           ]},
    "si": {"categoria": "conjunció condicional",
           "definicion": "Conjunció condicional.",
           "ejemplos": [
               "Si plou, ens quedem a casa.",
               "Si estudies, aprovaràs.",
               "Si vols, t'ajude.",
               "Si tens temps, vine demà.",
               "Si no ho proves, mai ho sabràs."
           ]},

    "més": {"categoria": "quantificador/comparatiu",
            "definicion": "Comparatiu de quantitat ('més = más').",
            "ejemplos": [
                "Vull més aigua.",
                "Açò és més car que allò.",
                "Necessitem més temps.",
                "Cada dia estudie més hores.",
                "Vol més cafè al matí.",
                "Hi ha més gent a la plaça hui."
            ]},
    "mes": {"categoria": "nom (mes del calendari)",
            "definicion": "Nom del calendari.",
            "ejemplos": [
                "El mes de juny fa calor.",
                "Cada mes estalvie un poc.",
                "Aquest mes començarem.",
                "El pròxim mes hi haurà vacances.",
                "És el mes més llarg de l'any."
            ]},

    "bé": {"categoria": "adverbi",
           "definicion": "Adverbi ('bé = bien').",
           "ejemplos": [
               "Estic bé, gràcies.",
               "Fes-ho bé, si us plau.",
               "No m'ha paregut bé.",
               "Treballa molt bé sota pressió.",
               "Tot ha eixit bé al final."
           ]},
    "be": {"categoria": "nom (animal jove)",
           "definicion": "Nom: 'corder', 'ovella jove'.",
           "ejemplos": [
               "Va comprar un be al mercat.",
               "El be pastura al camp.",
               "Han nascut dos bens.",
               "El be balava sense parar.",
               "El pastor cuidava un be malalt."
           ]},

    "déu": {"categoria": "nom propi (entitat divina)",
            "definicion": "Nom: 'déu = dios'.",
            "ejemplos": [
                "Crec en un sol Déu.",
                "El Déu dels antics era venerat.",
                "La gent resava al seu Déu.",
                "Van construir un temple dedicat a Déu.",
                "Déu és omnipotent segons la fe."
            ]},
    "deu": {"categoria": "numeral / forma de 'deure'",
            "definicion": "Nombre 'deu = diez' o forma de 'deure' (ha/han de).",
            "ejemplos": [
                "En té deu cromos.",
                "Deu estudiar més per a aprovar.",
                "Deu ser tard.",
                "Han arribat deu persones.",
                "Deu treballar molt per aconseguir-ho."
            ]},

    "és": {"categoria": "verb 'ser' (3a sing.)",
           "definicion": "Forma verbal del verb 'ser'.",
           "ejemplos": [
               "Ell és professor.",
               "La casa és gran.",
               "És evident.",
               "El llibre és interessant.",
               "És massa tard per eixir.",
               "És el meu millor amic."
           ]},
    "es": {"categoria": "pronom",
           "definicion": "Pronom personal.",
           "ejemplos": [
               "Es pentina cada matí.",
               "Es va caure al terra.",
               "Es mira al mirall.",
               "Es van saludar cordialment.",
               "Es va vestir ràpidament."
           ]},

    "mà": {"categoria": "nom (part del cos)",
           "definicion": "Part del cos ('mà = mano').",
           "ejemplos": [
               "La mà em fa mal.",
               "Agafa'm de la mà.",
               "Dóna'm la mà.",
               "Alça la mà per preguntar.",
               "Va escriure amb la mà esquerra."
           ]},
    "ma": {"categoria": "adjectiu possessiu",
           "definicion": "Adjectiu possessiu ('ma = mi').",
           "ejemplos": [
               "Ma casa és la teua.",
               "Ma mare treballa ací.",
               "Ma germana vindrà.",
               "Ma terra és especial per a mi.",
               "Ma família viu al poble."
           ]},

    "món": {"categoria": "nom",
            "definicion": "'Món = mundo'.",
            "ejemplos": [
                "El món és gran.",
                "Viatjar pel món és enriquidor.",
                "És el meu món.",
                "El món canvia ràpidament.",
                "Tot el món ho sap."
            ]},
    "mon": {"categoria": "possessiu arcaic",
            "definicion": "Possessiu arcaic ('mon = mi').",
            "ejemplos": [
                "Mon pare treballa al camp.",
                "Mon oncle viu lluny.",
                "Mon cosí és menut.",
                "Mon avi sempre conta històries.",
                "Mon germà juga al futbol."
            ]},

    "pèl": {"categoria": "nom",
            "definicion": "'Pèl = pelo, cabell' (filament).",
            "ejemplos": [
                "Tens un pèl al jersei.",
                "El gat ha deixat pèl al sofà.",
                "Se m'ha caigut un pèl.",
                "El pèl és molt fi.",
                "Els gossos muden el pèl a la primavera."
            ]},
    "pel": {"categoria": "contracció ('per el')",
            "definicion": "Contracció de 'per el'.",
            "ejemplos": [
                "Passe pel carrer major.",
                "Vaig pel camí antic.",
                "Mira pel finestral.",
                "Corre pel passadís.",
                "Busca pel calaix."
            ]},

    "què": {"categoria": "pronom interrogatiu/exclamatiu",
            "definicion": "Pronom interrogatiu/exclamatiu.",
            "ejemplos": [
                "Què vols menjar?",
                "Mira què ha passat!",
                "Què tal estàs?",
                "Què fas ací?",
                "Què vols dir exactament?"
            ]},
    "que": {"categoria": "conjunció / pronom relatiu",
            "definicion": "Conjunció o pronom relatiu.",
            "ejemplos": [
                "Pensa que vindrà.",
                "El llibre que llegisc és interessant.",
                "Diuen que plourà.",
                "Crec que tens raó.",
                "És el projecte que esperàvem."
            ]},

    "sé": {"categoria": "verb 'saber' (1a sing.)",
           "definicion": "Forma verbal de 'saber'.",
           "ejemplos": [
               "Jo sé la resposta.",
               "No sé què dir-te.",
               "Sé que tens raó.",
               "No sé si vindrà.",
               "Sé tocar la guitarra."
           ]},
    "se": {"categoria": "pronom",
           "definicion": "Pronom personal.",
           "ejemplos": [
               "Se'n va anar de pressa.",
               "Se sent feliç.",
               "Se'n recorda sovint.",
               "Se n'anà corrent.",
               "Se sorprengué amb la notícia."
           ]},

    "sòl": {"categoria": "nom (terra ferma/suelo)",
            "definicion": "'Sòl = suelo, terra ferma'.",
            "ejemplos": [
                "El sòl està mullat.",
                "No poses això al sòl.",
                "El sòl és irregular.",
                "El sòl de la cuina és nou.",
                "El sòl forestal és ric en nutrients."
            ]},
    "sol": {"categoria": "nom (astre) / adjectiu ('sol = a soles')",
            "definicion": "Nom (astre 'sol') o adjectiu ('sol = solo').",
            "ejemplos": [
                "El sol brilla.",
                "Estic sol a casa.",
                "Prefereix estar sol.",
                "El sol escalfa la terra.",
                "El sol es pon a l'oest."
            ]},

    "són": {"categoria": "verb 'ser' (3a pl.)",
            "definicion": "Forma verbal de 'ser' (3a persona plural).",
            "ejemplos": [
                "Ells són amics.",
                "Les cases són grans.",
                "Són ben educats.",
                "Els meus pares són mestres.",
                "Són de València."
            ]},
    "son": {"categoria": "nom (somnolència)",
            "definicion": "'Son = sueño, ganes de dormir'.",
            "ejemplos": [
                "Tinc son.",
                "El bebè té son.",
                "Em fa son llegir.",
                "Ell té molta son.",
                "Després de dinar em ve son."
            ]},

    "té": {"categoria": "verb 'tindre' (3a sing.)",
           "definicion": "Forma verbal de 'tindre'.",
           "ejemplos": [
               "Ella té un cotxe.",
               "El xic té gana.",
               "Té pressa.",
               "Té tres gats a casa.",
               "Té molta sort."
           ]},
    "te": {"categoria": "pronom / nom (beguda)",
           "definicion": "Pronom ('a tu') o beguda ('te').",
           "ejemplos": [
               "Això és per a te.",
               "Vull un te calent.",
               "El te verd m'agrada.",
               "Beu un te amb llet.",
               "Regala'm un te d'herbes."
           ]},

    "ús": {"categoria": "nom",
           "definicion": "'Ús = utilización' d'alguna cosa.",
           "ejemplos": [
               "L'ús del mòbil està regulat.",
               "Fa ús del diccionari.",
               "En limita l'ús.",
               "L'ús de plàstic ha disminuït.",
               "Estudia l'ús correcte dels verbs."
           ]},
    "us": {"categoria": "pronom (a vosaltres)",
           "definicion": "Pronom personal ('a vosaltres').",
           "ejemplos": [
               "Us espere a la porta.",
               "Ja us he vist.",
               "Us ho explique després.",
               "Us recomane aquest llibre.",
               "Us vaig telefonar ahir."
           ]},

    "vós": {"categoria": "pronom de cortesia",
            "definicion": "Pronom personal de cortesia.",
            "ejemplos": [
                "Vós sou benvingut.",
                "Com esteu, vós?",
                "Gràcies a vós.",
                "Vós teniu la paraula.",
                "Vós sereu recordat sempre."
            ]},
    "vos": {"categoria": "pronom (a vosaltres)",
            "definicion": "Pronom personal ('a vosaltres').",
            "ejemplos": [
                "Vos estime molt.",
                "Vos ajudaré en tot.",
                "Vos ho diré demà.",
                "Vos vaig veure ahir.",
                "Vos vaig escriure un missatge."
            ]},
}

pares = [
    ("bé", "be"),
    ("déu", "deu"),
    ("és", "es"),
    ("mà", "ma"),
    ("més", "mes"),
    ("món", "mon"),
    ("pèl", "pel"),
    ("què", "que"),
    ("sé", "se"),
    ("sòl", "sol"),
    ("són", "son"),
    ("té", "te"),
    ("ús", "us"),
    ("vós", "vos"),
    ("sí", "si"),
]

parelles = {}
for acent, sense in pares:
    parelles[acent] = sense
    parelles[sense] = acent

# 4. AHORA SÍ podemos usar las funciones en el bloque try
try:
    logger.info("Iniciando aplicación...")
    
    # Inicializar estado de sesión
    init_session_state()
    
    # Configuración de página
    st.set_page_config(
        page_title="📘 Monosíl·labs: accents diacrítics en valencià",
        page_icon="📘",
        layout="centered",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # Inyectar CSS personalizado
    inject_custom_css()

except Exception as e:
    st.error(f"Error en la aplicación: {str(e)}")
    logger.exception("Error en la aplicación")
    raise

# Inyectar CSS personalizado AL INICIO
inject_custom_css()
col_title, col_theme = st.columns([4, 1])

with col_title:
    st.title("📘 Monosíl·labs: accents diacrítics en valencià")
    st.caption("Consulta definicions, exemples i parelles")
        
with st.expander("Saps què és un monosíl·lab?"):
    st.markdown(
        "**Monosíl·lab**: paraula d'una sola síl·laba.\n\n"
        "**Accent diacrític**: accent que diferencia paraules homògrafes amb "
        "significats o funcions gramaticals distintes (p. ex., **més** vs **mes**, **té** vs **te**)."
    )

# ===========================
# Estado de sesión
# ===========================
if "historial" not in st.session_state:
    st.session_state.historial = []
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "quiz_n" not in st.session_state:
    st.session_state.quiz_n = 10  # valor per defecte
if "scores" not in st.session_state:
    st.session_state.scores = []  # llista de dicts: {"nom": "...", "puntuacio": x, "total": y, "data": "AAAA-MM-DD HH:MM"}

# ===========================
# Barra lateral (menú)
# ===========================

MENU_RANK = "🏆 Ránquing Quiz"

with st.sidebar:
    st.header("📋 Menú")

    # Indicador de tema actual
    theme_icon = "☀️" if st.session_state.dark_mode else "🌙"
    theme_text = "Canviar a tema clar" if st.session_state.dark_mode else "Canviar a tema fosc"
    
    # ARREGLO: No usar rerun_safe() aquí, solo cambiar el estado
    if st.button(f"{theme_icon} {theme_text}", key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        # NO hacer rerun aquí para mantener la página actual

    # El radio lee/escribe directamente en session_state["menu"]
    st.radio(
        "Acció",
        [
            "🔍 Cerca un monosíl·lab",
            "🃏 Llista",
            "📚 Llista detallada",
            "🕘 Historial",
            "📝 Mini-quiz",
            MENU_RANK,
        ],
        key="menu",
    )

    st.divider()
    st.info(f"Versió: {datetime.now():%Y-%m-%d %H:%M:%S}")

# Router: SIEMPRE después de construir el sidebar
opcio = st.session_state["menu"]

# ===========================
# Vistas
# ===========================
if opcio == "🔍 Cerca un monosíl·lab":
    st.header("🔍 Cerca un monosíl·lab")
    
    col_input, col_btn = st.columns([3, 1])
    
    with col_input:
        paraula_input = st.text_input(
            "Escriu el monosíl·lab (amb o sense accent):",
            placeholder="Ex: més, que, sí...",
            key="search_input"
        )
    
    with col_btn:
        st.write("")  # Espaciado para alinear
        search_clicked = st.button("🔍 Cerca", key="search_btn")

    # Procesar búsqueda si se presionó Enter o el botón
    if paraula_input or search_clicked:
        search_term = st.session_state.get("search_input", "").strip()
        if search_term:
            p = search_term.lower()
            key = p if p in monosilabos else None

            if key:
                # Añadir al historial (evita duplicados consecutivos)
                if not st.session_state.historial or st.session_state.historial[-1] != key:
                    st.session_state.historial.append(key)

                # Mostrar información
                display_word_info(key)

            else:
                st.warning("No està en la base de dades. Revisa l'accent.")
                # Mostrar pistas con colores
                sugerides = search_suggestions(search_term)
                if sugerides:
                    st.markdown("**Pistes (mateixa lletra inicial):** " + ", ".join(color_word(w) for w in sugerides))
                else:
                    st.markdown("**Paraules disponibles:** " + ", ".join(color_word(w) for w in sorted(monosilabos.keys())))

elif opcio == "🃏 Llista":
    st.header("Monosíl·labs disponibles (en parelles)")
    for acent, sense in pares:
        st.markdown(f"- {color_word(acent)} / {color_word(sense)}")

elif opcio == "📚 Llista detallada":
    st.header("Monosíl·labs amb definicions i exemples")
    for acent, sense in pares:
        for p in (acent, sense):
            if p in monosilabos:
                info = monosilabos[p]
                st.markdown(f"**— {color_word(p)} —**")
                st.write("**Categoria:**", info.get("categoria", "—"))
                st.write("**Definició:**", info["definicion"])
                st.write("**Exemples:**")
                for ex in info["ejemplos"]:
                    st.markdown("- " + ex)

elif opcio == "🕘 Historial":
    st.header("Historial de cerques")
    if st.session_state.historial:
        for h in st.session_state.historial:
            st.write("-", h)
        # Botón para limpiar historial (lo dejamos ya preparado)
        if st.button("🧹 Netejar historial"):
            st.session_state.historial.clear()
            st.success("Historial netejat.")
    else:
        st.write("Encara no hi ha cerques.")
        
elif opcio == "📝 Mini-quiz":
    st.header("📝 Mini-quiz: tria la forma correcta")

    # Estados necesarios
    if "quiz" not in st.session_state:
        st.session_state.quiz = None
    if "quiz_n" not in st.session_state:
        st.session_state.quiz_n = 10
    if "scores" not in st.session_state:
        st.session_state.scores = []
    if "quiz_corrected" not in st.session_state:
        st.session_state.quiz_corrected = False
    if "last_score" not in st.session_state:
        st.session_state.last_score = {}

    quiz = st.session_state.quiz

    # Selector y botón en la misma línea
    col_sel, col_btn = st.columns([1, 1])
    with col_sel:
        st.session_state.quiz_n = st.selectbox(
            "Nombre de preguntes",
            options=[5, 10, 20],
            index=[5, 10, 20].index(st.session_state.get("quiz_n", 10)),
            help="Tria quantes preguntes vols que tinga el quiz."
        )
    with col_btn:
        st.write("")  # Espaciado para alinear con el selectbox
        if st.button("🎮 Nou quiz"):
            st.session_state.quiz_corrected = False
            st.session_state.last_score = {}
            quiz = generar_quiz(st.session_state.quiz_n)
            st.session_state.quiz = quiz
            st.rerun()

    if not quiz:
        st.info("Prem **🎮 Nou quiz** per a començar.")
    else:
        # BARRA DE PROGRESO
        answered_count = sum(1 for r in quiz["respuestas"] if r is not None)
        show_quiz_progress(1, len(quiz["preguntas"]), answered_count)
        
        # Renderizar preguntas con mejor diseño
        for i, q in enumerate(quiz["preguntas"]):
            st.markdown(f"""
            <div class="quiz-question">
                <h4>Pregunta {i+1}</h4>
                <p style="font-size: 1.1em; margin-bottom: 1rem;">{q['enunciado']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Selectbox con mejor UX
            current_answer = quiz["respuestas"][i]
            seleccion = st.selectbox(
                "Tria la forma correcta:",
                options=["— Selecciona una opció —"] + q["opciones"],
                index=(["— Selecciona una opció —"] + q["opciones"]).index(current_answer) if current_answer in q["opciones"] else 0,
                key=f"sel_{i}",
                help=f"Pregunta {i+1} de {len(quiz['preguntas'])}"
            )
            
            if seleccion != "— Selecciona una opció —":
                quiz["respuestas"][i] = seleccion
            else:
                quiz["respuestas"][i] = None
            
            st.markdown("---")

        # Actualizar progreso tras cambios
        answered_count = sum(1 for r in quiz["respuestas"] if r is not None)
        
        # Botón corregir con validación
        can_correct = answered_count == len(quiz["preguntas"])
        
        if can_correct:
            if st.button("✅ Corregir", key="btn_corregir", type="primary"):
                correctes = sum(
                    r == q["correcta"]
                    for r, q in zip(quiz["respuestas"], quiz["preguntas"])
                    if r
                )
                total = len(quiz["preguntas"])
                st.session_state.quiz_corrected = True
                st.session_state.last_score = {
                    "puntuacio": correctes,
                    "total": total,
                    "nom": st.session_state.get("last_score", {}).get("nom", ""),
                }
                st.rerun()
        else:
            st.warning(f"⚠️ Respon totes les preguntes per corregir. ({answered_count}/{len(quiz['preguntas'])} respostes)")

        # -------- Panel post-corrección (estable en rerun) --------
        if st.session_state.get("quiz_corrected"):
            score = st.session_state.get("last_score", {})
            correctes = score.get("puntuacio", 0)
            total = score.get("total", 0)

            st.success(f"Has encertat {correctes}/{total}")

            from datetime import datetime
            st.session_state.last_score["nom"] = st.text_input(
                "El teu nom (opcional):",
                value=st.session_state.last_score.get("nom", ""),
                key="inp_nom_quiz"
            )
            data_str = datetime.now().strftime("%Y-%m-%d %H:%M")

            colA, colB, colC = st.columns([1, 1, 1])

            with colA:
                if st.button("💾 Guardar ránquing", key="btn_save_rank"):
                    record = {
                        "nom": st.session_state.last_score.get("nom", ""),
                        "puntuacio": correctes,
                        "total": total,
                        "data": data_str,
                    }
                    if "scores" not in st.session_state:
                        st.session_state.scores = []
                    st.session_state.scores.append(record)
                    st.success("Resultat guardat en la sessió.")
                    try:
                        if "append_score_to_github" in globals():
                            ok = append_score_to_github(record)
                            if ok:
                                st.success("Ránquing a GitHub actualitzat.")
                            else:
                                st.info("No s'ha pogut guardar a GitHub.")
                    except Exception as e:
                        st.info(f"No s'ha pogut guardar a GitHub: {e}")

            with colB:
                if st.button("🏆 Veure ránquing", key="btn_go_rank"):
                    st.session_state["menu"] = MENU_RANK
                    st.rerun()

            with colC:
                if st.button("📝 Nou quiz", key="btn_new_quiz_after"):
                    st.session_state.quiz_corrected = False
                    st.session_state.last_score = {}
                    st.session_state.quiz = generar_quiz(st.session_state.quiz_n)
                    st.rerun()

elif opcio == "🏆 Ránquing Quiz":
    import pandas as pd
    from datetime import datetime

    st.header("🏆 Ránquing Quiz")

    # Botón de refresco (limpia caché y relee)
    if st.button("🔄 Actualitza ránquing ara"):
        st.cache_data.clear()
        st.rerun()

    # Leer datos
    try:
        scores, _ = load_scores_from_github()
    except:
        scores = []

    if not scores:
        st.info("Encara no hi ha puntuacions al ránquing.")
    else:
        # Separar por número de preguntas
        scores_5 = [s for s in scores if s.get("total") == 5]
        scores_10 = [s for s in scores if s.get("total") == 10]
        scores_20 = [s for s in scores if s.get("total") == 20]

        # Función para ordenar y crear DataFrame
        def create_ranking_df(scores_list):
            def pct(r):
                den = max(1, r.get("total", 1))
                return (r.get("puntuacio", 0) / den)

            def parse_dt(s: str):
                try:
                    return datetime.strptime(s, "%Y-%m-%d %H:%M")
                except Exception:
                    return datetime.min

            scores_sorted = sorted(
                scores_list,
                key=lambda r: (pct(r), parse_dt(r.get("data", ""))),
                reverse=True
            )

            rows = []
            for r in scores_sorted:
                num = r.get("puntuacio", 0)
                den = max(1, r.get("total", 1))
                rows.append({
                    "Nom": r.get("nom", "—"),
                    "Punts": f"{num}/{den}",
                    "%": round(100 * num / den),
                    "Data": r.get("data", "—"),
                })

            return pd.DataFrame(rows)

        # Crear tabs para cada ranking
        tab1, tab2, tab3 = st.tabs(["5 preguntes", "10 preguntes", "20 preguntes"])
        
        with tab1:
            if scores_5:
                df_5 = create_ranking_df(scores_5)
                st.dataframe(df_5, hide_index=True, use_container_width=True)
            else:
                st.info("Encara no hi ha puntuacions per a 5 preguntes.")
        
        with tab2:
            if scores_10:
                df_10 = create_ranking_df(scores_10)
                st.dataframe(df_10, hide_index=True, use_container_width=True)
            else:
                st.info("Encara no hi ha puntuacions per a 10 preguntes.")
                
        with tab3:
            if scores_20:
                df_20 = create_ranking_df(scores_20)
                st.dataframe(df_20, hide_index=True, use_container_width=True)
            else:
                st.info("Encara no hi ha puntuacions per a 20 preguntes.")
