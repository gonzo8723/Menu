import streamlit as st
import pandas as pd
from datetime import datetime

archivo = r"C:\Users\gonzo\OneDrive\Desktop\sushi_master.xlsx"

st.set_page_config(page_title="Sushi Master 🍣")

st.title("🍣 Sushi Master")

st.subheader("Menú")

menu = {
    "california": 120,
    "sushiburger": 150,
    "yakimeshi": 90
}

pedido = []

for producto, precio in menu.items():
    cantidad = st.number_input(f"{producto} (${precio})", min_value=0, step=1)
    
    if cantidad > 0:
        pedido.append((producto, cantidad, precio))

if st.button("📲 Hacer pedido"):
    if pedido:

        # =========================
        # 📥 GUARDAR EN EXCEL
        # =========================
        ventas = pd.read_excel(archivo, sheet_name="ventas")

        nuevas_ventas = []

        for producto, cantidad, precio in pedido:
            nuevas_ventas.append({
                "fecha": datetime.now(),
                "producto": producto,
                "cantidad": cantidad,
                "precio": precio,
                "total_venta": cantidad * precio
            })

        nuevas_ventas_df = pd.DataFrame(nuevas_ventas)

        ventas = pd.concat([ventas, nuevas_ventas_df], ignore_index=True)

        # guardar sin borrar archivo
        with pd.ExcelWriter(archivo, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            ventas.to_excel(writer, sheet_name="ventas", index=False)

        # =========================
        # 📲 WHATSAPP
        # =========================
        mensaje = "Hola, quiero ordenar:%0A"
        total = 0

        for producto, cantidad, precio in pedido:
            mensaje += f"- {producto} x{cantidad}%0A"
            total += cantidad * precio

        mensaje += f"%0ATotal: ${total}"

        numero = "5213781861057"
        link = f"https://wa.me/{numero}?text={mensaje}"

        st.success("Pedido guardado ✅")
        st.link_button("Enviar pedido por WhatsApp", link)

    else:
        st.warning("Selecciona al menos un producto")