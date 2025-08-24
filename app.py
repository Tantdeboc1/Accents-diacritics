import streamlit as st

# Data from the original script
monosilabos = {
    "sí": {
        "definicion": "Adverbi d'afirmació.",
        "ejemplos": ["Sí, vindré demà.", "Va dir que sí a la proposta."]
    },
    "si": {
        "definicion": "Conjunció condicional.",
        "ejemplos": ["Si plou, ens quedem a casa.", "Si estudies, aprovaràs."]
    },
    "més": {
        "definicion": "Comparatiu de quantitat ('més = más').",
        "ejemplos": ["Vull més aigua.", "Açò és més car que allò."]
    },
    "mes": {
        "definicion": "Nom del calendari.",
        "ejemplos": ["El mes de juny fa calor.", "Cada mes estalvie un poc."]
    },
    "bé": {
        "definicion": "Adverbi ('bé = bien').",
        "ejemplos": ["Estic bé, gràcies.", "Fes-ho bé, si us plau."]
    },
    "be": {
        "definicion": "Nom: 'corder', 'ovella jove'.",
        "ejemplos": ["Va comprar un be al mercat.", "El be pastura al camp."]
    },
    "déu": {
        "definicion": "Nom: 'déu = dios' (entitat divina).",
        "ejemplos": ["Crec en un sol Déu.", "El Déu dels antics era venerat."]
    },
    "deu": {
        "definicion": "Nombre 'deu = diez' o forma de 'deure' (ha/han de).",
        "ejemplos": ["En té deu cromos.", "Deu estudiar més per a aprovar."]
    },
    "és": {
        "definicion": "Forma verbal del verb 'ser'.",
        "ejemplos": ["Ell és professor.", "La casa és gran."]
    },
    "es": {
        "definicion": "Pronom personal.",
        "ejemplos": ["Es pentina cada matí.", "Es va caure al terra."]
    },
    "mà": {
        "definicion": "Part del cos ('mà = mano').",
        "ejemplos": ["La mà em fa mal.", "Agafa'm de la mà."]
    },
    "ma": {
        "definicion": "Adjectiu possessiu ('ma = mi').",
        "ejemplos": ["Ma casa és la teua.", "Ma mare treballa ací."]
    },
    "món": {
        "definicion": "'Món = mundo'.",
        "ejemplos": ["El món és gran.", "Viatjar pel món és enriquidor."]
    },
    "mon": {
        "definicion": "Possessiu arcaic ('mon = mi').",
        "ejemplos": ["Mon pare treballa al camp.", "Mon oncle viu lluny."]
    },
    "pèl": {
        "definicion": "'Pèl = pelo, cabell' (filament).",
        "ejemplos": ["Tens un pèl al jersei.", "El gat ha deixat pèl al sofà."]
    },
    "pel": {
        "definicion": "Contracció de 'per el'.",
        "ejemplos": ["Passe pel carrer major.", "Vaig pel camí antic."]
    },
    "què": {
        "definicion": "Pronom interrogatiu/exclamatiu.",
        "ejemplos": ["Què vols menjar?", "Mira què ha passat!"]
    },
    "que": {
        "definicion": "Conjunció o pronom relatiu.",
        "ejemplos": ["Pensa que vindrà.", "El llibre que llegisc és interessant."]
    },
    "sé": {
        "definicion": "Forma verbal de 'saber'.",
        "ejemplos": ["Jo sé la resposta.", "No sé què dir-te."]
    },
    "se": {
        "definicion": "Pronom personal.",
        "ejemplos": ["Se'n va anar de pressa.", "Se sent feliç."]
    },
    "sòl": {
        "definicion": "'Sòl = suelo, terra ferma'.",
        "ejemplos": ["El sòl està mullat.", "No poses això al sòl."]
    },
    "sol": {
        "definicion": "Nom (astre 'sol') o adjectiu ('sol = solo').",
        "ejemplos": ["El sol brilla.", "Estic sol a casa."]
    },
    "són": {
        "definicion": "Forma verbal de 'ser' (3a persona plural).",
        "ejemplos": ["Ells són amics.", "Les cases són grans."]
    },
    "son": {
        "definicion": "'Son = sueño, ganes de dormir'.",
        "ejemplos": ["Tinc son.", "El bebé té son."]
    },
    "té": {
        "definicion": "Forma verbal de 'tindre'.",
        "ejemplos": ["Ella té un cotxe.", "El xic té gana."]
    },
    "te": {
        "definicion": "Pronom ('a tu') o beguda ('te').",
        "ejemplos": ["Això és per a te.", "Vull un te calent."]
    },
    "ús": {
        "definicion": "'Ús = utilización' d'alguna cosa.",
        "ejemplos": ["L'ús del mòbil està regulat.", "Fa ús del diccionari."]
    },
    "us": {
        "definicion": "Pronom personal ('a vosaltres').",
        "ejemplos": ["Us espere a la porta.", "Ja us he vist."]
    },
    "vós": {
        "definicion": "Pronom personal de cortesia.",
        "ejemplos": ["Vós sou benvingut.", "Com esteu, vós?"]
    },
    "vos": {
        "definicion": "Pronom personal ('a vosaltres').",
        "ejemplos": ["Vos estime molt.", "Vos ajudaré en tot."]
    },
}

