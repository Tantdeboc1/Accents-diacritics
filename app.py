# =========================
# app.py — Monosíl·labs
# =========================
import streamlit as st
import pandas as pd
import random
import json, base64, requests, time
import unicodedata, re
from datetime import datetime

# -------------------------
# Config de página (una vez)
# -------------------------
st.set_page_config(
    page_title="📘 Monosíl·labs: accents diacrìtics en valencià",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None
    }
)

# -------------------------
# Estado inicial seguro
# -------------------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "menu" not in st.session_state:
    st.session_state.menu = "🔍 Cerca un monosíl·lab"
if "historial" not in st.session_state:
    st.session_state.historial = []
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "quiz_n" not in st.session_state:
    st.session_state.quiz_n = 10
if "quiz_corrected" not in st.session_state:
    st.session_state.quiz_corrected = False
if "last_score" not in st.session_state:
    st.session_state.last_score = {}
if "scores" not in st.session_state:
    st.session_state.scores = []


# -------------------------
# CSS (usa session_state.dark_mode)
# -------------------------
def inject_custom_css():
    """CSS personalitzat amb suport per a mode fosc i clar, sense trencar DataFrame/canvas."""
    dark = st.session_state.get("dark_mode", False)

    if dark:
        # ===== MODE FOSC =====
        st.markdown("""
        <style>
        :root {
            --bg: #1e1e1e; --bg-2: #2a2a2a; --bg-3: #2d2d2d;
            --fg: #f5f7fa; --border: #404040; --accent: #4a9eff;
            --btn: #2d2d2d; --btn-hover: #404040;
            --code-bg: #1a1a1a; --code-fg: #e0e0e0;
        }

        html, body, .stApp, [data-testid="stAppViewContainer"], .block-container {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
        }
        .stMarkdown, .stText, .stCaption, .stMetric, .stAlert, .stCodeBlock,
        h1, h2, h3, h4, h5, h6, p, span, label { color: var(--fg) !important; }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--bg-2) !important;
            color: var(--fg) !important;
        }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label { color: var(--fg) !important; }

        /* Inputs */
        .stTextInput input,
        .stTextArea textarea {
            background-color: var(--bg-3) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }

        /* Botons base i primaris */
        .stButton > button {
            background-color: var(--btn) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }
        .stButton > button:hover { background-color: var(--btn-hover) !important; }
        button[data-testid="baseButton-primary"] {
            background-color: var(--accent) !important;
            border-color: var(--accent) !important;
            color: #ffffff !important;
        }

        /* Blocs quiz */
        .quiz-question {
            border-left: 4px solid var(--accent);
            padding: 1rem; margin: 1rem 0;
            background-color: var(--bg-2);
            border-radius: 6px; border: 1px solid var(--border);
        }

        /* DataFrame (fosc): contenidor i canvas */
        [data-testid="stDataFrame"] {
            background-color: var(--bg-2) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
            border-radius: 6px;
        }
        [data-testid="stDataFrame"] table th,
        [data-testid="stDataFrame"] table td {
            background-color: var(--bg-2) !important;
            color: var(--fg) !important;
            border-color: var(--border) !important;
        }
        [data-testid="stDataFrame"] canvas {
            background-color: var(--bg-2) !important;
            image-rendering: auto !important;
        }

        /* Codi */
        .stCode, .stCodeBlock, [data-testid="stCodeBlock"], pre, code {
            background-color: var(--code-bg) !important;
            color: var(--code-fg) !important;
            border: 1px solid var(--border) !important;
        }

        /* Tooltips (fosc) — fons clar + text fosc */
        [data-testid="stTooltipContent"],
        div[role="tooltip"] {
            background: #f5f7fa !important;
            color: #111827 !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35) !important;
            z-index: 9999 !important;
        }
        div[role="tooltip"] * { color: inherit !important; }

        /* Accent per a subratllats puntuals */
        .accented { color: #1e90ff !important; font-weight: 600; }
        </style>
        """, unsafe_allow_html=True)

    else:
        # ===== MODE CLAR =====
        st.markdown("""
        <style>
        :root {
            --bg: #ffffff; --bg-2: #f8f9fa; --bg-3: #ffffff;
            --fg: #111827; --muted: #374151; --border: #d1d5db;
            --accent: #0066cc; --btn: #ffffff; --btn-hover: #e9ecef;
            --code-bg: #f8f9fa; --code-fg: #333333;
        }

        html, body, .stApp, [data-testid="stAppViewContainer"], .block-container {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
        }
        .stMarkdown, .stText, .stCaption, .stMetric, .stAlert, .stCodeBlock,
        h1, h2, h3, h4, h5, h6, p, span, label { color: var(--fg) !important; }

        /* Sidebar (clar) */
        [data-testid="stSidebar"] { background-color: var(--bg-2) !important; }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label { color: var(--fg) !important; }

        /* Inputs text & focus */
        .stTextInput input {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }
        .stTextInput input:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 1px var(--accent) inset !important;
        }
        .stTextInput input::placeholder { color: #6b7280 !important; }
        .stTextArea textarea {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }

        /* Selectbox control cerrado */
        .stSelectbox [data-baseweb="select"],
        .stSelectbox [data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #111827 !important;
            border: 1px solid #d1d5db !important;
        }
        .stSelectbox [data-baseweb="select"] input,
        .stSelectbox [data-baseweb="select"] [data-baseweb="single-value"],
        .stSelectbox [data-baseweb="select"] [data-baseweb="placeholder"] {
            color: #111827 !important;
        }
        .stSelectbox svg, .stSelectbox svg * {
            fill: #111827 !important;
            stroke: #111827 !important;
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
        button[data-testid="baseButton-primary"] {
            background-color: var(--accent) !important;
            border-color: var(--accent) !important;
            color: #ffffff !important;
        }

        /* Bloques quiz */
        .quiz-question {
            border-left: 4px solid var(--accent);
            padding: 1rem; margin: 1rem 0;
            background-color: var(--bg);
            border-radius: 6px; border: 1px solid var(--border);
        }

        /* DataFrame claro */
        [data-testid="stDataFrame"],
        [data-testid="stDataFrame"] table,
        [data-testid="stDataFrame"] th,
        [data-testid="stDataFrame"] td,
        [data-testid="stDataFrame"] canvas {
            background-color: #ffffff !important;
            color: #111827 !important;
            border-color: #e5e7eb !important;
        }

        /* Tabs claro */
        [data-testid="stTabs"] [role="tablist"] {
            background-color: #ffffff !important;
            border-bottom: 1px solid #e5e7eb !important;
        }
        [data-testid="stTabs"] [role="tab"] {
            background-color: #f8f9fa !important;
            color: #111827 !important;
            border: 1px solid #e5e7eb !important;
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            background-color: #ffffff !important;
            color: #111827 !important;
        }

        /* Código */
        .stCode, .stCodeBlock, [data-testid="stCodeBlock"], pre, code {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }

        /* Tooltips (clar) */
        [data-testid="stTooltipContent"],
        div[role="tooltip"] {
            background: #111827 !important;
            color: #ffffff !important;
        }

        /* Expander */
        [data-testid="stExpander"],
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            background-color: var(--bg) !important;
            color: var(--fg) !important;
            border: 1px solid var(--border) !important;
        }

        .accented { color: #0066cc !important; font-weight: 600; }

        /* === OVERRIDE nuclear: popover/selectbox siempre blanco en modo claro === */
        :root body [data-baseweb="popover"],
        :root body [data-baseweb="popover"] *,
        :root body div[role="listbox"],
        :root body div[role="listbox"] *,
        :root body [data-baseweb="menu"],
        :root body [data-baseweb="menu"] * {
            background-color: #ffffff !important;
            color: #111827 !important;
            border-color: #d1d5db !important;
        }
        div[role="listbox"] [role="option"],
        [data-baseweb="menu"] [role="option"],
        [data-baseweb="menu"] li {
            background-color: #ffffff !important;
            color: #111827 !important;
        }
        div[role="listbox"] [role="option"]:hover,
        div[role="listbox"] [role="option"][aria-selected="true"],
        [data-baseweb="menu"] [role="option"]:hover,
        [data-baseweb="menu"] [role="option"][aria-selected="true"],
        [data-baseweb="menu"] li:hover {
            background-color: #eef3f8 !important;
            color: #111827 !important;
        }
        </style>
        """, unsafe_allow_html=True)
