from datetime import date

import streamlit as st

from config.team import TEAM_MEMBERS
from services.work_hours_service import (
    WorkHoursService,
)


def format_hours(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "0h"

    if value.is_integer():
        return f"{int(value)}h"

    return (
        f"{value:.1f}"
        .replace(".", ",")
        + "h"
    )


def format_date(value):
    if not value:
        return "-"

    try:
        return date.fromisoformat(
            str(value)
        ).strftime("%d/%m/%Y")
    except ValueError:
        return str(value)


@st.dialog(
    "Registrar horas trabalhadas",
    width="large",
)
def register_work_hours_dialog(
    deliverable
):
    deliverable_id = deliverable["id"]
    deliverable_title = (
        deliverable["title"]
        or "Sem título"
    )

    st.caption("Deliverable")
    st.write(f"**{deliverable_title}**")

    with st.form(
        f"register_hours_{deliverable_id}"
    ):
        col1, col2, col3 = st.columns(3)

        with col1:
            collaborator = st.selectbox(
                "Colaborador",
                options=TEAM_MEMBERS,
            )

        with col2:
            worked_hours = st.number_input(
                "Horas trabalhadas",
                min_value=0.25,
                max_value=200.0,
                value=1.0,
                step=0.25,
                format="%.2f",
            )

        with col3:
            work_date = st.date_input(
                "Data",
                value=date.today(),
                format="DD/MM/YYYY",
            )

        description = st.text_area(
            "Descrição da atividade",
            placeholder=(
                "Ex.: revisão do relatório, "
                "análise técnica ou elaboração "
                "de documento."
            ),
            height=100,
        )

        submitted = st.form_submit_button(
            "Registrar horas",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            try:
                WorkHoursService.register_work_log(
                    deliverable_id=deliverable_id,
                    collaborator=collaborator,
                    worked_hours=worked_hours,
                    work_date=work_date,
                    description=description,
                )

                st.session_state[
                    "work_hours_registered"
                ] = True

                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    "Erro ao registrar horas: "
                    f"{error}"
                )

    st.divider()
    st.markdown("#### Lançamentos existentes")

    logs = (
        WorkHoursService
        .get_deliverable_logs(
            deliverable_id
        )
    )

    if not logs:
        st.info(
            "Nenhuma hora registrada para "
            "este deliverable."
        )
        return

    for work_log in logs:
        with st.container(border=True):
            info_col, delete_col = (
                st.columns([5, 1])
            )

            with info_col:
                st.markdown(
                    (
                        f"**{work_log['collaborator']}** "
                        f"— {format_hours(work_log['worked_hours'])}"
                    )
                )

                st.caption(
                    format_date(
                        work_log["work_date"]
                    )
                )

                if work_log.get(
                    "description"
                ):
                    st.write(
                        work_log["description"]
                    )

            with delete_col:
                if st.button(
                    "🗑️",
                    key=(
                        "delete_work_log_"
                        f"{work_log['id']}"
                    ),
                    help="Excluir lançamento",
                    use_container_width=True,
                ):
                    WorkHoursService.delete_work_log(
                        work_log["id"]
                    )

                    st.rerun()
