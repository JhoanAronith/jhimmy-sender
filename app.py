import streamlit as st
import pandas as pd
import urllib.parse
import math

st.set_page_config(page_title="JhimmySender Pro", layout="wide")

st.title("📲 JhimmySender")

PLANTILLAS = [
    lambda n, m: f"¡¡¡Buen Dia!!! {n}\nTrate de contactarlo sin éxito, comunicarle que usted cuenta con una campaña pre-aprobada de S/ {m}, que puede retirar solo con su DNI.\n\nSi desea más información comunicarse con: 972107359",
    lambda n, m: f"¡Buenos Días! {n}\nMe comunico para informarle que tiene disponible una oferta especial pre-aprobada de S/ {m}. Solo necesita presentar su DNI para acceder.\n\nConsultas al: 972107359",
    lambda n, m: f"¡Hola {n}, buen día!\nIntenté contactarle anteriormente. Le comento que cuenta con un crédito pre-aprobado de S/ {m}, retirable únicamente con su DNI.\n\nMayor información: 972107359",
    lambda n, m: f"Estimado/a {n}, ¡buenos días!\nNos comunicamos para avisarle que tiene una propuesta pre-aprobada por S/ {m}, disponible para retirar con solo su DNI.\n\nPara más detalles escríbanos al: 972107359",
    lambda n, m: f"¡Muy buenos días, {n}!\nQuería informarle que usted posee una campaña vigente pre-aprobada de S/ {m}. Puede hacer efectivo el retiro presentando su DNI.\n\nContáctenos al: 972107359"
]

if "enviados" not in st.session_state:
    st.session_state.enviados = set()
if "df_master" not in st.session_state:
    st.session_state.df_master = None

archivo = st.file_uploader("Sube tu Excel", type=["xlsx", "csv"])

if archivo:
    if st.session_state.df_master is None:
        df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
        df = df.dropna(subset=['T1', 'NOMBRE'])
        df['OFERTA_LD'] = pd.to_numeric(df['OFERTA_LD'], errors='coerce').fillna(0)
        df = df[df['OFERTA_LD'] > 0]
        # Guardamos con una columna ID estable para rastrear enviados
        df = df.reset_index(drop=True)
        df['_id'] = df.index
        st.session_state.df_master = df

if st.session_state.df_master is not None:
    df = st.session_state.df_master.copy()

    col_ord, col_pag = st.columns([2, 2])

    with col_ord:
        orden = st.radio("Ordenar ofertas:", ["Menor a Mayor ⬆️", "Mayor a Menor ⬇️"], horizontal=True)
        ascendente = orden == "Menor a Mayor ⬆️"
        # Ordenar y resetear índice para que iloc funcione correctamente
        df = df.sort_values('OFERTA_LD', ascending=ascendente).reset_index(drop=True)

    # Filtrar enviados usando el ID estable (_id), no el índice
    df_pendientes = df[~df['_id'].isin(st.session_state.enviados)].reset_index(drop=True)

    registros_por_pagina = 100
    total_paginas = max(1, math.ceil(len(df_pendientes) / registros_por_pagina))

    with col_pag:
        if total_paginas > 1:
            num_pagina = st.number_input(f"Página (1-{total_paginas}):", min_value=1, max_value=total_paginas, value=1)
        else:
            num_pagina = 1

    st.info(f"Pendientes: {len(df_pendientes)} | Enviados hoy: {len(st.session_state.enviados)}")

    if st.button("🔄 Resetear lista de enviados"):
        st.session_state.enviados = set()
        st.rerun()

    st.divider()

    inicio = (num_pagina - 1) * registros_por_pagina
    fin = inicio + registros_por_pagina
    df_pagina = df_pendientes.iloc[inicio:fin]

    for i, fila in df_pagina.iterrows():
        nombre = str(fila['NOMBRE']).strip()
        tel = str(fila['T1']).split('.')[0]
        monto = f"{int(fila['OFERTA_LD']):,}"
        stable_id = fila['_id']

        plantilla = PLANTILLAS[i % len(PLANTILLAS)]
        mensaje = plantilla(nombre, monto)
        url_wa = f"https://wa.me/51{tel}?text={urllib.parse.quote(mensaje)}"

        c1, c2, c3 = st.columns([4, 2, 1])

        c1.markdown(f"👤 **{nombre}** \n📞 {tel} | 💰 **S/ {monto}**")
        c2.link_button("Enviar Mensaje ✉️", url_wa, use_container_width=True)

        if c3.button("✅ OK", key=f"ok_{stable_id}", use_container_width=True):
            st.session_state.enviados.add(stable_id)
            st.rerun()

else:
    st.warning("Por favor, sube un archivo para comenzar.")

if st.session_state.df_master is not None:
    if st.button("🗑️ Borrar Excel actual y subir otro"):
        st.session_state.df_master = None
        st.session_state.enviados = set()
        st.rerun()