# -------------------------
# Toggle de tema (antes del CSS)
# -------------------------
with st.sidebar:
    toggle_label = "Canvia a mode fosc" if not st.session_state.dark_mode else "Canvia a mode clar"
    new_dark = st.toggle(toggle_label, value=st.session_state.dark_mode, key="__theme_toggle")
if new_dark != st.session_state.dark_mode:
    st.session_state.dark_mode = new_dark
    st.rerun()

# Inyectar CSS una sola vez
inject_custom_css()


# -------------------------
# Datos base (monosíl·labs)
# -------------------------
pares = [
    ("bé", "be"), ("déu", "deu"), ("és", "es"), ("mà", "ma"),
    ("més", "mes"), ("món", "mon"), ("pèl", "pel"), ("què", "que"),
    ("sé", "se"), ("sòl", "sol"), ("són", "son"), ("té", "te"),
    ("ús", "us"), ("vós", "vos"), ("sí", "si"),
]

parelles = {}
for acent, sense in pares:
    parelles[acent] = sense
    parelles[sense] = acent

monosilabos = {
    "sí": {
        "categoria": "adverbi d'afirmació",
        "definicion": "Adverbi d'afirmació.",
        "ejemplos": [
            "Sí, vindré demà.",
            "Va dir que sí a la proposta.",
            "Sí que ho sabia.",
            "I tant que sí!",
            "Sí, estic d'acord amb tu.",
            "Sí, és veritat.",
            "Sí, això és correcte.",
            "Em va dir que sí sense dubtar.",
            "Sí, ho faré ara mateix.",
            "Sí, ho he comprovat diverses vegades."
        ]
    },
    "si": {
        "categoria": "conjunció condicional",
        "definicion": "Conjunció condicional.",
        "ejemplos": [
            "Si plou, ens quedem a casa.",
            "Si estudies, aprovaràs.",
            "Si vols, t'ajude.",
            "Si tens temps, vine demà.",
            "Si no ho proves, mai ho sabràs.",
            "Si véns, porta menjar.",
            "Si truques, et contestaré.",
            "Si estàs malalt, queda't a casa.",
            "Si treballes dur, tindràs èxit.",
            "Si cau, es farà mal."
        ]
    },

    "més": {
        "categoria": "quantificador/comparatiu",
        "definicion": "Comparatiu de quantitat ('més = más').",
        "ejemplos": [
            "Vull més aigua.",
            "Això és més car que allò.",
            "Necessitem més temps.",
            "Cada dia estudie més hores.",
            "Vol més cafè al matí.",
            "Hi ha més gent a la plaça hui.",
            "M'agrada més aquest llibre.",
            "Necessites més paciència.",
            "Ell corre més que jo.",
            "Menja més fruita per estar sa."
        ]
    },
    "mes": {
        "categoria": "nom (mes del calendari)",
        "definicion": "Nom del calendari.",
        "ejemplos": [
            "El mes de juny fa calor.",
            "Cada mes estalvie un poc.",
            "Aquest mes començarem.",
            "El pròxim mes hi haurà vacances.",
            "És el mes més llarg de l'any.",
            "El mes passat vam viatjar.",
            "Cada mes canvien els preus.",
            "Va nàixer el mes de maig.",
            "Este mes hem treballat molt.",
            "El mes d'agost sol ser calorós."
        ]
    },

    "bé": {
        "categoria": "adverbi",
        "definicion": "Adverbi ('bé = bien').",
        "ejemplos": [
            "Estic bé, gràcies.",
            "Fes-ho bé, si us plau.",
            "No m'ha paregut bé.",
            "Treballa molt bé sota pressió.",
            "Tot ha eixit bé al final.",
            "Mira-ho bé abans de signar.",
            "Ho has entés bé?",
            "Em sembla bé la teua idea.",
            "Va parlar molt bé al congrés.",
            "M'ho he passat bé avui."
        ]
    },
    "be": {
        "categoria": "nom (animal jove)",
        "definicion": "Nom: 'corder', 'ovella jove'.",
        "ejemplos": [
            "Va comprar un be al mercat.",
            "El be pastura al camp.",
            "Han nascut dos bens.",
            "El be balava sense parar.",
            "El pastor cuidava un be malalt.",
            "El be va créixer ràpid.",
            "Els bens juguen a l'herba.",
            "Un be va fugir de l'estable.",
            "Ha venut els bens al mercat.",
            "El be estava amb la mare."
        ]
    },
}
def search_suggestions(prefix: str):
    inicial = prefix.strip().lower()[:1]
    return sorted([w for w in monosilabos if w.lower().startswith(inicial)])
