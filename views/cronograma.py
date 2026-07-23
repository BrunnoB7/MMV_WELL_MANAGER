import calendar
from datetime import date, datetime

import pandas as pd
import streamlit as st

from database.database import get_connection
from services.dashboard_service import DashboardService
from services.meeting_service import MeetingService


MONTH_NAMES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

WEEKDAY_NAMES = [
    "Seg",
    "Ter",
    "Qua",
    "Qui",
    "Sex",
    "Sáb",
    "Dom",
]


def load_schedule_css():
    st.markdown(
        """
        <style>
            .schedule-header {
                padding: 22px 26px;
                border-radius: 15px;
                margin-bottom: 20px;
                background: linear-gradient(
                    135deg,
                    rgba(15, 52, 96, 0.96),
                    rgba(16, 86, 82, 0.90)
                );
                border: 1px solid rgba(128, 128, 128, 0.18);
            }

            .schedule-header h1 {
                margin: 0;
                color: white;
                font-size: 1.9rem;
            }

            .schedule-header p {
                margin: 6px 0 0 0;
                color: rgba(255, 255, 255, 0.82);
            }

            .calendar-weekday {
                text-align: center;
                font-size: 0.78rem;
                font-weight: 650;
                opacity: 0.65;
                padding: 5px 0 8px 0;
            }

            .calendar-legend {
                display: flex;
                flex-wrap: wrap;
                gap: 14px;
                margin: 8px 0 15px 0;
                font-size: 0.80rem;
                opacity: 0.78;
            }

            .calendar-legend-item {
                display: flex;
                align-items: center;
                gap: 5px;
            }

            .activity-card {
                padding: 14px 16px;
                margin-bottom: 10px;
                border: 1px solid rgba(128, 128, 128, 0.18);
                border-left: 4px solid #1565C0;
                border-radius: 10px;
                background: rgba(21, 101, 192, 0.05);
            }

            .activity-card-title {
                font-size: 0.98rem;
                font-weight: 680;
                margin-bottom: 6px;
            }

            .activity-card-details {
                font-size: 0.81rem;
                line-height: 1.55;
                opacity: 0.76;
            }

            .final-date-card {
                padding: 14px 16px;
                border: 1px solid rgba(220, 38, 38, 0.22);
                border-left: 4px solid #DC2626;
                border-radius: 10px;
                background: rgba(220, 38, 38, 0.06);
                margin-bottom: 15px;
            }

            .final-date-title {
                font-size: 0.88rem;
                font-weight: 700;
                color: #DC2626;
            }

            .final-date-value {
                font-size: 1.35rem;
                font-weight: 750;
                margin-top: 3px;
            }

            .selected-date-title {
                font-size: 1.08rem;
                font-weight: 680;
                margin-bottom: 12px;
            }

            div[data-testid="stButton"] > button {
                min-height: 52px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def parse_database_date(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    text = str(value).strip()

    if not text:
        return None

    accepted_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for date_format in accepted_formats:
        try:
            return datetime.strptime(
                text,
                date_format,
            ).date()

        except ValueError:
            continue

    try:
        return pd.to_datetime(
            text,
            errors="raise",
        ).date()

    except (ValueError, TypeError):
        return None


def format_date(value):
    parsed_date = parse_database_date(value)

    if parsed_date is None:
        return "-"

    return parsed_date.strftime("%d/%m/%Y")


def load_deliverables_with_deadline():
    query = """
        SELECT
            id,
            title,
            discipline,
            status,
            progress,
            manager,
            deadline,
            priority
        FROM deliverables
        WHERE deadline IS NOT NULL
          AND TRIM(deadline) <> ''
        ORDER BY
            deadline ASC,
            title ASC
    """

    connection = get_connection()

    try:
        rows = connection.execute(query).fetchall()

        deliverables = []

        for row in rows:
            item = dict(row)
            item["parsed_deadline"] = parse_database_date(
                item.get("deadline")
            )

            if item["parsed_deadline"] is not None:
                deliverables.append(item)

        return deliverables

    finally:
        connection.close()


def group_deliverables_by_date(deliverables):
    grouped = {}

    for deliverable in deliverables:
        deadline = deliverable["parsed_deadline"]

        if deadline not in grouped:
            grouped[deadline] = []

        grouped[deadline].append(deliverable)

    return grouped


def initialize_calendar_state(
    deliverables,
    project_end_date,
):
    if "schedule_selected_date" not in st.session_state:
        st.session_state.schedule_selected_date = None

    if "schedule_display_year" not in st.session_state:
        initial_date = date.today()

        future_deadlines = sorted(
            [
                item["parsed_deadline"]
                for item in deliverables
                if item["parsed_deadline"] >= date.today()
            ]
        )

        if future_deadlines:
            initial_date = future_deadlines[0]

        elif deliverables:
            initial_date = deliverables[0]["parsed_deadline"]

        elif project_end_date:
            initial_date = project_end_date

        st.session_state.schedule_display_year = (
            initial_date.year
        )

        st.session_state.schedule_display_month = (
            initial_date.month
        )


def go_to_previous_month():
    current_year = st.session_state.schedule_display_year
    current_month = st.session_state.schedule_display_month

    if current_month == 1:
        st.session_state.schedule_display_month = 12
        st.session_state.schedule_display_year = (
            current_year - 1
        )

    else:
        st.session_state.schedule_display_month = (
            current_month - 1
        )


def go_to_next_month():
    current_year = st.session_state.schedule_display_year
    current_month = st.session_state.schedule_display_month

    if current_month == 12:
        st.session_state.schedule_display_month = 1
        st.session_state.schedule_display_year = (
            current_year + 1
        )

    else:
        st.session_state.schedule_display_month = (
            current_month + 1
        )


def go_to_today():
    today = date.today()

    st.session_state.schedule_display_year = today.year
    st.session_state.schedule_display_month = today.month
    st.session_state.schedule_selected_date = today


def select_calendar_date(selected_date):
    st.session_state.schedule_selected_date = selected_date


def build_day_label(
    current_date,
    activity_count,
    meeting_count,
    project_end_date,
):
    labels = [str(current_date.day)]

    if activity_count:
        labels.append(
            f"● {activity_count} entrega(s)"
        )

    if meeting_count:
        labels.append(
            f"👥 {meeting_count}"
        )

    if project_end_date == current_date:
        labels.append("🏁")

    if current_date == date.today():
        labels.append("Hoje")

    return "\n".join(labels)


def render_calendar(
    deliverables_by_date,
    meetings_by_date,
    project_end_date,
):
    display_year = st.session_state.schedule_display_year
    display_month = st.session_state.schedule_display_month

    previous_column, title_column, next_column = st.columns(
        [1, 4, 1]
    )

    with previous_column:
        st.button(
            "←",
            key="schedule_previous_month",
            use_container_width=True,
            on_click=go_to_previous_month,
        )

    with title_column:
        st.markdown(
            (
                "<h3 style='text-align:center; margin-top:8px;'>"
                f"{MONTH_NAMES[display_month]} de {display_year}"
                "</h3>"
            ),
            unsafe_allow_html=True,
        )

    with next_column:
        st.button(
            "→",
            key="schedule_next_month",
            use_container_width=True,
            on_click=go_to_next_month,
        )

    today_column, final_column = st.columns([1, 2])

    with today_column:
        st.button(
            "Ir para hoje",
            key="schedule_go_to_today",
            use_container_width=True,
            on_click=go_to_today,
        )

    with final_column:
        if project_end_date:
            if st.button(
                (
                    "🏁 Ir para a data final — "
                    f"{project_end_date.strftime('%d/%m/%Y')}"
                ),
                key="schedule_go_to_final_date",
                use_container_width=True,
            ):
                st.session_state.schedule_display_year = (
                    project_end_date.year
                )

                st.session_state.schedule_display_month = (
                    project_end_date.month
                )

                st.session_state.schedule_selected_date = (
                    project_end_date
                )

                st.rerun()

    st.markdown(
        (
            '<div class="calendar-legend">'
            '<div class="calendar-legend-item">'
            "● Dia com atividade"
            "</div>"
            '<div class="calendar-legend-item">'
            "🏁 Data final do projeto"
            "</div>"
            '<div class="calendar-legend-item">'
            "Hoje = data atual"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    weekday_columns = st.columns(7)

    for index, weekday_name in enumerate(WEEKDAY_NAMES):
        with weekday_columns[index]:
            st.markdown(
                (
                    '<div class="calendar-weekday">'
                    f"{weekday_name}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

    month_calendar = calendar.Calendar(
        firstweekday=calendar.MONDAY
    )

    month_weeks = month_calendar.monthdayscalendar(
        display_year,
        display_month,
    )

    selected_date = st.session_state.schedule_selected_date

    for week_index, week in enumerate(month_weeks):
        week_columns = st.columns(7)

        for weekday_index, day_number in enumerate(week):
            with week_columns[weekday_index]:
                if day_number == 0:
                    st.markdown(
                        "<div style='height:52px;'></div>",
                        unsafe_allow_html=True,
                    )
                    continue

                current_date = date(
                    display_year,
                    display_month,
                    day_number,
                )

                activities = deliverables_by_date.get(
                    current_date,
                    [],
                )

                activity_count = len(activities)

                meetings = meetings_by_date.get(
                    current_date,
                    [],
                )
                
                meeting_count = len(meetings)

                label = build_day_label(
                    current_date=current_date,
                    activity_count=activity_count,
                    meeting_count=meeting_count,
                    project_end_date=project_end_date,
                )

                button_type = (
                    "primary"
                    if selected_date == current_date
                    else "secondary"
                )

                if st.button(
                    label,
                    key=(
                        "schedule_day_"
                        f"{display_year}_"
                        f"{display_month}_"
                        f"{day_number}_"
                        f"{week_index}_"
                        f"{weekday_index}"
                    ),
                    type=button_type,
                    use_container_width=True,
                ):
                    select_calendar_date(current_date)
                    st.rerun()


def render_activity_card(activity):
    title = activity.get("title") or "Sem título"
    discipline = (
        activity.get("discipline")
        or "Não definida"
    )

    manager = (
        activity.get("manager")
        or "Não definido"
    )

    status = (
        activity.get("status")
        or "Não definido"
    )

    priority = (
        activity.get("priority")
        or "Não definida"
    )

    progress = activity.get("progress") or 0

    try:
        progress = int(float(progress))
    except (TypeError, ValueError):
        progress = 0

    progress = max(0, min(100, progress))

    st.markdown(
        (
            '<div class="activity-card">'
            f'<div class="activity-card-title">{title}</div>'
            '<div class="activity-card-details">'
            f"<strong>Disciplina:</strong> {discipline}<br>"
            f"<strong>Responsável:</strong> {manager}<br>"
            f"<strong>Status:</strong> {status}<br>"
            f"<strong>Prioridade:</strong> {priority}"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    st.progress(progress / 100)

    st.caption(f"{progress}% concluído")


def render_selected_date_activities(
    deliverables_by_date,
    meetings_by_date,
    project_end_date,
):
    selected_date = st.session_state.schedule_selected_date

    st.divider()

    if selected_date is None:
        st.info(
            "Selecione um dia no calendário para visualizar "
            "as atividades previstas."
        )
        return

    activities = deliverables_by_date.get(
        selected_date,
        [],
    )

    meetings = meetings_by_date.get(
        selected_date,
        [],
    )

    st.markdown(
        (
            '<div class="selected-date-title">'
            f"Atividades de {selected_date.strftime('%d/%m/%Y')}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if selected_date == project_end_date:
        st.markdown(
            (
                '<div class="final-date-card">'
                '<div class="final-date-title">'
                "🏁 DATA FINAL DO PROJETO"
                "</div>"
                '<div class="final-date-value">'
                f"{selected_date.strftime('%d/%m/%Y')}"
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    if meetings:
        st.markdown(
            (
                '<div class="selected-date-title" '
                'style="margin-top:20px;">'
                "👥 Reuniões do dia"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    
        for meeting in meetings:
            status = (
                meeting.get("status")
                or "Agendada"
            )
    
            st.markdown(
                (
                    '<div class="activity-card">'
                    '<div class="activity-card-title">'
                    f'👥 {meeting.get("title") or "Sem título"}'
                    "</div>"
                    '<div class="activity-card-details">'
                    f'<strong>Horário:</strong> '
                    f'{str(meeting.get("start_time") or "-")[:5]}<br>'
                    f'<strong>Duração:</strong> '
                    f'{meeting.get("duration_minutes") or 0} minutos<br>'
                    f'<strong>Participantes:</strong> '
                    f'{meeting.get("participants") or "Não informados"}<br>'
                    f'<strong>Status:</strong> {status}'
                    "</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
    
            recording_link = meeting.get(
                "recording_link"
            )
    
            if recording_link:
                st.link_button(
                    "▶️ Abrir gravação",
                    recording_link,
                    key=(
                        "calendar_recording_"
                        f"{meeting['id']}"
                    ),
                )

    if not activities and not meetings:
        st.info(
            "Não existem entregas ou reuniões "
            "cadastradas para esta data."
        )
        return

    st.markdown(
            (
                '<div class="selected-date-title" '
                'style="margin-top:20px;">'
                f"📝 {len(activities)} atividade(s) prevista(s) para esta data."
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    
    # st.caption(
    #     f"{len(activities)} atividade(s) prevista(s) "
    #     "para esta data."
    # )

    for activity in activities:
        render_activity_card(activity)


def render_upcoming_deliveries(deliverables):
    today = date.today()

    upcoming = [
        item
        for item in deliverables
        if item["parsed_deadline"] >= today
    ]

    upcoming = sorted(
        upcoming,
        key=lambda item: (
            item["parsed_deadline"],
            item.get("title") or "",
        ),
    )[:10]

    with st.expander(
        "📋 Visualizar próximas entregas",
        expanded=False,
    ):
        if not upcoming:
            st.info("Não existem próximas entregas cadastradas.")
            return

        table = pd.DataFrame(
            [
                {
                    "Atividade": item.get("title") or "Sem título",
                    "Disciplina": (
                        item.get("discipline")
                        or "Não definida"
                    ),
                    "Prazo": format_date(
                        item.get("deadline")
                    ),
                    "Status": (
                        item.get("status")
                        or "Não definido"
                    ),
                    "Progresso": (
                        item.get("progress")
                        or 0
                    ),
                    "Responsável": (
                        item.get("manager")
                        or "Não definido"
                    ),
                }
                for item in upcoming
            ]
        )

        table["Progresso"] = (
            pd.to_numeric(
                table["Progresso"],
                errors="coerce",
            )
            .fillna(0)
            .clip(0, 100)
            .astype(int)
        )

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Atividade": st.column_config.TextColumn(
                    "Atividade",
                    width="large",
                ),
                "Progresso": st.column_config.ProgressColumn(
                    "Progresso",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                ),
            },
        )



def group_meetings_by_date(meetings):
    grouped = {}

    for meeting in meetings:
        if (
            str(meeting.get("status") or "")
            .strip()
            .lower()
            == "cancelada"
        ):
            continue

        meeting_date = parse_database_date(
            meeting.get("meeting_date")
        )

        if meeting_date is None:
            continue

        if meeting_date not in grouped:
            grouped[meeting_date] = []

        grouped[meeting_date].append(meeting)

    return grouped

def cronograma_page():
    load_schedule_css()

    settings = DashboardService.get_project_settings()

    project_end_date = parse_database_date(
        settings.get("end_date")
    )

    deliverables = load_deliverables_with_deadline()

    deliverables_by_date = group_deliverables_by_date(
        deliverables
    )

    meetings = MeetingService.get_all()

    meetings_by_date = group_meetings_by_date(meetings)

    initialize_calendar_state(
        deliverables=deliverables,
        project_end_date=project_end_date,
    )

    st.markdown(
        (
            '<div class="schedule-header">'
            "<h1>📅 Cronograma de entregas</h1>"
            "<p>"
            "Acompanhamento das datas previstas para conclusão "
            "das atividades do projeto."
            "</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    metric_1, metric_2, metric_3 = st.columns(3)

    total_deliverables = len(deliverables)

    future_deliverables = len(
        [
            item
            for item in deliverables
            if item["parsed_deadline"] >= date.today()
        ]
    )

    overdue_deliverables = len(
        [
            item
            for item in deliverables
            if (
                item["parsed_deadline"] < date.today()
                and str(
                    item.get("status") or ""
                ).strip().lower()
                not in {
                    "concluído",
                    "concluido",
                    "finalizado",
                    "completed",
                }
            )
        ]
    )

    metric_1.metric(
        "Entregas cadastradas",
        total_deliverables,
    )

    metric_2.metric(
        "Próximas entregas",
        future_deliverables,
    )

    metric_3.metric(
        "Entregas vencidas",
        overdue_deliverables,
    )

    if project_end_date:
        st.markdown(
            (
                '<div class="final-date-card">'
                '<div class="final-date-title">'
                "🏁 DATA PREVISTA PARA FINALIZAÇÃO DO PROJETO"
                "</div>"
                '<div class="final-date-value">'
                f"{project_end_date.strftime('%d/%m/%Y')}"
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    else:
        st.warning(
            "A data final do projeto ainda não foi configurada "
            "no Dashboard."
        )

    with st.container(border=True):
        render_calendar(
            deliverables_by_date=deliverables_by_date,
            meetings_by_date=meetings_by_date,
            project_end_date=project_end_date,
        )

    render_selected_date_activities(
        deliverables_by_date=deliverables_by_date,
        meetings_by_date=meetings_by_date,
        project_end_date=project_end_date,
    )

    st.write("")

    render_upcoming_deliveries(deliverables)
