import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="WhatsApp Bulk Sender", layout="wide")

st.title("JhimmySender")

archivo = st.file_uploader("Sube tu Excel", type=["xlsx", "csv"])

PLANTILLAS = [
    lambda nombre, monto: (
        f"¡¡¡Buen Dia!!! {nombre}\n"
        f"Trate de contactarlo sin éxito, comunicarle que usted cuenta con una campaña "
        f"pre-aprobada de {monto}, que puede retirar solo con su DNI.\n\n"
        f"Si desea más información comunicarse con: 972107359"
    ),
    lambda nombre, monto: (
        f"¡Buenos Días! {nombre}\n"
        f"Me comunico para informarle que tiene disponible una oferta especial "
        f"pre-aprobada de {monto}. Solo necesita presentar su DNI para acceder.\n\n"
        f"Consultas al: 972107359"
    ),
    lambda nombre, monto: (
        f"¡Hola {nombre}, buen día!\n"
        f"Intenté contactarle anteriormente. Le comento que cuenta con un crédito "
        f"pre-aprobado de {monto}, retirable únicamente con su DNI.\n\n"
        f"Mayor información: 972107359"
    ),
    lambda nombre, monto: (
        f"Estimado/a {nombre}, ¡buenos días!\n"
        f"Nos comunicamos para avisarle que tiene una propuesta pre-aprobada "
        f"por {monto}, disponible para retirar con solo su DNI.\n\n"
        f"Para más detalles escríbanos al: 972107359"
    ),
    lambda nombre, monto: (
        f"¡Muy buenos días, {nombre}!\n"
        f"Quería informarle que usted posee una campaña vigente pre-aprobada "
        f"de {monto}. Puede hacer efectivo el retiro presentando su DNI.\n\n"
        f"Contáctenos al: 972107359"
    ),
]

# Inicializar session state
if "enviados" not in st.session_state:
    st.session_state.enviados = set()

if archivo:
    try:
        df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
        df = df.dropna(subset=['T1', 'NOMBRE'])

        df['OFERTA_LD'] = pd.to_numeric(df['OFERTA_LD'], errors='coerce').fillna(0)
        df = df.sort_values('OFERTA_LD', ascending=True).reset_index(drop=True)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            busqueda = st.text_input("Buscar por nombre del cliente:").upper()
        with col_f2:
            limite = st.number_input("Cantidad de filas a mostrar:", min_value=10, max_value=1000, value=50)

        if busqueda:
            df = df[df['NOMBRE'].str.contains(busqueda, na=False)]

        # Filtrar los ya enviados
        df = df[~df.index.isin(st.session_state.enviados)]

        df_mostrar = df.head(limite)

        col_info, col_reset = st.columns([6, 1])
        col_info.caption(f"Mostrando {len(df_mostrar)} de {len(df)} registros pendientes. ✅ Enviados: {len(st.session_state.enviados)}")
        if col_reset.button("🔄 Resetear"):
            st.session_state.enviados = set()
            st.rerun()

        st.divider()

        for i, fila in df_mostrar.iterrows():
            nombre = str(fila['NOMBRE']).strip()
            tel = str(fila['T1']).split('.')[0]
            monto = str(int(fila['OFERTA_LD']))

            plantilla = PLANTILLAS[i % len(PLANTILLAS)]
            mensaje = plantilla(nombre, monto)
            url_wa = f"https://wa.me/51{tel}?text={urllib.parse.quote(mensaje)}"

            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(f"**{nombre}** ({tel}) — 💰 S/ {monto}")
            c2.link_button("Enviar WhatsApp ✉️", url_wa, use_container_width=True)

            # Al hacer clic en OK → marcar como enviado y rerenderizar
            if c3.button("✅ OK", key=f"ok_{i}"):
                st.session_state.enviados.add(i)
                st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")