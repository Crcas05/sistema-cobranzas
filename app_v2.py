# =========================================================
# SISTEMA EMPRESARIAL DE COBRANZAS
# app_v2.py
# =========================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image
import os

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Sistema de Cobranzas",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

[data-testid="stAppViewContainer"]{
    background-color:#f4f6f9;
}

[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#0b6b57,#075e54);
    width:290px !important;
}

.block-container{
    padding-top:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

/* TITULO */

.main-title{
    font-size:54px;
    font-weight:800;
    color:#0f172a;
    margin-bottom:25px;
}

/* SIDEBAR */

.sidebar-title{
    color:white;
    font-size:20px;
    font-weight:700;
    text-align:center;
    margin-top:10px;
    margin-bottom:20px;
}

/* KPI */

.kpi-card{
    background:white;
    border-radius:18px;
    padding:20px;
    box-shadow:0 2px 10px rgba(0,0,0,0.08);
    border:1px solid #e5e7eb;
    height:130px;
}

.kpi-flex{
    display:flex;
    align-items:center;
    gap:18px;
}

.kpi-icon{
    width:65px;
    height:65px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:34px;
    color:white;
}

.icon-green{
    background:#22c55e;
}

.icon-blue{
    background:#2196f3;
}

.icon-yellow{
    background:#f59e0b;
}

.icon-red{
    background:#ef4444;
}

.kpi-title{
    font-size:20px;
    font-weight:600;
    color:#475569;
}

.kpi-value{
    font-size:34px;
    font-weight:800;
    color:#0f172a;
}

/* SECCIONES */

.section-card{
    background:white;
    border-radius:18px;
    padding:18px;
    box-shadow:0 2px 10px rgba(0,0,0,0.06);
    margin-top:20px;
}

.section-title{
    font-size:22px;
    font-weight:700;
    color:#0f172a;
    margin-bottom:10px;
}

/* TABLAS */

.custom-table{
    width:100%;
    border-collapse:collapse;
}

.custom-table th{
    text-align:left;
    background:#f8fafc;
    color:#334155;
    padding:12px;
    font-size:15px;
}

.custom-table td{
    padding:12px;
    border-bottom:1px solid #e2e8f0;
    color:#0f172a;
    font-size:15px;
}

.estado-vencido{
    color:#ef4444;
    font-weight:700;
}

.estado-porvencer{
    color:#16a34a;
    font-weight:700;
}

.riesgo-alto{
    color:#ef4444;
    font-weight:700;
}

.riesgo-medio{
    color:#f59e0b;
    font-weight:700;
}

.riesgo-bajo{
    color:#16a34a;
    font-weight:700;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA
# =========================================================

ARCHIVO = "cobranzas_empresarial_80k.csv"

if not os.path.exists(ARCHIVO):
    st.error("No existe el CSV")
    st.stop()

@st.cache_data
def cargar_data():

    df = pd.read_csv(
        ARCHIVO,
        sep=";"
    )

    df.columns = df.columns.str.strip()

    df["Fecha_Desembolso"] = pd.to_datetime(
        df["Fecha_Desembolso"],
        dayfirst=True,
        errors="coerce"
    )

    df["Fecha_Vencimiento"] = pd.to_datetime(
        df["Fecha_Vencimiento"],
        dayfirst=True,
        errors="coerce"
    )

    df["Fecha_Ultimo_Pago"] = pd.to_datetime(
        df["Fecha_Ultimo_Pago"],
        dayfirst=True,
        errors="coerce"
    )

    return df

df = cargar_data()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    logo = Image.open("logo.png")
    st.image(logo, width=140)

    st.markdown(
        "<div class='sidebar-title'>Sistema de Cobranza</div>",
        unsafe_allow_html=True
    )

    menu = option_menu(
        menu_title=None,
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
            "grid-fill",
            "people-fill",
            "search",
            "wallet2",
            "bell-fill",
            "clock-history",
            "pencil-square",
            "download"
        ],
        default_index=0,
        styles={
            "container":{
                "padding":"0!important",
                "background-color":"transparent",
                "border":"none"
            },
            "icon":{
                "color":"white",
                "font-size":"18px"
            },
            "nav-link":{
                "font-size":"18px",
                "text-align":"left",
                "margin":"6px 0",
                "padding":"14px",
                "border-radius":"12px",
                "color":"white",
                "background-color":"transparent"
            },
            "nav-link-selected":{
                "background-color":"#1fc98a",
                "color":"white",
                "font-weight":"700"
            }
        }
    )

# =========================================================
# DASHBOARD
# =========================================================

if menu == "Dashboard":

    st.markdown(
        "<div class='main-title'>Dashboard</div>",
        unsafe_allow_html=True
    )

    clientes_activos = df["ID_Cliente"].nunique()

    total_cobrar = df["Saldo_Pendiente"].sum()

    vencidos = df[df["Estado_Pago"] == "Pendiente"]["Saldo_Pendiente"].sum()

    clientes_riesgo = len(
        df[df["Nivel_Riesgo"] == "Alto"]
    )

    c1,c2,c3,c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-flex">
                <div class="kpi-icon icon-green">👥</div>
                <div>
                    <div class="kpi-title">Clientes Activos</div>
                    <div class="kpi-value">{clientes_activos:,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-flex">
                <div class="kpi-icon icon-blue">💲</div>
                <div>
                    <div class="kpi-title">Total por Cobrar</div>
                    <div class="kpi-value">S/ {total_cobrar:,.0f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-flex">
                <div class="kpi-icon icon-yellow">⏰</div>
                <div>
                    <div class="kpi-title">Vencidos</div>
                    <div class="kpi-value">S/ {vencidos:,.0f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-flex">
                <div class="kpi-icon icon-red">❗</div>
                <div>
                    <div class="kpi-title">Clientes en Riesgo</div>
                    <div class="kpi-value">{clientes_riesgo:,}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # GRAFICOS
    # =====================================================

    col1,col2 = st.columns(2)

    # DONUT

    with col1:

        st.markdown("""
        <div class='section-card'>
        <div class='section-title'>
        Cartera por Vencer vs Vencida
        </div>
        """, unsafe_allow_html=True)

        por_vencer = len(
            df[df["Estado_Pago"] == "Pagado"]
        )

        vencida = len(
            df[df["Estado_Pago"] == "Pendiente"]
        )

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Vencida","Por Vencer"],
                    values=[vencida,por_vencer],
                    hole=0.58,
                    marker=dict(
                        colors=["#ef4444","#22c55e"]
                    ),
                    textinfo="percent",
                    textfont_size=22
                )
            ]
        )

        fig.update_layout(
            height=420,
            paper_bgcolor="white",
            plot_bgcolor="white",
            legend=dict(
                font=dict(
                    size=18,
                    color="#111827"
                )
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("""
        <div style='padding-left:30px;padding-bottom:20px;'>

        <p style='font-size:18px;color:#22c55e;font-weight:700;'>
        ● Por Vencer
        </p>

        <p style='font-size:18px;color:#ef4444;font-weight:700;'>
        ● Vencida
        </p>

        </div>
        </div>
        """, unsafe_allow_html=True)

    # LINEA

    with col2:

        st.markdown("""
        <div class='section-card'>
        <div class='section-title'>
        Cobranzas por Mes
        </div>
        """, unsafe_allow_html=True)

        serie = df.groupby("Region")["Monto_Deuda"].sum().reset_index()

        fig2 = px.line(
            serie,
            x="Region",
            y="Monto_Deuda",
            markers=True
        )

        fig2.update_traces(
            line_color="#16a34a",
            line_width=4,
            marker=dict(
                size=10,
                color="#16a34a"
            )
        )

        fig2.update_layout(
            height=420,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(
                size=15,
                color="#111827"
            ),
            xaxis=dict(
                tickfont=dict(size=14,color="#111827")
            ),
            yaxis=dict(
                tickfont=dict(size=14,color="#111827")
            ),
            showlegend=False
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # TABLAS
    # =====================================================

    c5,c6 = st.columns(2)

    # PROXIMOS PAGOS

    with c5:

        st.markdown("""
        <div class='section-card'>
        <div class='section-title'>
        Próximos Pagos
        </div>
        """, unsafe_allow_html=True)

        pagos = df.sort_values(
            "Fecha_Vencimiento"
        ).head(8)

        html_pagos = """
        <table class='custom-table'>
        <tr>
            <th>Cliente</th>
            <th>Monto</th>
            <th>Vencimiento</th>
            <th>Estado</th>
        </tr>
        """

        for _,row in pagos.iterrows():

            estado = "Vencido"

            clase = "estado-vencido"

            if row["Dias_Atraso"] <= 0:
                estado = "Por Vencer"
                clase = "estado-porvencer"

            html_pagos += f"""
            <tr>
                <td>{row['Nombre_Completo']}</td>
                <td>S/ {row['Saldo_Pendiente']:,.0f}</td>
                <td>{row['Fecha_Vencimiento'].strftime('%d/%m/%Y')}</td>
                <td class='{clase}'>{estado}</td>
            </tr>
            """

        html_pagos += "</table>"

        st.markdown(
            html_pagos,
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # CLIENTES EN RIESGO

    with c6:

        st.markdown("""
        <div class='section-card'>
        <div class='section-title'>
        Clientes en Riesgo
        </div>
        """, unsafe_allow_html=True)

        riesgo = df.head(8)

        html_riesgo = """
        <table class='custom-table'>
        <tr>
            <th>Cliente</th>
            <th>Estado</th>
        </tr>
        """

        for _,row in riesgo.iterrows():

            nivel = row["Nivel_Riesgo"]

            clase = "riesgo-bajo"

            if nivel == "Alto":
                clase = "riesgo-alto"

            elif nivel == "Medio":
                clase = "riesgo-medio"

            html_riesgo += f"""
            <tr>
                <td>{row['Nombre_Completo']}</td>
                <td class='{clase}'>
                    Riesgo {nivel}
                </td>
            </tr>
            """

        html_riesgo += "</table>"

        st.markdown(
            html_riesgo,
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)