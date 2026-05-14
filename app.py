import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date
from mensaje import enviar_whatsapp
from PIL import Image
from streamlit_option_menu import option_menu

# -----------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------
st.set_page_config(
    page_title="Sistema de Cobranzas",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------
# CSS PREMIUM
# -----------------------------------------------------
st.markdown("""
<style>

/* Fondo principal */
.stApp{
    background-color: #0E1117;
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#0f172a,#111827);
    border-right: 1px solid #1f2937;
}

/* Títulos */
h1, h2, h3{
    color: white !important;
    font-weight: 700;
}

/* Cards métricas */
[data-testid="metric-container"]{
    background: linear-gradient(145deg,#1e293b,#0f172a);
    border: 1px solid #334155;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}

/* Hover cards */
[data-testid="metric-container"]:hover{
    transform: translateY(-5px);
    transition: 0.3s ease;
}

/* Botones */
.stButton>button{
    background: linear-gradient(90deg,#10b981,#059669);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: bold;
    padding: 10px 18px;
}

/* Hover botones */
.stButton>button:hover{
    background: linear-gradient(90deg,#059669,#047857);
    color: white;
}

/* Dataframes */
[data-testid="stDataFrame"]{
    border-radius: 15px;
    overflow: hidden;
}

/* Inputs */
.stTextInput input,
.stNumberInput input{
    border-radius: 10px;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"]{
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# ARCHIVO
# -----------------------------------------------------
ARCHIVO = "cobranzas.csv"

if not os.path.exists(ARCHIVO):
    st.error("No se encontró cobranzas.csv")
    st.stop()

# -----------------------------------------------------
# LOGO
# -----------------------------------------------------
logo = Image.open("logo.png")

# -----------------------------------------------------
# CARGAR DATA
# -----------------------------------------------------
@st.cache_data
def cargar_data():
    return pd.read_csv(ARCHIVO)

def guardar_data(df):
    df.to_csv(ARCHIVO, index=False)

# -----------------------------------------------------
# LOGIN
# -----------------------------------------------------
def login():

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.image(logo, width=180)

        st.markdown("<h1 style='text-align:center;'>Sistema Inteligente de Cobranzas</h1>", unsafe_allow_html=True)

        st.markdown("### Acceso Seguro")

        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")

        if st.button("Ingresar", use_container_width=True):

            if usuario == "admin" and clave == "1234":
                st.session_state["login"] = True
                st.rerun()

            else:
                st.error("Credenciales incorrectas")

# -----------------------------------------------------
# DASHBOARD
# -----------------------------------------------------
def dashboard(df):

    st.markdown("# 📊 Dashboard Ejecutivo")

    deuda_total = df["Monto_Deuda"].sum()
    recuperado = df["Monto_Pagado"].sum()
    pendiente = deuda_total - recuperado
    clientes_riesgo = len(df[df["Estado_Pago"] == "Pendiente"])

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("💰 Deuda Total", f"S/ {deuda_total:,.0f}")
    c2.metric("✅ Recuperado", f"S/ {recuperado:,.0f}")
    c3.metric("⚠️ Pendiente", f"S/ {pendiente:,.0f}")
    c4.metric("🚨 Clientes Riesgo", clientes_riesgo)

    st.markdown("##")

    col1, col2 = st.columns(2)

    # BARRAS
    region = df.groupby("Region")["Monto_Deuda"].sum().reset_index()

    fig1 = px.bar(
        region,
        x="Region",
        y="Monto_Deuda",
        color="Monto_Deuda",
        text_auto=True,
        template="plotly_dark"
    )

    fig1.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font_color="white",
        height=450
    )

    col1.plotly_chart(fig1, use_container_width=True)

    # DONA
    estado = df.groupby("Estado_Pago").size().reset_index(name="Cantidad")

    fig2 = px.pie(
        estado,
        names="Estado_Pago",
        values="Cantidad",
        hole=0.6,
        template="plotly_dark"
    )

    fig2.update_layout(
        paper_bgcolor="#0E1117",
        font_color="white",
        height=450
    )

    col2.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------
# MOROSOS
# -----------------------------------------------------
def morosos(df):

    st.title("⚠️ Clientes Morosos")

    morosos = df[df["Estado_Pago"] == "Pendiente"]

    st.dataframe(
        morosos,
        use_container_width=True
    )

# -----------------------------------------------------
# FILTROS
# -----------------------------------------------------
def filtros(df):

    st.title("🔍 Filtrar Clientes")

    c1, c2, c3 = st.columns(3)

    with c1:
        region = st.selectbox(
            "Región",
            ["Todos"] + list(df["Region"].unique())
        )

    with c2:
        estado = st.selectbox(
            "Estado",
            ["Todos"] + list(df["Estado_Pago"].unique())
        )

    with c3:
        buscar = st.text_input("Buscar Cliente")

    if region != "Todos":
        df = df[df["Region"] == region]

    if estado != "Todos":
        df = df[df["Estado_Pago"] == estado]

    if buscar:
        df = df[df["Cliente"].str.contains(buscar, case=False)]

    st.dataframe(df, use_container_width=True)

# -----------------------------------------------------
# REGISTRAR PAGO
# -----------------------------------------------------
def registrar_pago(df):

    st.title("💵 Registrar Pago")

    cliente = st.selectbox(
        "Cliente",
        df["Cliente"].unique()
    )

    monto = st.number_input(
        "Monto",
        min_value=0.0
    )

    if st.button("Registrar Pago"):

        idx = df[df["Cliente"] == cliente].index[0]

        df.loc[idx,"Monto_Pagado"] += monto
        df.loc[idx,"Fecha_Pago"] = str(date.today())

        if df.loc[idx,"Monto_Pagado"] >= df.loc[idx,"Monto_Deuda"]:
            df.loc[idx,"Estado_Pago"] = "Pagado"

        guardar_data(df)

        st.success("Pago registrado correctamente")

# -----------------------------------------------------
# RECORDATORIOS
# -----------------------------------------------------
def recordatorios(df):

    st.title("📩 Recordatorios Automáticos")

    pendientes = df[df["Estado_Pago"] == "Pendiente"]

    st.dataframe(
        pendientes[
            ["Cliente","Telefono","Monto_Deuda","Fecha_Vencimiento"]
        ],
        use_container_width=True
    )

    if st.button("📲 Enviar Recordatorios"):

        numeros = ["51926340701", "51955564417"]

        for i in range(min(2, len(pendientes))):

            fila = pendientes.iloc[i]

            nombre = fila["Cliente"]
            deuda = fila["Monto_Deuda"]

            try:
                atraso = (
                    pd.Timestamp.today() -
                    pd.to_datetime(fila["Fecha_Vencimiento"])
                ).days

            except:
                atraso = 0

            for num in numeros:
                enviar_whatsapp(nombre, num, deuda, atraso)

        st.success("WhatsApp abiertos correctamente")

# -----------------------------------------------------
# HISTORIAL
# -----------------------------------------------------
def historial(df):

    st.title("📜 Historial de Pagos")

    pagos = df[df["Monto_Pagado"] > 0]

    st.dataframe(
        pagos,
        use_container_width=True
    )

# -----------------------------------------------------
# EDITAR CLIENTE
# -----------------------------------------------------
def editar(df):

    st.title("✏️ Editar Cliente")

    cliente = st.selectbox(
        "Cliente",
        df["Cliente"].unique()
    )

    idx = df[df["Cliente"] == cliente].index[0]

    deuda = st.number_input(
        "Nueva deuda",
        value=float(df.loc[idx,"Monto_Deuda"])
    )

    if st.button("Guardar Cambios"):

        df.loc[idx,"Monto_Deuda"] = deuda

        guardar_data(df)

        st.success("Cliente actualizado")

# -----------------------------------------------------
# EXPORTAR
# -----------------------------------------------------
def exportar(df):

    st.title("⬇️ Exportar Reporte")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Descargar CSV",
        csv,
        "reporte.csv",
        "text/csv"
    )

# -----------------------------------------------------
# MAIN
# -----------------------------------------------------
if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:

    login()

else:

    df = cargar_data()

    # SIDEBAR
    with st.sidebar:

        st.image(logo, width=180)

        st.markdown("## Sistema de Cobranza")

        if st.button("Cerrar Sesión", use_container_width=True):

            st.session_state["login"] = False
            st.rerun()

        menu = option_menu(
            menu_title="",
            options=[
                "Dashboard",
                "Clientes Morosos",
                "Filtrar Clientes",
                "Registrar Pago",
                "Recordatorios",
                "Historial",
                "Editar Cliente",
                "Exportar CSV"
            ],
            icons=[
                "speedometer2",
                "people-fill",
                "search",
                "cash-coin",
                "bell-fill",
                "clock-history",
                "pencil-square",
                "download"
            ],
            default_index=0,
            styles={
                "container": {
                    "padding": "5!important",
                    "background-color": "#0f172a",
                },

                "icon": {
                    "color": "#10b981",
                    "font-size": "18px"
                },

                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin":"5px",
                    "--hover-color": "#1e293b",
                    "border-radius": "10px",
                },

                "nav-link-selected": {
                    "background-color": "#10b981",
                },
            }
        )

    # MENÚ
    if menu == "Dashboard":
        dashboard(df)

    elif menu == "Clientes Morosos":
        morosos(df)

    elif menu == "Filtrar Clientes":
        filtros(df)

    elif menu == "Registrar Pago":
        registrar_pago(df)

    elif menu == "Recordatorios":
        recordatorios(df)

    elif menu == "Historial":
        historial(df)

    elif menu == "Editar Cliente":
        editar(df)

    elif menu == "Exportar CSV":
        exportar(df)