# Word pairs for contrasting
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

# Create dictionary for word pairs
parelles = {}
for acent, sense in pares:
    parelles[acent] = sense
    parelles[sense] = acent

# Initialize session state
if 'historial' not in st.session_state:
    st.session_state.historial = []

if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = True

def display_word_info(paraula, show_contrast=True):
    """Display information for a word and optionally its contrasting pair"""
    if paraula in monosilabos:
        info = monosilabos[paraula]
        
        # Determine if word has accent for styling
        has_accent = any(c in paraula for c in 'àáèéìíòóùúç')
        
        if has_accent:
            st.markdown(f"### :blue[{paraula}] _(amb accent)_")
        else:
            st.markdown(f"### {paraula} _(sense accent)_")
        
        st.write(f"**Definició:** {info['definicion']}")
        st.write("**Exemples:**")
        for ejemplo in info['ejemplos']:
            st.write(f"• {ejemplo}")
        
        # Show contrasting word if requested and available
        if show_contrast and paraula in parelles:
            altra = parelles[paraula]
            if altra in monosilabos:
                st.markdown("---")
                st.markdown("#### Paraula contrastant:")
                display_word_info(altra, show_contrast=False)

def search_suggestions(paraula):
    """Get suggestions for misspelled or partial words"""
    sugerides = [p for p in monosilabos.keys() if p.startswith(paraula[:1])]
    return sorted(sugerides)

# Main app
st.title("🎓 Els accents diacrítics")
st.markdown("---")

# Educational explanation
if st.session_state.show_explanation:
    with st.expander("ℹ️ Què és un accent diacrític?", expanded=False):
        st.info("""
        Un accent diacrític és un accent que diferencia paraules iguals en l'escriptura,
        però amb significat o funció gramatical distinta.
        
        **Exemple:** 'més' (quantitat) / 'mes' (del calendari)
        
        A continuació, podràs consultar definicions i exemples de cada cas.
        """)

# Sidebar for navigation
st.sidebar.title("Navegació")
opcio = st.sidebar.radio(
    "Selecciona una opció:",
    ["🔍 Buscar paraula", "📋 Llista de parelles", "📚 Llista detallada", "📈 Historial"]
)

# Main content based on selected option
if opcio == "🔍 Buscar paraula":
    st.header("Buscar monosíl·lab")
    
    # Search input
    paraula = st.text_input("Escriu el monosíl·lab (amb o sense accent):", 
                           placeholder="Ex: més, que, sí...").strip().lower()
    
    if paraula:
        if paraula in monosilabos:
            # Add to history
            if paraula not in st.session_state.historial:
                st.session_state.historial.append(paraula)
            
            # Display word information
            display_word_info(paraula)
            
        else:
            st.warning("No està en la base de dades. Revisa l'accent.")
            
            # Show suggestions
            sugerides = search_suggestions(paraula)
            if sugerides:
                st.info(f"**Pistes** (mateixa lletra inicial): {', '.join(sugerides)}")
            else:
                st.info(f"**Paraules disponibles:** {', '.join(sorted(monosilabos.keys()))}")

elif opcio == "📋 Llista de parelles":
    st.header("Monosíl·labs disponibles (en parelles)")
    
    col1, col2 = st.columns(2)
    
    for i, (acent, sense) in enumerate(pares):
        if i % 2 == 0:
            with col1:
                st.markdown(f"**{acent}** / {sense}")
        else:
            with col2:
                st.markdown(f"**{acent}** / {sense}")
    
    st.markdown("---")
    st.info("💡 **Consell:** Fes clic a 'Buscar paraula' per veure definicions i exemples detallats.")

elif opcio == "📚 Llista detallada":
    st.header("Monosíl·labs amb definicions i exemples")
    
    # Filter options
    filter_option = st.selectbox(
        "Filtrar per:",
        ["Totes les paraules", "Només amb accent", "Només sense accent"]
    )
    
    # Display words based on filter
    for acent, sense in pares:
        words_to_show = []
        
        if filter_option == "Totes les paraules":
            words_to_show = [acent, sense]
        elif filter_option == "Només amb accent":
            words_to_show = [acent]
        elif filter_option == "Només sense accent":
            words_to_show = [sense]
        
        for paraula in words_to_show:
            if paraula in monosilabos:
                with st.expander(f"{paraula} - {monosilabos[paraula]['definicion'][:50]}..."):
                    display_word_info(paraula, show_contrast=False)

elif opcio == "📈 Historial":
    st.header("Historial de cerques")
    
    if st.session_state.historial:
        st.success(f"**Total de cerques:** {len(st.session_state.historial)}")
        
        # Display history as a list
        for i, h in enumerate(reversed(st.session_state.historial), 1):
            st.write(f"{i}. {h}")
        
        # Option to clear history
        if st.button("🗑️ Esborrar historial"):
            st.session_state.historial = []
            st.rerun()
    else:
        st.info("Encara no hi ha cerques realitzades.")
        st.markdown("Comença cercant paraules amb l'opció **'Buscar paraula'**.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    Eina d'aprenentatge dels monosíl·labs valencians amb accent diacrític
    </div>
    """, 
    unsafe_allow_html=True
)
