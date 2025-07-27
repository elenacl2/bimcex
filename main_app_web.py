import streamlit as st
from rellenar_cee_dades import generar_excel_datos_cee
from rellenar_ae_dades import generar_excel_datos_ae
import tempfile
import os

st.set_page_config(page_title="Certificació Energètica BIM", layout="centered")
st.title("🔍 Certificació Energètica CE3X / AE des de gbXML")

uploaded_file = st.file_uploader("📤 Pujar fitxer gbXML", type=["xml"])

tipo_plantilla = st.radio("Selecciona la plantilla a generar:", ["CE3X", "Auditoria Energètica (AE)"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
        tmp.write(uploaded_file.read())
        ruta_temporal = tmp.name

    if st.button("Generar plantilla Excel"):
        with st.spinner("Processant..."):
            if tipo_plantilla == "CE3X":
                generar_excel_datos_cee(ruta_temporal)
                ruta_salida = ruta_temporal.replace(".xml", "_datos_cee.xlsx")
            else:
                generar_excel_datos_ae(ruta_temporal)
                ruta_salida = ruta_temporal.replace(".xml", "_datos_ae.xlsx")

        with open(ruta_salida, "rb") as f:
            st.success("✅ Fitxer generat amb èxit!")
            st.download_button("📥 Descarregar plantilla", f, file_name=os.path.basename(ruta_salida))
