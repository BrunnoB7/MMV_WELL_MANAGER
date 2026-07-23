import streamlit as st
from streamlit_option_menu import option_menu


def show_sidebar():

    with st.sidebar:

        st.image('data/logo_syngular_png.png')

        selected = option_menu(
            menu_title=None,

            options=[
                "Dashboard",
                "Fluxo do Projeto",
                "Tarefas",
                "Cronograma",
                "Documentos",
                # "Equipe",
                # "Riscos",
                "Reuniões",
                "Horas trabalhadas",
                # "Indicadores",
                # "Administração",
            ],

            icons=[
                "speedometer2",
                "diagram-3",
                "clipboard-check",
                "calendar3",
                "folder",
                # "people",
                # "exclamation-triangle",
                "journal-text",
                "clock-history",
                # "graph-up",
                # "gear",
            ],

            default_index=0,

            styles={
                "container": {
                    "padding": "8px",
                    "background-color": "#202124",
                    "border-radius": "12px",
                },

                "icon": {
                    "color": "#D32F2F",
                    "font-size": "20px",
                },

                "nav-link": {
                    "color": "#FFFFFF",
                    "font-size": "16px",
                    "font-weight": "500",
                    "text-align": "left",
                    "margin": "4px 0",
                    "padding": "12px 14px",
                    "border-radius": "8px",
                    "--hover-color": "#3A3B3F",
                },

                "nav-link-selected": {
                    "background-color": "#B71C1C",
                    "color": "#FFFFFF",
                    "font-weight": "700",
                },
            },
        )

        st.markdown(
            """
            <div style="
                margin-top: 24px;
                padding-top: 14px;
                border-top: 1px solid #555555;
                text-align: center;
                color: #AFAFAF;
                font-size: 12px;
            ">
                BECCS Baseline Manager<br>
                Versão 1.0
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected
