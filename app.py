# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import re

# ===========================
# Configuración de página
# ===========================
st.set_page_config(
    page_title="Monosíl·labs (accent diacrític) · Valencià",
    page_icon="🔎",
    layout="centered",
)

st.title("Monosíl·labs amb accent diacrític (valencià)")
st.caption("Consulta definicions, exemples i parelles amb/sense accent")

# ===========================
# Utilidades
# ===========================
def strip_accents(s: str) -> str:
    """Quita acentos y baja a minúsculas para búsquedas tolerantes."""
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def search_suggestions(prefix: str):
    """Sugerencias por inicial (con o sin acentos, según ajuste)."""
    if st.session_state.get("buscar_sin_acentos"):
        inicial = strip_accents(prefix)[:1]
        return sorted([w for w in monosilabos if strip_accents(w).startswith(inicial)])
    else:
        inicial = prefix.strip().lower()[:1]
        return sorted([w for w in monosilabos if w.lower().startswith(inicial)])

def display_word_info(paraula: str):
    """Muestra la paraula, la categoria, la definició, exemples y el contrast."""
    info = monosilabos[paraula]
    st.subheader(f"— {paraula} —")
    st.write("**Categoria:**", info.get("categoria", "—"))
    st.write("**Definició:**", info["definicion"])
    st.write("**Exemples:**")
    for ex in info["ejemplos"]:
        st.write(f"- {ex}")

    # Mostrar la paraula en contrast (si existe)
    if paraula in parelles:
        altra = parelles[paraula]
        if altra in monosilabos:
            info2 = monosilabos[altra]
            st.subheader(f"— {altra} — *(contrast)*")
            st.write("**Categoria:**", info2.get("categoria", "—"))
            st.write("**Definició:**", info2["definicion"])
            st.write("**Exemples:**")
            for ex in info2["ejemplos"]:
                st.write(f"- {ex}")
import random, re

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

