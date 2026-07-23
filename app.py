import streamlit as st
import json
from pathlib import Path
from database.database import initialize_database
from views.deliverables import deliverables_page
from components.sidebar import show_sidebar
from components.database_backup import render_database_backup
from views.dashboard import dashboard
from views.cronograma import cronograma_page
from views.documentos import documentos_page
from views.fluxo_projeto import fluxo_projeto_page
from views.reunioes import meetings_page
from views.work_hours import (
    work_hours_page,
)

# -------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------------

st.set_page_config(
    page_title="BECCS Well Baseline Manager",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
    /* Esconde o menu de três pontos */
    #MainMenu {
        visibility: hidden;
    }

    /* Esconde Share, GitHub, Edit e outros botões da direita */
    [data-testid="stToolbarActions"] {
        display: none !important;
    }

    /* Esconde o botão de deploy, caso apareça */
    [data-testid="stAppDeployButton"] {
        display: none !important;
    }

    /* Esconde indicadores de status/conexão */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Mantém o cabeçalho transparente */
    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Garante que a seta de reabrir a sidebar continue visível */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
initialize_database()
# -------------------------------------------------------
# CARREGA CSS
# -------------------------------------------------------

css_path = Path("assets/style.css")

if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------------------------------------
# CARREGA CONFIGURAÇÕES
# -------------------------------------------------------

config_path = Path("data/config.json")

if config_path.exists():
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    config = {}

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

selected = show_sidebar()
render_database_backup()
# -------------------------------------------------------
# PÁGINAS
# -------------------------------------------------------

if selected == "Dashboard":
    dashboard()

elif selected == "Tarefas":

    deliverables_page()

elif selected == "Cronograma":
    cronograma_page()

elif selected == "Equipe":

    st.title("👥 Equipe")

    st.info("Em desenvolvimento")

elif selected == "Documentos":
    documentos_page()

elif selected == "Fluxo do Projeto":
    fluxo_projeto_page()

elif selected == "Riscos":

    st.title("⚠️ Riscos")

    st.info("Em desenvolvimento")

elif selected == "Reuniões":

    meetings_page()

elif selected == "Horas trabalhadas":
    work_hours_page()

elif selected == "Configurações":

    st.title("⚙️ Configurações")

    st.info("Em desenvolvimento")
