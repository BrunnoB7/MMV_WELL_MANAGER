from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from database.database import get_connection
from integrations.ms_project import (
    get_project_info,
    import_project_to_database,
)


def load_schedule():
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM schedule
        ORDER BY task_id
        """,
        conn,
    )

    conn.close()

    return df


def cronograma_page():
    st.title("📅 Cronograma")
    st.caption("Sincronização com Microsoft Project")

    info = get_project_info()

    c1, c2, c3 = st.columns(3)

    c1.metric("Atividades", info["tasks"])
    c2.metric("Marcos", info["milestones"])
    c3.metric(
        "Última sincronização",
        info["last_import"] or "Nunca",
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Importar Excel exportado do Microsoft Project",
        type=["xlsx"],
        help="Selecione o arquivo Excel exportado pelo Microsoft Project.",
    )

    col_import, col_fixed = st.columns(2)

    with col_import:
        if st.button(
            "Importar arquivo selecionado",
            use_container_width=True,
            disabled=uploaded_file is None,
        ):
            try:
                result = import_project_to_database(uploaded_file)

                st.success(
                    f"Importação concluída: "
                    f"{result['tasks']} atividades, "
                    f"{result['deliverables']} deliverables e "
                    f"{result['milestones']} marcos."
                )

                st.rerun()

            except Exception as error:
                st.error(str(error))

    with col_fixed:
        if st.button(
            "Importar arquivo da pasta data/project",
            use_container_width=True,
        ):
            try:
                result = import_project_to_database()

                st.success(
                    f"Importação concluída: "
                    f"{result['tasks']} atividades."
                )

                st.rerun()

            except Exception as error:
                st.error(str(error))

    st.divider()

    schedule = load_schedule()

    if schedule.empty:
        st.info("Nenhum cronograma importado.")
        return

    schedule["start_date"] = pd.to_datetime(
        schedule["start_date"],
        errors="coerce",
    )

    schedule["finish_date"] = pd.to_datetime(
        schedule["finish_date"],
        errors="coerce",
    )

    valid_schedule = schedule.dropna(
        subset=["start_date", "finish_date"]
    ).copy()

    disciplines = sorted(
        schedule["discipline"].dropna().unique().tolist()
    )

    selected_disciplines = st.multiselect(
        "Filtrar disciplinas",
        disciplines,
        default=disciplines,
    )

    if selected_disciplines:
        valid_schedule = valid_schedule[
            valid_schedule["discipline"].isin(selected_disciplines)
        ]

    show_summary = st.checkbox(
        "Exibir tarefas-resumo",
        value=True,
    )

    if not show_summary:
        valid_schedule = valid_schedule[
            valid_schedule["summary"] == 0
        ]

    st.subheader("Gráfico de Gantt")

    if valid_schedule.empty:
        st.warning("Nenhuma atividade encontrada para os filtros.")
    else:
        gantt = px.timeline(
            valid_schedule,
            x_start="start_date",
            x_end="finish_date",
            y="task_name",
            color="discipline",
            hover_data={
                "progress": True,
                "responsible": True,
                "start_date": True,
                "finish_date": True,
                "task_name": False,
            },
        )

        gantt.update_yaxes(
            autorange="reversed",
            title=None,
        )

        gantt.update_xaxes(title=None)

        gantt.update_layout(
            height=max(500, len(valid_schedule) * 28),
            legend_title_text="Disciplina",
            margin=dict(l=10, r=10, t=30, b=10),
        )

        gantt.add_vline(
            x=pd.Timestamp(date.today()).timestamp() * 1000,
            line_dash="dash",
            annotation_text="Hoje",
        )

        st.plotly_chart(
            gantt,
            use_container_width=True,
        )

    st.subheader("Marcos")

    milestones = schedule[schedule["milestone"] == 1][
        [
            "task_name",
            "finish_date",
            "progress",
            "responsible",
            "discipline",
        ]
    ]

    if milestones.empty:
        st.info("Nenhum marco encontrado.")
    else:
        st.dataframe(
            milestones,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Atividades do cronograma")

    table = schedule[
        [
            "task_id",
            "task_name",
            "discipline",
            "start_date",
            "finish_date",
            "progress",
            "responsible",
        ]
    ].copy()

    table.columns = [
        "ID",
        "Atividade",
        "Disciplina",
        "Início",
        "Fim",
        "Progresso (%)",
        "Responsável",
    ]

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )