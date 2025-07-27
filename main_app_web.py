import streamlit as st
from rellenar_cee_dades import generar_excel_datos_cee
from rellenar_ae_dades import generar_excel_datos_ae

st.set_page_config(
    page_title="BIMCEX - CE3X i AE",
    page_icon="📄",
    layout="centered"
)

# Cargar imagen
image = Image.open("bimcex_logo.png")

# Centrar con st.image
st.image(image, width=200)

# Subtítulo
st.markdown("""
<div style='text-align: center; font-size: 18px; margin-top: -10px;'>
    <i>Generador de plantilla de dades per la realització de Certificats Energètics i Auditories Energètiques en CE3X a partir de models BIM (format gbxml)</i>
</div>
""", unsafe_allow_html=True)


st.markdown("---")

# Selector de tipo de plantilla
opcio = st.radio(
    "Selecciona el tipus de plantilla que vols generar:",
    [
        "Plantilla de dades per Certificat Energètic (CE3X)",
        "Plantilla de dades per Auditoria Energètica (complement d'auditories CE3X)"
    ]
)

# Carga del archivo
arxiu = st.file_uploader("Puja el teu fitxer gbXML", type=["xml"])

# Botón de generación
if st.button("Generar plantilla") and arxiu is not None:
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        tmp.write(arxiu.read())
        ruta_tmp = tmp.name

    try:
        if opcio.startswith("Plantilla de dades per Certificat"):
            ruta_sortida = generar_excel_datos_cee(ruta_tmp)
        else:
            ruta_sortida = generar_excel_datos_ae(ruta_tmp)

        with open(ruta_sortida, "rb") as f:
            bytes_excel = f.read()

        nom_sortida = os.path.basename(ruta_sortida)
        st.success("✅ Plantilla generada correctament!")
        st.download_button("📥 Descarrega la plantilla", data=bytes_excel, file_name=nom_sortida)

    except Exception as e:
        st.error(f"❌ Error durant la generació: {e}")

elif arxiu is None:
    st.info("📁 Puja un fitxer gbXML per començar.")


