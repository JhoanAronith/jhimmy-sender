import streamlit as st
import pandas as pd
import urllib.parse
import math

st.set_page_config(page_title="JhimmySender Pro", layout="wide")

st.title("📲 JhimmySender")

PLANTILLAS = [

    lambda n, m: f"""¡Hola! {n}

✅ Este mes cuenta con un PRESTAMO DE LIBRE DISPONIBILIDAD con DESEMBOLSO INMEDIATO

💰 Monto aprobado: S/ {m}
📅 Puede elegir plazos desde 12 hasta 72 meses
✅ Solo necesita su DNI vigente
🔄 Tiene opción de amortizar o cancelar anticipadamente desde el 3er mes

🔥 SIN PROCESOS COMPLICADOS – RESPUESTA AGIL

⚠️ Para atención directa y sin demoras, escríbame a:
📞 972107359
(Asesor: JHIMMY MUÑOZ)

💬 Le brindaré una atención rápida y personalizada

📌 Aproveche esta oportunidad exclusiva con Santander Consumer.""",

    lambda n, m: f"""¡Buenos días! {n}

✅ Tiene disponible un CREDITO DE LIBRE DISPONIBILIDAD con ENTREGA INMEDIATA

💰 Importe aprobado: S/ {m}
📅 Plazos flexibles entre 12 y 72 meses
✅ Único requisito: DNI vigente
🔄 Posibilidad de pagos anticipados o cancelación desde el 3er mes

🔥 PROCESO SIMPLE – RESPUESTA RAPIDA

⚠️ Para evitar esperas, comuníquese directamente al:
📞 972107359
(Asesor: JHIMMY MUÑOZ)

💬 Atención inmediata y personalizada para usted

📌 No pierda esta oportunidad con Santander Consumer.""",

    lambda n, m: f"""¡Hola {n}!

✅ Cuenta con una oferta de PRESTAMO PERSONAL con DESEMBOLSO INMEDIATO

💰 Monto disponible: S/ {m}
📅 Financiamiento desde 12 hasta 72 meses
✅ Solo debe presentar su DNI vigente
🔄 Puede adelantar cuotas o cancelar el crédito desde el tercer mes

🔥 SIN TRAMITES ENGORROSOS – RESPUESTA INMEDIATA

⚠️ Escríbame directamente al:
📞 972107359
(Asesor: JHIMMY MUÑOZ)

💬 Le atenderé de forma directa y personalizada

📌 Beneficio exclusivo con Santander Consumer.""",

    lambda n, m: f"""Estimado/a {n}

✅ Tiene acceso a un PRESTAMO DE LIBRE DISPONIBILIDAD con ENTREGA RAPIDA

💰 Línea aprobada: S/ {m}
📅 Puede escoger plazos de 12 a 72 meses
✅ Requisito principal: DNI vigente
🔄 Opción de amortizar o cancelar anticipadamente desde el tercer mes

🔥 SIN COMPLICACIONES – ATENCION EFICIENTE

⚠️ Para atención directa, contácteme al:
📞 972107359
(Asesor: JHIMMY MUÑOZ)

💬 Recibirá asesoría personalizada al instante

📌 Aproveche esta campaña exclusiva de Santander Consumer.""",

    lambda n, m: f"""¡Muy buen día, {n}!

✅ Dispone de un CREDITO DE LIBRE DISPONIBILIDAD con DESEMBOLSO INMEDIATO

💰 Monto asignado: S/ {m}
📅 Plazos adaptables entre 12 y 72 meses
✅ Solo requiere DNI vigente
🔄 Puede realizar pagos adelantados o cancelar desde el tercer mes

🔥 PROCESO RAPIDO Y SIN COMPLICACIONES

⚠️ Para una atención más ágil, escríbame al:
📞 972107359
(Asesor: JHIMMY MUÑOZ)

💬 Atención directa y personalizada para usted

📌 No deje pasar esta oportunidad con Santander Consumer."""
]

if "enviados" not in st.session_state:
    st.session_state.enviados = set()

if "df_master" not in st.session_state:
    st.session_state.df_master = None

archivo = st.file_uploader("Sube tu Excel", type=["xlsx", "csv"])

if archivo:

    if st.session_state.df_master is None:

        df = (
            pd.read_excel(archivo)
            if archivo.name.endswith('xlsx')
            else pd.read_csv(archivo)
        )

        df = df.dropna(subset=['T1', 'NOMBRE'])

        df['OFERTA_LD'] = pd.to_numeric(
            df['OFERTA_LD'],
            errors='coerce'
        ).fillna(0)

        df = df[df['OFERTA_LD'] > 0]

        df = df.reset_index(drop=True)

        df['_id'] = df.index

        st.session_state.df_master = df

if st.session_state.df_master is not None:

    df = st.session_state.df_master.copy()

    col_ord, col_pag = st.columns([2, 2])

    with col_ord:

        orden = st.radio(
            "Ordenar ofertas:",
            ["Menor a Mayor ⬆️", "Mayor a Menor ⬇️"],
            horizontal=True
        )

        ascendente = orden == "Menor a Mayor ⬆️"

        df = df.sort_values(
            'OFERTA_LD',
            ascending=ascendente
        ).reset_index(drop=True)

    df_pendientes = df[
        ~df['_id'].isin(st.session_state.enviados)
    ].reset_index(drop=True)

    registros_por_pagina = 100

    total_paginas = max(
        1,
        math.ceil(len(df_pendientes) / registros_por_pagina)
    )

    with col_pag:

        if total_paginas > 1:

            num_pagina = st.number_input(
                f"Página (1-{total_paginas}):",
                min_value=1,
                max_value=total_paginas,
                value=1
            )

        else:
            num_pagina = 1

    st.info(
        f"Pendientes: {len(df_pendientes)} | "
        f"Enviados hoy: {len(st.session_state.enviados)}"
    )

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

        url_wa = (
            f"whatsapp://send"
            f"?phone=51{tel}"
            f"&text={urllib.parse.quote(mensaje, safe='', encoding='utf-8')}"
        )

        c1, c2, c3 = st.columns([4, 2, 1])

        c1.markdown(
            f"👤 **{nombre}**  \n"
            f"📞 {tel} | 💰 **S/ {monto}**"
        )

        c2.link_button(
            "Enviar Mensaje ✉️",
            url_wa,
            use_container_width=True
        )

        if c3.button(
            "✅ OK",
            key=f"ok_{stable_id}",
            use_container_width=True
        ):
            st.session_state.enviados.add(stable_id)
            st.rerun()

else:
    st.warning("Por favor, sube un archivo para comenzar.")

if st.session_state.df_master is not None:

    if st.button("🗑️ Borrar Excel actual y subir otro"):

        st.session_state.df_master = None

        st.session_state.enviados = set()

        st.rerun()
