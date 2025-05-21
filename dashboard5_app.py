import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Configuración general
st.set_page_config(layout="wide", page_title="Dashboard de Ventas Supermercado")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# Barra lateral con filtros
st.sidebar.header("Filtros Interactivos")

# Filtro de fechas
min_date = df["Date"].min()
max_date = df["Date"].max()
fecha_rango = st.sidebar.date_input("Selecciona un rango de fechas", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filtro Línea de Producto
st.sidebar.markdown("**Línea de Producto**")
categorias = df["Product line"].unique()
categorias_seleccionadas = []
for categoria in categorias:
    if st.sidebar.toggle(categoria, value=True, key=f"cat_{categoria}"):
        categorias_seleccionadas.append(categoria)

# Filtro Tipo de Cliente
tipos_cliente = df["Customer type"].unique().tolist()
tipos_cliente.insert(0, "Todos")
tipo_cliente_seleccionado = st.sidebar.radio("Tipo de Cliente", tipos_cliente, horizontal=True)

# Filtro Sucursal
st.sidebar.markdown("**Sucursal**")
sucursales = sorted(df["Branch"].unique())
sucursales_seleccionadas = []
for suc in sucursales:
    if st.sidebar.toggle(suc, value=True, key=f"suc_{suc}"):
        sucursales_seleccionadas.append(suc)

# Filtrar dataset
df_filtered = df[
    (df["Date"] >= pd.to_datetime(fecha_rango[0])) &
    (df["Date"] <= pd.to_datetime(fecha_rango[1])) &
    (df["Product line"].isin(categorias_seleccionadas))
]

if tipo_cliente_seleccionado != "Todos":
    df_filtered = df_filtered[df_filtered["Customer type"] == tipo_cliente_seleccionado]

if sucursales_seleccionadas:
    df_filtered = df_filtered[df_filtered["Branch"].isin(sucursales_seleccionadas)]
else:
    df_filtered = df_filtered[0:0]

# KPIs
ingreso_total = df_filtered["gross income"].sum()
ticket_promedio = df_filtered["Total"].mean()
cliente_counts = df_filtered["Customer type"].value_counts(normalize=True) * 100
miembros_pct = cliente_counts.get("Member", 0)
normales_pct = cliente_counts.get("Normal", 0)
producto_top = df_filtered["Product line"].value_counts().idxmax() if not df_filtered.empty else "N/A"
sucursal_top = df_filtered.groupby("Branch")["gross income"].sum().idxmax() if not df_filtered.empty else "N/A"

# KPIs visuales
st.markdown("## 📊 Indicadores Clave del Negocio")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("💵 Ingreso Total", f"${ingreso_total:,.0f}")
    st.metric("🧾 Ticket Promedio", f"${ticket_promedio:,.2f}")
with kpi2:
    st.metric("👤 % Clientes Miembros", f"{miembros_pct:.1f}%")
    st.metric("👥 % Clientes Normales", f"{normales_pct:.1f}%")
with kpi3:
    st.metric("🏆 Producto Más Vendido", producto_top)
    st.metric("🏬 Sucursal con + Ingreso", sucursal_top)

# Título
st.title("📈 Dashboard de Ventas - Supermercado")

# Crear grilla 2 columnas x 4 filas para gráficos
for fila in range(4):
    col1, col2 = st.columns(2)
    if fila == 0:
        with col1:
            st.subheader("Evolución de las Ventas Totales")
            ventas_diarias = df_filtered.groupby("Date")["Total"].sum().reset_index()
            fig1, ax1 = plt.subplots(figsize=(8, 3.5))
            sns.lineplot(data=ventas_diarias, x="Date", y="Total", ax=ax1)
            ax1.set_xlabel("Fecha")
            ax1.set_ylabel("Total Ventas")
            st.pyplot(fig1)
        with col2:
            st.subheader("Distribución de Calificaciones")
            fig2, ax2 = plt.subplots(figsize=(8, 3.5))
            sns.histplot(df_filtered["Rating"], bins=20, kde=True, ax=ax2)
            st.pyplot(fig2)

    elif fila == 1:
        with col1:
            st.subheader("Métodos de Pago Preferidos")
            payment_counts = df_filtered["Payment"].value_counts().reset_index()
            payment_counts.columns = ["Payment Method", "Count"]
            fig3, ax3 = plt.subplots(figsize=(8, 3.5))
            sns.barplot(data=payment_counts, x="Payment Method", y="Count", palette="viridis", ax=ax3)
            ax3.set_ylabel("Cantidad")
            st.pyplot(fig3)
        with col2:
            st.subheader("Ingresos por Línea de Producto")
            ingresos_por_categoria = df_filtered.groupby("Product line")["Total"].sum().sort_values(ascending=False).reset_index()
            fig4, ax4 = plt.subplots(figsize=(8, 3.5))
            sns.barplot(data=ingresos_por_categoria, x="Total", y="Product line", palette="mako", ax=ax4)
            st.pyplot(fig4)

    elif fila == 2:
        with col1:
            st.subheader("Gasto por Tipo de Cliente")
            fig5, ax5 = plt.subplots(figsize=(8, 3.5))
            sns.boxplot(data=df_filtered, x="Customer type", y="Total", palette="Set2", ax=ax5)
            st.pyplot(fig5)
        with col2:
            st.subheader("Relación entre Costo y Ganancia Bruta")
            fig6, ax6 = plt.subplots(figsize=(8, 3.5))
            sns.scatterplot(data=df_filtered, x="cogs", y="gross income", hue="Branch", palette="tab10", ax=ax6)
            st.pyplot(fig6)

    elif fila == 3:
        with col1:
            st.subheader("📌 Correlación de Variables Numéricas")
            fig7, ax7 = plt.subplots(figsize=(8, 4))
            numeric_df = df_filtered[["Unit price", "Quantity", "Total", "cogs", "gross income", "Rating"]]
            correlation = numeric_df.corr()
            sns.heatmap(correlation, annot=True, cmap="coolwarm", ax=ax7)
            st.pyplot(fig7)
        with col2:
            st.subheader("Ingreso Bruto por Sucursal y Línea de Producto")
            composition = df_filtered.groupby(["Branch", "Product line"])["gross income"].sum().reset_index()
            fig8, ax8 = plt.subplots(figsize=(8, 4))
            sns.barplot(data=composition, x="gross income", y="Product line", hue="Branch", dodge=True, ax=ax8)
            ax8.legend(title="Sucursal")
            st.pyplot(fig8)

# Visualización Avanzada en 3D
st.markdown("---")
st.title("📊 Visualización Avanzada en 3D")

# Mapear líneas de producto a L1, L2, ...
lineas = df_filtered["Product line"].unique()
linea_map = {v: f"L{i+1}" for i, v in enumerate(lineas)}
df_filtered["product_line_short"] = df_filtered["Product line"].map(linea_map)
product_map = {v: i for i, v in enumerate(df_filtered["product_line_short"].unique())}
df_filtered["product_num"] = df_filtered["product_line_short"].map(product_map)

# Mapeo de otras variables
branch_map = {k: i for i, k in enumerate(df_filtered["Branch"].unique())}
df_filtered["branch_num"] = df_filtered["Branch"].map(branch_map)
tipo_map = {k: i for i, k in enumerate(df_filtered["Customer type"].unique())}
df_filtered["tipo_num"] = df_filtered["Customer type"].map(tipo_map)
payment_map = {"Cash": 0, "Debit card": 1, "Credit card": 2}
df_filtered["payment_num"] = df_filtered["Payment"].map(payment_map)
df_filtered["date_ordinal"] = df_filtered["Date"].map(pd.Timestamp.toordinal)

# Crear nueva grilla: 2 columnas x 3 filas
for i in range(3):
    col1, col2 = st.columns(2)

    if i == 0:
        with col1:
            st.subheader("Precio vs Costo vs Ganancia")
            sample = df_filtered.sample(min(100, len(df_filtered)))
            fig9 = plt.figure(figsize=(8, 5))
            ax9 = fig9.add_subplot(111, projection='3d')
            ax9.plot_trisurf(sample["Unit price"], sample["cogs"], sample["gross income"], cmap='viridis', edgecolor='none')
            ax9.set_xlabel("Precio Unitario")
            ax9.set_ylabel("Costo")
            ax9.set_zlabel("Ganancia Bruta")
            st.pyplot(fig9)

        with col2:
            st.subheader("Sucursal vs Producto vs Venta")
            fig10 = plt.figure(figsize=(8, 5))
            ax10 = fig10.add_subplot(111, projection='3d')
            ax10.scatter(df_filtered["branch_num"], df_filtered["product_num"], df_filtered["Total"], c='orange')
            ax10.set_xlabel("Sucursal")
            ax10.set_ylabel("Producto")
            ax10.set_zlabel("Ventas")
            ax10.set_xticks(list(branch_map.values()))
            ax10.set_xticklabels(list(branch_map.keys()))
            ax10.set_yticks(list(product_map.values()))
            ax10.set_yticklabels(list(product_map.keys()), rotation=30, ha='right')
            st.pyplot(fig10)

    if i == 1:
        with col1:
            st.subheader("Tipo Cliente vs Producto vs Gasto")
            fig11 = plt.figure(figsize=(8, 5))
            ax11 = fig11.add_subplot(111, projection='3d')
            ax11.scatter(df_filtered["tipo_num"], df_filtered["product_num"], df_filtered["Total"], c='purple')
            ax11.set_xlabel("Tipo Cliente")
            ax11.set_ylabel("Producto")
            ax11.set_zlabel("Gasto")
            ax11.set_xticks(list(tipo_map.values()))
            ax11.set_xticklabels(list(tipo_map.keys()))
            ax11.set_yticks(list(product_map.values()))
            ax11.set_yticklabels(list(product_map.keys()), rotation=30, ha='right')
            st.pyplot(fig11)

        with col2:
            st.subheader("Fecha vs Producto vs Ventas")
            fig12 = plt.figure(figsize=(8, 5))
            ax12 = fig12.add_subplot(111, projection='3d')
            ax12.scatter(df_filtered["date_ordinal"], df_filtered["product_num"], df_filtered["Total"], c='teal')
            ax12.set_xlabel("Fecha")
            ax12.set_ylabel("Producto")
            ax12.set_zlabel("Ventas")
            st.pyplot(fig12)

    if i == 2:
        with col1:
            st.subheader("Método de Pago vs Total Venta")
            fig13 = plt.figure(figsize=(8, 5))
            ax13 = fig13.add_subplot(111, projection='3d')
            ax13.scatter(df_filtered["payment_num"], df_filtered["date_ordinal"], df_filtered["Total"], c='brown')
            ax13.set_xlabel("Método de Pago")
            ax13.set_ylabel("Fecha")
            ax13.set_zlabel("Total Venta")
            ax13.set_xticks(list(payment_map.values()))
            ax13.set_xticklabels(list(payment_map.keys()))
            st.pyplot(fig13)

        with col2:
            st.subheader("Ingreso Bruto vs Sucursal vs Línea de Producto")
            fig14 = plt.figure(figsize=(8, 5))
            ax14 = fig14.add_subplot(111, projection='3d')
            ax14.scatter(df_filtered["branch_num"], df_filtered["product_num"], df_filtered["gross income"], c='navy')
            ax14.set_xlabel("Sucursal")
            ax14.set_ylabel("Producto")
            ax14.set_zlabel("Ingreso Bruto")
            ax14.set_xticks(list(branch_map.values()))
            ax14.set_xticklabels(list(branch_map.keys()))
            ax14.set_yticks(list(product_map.values()))
            ax14.set_yticklabels(list(product_map.keys()), rotation=30, ha='right')
            st.pyplot(fig14)

# Footer
st.markdown("---")
st.title("🧠 **Análisis final:**")
st.markdown("   Este dashboard ofrece una visión segmentada y dinámica del desempeño del supermercado. "
            " La interactividad de los dashboards potencia la toma de decisiones de los equipos al permitir filtrar, visualizar y profundizar en los "
            " datos de manera inmediata e intuitiva, identificar rápidamente datos clave en tiempo real, fomentar la democratización de la información "
            " y genera el feedback de uso que impulsa la optimización continua de las organizaciones."
            " En una cadena de tiendas de conveniencia, el gráfico de barras + líneas permite comparar "
            " de un vistazo las ventas absolutas por periodo (barras) y la evolución de una métrica clave,"
            " como número de transacciones o ticket promedio (línea), sobre el mismo eje temporal."
            " Así se correlacionan las ventas con cambios en el comportamiento del cliente de forma inmediata y sin recurrir a dos gráficos separados."
            " Usando cuatro librerías: Pandas, Streamlit, Matplotlib y Seaborn se crean filtros que permiten una visualización avanzada"
            " e interactiva de los datos, adaptada automáticamente a la configuración seleccionada."
            " Gracias al enfoque presentado en Visualización de Información en la Era del Big Data, "
            " se facilita una presentación más clara, estructurada y comprensible de los datos, lo que permite "
            " articular una postura bien fundamentada frente al contenido teórico expuesto. La visualización no solo organiza la información, "
            " sino que también invita a cuestionarla, enriqueciendo el análisis y mejorando su coherencia.")
st.markdown("---")
st.title("🧠 ***Desarrollado por Grupo 31 del Diplomado de Big Data & Machine Learning:***")
st.markdown(" Ignacio Javier Cassinelli Hernandez   - "
            "Jose Francisco Javier Echeverria Virot   - "
            "Marta Viviana Garrido Calderon   - "
            "Daniel Esteban Sobarzo Carrasco")
