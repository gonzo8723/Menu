import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Sushi Master 🍣")
st.title("🍣 Sushi Master")
st.subheader("Menú")

# Menú de productos
menu = {
    "california": 120,
    "sushiburger": 150,
    "yakimeshi": 90
}

pedido = []
total = 0

# Interfaz para seleccionar cantidades
for producto, precio in menu.items():
    cantidad = st.number_input(f"{producto} (${precio})", min_value=0, step=1, key=producto)
    
    if cantidad > 0:
        pedido.append((producto, cantidad, precio))
        total += cantidad * precio

st.markdown("---")

# Lógica del botón único
if pedido:
    # Construcción del mensaje para WhatsApp
    mensaje = "Hola, quiero ordenar:%0A"
    for producto, cantidad, precio in pedido:
        mensaje += f"- {producto} x{cantidad}%0A"
    
    mensaje += f"%0ATotal: ${total}"
    
    # Número de teléfono (Asegúrate de que incluya el código de país sin el +)
    numero = "5213781861057"
    link = f"https://wa.me/{numero}?text={mensaje}"

    # Botón único de envío
    st.link_button("📲 Enviar pedido vía WhatsApp", link, use_container_width=True)
else:
    st.info("Selecciona al menos un producto para habilitar el envío.")
