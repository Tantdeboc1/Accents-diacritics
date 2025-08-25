# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import re
import unicodedata
from datetime import datetime
import random
# ===========================
# Configuración de página
# ===========================
st.set_page_config(
    page_title="📘 Monosíl·labs: accents diacrítics en valencià",
    page_icon="📘",
    layout="centered",
)

st.title("📘 Monosíl·labs: accents diacrítics en valencià")
st.caption("Consulta definicions, exemples i parelles")

with st.expander("Saps què és un monosíl·lab?"):
    st.markdown(
        "**Monosíl·lab**: paraula d’una sola síl·laba.\n\n"
        "**Accent diacrític**: accent que diferencia paraules homògrafes amb "
        "significats o funcions gramaticals distintes (p. ex., **més** vs **mes**, **té** vs **te**)."
    )
# ===========================
# Utilidades
# ===========================

def _is_accented(word: str) -> bool:
    # True si la palabra tiene marca diacrítica (á, é, í, ó, ú, à, è, ò, ï, ü, etc.)
    nfd = unicodedata.normalize("NFD", word or "")
    return any(unicodedata.category(ch) == "Mn" for ch in nfd)

def color_word(word: str) -> str:
    # Devuelve Markdown con color: azul si acentuada, gris si no
    return f":blue[{word}]" if _is_accented(word) else f":gray[{word}]"

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

    # Exemples (2 aleatoris)
    st.write("**Exemples:**")
    ej = random.sample(info["ejemplos"], k=min(2, len(info["ejemplos"])))
    for ex in ej:
        st.write(f"- {ex}")

    # Bloc per copiar: definició + exemples mostrats
    bloc = f"{paraula.capitalize()}\n{info['definicion']}\n" + "\n".join(f"- {e}" for e in ej)
    st.code(bloc)
    st.button("📋 Copiar (selecciona i copia)", help="Selecciona el bloc i copia'l")

    # — Contrast (si existeix) —
    if paraula in parelles:
        altra = parelles[paraula]
        if altra in monosilabos:
            info2 = monosilabos[altra]
            st.markdown(f"### — {color_word(altra)} — *_(contrast)_*")
            st.write("**Categoria:**", info2.get("categoria", "—"))
            st.write("**Definició:**", info2["definicion"])

            # Exemples (2 aleatoris) de la parella
            st.write("**Exemples:**")
            ej2 = random.sample(info2["ejemplos"], k=min(2, len(info2["ejemplos"])))
            for ex in ej2:
                st.write(f"- {ex}")

            # Bloc per copiar de la paraula contrast
            bloc2 = f"{altra.capitalize()}\n{info2['definicion']}\n" + "\n".join(f"- {e}" for e in ej2)
            st.code(bloc2)
            st.button("📋 Copiar (selecciona i copia)", help="Selecciona el bloc i copia'l", key=f"copy_{altra}")


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
            "ejemplos": [
                "Tens un pèl al jersei.",
                "El gat ha deixat pèl al sofà.",
                "Se m’ha caigut un pèl.",
                "El pèl és molt fi.",
                "Els gossos muden el pèl a la primavera."
            ]},
    "pel": {"categoria": "contracció (‘per el’)",
            "definicion": "Contracció de ‘per el’.",
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

    "sé": {"categoria": "verb ‘saber’ (1a sing.)",
           "definicion": "Forma verbal de ‘saber’.",
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
               "Se’n va anar de pressa.",
               "Se sent feliç.",
               "Se’n recorda sovint.",
               "Se n’anà corrent.",
               "Se sorprengué amb la notícia."
           ]},

    "sòl": {"categoria": "nom (terra ferma/suelo)",
            "definicion": "‘Sòl = suelo, terra ferma’.",
            "ejemplos": [
                "El sòl està mullat.",
                "No poses això al sòl.",
                "El sòl és irregular.",
                "El sòl de la cuina és nou.",
                "El sòl forestal és ric en nutrients."
            ]},
    "sol": {"categoria": "nom (astre) / adjectiu (‘sol = a soles’)",
            "definicion": "Nom (astre ‘sol’) o adjectiu (‘sol = solo’).",
            "ejemplos": [
                "El sol brilla.",
                "Estic sol a casa.",
                "Prefereix estar sol.",
                "El sol escalfa la terra.",
                "El sol es pon a l’oest."
            ]},

    "són": {"categoria": "verb ‘ser’ (3a pl.)",
            "definicion": "Forma verbal de ‘ser’ (3a persona plural).",
            "ejemplos": [
                "Ells són amics.",
                "Les cases són grans.",
                "Són ben educats.",
                "Els meus pares són mestres.",
                "Són de València."
            ]},
    "son": {"categoria": "nom (somnolència)",
            "definicion": "‘Son = sueño, ganes de dormir’.",
            "ejemplos": [
                "Tinc son.",
                "El bebé té son.",
                "Em fa son llegir.",
                "Ell té molta son.",
                "Després de dinar em ve son."
            ]},

    "té": {"categoria": "verb ‘tindre’ (3a sing.)",
           "definicion": "Forma verbal de ‘tindre’.",
           "ejemplos": [
               "Ella té un cotxe.",
               "El xic té gana.",
               "Té pressa.",
               "Té tres gats a casa.",
               "Té molta sort."
           ]},
    "te": {"categoria": "pronom / nom (beguda)",
           "definicion": "Pronom (‘a tu’) o beguda (‘te’).",
           "ejemplos": [
               "Això és per a te.",
               "Vull un te calent.",
               "El te verd m’agrada.",
               "Beu un te amb llet.",
               "Regala’m un te d’herbes."
           ]},

    "ús": {"categoria": "nom",
           "definicion": "‘Ús = utilización’ d’alguna cosa.",
           "ejemplos": [
               "L’ús del mòbil està regulat.",
               "Fa ús del diccionari.",
               "En limita l’ús.",
               "L’ús de plàstic ha disminuït.",
               "Estudia l’ús correcte dels verbs."
           ]},
    "us": {"categoria": "pronom (a vosaltres)",
           "definicion": "Pronom personal (‘a vosaltres’).",
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
            "definicion": "Pronom personal (‘a vosaltres’).",
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

# ===========================
# Estado de sesión
# ===========================
if "historial" not in st.session_state:
    st.session_state.historial = []
    
# Estat per al quiz
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "quiz_n" not in st.session_state:
    st.session_state.quiz_n = 10  # valor per defecte
if "scores" not in st.session_state:
    st.session_state.scores = []  # llista de dicts: {"nom": "...", "puntuacio": x, "total": y, "data": "AAAA-MM-DD HH:MM"}

# ===========================
# Barra lateral (menú)
# ===========================
with st.sidebar:
    st.header("Menú")
    opcio = st.radio(
        "Acció",
        ["🔎 Cerca un monosíl·lab", "📃 Llista", "📚 Llista detallada", "🕘 Historial", "📝 Mini-quiz"],
        index=0
    )
    st.divider()
# Marca de versió automàtica

with st.sidebar:
    st.info(f"Versió de l’app: {datetime.now():%Y-%m-%d %H:%M:%S}")
# ===========================
# Vistas
# ===========================
if opcio == "🔎 Cerca un monosíl·lab":
    st.header("Cerca un monosíl·lab")
    paraula_input = st.text_input(
        "Escriu el monosíl·lab (amb o sense accent):",
        placeholder="Ex: més, que, sí..."
    )

    if paraula_input:
        p = paraula_input.strip().lower()
        key = p if p in monosilabos else None

        if key:
            # Añadir al historial (evita duplicados consecutivos)
            if not st.session_state.historial or st.session_state.historial[-1] != key:
                st.session_state.historial.append(key)

            # Mostrar información
            display_word_info(key)

        else:
            st.warning("No està en la base de dades. Revisa l'accent.")
            # Mostrar pistes amb colors
            sugerides = search_suggestions(paraula_input)
            if sugerides:
                st.markdown("**Pistes (mateixa lletra inicial):** " + ", ".join(color_word(w) for w in sugerides))
            else:
                st.markdown("**Paraules disponibles:** " + ", ".join(color_word(w) for w in sorted(monosilabos.keys())))



elif opcio == "📃 Llista":
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
    st.header("Mini-quiz: tria la forma correcta")

    # -------- Estado inicial necesario --------
    if "quiz" not in st.session_state:
        st.session_state.quiz = None
    if "quiz_n" not in st.session_state:
        st.session_state.quiz_n = 10  # valor por defecte
    if "scores" not in st.session_state:
        st.session_state.scores = []  # {"nom": "...", "puntuacio": x, "total": y, "data": "AAAA-MM-DD HH:MM"}

    # -------- Selector nº de preguntes + botón nuevo quiz --------
    col_sel, col_btn = st.columns([1, 1])
    with col_sel:
        st.session_state.quiz_n = st.selectbox(
            "Nombre de preguntes",
            options=[5, 10, 20],
            index=[5, 10, 20].index(st.session_state.get("quiz_n", 10)),
            help="Tria quantes preguntes vols per al quiz."
        )
    with col_btn:
        if st.button(f"🔁 Nou quiz ({st.session_state.quiz_n} preguntes)", key="btn_new_quiz_top"):
            preg = generar_preguntas(st.session_state.quiz_n)
            if not preg:
                st.error("No s'han pogut generar preguntes. Revisa que els exemples continguen la paraula exacta.")
            else:
                st.session_state.quiz = {
                    "preguntas": preg,
                    "respuestas": [None] * len(preg),
                    "terminado": False,
                    "guardat": False
                }

    quiz = st.session_state.get("quiz")

    # -------- Si no hi ha quiz, indicació --------
    if not quiz:
        st.info("Prem **Nou quiz** per a començar.")
    else:
        # -------- Render de preguntes (2 opcions en desplegable) --------
        for i, q in enumerate(quiz["preguntas"]):
            st.markdown(f"**{i+1}.** {q['enunciado']}")
            seleccion = st.selectbox(
                f"Tria la forma correcta ({i+1})",
                options=["—"] + q["opciones"],
                index=(["—"] + q["opciones"]).index(quiz["respuestas"][i]) if quiz["respuestas"][i] in q["opciones"] else 0,
                key=f"sel_{i}"
            )
            quiz["respuestas"][i] = seleccion if seleccion != "—" else None
            st.write("")

        # -------- Botó d'enviament --------
        if not quiz["terminado"]:
            if st.button("✅ Enviar respostes", key="btn_submit_quiz"):
                quiz["terminado"] = True

        # -------- Correcció i feedback --------
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

            total = len(quiz["preguntas"])
            st.success(f"Puntuació: **{correctes}/{total}**")

            if fallos:
                st.error("Repàs d'errors:")
                for i, q, elegida in fallos:
                    def_ok = monosilabos[q["correcta"]]["definicion"]
                    def_p = monosilabos[q["pareja"]]["definicion"]
                    solucio = q["enunciado"].replace("_____", f"**{q['correcta']}**")
                    st.markdown(
                        f"- **{i+1}.** {solucio}"
                        f"<br/>Resposta triada: *{elegida or '—'}*  |  Correcta: **{q['correcta']}**"
                        f"<br/>· {q['correcta']}: {def_ok}"
                        f"<br/>· {q['pareja']}: {def_p}",
                        unsafe_allow_html=True
                    )

            st.divider()

            # -------- Rànquing estil arcade --------
            st.subheader("🏆 Rànquing (estil arcade)")
            col_nom, col_guardar = st.columns([2, 1])
            with col_nom:
                nom_input = st.text_input(
                    "Escriu el teu nom (5 lletres màx.)",
                    max_chars=5,
                    placeholder="p.ex. JOSEP",
                    help="Nom curt per a la classificació. 1–5 lletres (A–Z)."
                )
            with col_guardar:
                from datetime import datetime
                if st.button("💾 Guardar puntuació", key="btn_save_score", disabled=quiz.get("guardat", False)):
                    nom_clean = (nom_input or "").strip().upper()
                    import re
                    if not re.fullmatch(r"[A-Z]{1,5}", nom_clean):
                        st.error("Nom invàlid. Usa 1–5 lletres (A–Z), sense espais ni números.")
                    else:
                        record = {
                            "nom": nom_clean,
                            "puntuacio": correctes,
                            "total": total,
                            "data": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        # 1) Desa en memòria de sessió
                        st.session_state.scores.append(record)

                        # 2) (Opcional) si tens integrat guardat a GitHub:
                        if "append_score_to_github" in globals():
                            try:
                                ok = append_score_to_github(record)
                                if ok:
                                    st.success("Puntuació guardada al rànquing (persistència a GitHub)!")
                                else:
                                    st.warning("S'ha guardat en memòria, però no a GitHub.")
                            except Exception as e:
                                st.warning("No s'ha pogut guardar a GitHub; guardada en memòria.")
                        else:
                            st.info("Guardada en memòria. (Pots activar persistència a GitHub més endavant.)")

                        quiz["guardat"] = True

            # -------- Mostrar rànquing (Top 10) --------
            # Si tens lectura remota de GitHub, pots combinar:
            scores_all = st.session_state.scores[:]  # bàsic: només memòria
            # (Opcional) carregar del repo si tens load_scores_from_github():
            if "load_scores_from_github" in globals():
                try:
                    scores_remote, _ = load_scores_from_github()
                    # barreja senzill: afegeix locals que no estiguen al remot
                    for s in scores_remote:
                        if s not in scores_all:
                            scores_all.append(s)
                except Exception:
                    pass

            if scores_all:
                scores_sorted = sorted(
                    scores_all,
                    key=lambda x: (x["puntuacio"], x["data"]),
                    reverse=True
                )

                st.markdown("**Top 10**")
                for idx, s in enumerate(scores_sorted[:10], start=1):
                    barra = "█" * max(1, int(10 * s["puntuacio"] / s["total"]))
                    st.write(f"{idx:>2}. {s['nom']} — {s['puntuacio']}/{s['total']}  ({s['data']})  {barra}")

                # Descarrega CSV del rànquing actual
                import io, csv
                buf = io.StringIO()
                w = csv.writer(buf)
                w.writerow(["posicio", "nom", "puntuacio", "total", "data"])
                for idx, s in enumerate(scores_sorted, start=1):
                    w.writerow([idx, s["nom"], s["puntuacio"], s["total"], s["data"]])
                st.download_button(
                    "⬇️ Descarregar rànquing (CSV)",
                    buf.getvalue().encode("utf-8"),
                    file_name="ranquing_quiz.csv",
                    mime="text/csv",
                    key="btn_download_scores"
                )

            st.divider()

            # -------- Botons finals --------
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔁 Repetir (mateix quiz)", key="btn_repeat_same"):
                    quiz["terminado"] = False
            with col2:
                if st.button("🆕 Nou quiz diferent", key="btn_new_quiz_diff"):
                    preg = generar_preguntas(st.session_state.quiz_n)
                    if not preg:
                        st.error("No s'han pogut generar preguntes noves.")
                    else:
                        st.session_state.quiz = {
                            "preguntas": preg,
                            "respuestas": [None] * len(preg),
                            "terminado": False,
                            "guardat": False
                        }


















