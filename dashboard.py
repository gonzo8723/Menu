import pandas as pd
import streamlit as st

# configuración
st.set_page_config(page_title="Dashboard Sushi", layout="wide")

archivo = r"C:\Users\gonzo\OneDrive\Desktop\sushi_master.xlsx"

if st.button("🔄 Refrescar"):
    st.rerun()
# =========================
# 📥 CARGAR DATOS
# =========================
ingredientes = pd.read_excel(archivo, sheet_name="ingrediente")
recetas = pd.read_excel(archivo, sheet_name="recetas")
ventas = pd.read_excel(archivo, sheet_name="ventas")
inventario = pd.read_excel(archivo, sheet_name="inventario")

# =========================
# 📅 FILTROS (AQUÍ VAN)
# =========================
ventas["fecha"] = pd.to_datetime(ventas["fecha"])

st.sidebar.header("Filtros")

if ventas.empty:
    st.warning("No hay ventas registradas aún")

    fecha_inicio = pd.Timestamp.today()
    fecha_fin = pd.Timestamp.today()

    ventas_filtradas = ventas

else:
    ventas["fecha"] = pd.to_datetime(ventas["fecha"])

    fecha_inicio = st.sidebar.date_input("Fecha inicio", ventas["fecha"].min())
    fecha_fin = st.sidebar.date_input("Fecha fin", ventas["fecha"].max())


    

ventas_filtradas = ventas[
    (ventas["fecha"].dt.date >= fecha_inicio) &
    (ventas["fecha"].dt.date <= fecha_fin)
]

# =========================
# 💰 COSTOS
# =========================
df = recetas.merge(ingredientes, on="ingrediente")
df["costo"] = df["cantidad"] * df["costo_unitario"]
costos = df.groupby("producto")["costo"].sum().reset_index()

# =========================
# 📊 VENTAS
# =========================
ventas_filtradas["total_venta"] = ventas_filtradas["cantidad"] * ventas_filtradas["precio"]

resumen_ventas = ventas_filtradas.groupby("producto")["total_venta"].sum().reset_index()
cantidad_vendida = ventas_filtradas.groupby("producto")["cantidad"].sum().reset_index()

resumen = resumen_ventas.merge(costos, on="producto")
resumen = resumen.merge(cantidad_vendida, on="producto")

resumen["costo_total"] = resumen["costo"] * resumen["cantidad"]
resumen["ganancia"] = resumen["total_venta"] - resumen["costo_total"]

# =========================
# 📦 INVENTARIO
# =========================
# INVENTARIO REAL (sin filtro)
uso = recetas.merge(ventas_filtradas, on="producto")

uso["uso_total"] = uso["cantidad_x"] * uso["cantidad_y"]

consumo = uso.groupby("ingrediente")["uso_total"].sum().reset_index()

inventario_actualizado = inventario.merge(consumo, on="ingrediente", how="left")

inventario_actualizado["uso_total"] = inventario_actualizado["uso_total"].fillna(0)

inventario_actualizado["stock_restante"] = (
    inventario_actualizado["stock"] - inventario_actualizado["uso_total"]
)

# =========================
# 🎨 DASHBOARD
# =========================
st.title("🍣 Dashboard de Sushi")

col1, col2, col3 = st.columns(3)

col1.metric("💰 Ventas Totales", resumen["total_venta"].sum())
col2.metric("💸 Costos Totales", resumen["costo_total"].sum())
col3.metric("📈 Ganancia", resumen["ganancia"].sum())

st.subheader("📊 Ventas por producto")
st.bar_chart(resumen.set_index("producto")["total_venta"])

st.subheader("💰 Ganancia por producto")
st.bar_chart(resumen.set_index("producto")["ganancia"])

st.subheader("🔥 Productos más vendidos")
top = ventas_filtradas.groupby("producto")["cantidad"].sum().sort_values(ascending=False)
st.dataframe(top)

st.subheader("📦 Inventario actual")
st.dataframe(inventario_actualizado)

bajo = inventario_actualizado[inventario_actualizado["stock_restante"] < 2]



    # =========================
# 🛒 LISTA DE COMPRAS
# =========================

# calcular cuánto falta
inventario_actualizado["faltante"] = (
    inventario_actualizado["minimo"] - inventario_actualizado["stock_restante"]
)

# solo los que necesitan compra
compras = inventario_actualizado[inventario_actualizado["faltante"] > 0]

st.subheader("🛒 Lista de compras")

if not compras.empty:
    st.warning("⚠️ Necesitas comprar:")

    st.dataframe(compras[["ingrediente", "faltante"]])
    

else:
    st.success("✅ Todo el inventario está bien")
compras = compras.merge(ingredientes, on="ingrediente", how="left")
compras["costo_compra"] = compras["faltante"] * compras["costo_unitario"]

st.subheader("💰 Costo de reposición")
st.dataframe(compras[["ingrediente", "faltante", "costo_compra"]])

if "ultimo_total" not in st.session_state:
    st.session_state.ultimo_total = len(ventas)
    
    
if len(ventas) > st.session_state.ultimo_total:
    st.success("🚨 Nuevo pedido recibido")

    
st.dataframe(
    resumen.style.format({
        "costo": "${:,.2f} ",
        "total_venta": "${:,.2f} ",
        "costo_total": "${:,.2f} ",
        "ganancia": "${:,.2f} MNX"
    })
)    

st.subheader("⚠️ Administración")

if st.button("🧹 Resetear ventas"):
    ventas_vacias = pd.DataFrame(columns=["fecha", "producto", "cantidad", "precio", "total_venta"])

    with pd.ExcelWriter(archivo, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        ventas_vacias.to_excel(writer, sheet_name="ventas", index=False)

    st.warning("Ventas reiniciadas ⚠️")
    st.rerun()