# -------------------------
# GitHub helpers (ranking)
# -------------------------
def _gh_headers():
    return {
        "Authorization": f"Bearer {st.secrets.get('GITHUB_TOKEN','')}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def _gh_file_url():
    owner_repo = st.secrets.get("GITHUB_REPO","")
    branch = st.secrets.get("GITHUB_BRANCH", "main")
    path = st.secrets.get("GITHUB_SCORES_PATH", "scores.jsonl")
    return f"https://api.github.com/repos/{owner_repo}/contents/{path}?ref={branch}"

def _gh_put_url():
    owner_repo = st.secrets.get("GITHUB_REPO","")
    path = st.secrets.get("GITHUB_SCORES_PATH", "scores.jsonl")
    return f"https://api.github.com/repos/{owner_repo}/contents/{path}"

@st.cache_data(ttl=60)
def load_scores_from_github():
    try:
        r = requests.get(_gh_file_url(), headers=_gh_headers(), timeout=10)
        if r.status_code == 404:
            return [], None
        r.raise_for_status()
        data = r.json()
        content_b64 = data.get("content","")
        sha = data.get("sha")
        content = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
        scores = []
        for line in content.splitlines():
            if line.strip():
                scores.append(json.loads(line))
        return scores, sha
    except Exception as e:
        st.info(f"No s'ha pogut llegir el rànguing: {e}")
        return [], None

def append_score_to_github(record: dict):
    try:
        scores, sha = load_scores_from_github()
        lines = [json.dumps(s, ensure_ascii=False) for s in scores]
        lines.append(json.dumps(record, ensure_ascii=False))
        new_content = "\n".join(lines) + "\n"
        payload = {
            "message": f"Add score: {record.get('nom','')} {record.get('puntuacio','?')}/{record.get('total','?')}",
            "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
            "branch": st.secrets.get("GITHUB_BRANCH", "main"),
        }
        if sha:
            payload["sha"] = sha
        r = requests.put(_gh_put_url(), headers=_gh_headers(), json=payload, timeout=15)
        if r.status_code in (200, 201):
            st.cache_data.clear()
            return True
        if r.status_code == 409:
            time.sleep(0.8)
            st.cache_data.clear()
            return append_score_to_github(record)
        r.raise_for_status()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.info(f"No s'ha pogut guardar a GitHub: {e}")
        return False


# -------------------------
# Utilidades varias
# -------------------------
def safe_rerun():
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            pass

def display_word_info(paraula: str):
    info = monosilabos[paraula]

    st.markdown(f"### — {paraula} —")
    st.write("**Categoria:**", info.get("categoria", "—"))
    st.write("**Definició:**", info["definicion"])

    # ejemplos (persistimos 2 por palabra)
    key_ej = f"examples_{paraula}"
    if key_ej not in st.session_state:
        st.session_state[key_ej] = random.sample(info["ejemplos"], k=min(2, len(info["ejemplos"])))
    ej = st.session_state[key_ej]

    st.write("**Exemples:**")
    for ex in ej:
        st.markdown("- " + ex)

    bloc = f"{paraula.capitalize()}\n{info['definicion']}\n" + "\n".join(f"- {e}" for e in ej)
    st.code(bloc)

    col1, col2 = st.columns(2)
    with col1:
        st.button("Copia", help="Selecciona el bloc i copia'l",
                  key=f"copy_btn_{paraula}", type="primary")
    with col2:
        if st.button("Generar nous exemples", key=f"new_examples_{paraula}"):
            st.session_state[key_ej] = random.sample(info["ejemplos"], k=min(2, len(info["ejemplos"])))
            safe_rerun()

    # contrast
    if paraula in parelles:
        altra = parelles[paraula]
        if altra in monosilabos:
            info2 = monosilabos[altra]
            st.markdown(f"### — {altra} — *_(contrast)_*")
            st.write("**Categoria:**", info2.get("categoria", "—"))
            st.write("**Definició:**", info2["definicion"])

            key_ej2 = f"examples_{altra}"
            if key_ej2 not in st.session_state:
                st.session_state[key_ej2] = random.sample(info2["ejemplos"], k=min(2, len(info2["ejemplos"])))
            ej2 = st.session_state[key_ej2]

            st.write("**Exemples:**")
            for ex in ej2:
                st.markdown("- " + ex)

            bloc2 = f"{altra.capitalize()}\n{info2['definicion']}\n" + "\n".join(f"- {e}" for e in ej2)
            st.code(bloc2)

            col3, col4 = st.columns(2)
            with col3:
                st.button("Copia", help="Selecciona el bloc i copia'l",
                          key=f"copy_btn_{altra}", type="primary")
            with col4:
                if st.button("Generar nous exemples", key=f"new_examples_{altra}"):
                    st.session_state[key_ej2] = random.sample(info2["ejemplos"], k=min(2, len(info2["ejemplos"])))
                    safe_rerun()


# -------------------------
# Quiz helpers
# -------------------------
def make_cloze(sentence: str, word: str) -> str:
    return re.sub(rf"\b{re.escape(word)}\b", "_____", sentence, count=1)

def generar_preguntas(n=10):
    preguntas = []
    bolsa = []
    for w, info in monosilabos.items():
        if w in parelles and parelles[w] in monosilabos:
            for ex in info["ejemplos"]:
                if re.search(rf"\b{re.escape(w)}\b", ex):
                    bolsa.append((w, ex))
    random.shuffle(bolsa)
    for w, ex in bolsa[:n]:
        pareja = parelles[w]
        preguntas.append({
            "enunciado": make_cloze(ex, w),
            "correcta": w,
            "opciones": random.sample([w, pareja], k=2),
            "pareja": pareja,
        })
    return preguntas

def generar_quiz(n=10):
    preguntas = generar_preguntas(n)
    return {"preguntas": preguntas, "respuestas": [None]*len(preguntas)}

def show_quiz_progress(answered: int, total: int):
    st.progress(answered/max(1,total))
    st.caption(f"Respostes: {answered}/{total}")


# -------------------------
# Ranking (único render)
# -------------------------
def render_ranking():
    """Render estable:
       - Mode fosc -> st.dataframe (interactiu)
       - Mode clar -> st.table (HTML, sense canvas negre)
    """
    if st.button("🔄 Actualitza rànguing", key="refresh_ranking_btn"):
        st.cache_data.clear()
        safe_rerun()

    scores, _ = load_scores_from_github()
    if not scores:
        st.info("Encara no hi ha puntuacions.")
        return

    dark = st.session_state.get("dark_mode", False)

    for n_preg in [5, 10, 20]:
        subset = [s for s in scores if s.get("total") == n_preg]
        if not subset:
            continue

        # ordenar per % i data
        def pct(r): return (r.get("puntuacio", 0) / max(1, r.get("total", 1)))
        def dt(s): 
            try:
                return datetime.strptime(s or "", "%Y-%m-%d %H:%M")
            except Exception:
                return datetime.min

        subset_sorted = sorted(subset, key=lambda r: (pct(r), dt(r.get("data",""))), reverse=True)

        rows = []
        for r in subset_sorted:
            num = r.get("puntuacio", 0)
            den = max(1, r.get("total", 1))
            rows.append({
                "Nom": r.get("nom", "—"),
                "Punts": f"{num}/{den}",
                "%": round(100 * num / den),
                "Data": r.get("data", "—"),
            })
        df = pd.DataFrame(rows)

        with st.expander(f"Rànguing {n_preg} preguntes", expanded=(n_preg == 10)):
            if dark:
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                styler = (
                    df.style
                      .set_properties(**{
                          "background-color": "#ffffff",
                          "color": "#111827",
                          "border-color": "#e5e7eb",
                          "border-width": "1px",
                          "border-style": "solid"
                      })
                      .set_table_styles([
                          {"selector": "thead th",
                           "props": "background-color:#f8f9fa; color:#111827; border:1px solid #e5e7eb;"},
                          {"selector": "tbody td",
                           "props": "border:1px solid #e5e7eb;"},
                          {"selector": "tbody tr:nth-child(even) td",
                           "props": "background-color:#fcfcfc;"}
                      ])
                      .hide(axis="index")
                )
                st.table(styler)


# -------------------------
# UI superior
# -------------------------
st.title("📘 Monosíl·labs: accents diacrìtics en valencià")
with st.expander("Saps què és un monosíl·lab?"):
    st.markdown(
        "**Monosíl·lab**: paraula d'una sola síl·laba.\n\n"
        "**Accent diacrític**: accent que diferencia paraules homògrafes "
        "amb significats o funcions gramaticals distintes (p. ex., **més** vs **mes**, **té** vs **te**)."
    )

# -------------------------
# Menú lateral
# -------------------------
with st.sidebar:
    st.header("📋 Menú")
    st.radio(
        "Acció",
        [
            "🔍 Cerca un monosíl·lab",
            "🃏 Llista",
            "📚 Llista detallada",
            "🕘 Historial",
            "📝 Mini-quiz",
            "🏆 Rànguing Quiz",
        ],
        key="menu",
    )
    st.divider()
    st.info(f"Versió: {datetime.now():%Y-%m-%d %H:%M:%S}")

opcio = st.session_state.menu

# -------------------------
# Vistas
# -------------------------
if opcio == "🔍 Cerca un monosíl·lab":
    st.header("🔍 Cerca un monosíl·lab")
    col_input, col_btn = st.columns([3,1])

    with col_input:
        paraula_input = st.text_input(
            "Paraula:",
            placeholder="Escriu el monosíl·lab (amb o sense accent)…",
            key="search_input"
        )
    with col_btn:
        st.write("")  # espai
        search_clicked = st.button("Cerca", key="search_btn")

    if paraula_input or search_clicked:
        p = st.session_state.get("search_input","").strip().lower()
        if p in monosilabos:
            if not st.session_state.historial or st.session_state.historial[-1] != p:
                st.session_state.historial.append(p)
            display_word_info(p)
        else:
            st.warning("No està en la base de dades. Revisa l'accent.")
            sugerides = search_suggestions(p)
            if sugerides:
                st.markdown("**Pistes (mateixa lletra inicial):** " + ", ".join(sugerides))
            else:
                st.markdown("**Paraules disponibles:** " + ", ".join(sorted(monosilabos.keys())))

elif opcio == "🃏 Llista":
    st.header("🃏 Llista en parelles")
    for acent, sense in pares:
        st.markdown(f"- {acent} / {sense}")

elif opcio == "📚 Llista detallada":
    st.header("📚 Llista detallada")
    for acent, sense in pares:
        for p in (acent, sense):
            if p in monosilabos:
                info = monosilabos[p]
                st.markdown(f"**— {p} —**")
                st.write("**Categoria:**", info.get("categoria", "—"))
                st.write("**Definició:**", info["definicion"])
                st.write("**Exemples:**")
                for ex in info["ejemplos"]:
                    st.markdown("- " + ex)
                st.markdown("---")

elif opcio == "🕘 Historial":
    st.header("🕘 Historial")
    if st.session_state.historial:
        for h in st.session_state.historial:
            st.write("-", h)
        if st.button("🧹 Netejar historial"):
            st.session_state.historial.clear()
            st.success("Historial netejat.")
    else:
        st.info("Encara no hi ha cerques.")

elif opcio == "📝 Mini-quiz":
    st.header("📝 Mini-quiz: tria la forma correcta")
    # selector i boto
    col_sel, col_btn = st.columns([1,1])
    with col_sel:
        st.session_state.quiz_n = st.selectbox(
            "Nombre de preguntes:",
            options=[5,10,20],
            index=[5,10,20].index(st.session_state.get("quiz_n",10)),
            key="quiz_n_select"
        )
    with col_btn:
        st.write("")
        if st.button("Nou quiz", type="primary"):
            st.session_state.quiz_corrected = False
            st.session_state.last_score = {}
            st.session_state.quiz = generar_quiz(st.session_state.quiz_n)
            safe_rerun()

    quiz = st.session_state.get("quiz")
    if not quiz:
        st.info("Prem **Nou quiz** per a començar.")
    else:
        answered = sum(1 for r in quiz["respuestas"] if r is not None)
        show_quiz_progress(answered, len(quiz["preguntas"]))

        for i, q in enumerate(quiz["preguntas"]):
            st.markdown(f'<div class="quiz-question"><h4>Pregunta {i+1}</h4>'
                        f'<p style="margin:0.5rem 0 0.75rem 0">{q["enunciado"]}</p></div>',
                        unsafe_allow_html=True)
            opts = ["— Selecciona —"] + q["opciones"]
            idx = opts.index(quiz["respuestas"][i]) if quiz["respuestas"][i] in q["opciones"] else 0
            sel = st.selectbox("Tria la forma correcta:", options=opts, index=idx, key=f"sel_{i}")
            quiz["respuestas"][i] = None if sel == "— Selecciona —" else sel
            st.divider()

        answered = sum(1 for r in quiz["respuestas"] if r is not None)
        if answered == len(quiz["preguntas"]):
            if st.button("✅ Corregir", type="primary"):
                correctes = sum(r == q["correcta"] for r, q in zip(quiz["respuestas"], quiz["preguntas"]) if r)
                total = len(quiz["preguntas"])
                st.session_state.quiz_corrected = True
                st.session_state.last_score = {"puntuacio": correctes, "total": total, "nom": st.session_state.last_score.get("nom","")}
                safe_rerun()
        else:
            st.warning(f"Respon totes les preguntes ({answered}/{len(quiz['preguntas'])}).")

        if st.session_state.get("quiz_corrected"):
            score = st.session_state.get("last_score", {})
            st.success(f"Has encertat {score.get('puntuacio',0)}/{score.get('total',0)}")
            st.session_state.last_score["nom"] = st.text_input("El teu nom (opcional):", value=st.session_state.last_score.get("nom",""))

            colA, colB, colC = st.columns(3)
            with colA:
                if st.button("💾 Guardar rànguing"):
                    record = {
                        "nom": st.session_state.last_score.get("nom",""),
                        "puntuacio": score.get("puntuacio",0),
                        "total": score.get("total",0),
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    st.session_state.scores.append(record)
                    ok = append_score_to_github(record)
                    if ok:
                        st.success("Rànguing a GitHub actualitzat.")
            with colB:
                if st.button("📝 Nou quiz"):
                    st.session_state.quiz_corrected = False
                    st.session_state.last_score = {}
                    st.session_state.quiz = generar_quiz(st.session_state.quiz_n)
                    safe_rerun()
            with colC:
                if st.button("🏆 Veure rànguing"):
                    st.session_state.menu = "🏆 Rànguing Quiz"
                    safe_rerun()

elif opcio == "🏆 Rànguing Quiz":
    st.header("🏆 Rànguing Quiz")
    render_ranking()
