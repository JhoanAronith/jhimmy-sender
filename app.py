import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="WhatsApp Bulk Sender", layout="wide")

st.title("JhimmySender")

archivo = st.file_uploader("Sube tu Excel", type=["xlsx", "csv"])

if archivo:
    try:
        df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
        df = df.dropna(subset=['T1', 'NOMBRE'])
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            busqueda = st.text_input("Buscar por nombre del cliente:").upper()
        with col_f2:
            limite = st.number_input("Cantidad de filas a mostrar:", min_value=10, max_value=1000, value=50)

        if busqueda:
            df = df[df['NOMBRE'].str.contains(busqueda, na=False)]

        df_mostrar = df.head(limite)

        st.caption(f"Mostrando {len(df_mostrar)} de {len(df)} registros encontrados.")
        st.divider()

        for i, fila in df_mostrar.iterrows():
            nombre = str(fila['NOMBRE']).strip()
            tel = str(fila['T1']).split('.')[0]
            monto = str(fila.get('OFERTA_LD', '0'))
            
            mensaje = (f"¡¡¡Buen Dia!!! {nombre}\n"
                       f"Trate de contactarlo sin éxito, comunicarle que usted cuenta con una campaña "
                       f"pre-aprobada de {monto}, que puede retirar solo con su DNI.\n\n"
                       f"Si desea más información comunicarse con: 972107359")
            
            url_wa = f"https://wa.me/51{tel}?text={urllib.parse.quote(mensaje)}"

            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(f"**{nombre}** ({tel})")
            c2.link_button(f"Enviar WhatsApp", url_wa, use_container_width=True)
            c3.checkbox("OK", key=f"check_{i}")
            
    except Exception as e:
        st.error(f"Error: {e}")