# ===========================
# Dades (els 15 monosíl·labs)
# ===========================
monosilabos = {
    "sí": {"categoria": "adverbi d'afirmació",
           "definicion": "Adverbi d’afirmació.",
           "ejemplos": [
               "Sí, vindré demà.",
               "Va dir que sí a la proposta.",
               "Sí que ho sabia.",
               "I tant que sí!",
               "Sí, estic d’acord amb tu.",
               "Sí, és veritat."
           ]},
    "si": {"categoria": "conjunció condicional",
           "definicion": "Conjunció condicional.",
           "ejemplos": [
               "Si plou, ens quedem a casa.",
               "Si estudies, aprovaràs.",
               "Si vols, t’ajude.",
               "Si tens temps, vine demà.",
               "Si no ho proves, mai ho sabràs."
           ]},

    "més": {"categoria": "quantificador/comparatiu",
            "definicion": "Comparatiu de quantitat (‘més = más’).",
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
                "És el mes més llarg de l’any."
            ]},

    "bé": {"categoria": "adverbi",
           "definicion": "Adverbi (‘bé = bien’).",
           "ejemplos": [
               "Estic bé, gràcies.",
               "Fes-ho bé, si us plau.",
               "No m’ha paregut bé.",
               "Treballa molt bé sota pressió.",
               "Tot ha eixit bé al final."
           ]},
    "be": {"categoria": "nom (animal jove)",
           "definicion": "Nom: ‘corder’, ‘ovella jove’.",
           "ejemplos": [
               "Va comprar un be al mercat.",
               "El be pastura al camp.",
               "Han nascut dos bens.",
               "El be balava sense parar.",
               "El pastor cuidava un be malalt."
           ]},

    "déu": {"categoria": "nom propi (entitat divina)",
            "definicion": "Nom: ‘déu = dios’.",
            "ejemplos": [
                "Crec en un sol Déu.",
                "El Déu dels antics era venerat.",
                "La gent resava al seu Déu.",
                "Van construir un temple dedicat a Déu.",
                "Déu és omnipotent segons la fe."
            ]},
    "deu": {"categoria": "numeral / forma de ‘deure’",
            "definicion": "Nombre ‘deu = diez’ o forma de ‘deure’ (ha/han de).",
            "ejemplos": [
                "En té deu cromos.",
                "Deu estudiar més per a aprovar.",
                "Deu ser tard.",
                "Han arribat deu persones.",
                "Deu treballar molt per aconseguir-ho."
            ]},

    "és": {"categoria": "verb ‘ser’ (3a sing.)",
           "definicion": "Forma verbal del verb ‘ser’.",
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
           "definicion": "Part del cos (‘mà = mano’).",
           "ejemplos": [
               "La mà em fa mal.",
               "Agafa’m de la mà.",
               "Dóna’m la mà.",
               "Alça la mà per preguntar.",
               "Va escriure amb la mà esquerra."
           ]},
    "ma": {"categoria": "adjectiu possessiu",
           "definicion": "Adjectiu possessiu (‘ma = mi’).",
           "ejemplos": [
               "Ma casa és la teua.",
               "Ma mare treballa ací.",
               "Ma germana vindrà.",
               "Ma terra és especial per a mi.",
               "Ma família viu al poble."
           ]},

    "món": {"categoria": "nom",
            "definicion": "‘Món = mundo’.",
            "ejemplos": [
                "El món és gran.",
                "Viatjar pel món és enriquidor.",
                "És el meu món.",
                "El món canvia ràpidament.",
                "Tot el món ho sap."
            ]},
    "mon": {"categoria": "possessiu arcaic",
            "definicion": "Possessiu arcaic (‘mon = mi’).",
            "ejemplos": [
                "Mon pare treballa al camp.",
                "Mon oncle viu lluny.",
                "Mon cosí és menut.",
                "Mon avi sempre conta històries.",
                "Mon germà juga al futbol."
            ]},

    "pèl": {"categoria": "nom",
            "definicion": "‘Pèl = pelo, cabell’ (filament).",


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

# Índice normalizado para búsquedas sin acentos (se construye una vez)
index_norm = {strip_accents(k): k for k in monosilabos.keys()}

# ===========================
# Estado de sesión
# ===========================
if "historial" not in st.session_state:
    st.session_state.historial = []
if "buscar_sin_acentos" not in st.session_state:
    st.session_state.buscar_sin_acentos = True  # activado por defecto

# ===========================
# Barra lateral (menú)
# ===========================
with st.sidebar:
    st.header("Menú")
    opcio = st.radio("Acció",["🔍 Buscar paraula", "📃 Llista", "📚 Llista detallada", "🕘 Historial", "📝 Mini-quiz"],
    index=0
    st.divider()
    st.checkbox("Buscar sense accents (recomanat)", value=True, key="buscar_sin_acentos")
    st.caption("Ex.: escriu «mes» i trobarà «més».")

# ===========================
# Vistas
# ===========================
if opcio == "🔍 Buscar paraula":
    st.header("Buscar monosíl·lab")
    paraula_input = st.text_input(
        "Escriu el monosíl·lab (amb o sense accent):",
        placeholder="Ex: més, que, sí..."
    )

    if paraula_input:
        # Normalización opcional
        if st.session_state.buscar_sin_acentos:
            key = index_norm.get(strip_accents(paraula_input))
        else:
            key = paraula_input.strip().lower() if paraula_input.strip().lower() in monosilabos else None

        if key:
            # Añadir al historial (evita duplicados consecutivos)
            if not st.session_state.historial or st.session_state.historial[-1] != key:
                st.session_state.historial.append(key)

            # Mostrar información
            display_word_info(key)

        else:
            st.warning("No està en la base de dades. Revisa l'accent.")
            sugerides = search_suggestions(paraula_input)
            if sugerides:
                st.info(f"**Pistes** (mateixa lletra inicial): {', '.join(sugerides)}")
            else:
                st.info(f"**Paraules disponibles:** {', '.join(sorted(monosilabos.keys()))}")

elif opcio == "📃 Llista":
    st.header("Monosíl·labs disponibles (en parelles)")
    for acent, sense in pares:
        st.write(f"- {acent} / {sense}")

elif opcio == "📚 Llista detallada":
    st.header("Monosíl·labs amb definicions i exemples")
    for acent, sense in pares:
        for p in (acent, sense):
            if p in monosilabos:
                info = monosilabos[p]
                st.markdown(f"**— {p} —**")
                st.write("**Categoria:**", info.get("categoria", "—"))
                st.write("**Definició:**", info["definicion"])
                st.write("**Exemples:**")
                for ex in info["ejemplos"]:
                    st.write(f"- {ex}")

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
    st.header("Mini-quiz: tria la forma correcta (10 preguntes)")

    # Estado inicial del quiz
    if "quiz" not in st.session_state:
        st.session_state.quiz = None

    colA, colB = st.columns(2)
    with colA:
        if st.button("🔁 Nou quiz (10 preguntes)"):
            preg = generar_preguntas(10)
            if not preg:
                st.error("No s'han pogut generar preguntes. Revisa que els exemples continguen la paraula exacta.")
            else:
                st.session_state.quiz = {
                    "preguntas": preg,
                    "respuestas": [None]*len(preg),
                    "terminado": False
                }

    with colB:
        if st.session_state.get("quiz") and not st.session_state["quiz"]["terminado"]:
            if st.button("✅ Enviar respostes"):
                st.session_state["quiz"]["terminado"] = True

    quiz = st.session_state.get("quiz")

    if not quiz:
        st.info("Prem **Nou quiz** per a començar.")
    else:
        # Render de les preguntes
        for i, q in enumerate(quiz["preguntas"]):
            st.markdown(f"**{i+1}.** {q['enunciado']}")
            # Desplegable amb dues opcions (dropdown)
            seleccion = st.selectbox(
                f"Tria la forma correcta ({i+1})",
                options=["—"] + q["opciones"],   # “—” = sense contestar
                index=(["—"] + q["opciones"]).index(quiz["respuestas"][i]) if quiz["respuestas"][i] in q["opciones"] else 0,
                key=f"sel_{i}"
            )
            quiz["respuestas"][i] = seleccion if seleccion != "—" else None
            st.write("")

        # Correcció i feedback
        if quiz["terminado"]:
            contestades = sum(1 for r in quiz["respuestas"] if r is not None)
            if contestades < len(quiz["preguntas"]):
                st.warning(f"Has deixat {len(quiz['preguntas']) - contestades} sense contestar.")
            correctes = 0
            fallos = []
            for i, q in enumerate(quiz["preguntas"]):
                if quiz["respuestas"][i] == q["correcta"]:
                    correctes += 1
                else:
                    fallos.append((i, q, quiz["respuestas"][i]))

            st.success(f"Puntuació: **{correctes}/{len(quiz['preguntas'])}**")

            if fallos:
                st.error("Repàs d'errors:")
                for i, q, elegida in fallos:
                    # definicions per reforçar
                    def_ok = monosilabos[q["correcta"]]["definicion"]
                    def_p = monosilabos[q["pareja"]]["definicion"]
                    # mostra la frase amb la solució col·locada
                    solucio = q["enunciado"].replace("_____", f"**{q['correcta']}**")
                    st.markdown(
                        f"- **{i+1}.** {solucio}"
                        f"<br/>Resposta triada: *{elegida or '—'}*  |  Correcta: **{q['correcta']}**"
                        f"<br/>· {q['correcta']}: {def_ok}"
                        f"<br/>· {q['pareja']}: {def_p}",
                        unsafe_allow_html=True
                    )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔁 Repetir (mateix quiz)"):
                    quiz["terminado"] = False
            with col2:
                if st.button("🆕 Nou quiz diferent"):
                    preg = generar_preguntas(10)
                    if not preg:
                        st.error("No s'han pogut generar preguntes noves.")
                    else:
                        st.session_state.quiz = {
                            "preguntas": preg,
                            "respuestas": [None]*len(preg),
                            "terminado": False
                        }


