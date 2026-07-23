from datetime import date, datetime, time

import streamlit as st

from services.meeting_service import MeetingService


STATUS_COLORS = {
    "Agendada": "#2563EB",
    "Realizada": "#16A34A",
    "Cancelada": "#DC2626",
}


def load_meetings_css():
    st.markdown(
        """
        <style>
        .meetings-header {
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

        .meetings-header h1 {
            color: white;
            margin: 0;
            font-size: 1.9rem;
        }

        .meetings-header p {
            color: rgba(255, 255, 255, 0.82);
            margin: 6px 0 0 0;
        }

        .scheduled-meeting {
            padding: 15px 17px;
            margin-bottom: 12px;
            border-radius: 11px;
            border: 1px solid rgba(37, 99, 235, 0.20);
            border-left: 5px solid #2563EB;
            background: rgba(37, 99, 235, 0.05);
        }

        .completed-meeting {
            padding: 16px 18px;
            margin-bottom: 13px;
            border-radius: 12px;
            border: 1px solid rgba(22, 163, 74, 0.22);
            border-left: 5px solid #16A34A;
            background: rgba(22, 163, 74, 0.05);
        }

        .meeting-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 7px;
        }

        .meeting-info {
            font-size: 0.82rem;
            line-height: 1.6;
            opacity: 0.78;
        }

        .meeting-description {
            margin-top: 11px;
            padding: 11px 13px;
            border-radius: 8px;
            background: rgba(128, 128, 128, 0.07);
            font-size: 0.85rem;
            line-height: 1.5;
        }

        .meeting-status {
            display: inline-block;
            margin-top: 9px;
            padding: 4px 9px;
            border-radius: 20px;
            font-size: 0.73rem;
            font-weight: 700;
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 13px;
        }
        </style>
        """,
        unsafe_allow_html=True,
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


def format_time(value):
    if not value:
        return "-"

    return str(value)[:5]


def format_duration(minutes):
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        return "-"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours and remaining_minutes:
        return f"{hours}h {remaining_minutes}min"

    if hours:
        return f"{hours}h"

    return f"{remaining_minutes}min"


def participants_to_html(participants):
    if not participants:
        return "Não informados"

    participant_list = [
        participant.strip()
        for participant in str(
            participants
        ).replace(";", ",").split(",")
        if participant.strip()
    ]

    return ", ".join(participant_list)


@st.dialog("Nova reunião", width="large")
def create_meeting_dialog():
    with st.form("create_meeting_form"):
        title = st.text_input(
            "Título da reunião"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            meeting_date = st.date_input(
                "Data",
                value=date.today(),
                format="DD/MM/YYYY",
            )

        with col2:
            start_time = st.time_input(
                "Horário",
                value=time(9, 0),
            )

        with col3:
            duration_minutes = st.number_input(
                "Duração prevista (minutos)",
                min_value=15,
                max_value=480,
                value=60,
                step=15,
            )

        participants = st.text_area(
            "Participantes",
            placeholder=(
                "Bruno, Matheus, Eric..."
            ),
            help=(
                "Separe os participantes por vírgula."
            ),
        )

        status = st.selectbox(
            "Status",
            MeetingService.VALID_STATUSES,
            index=0,
        )

        description = st.text_area(
            "Descrição ou pauta",
            height=120,
        )

        recording_link = st.text_input(
            "Link da gravação",
            placeholder="https://...",
            help=(
                "Pode ser preenchido posteriormente, "
                "após a realização."
            ),
        )

        submitted = st.form_submit_button(
            "Cadastrar reunião",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            try:
                MeetingService.create_meeting(
                    title=title,
                    meeting_date=meeting_date,
                    start_time=start_time,
                    duration_minutes=duration_minutes,
                    participants=participants,
                    description=description,
                    recording_link=recording_link,
                    status=status,
                )

                st.session_state[
                    "meeting_created"
                ] = True

                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    f"Erro ao cadastrar reunião: {error}"
                )


@st.dialog("Editar reunião", width="large")
def edit_meeting_dialog(meeting):
    meeting_date = date.fromisoformat(
        meeting["meeting_date"]
    )

    start_time = datetime.strptime(
        meeting["start_time"][:5],
        "%H:%M",
    ).time()

    current_status = (
        meeting.get("status") or "Agendada"
    )

    status_index = (
        MeetingService.VALID_STATUSES.index(
            current_status
        )
        if current_status
        in MeetingService.VALID_STATUSES
        else 0
    )

    with st.form(
        f"edit_meeting_{meeting['id']}"
    ):
        title = st.text_input(
            "Título da reunião",
            value=meeting.get("title") or "",
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            new_date = st.date_input(
                "Data",
                value=meeting_date,
                format="DD/MM/YYYY",
            )

        with col2:
            new_start_time = st.time_input(
                "Horário",
                value=start_time,
            )

        with col3:
            duration_minutes = st.number_input(
                "Duração (minutos)",
                min_value=15,
                max_value=480,
                value=int(
                    meeting.get(
                        "duration_minutes"
                    ) or 60
                ),
                step=15,
            )

        participants = st.text_area(
            "Participantes",
            value=meeting.get(
                "participants"
            ) or "",
        )

        status = st.selectbox(
            "Status",
            MeetingService.VALID_STATUSES,
            index=status_index,
        )

        description_label = (
            "Descrição e resumo da reunião"
            if status == "Realizada"
            else "Descrição ou pauta"
        )

        description = st.text_area(
            description_label,
            value=meeting.get(
                "description"
            ) or "",
            height=130,
        )

        recording_link = st.text_input(
            "Link da gravação",
            value=meeting.get(
                "recording_link"
            ) or "",
            placeholder="https://...",
        )

        col_save, col_delete = st.columns(2)

        with col_save:
            submitted = st.form_submit_button(
                "Salvar alterações",
                type="primary",
                use_container_width=True,
            )

        with col_delete:
            delete_requested = (
                st.form_submit_button(
                    "Excluir reunião",
                    use_container_width=True,
                )
            )

        if submitted:
            try:
                MeetingService.update_meeting(
                    meeting_id=meeting["id"],
                    title=title,
                    meeting_date=new_date,
                    start_time=new_start_time,
                    duration_minutes=duration_minutes,
                    participants=participants,
                    description=description,
                    recording_link=recording_link,
                    status=status,
                )

                st.rerun()

            except Exception as error:
                st.error(str(error))

        if delete_requested:
            MeetingService.delete_meeting(
                meeting["id"]
            )
            st.rerun()


def render_scheduled_meeting(meeting):
    status_color = STATUS_COLORS.get(
        meeting.get("status"),
        "#2563EB",
    )

    st.markdown(
        (
            '<div class="scheduled-meeting">'
            f'<div class="meeting-title">'
            f'📅 {meeting.get("title") or "Sem título"}'
            "</div>"
            '<div class="meeting-info">'
            f'<strong>Data:</strong> '
            f'{format_date(meeting.get("meeting_date"))}<br>'
            f'<strong>Horário:</strong> '
            f'{format_time(meeting.get("start_time"))}<br>'
            f'<strong>Duração prevista:</strong> '
            f'{format_duration(meeting.get("duration_minutes"))}<br>'
            f'<strong>Participantes:</strong> '
            f'{participants_to_html(meeting.get("participants"))}'
            "</div>"
            '<div class="meeting-status" '
            f'style="color:{status_color};'
            f'background:{status_color}18;">'
            f'● {meeting.get("status")}'
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if st.button(
        "✏️ Editar reunião",
        key=f"edit_scheduled_{meeting['id']}",
        use_container_width=True,
    ):
        edit_meeting_dialog(meeting)


def render_completed_meeting(meeting):
    st.markdown(
        (
            '<div class="completed-meeting">'
            f'<div class="meeting-title">'
            f'✅ {meeting.get("title") or "Sem título"}'
            "</div>"
            '<div class="meeting-info">'
            f'<strong>Data:</strong> '
            f'{format_date(meeting.get("meeting_date"))}<br>'
            f'<strong>Horário:</strong> '
            f'{format_time(meeting.get("start_time"))}<br>'
            f'<strong>Duração:</strong> '
            f'{format_duration(meeting.get("duration_minutes"))}<br>'
            f'<strong>Participantes:</strong> '
            f'{participants_to_html(meeting.get("participants"))}'
            "</div>"
            '<div class="meeting-description">'
            '<strong>Resumo da reunião</strong><br>'
            f'{meeting.get("description") or "Sem descrição."}'
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        if st.button(
            "✏️ Editar",
            key=f"edit_completed_{meeting['id']}",
            use_container_width=True,
        ):
            edit_meeting_dialog(meeting)

    with button_col2:
        recording_link = meeting.get(
            "recording_link"
        )

        if recording_link:
            st.link_button(
                "▶️ Abrir gravação",
                recording_link,
                use_container_width=True,
            )
        else:
            st.button(
                "▶️ Sem gravação",
                key=f"no_recording_{meeting['id']}",
                disabled=True,
                use_container_width=True,
            )


def filter_completed_meetings(meetings):
    st.markdown("#### Filtros")

    today = date.today()

    meeting_dates = []

    for meeting in meetings:
        try:
            meeting_dates.append(
                date.fromisoformat(
                    meeting["meeting_date"]
                )
            )
        except (TypeError, ValueError):
            continue

    if meeting_dates:
        default_start_date = min(meeting_dates)
        default_end_date = max(meeting_dates)
    else:
        default_start_date = today.replace(
            month=1,
            day=1,
        )
        default_end_date = today

    col1, col2, col3 = st.columns(3)

    with col1:
        start_date_filter = st.date_input(
            "Realizadas a partir de",
            value=default_start_date,
            format="DD/MM/YYYY",
            key="completed_meetings_start_date",
        )

    with col2:
        end_date_filter = st.date_input(
            "Realizadas até",
            value=default_end_date,
            format="DD/MM/YYYY",
            key="completed_meetings_end_date",
        )

    with col3:
        minimum_duration = st.number_input(
            "Duração mínima (min)",
            min_value=0,
            max_value=480,
            value=0,
            step=15,
            key="completed_meetings_min_duration",
        )

    search_col, participant_col = st.columns(2)

    with search_col:
        search = st.text_input(
            "Buscar reunião",
            placeholder="Título ou descrição...",
            key="completed_meetings_search",
        )

    participants = sorted(
        {
            participant.strip()
            for meeting in meetings
            for participant in str(
                meeting.get("participants") or ""
            ).replace(";", ",").split(",")
            if participant.strip()
        }
    )

    with participant_col:
        selected_participant = st.selectbox(
            "Participante",
            ["Todos"] + participants,
            key="completed_meetings_participant",
        )

    only_with_recording = st.checkbox(
        "Mostrar somente reuniões com gravação",
        value=False,
        key="completed_meetings_with_recording",
    )

    if end_date_filter < start_date_filter:
        st.warning(
            "A data final não pode ser anterior "
            "à data inicial."
        )
        return []

    filtered = []

    for meeting in meetings:
        try:
            meeting_date = date.fromisoformat(
                meeting["meeting_date"]
            )
        except (TypeError, ValueError):
            continue

        if meeting_date < start_date_filter:
            continue

        if meeting_date > end_date_filter:
            continue

        try:
            duration = int(
                meeting.get("duration_minutes") or 0
            )
        except (TypeError, ValueError):
            duration = 0

        if duration < minimum_duration:
            continue

        if selected_participant != "Todos":
            meeting_participants = [
                participant.strip().lower()
                for participant in str(
                    meeting.get("participants") or ""
                ).replace(";", ",").split(",")
                if participant.strip()
            ]

            if (
                selected_participant.lower()
                not in meeting_participants
            ):
                continue

        if only_with_recording:
            recording_link = str(
                meeting.get("recording_link") or ""
            ).strip()

            if not recording_link:
                continue

        if search:
            searchable = (
                f"{meeting.get('title') or ''} "
                f"{meeting.get('description') or ''} "
                f"{meeting.get('participants') or ''}"
            ).lower()

            if search.lower() not in searchable:
                continue

        filtered.append(meeting)

    return filtered

def meetings_page():
    load_meetings_css()

    if st.session_state.pop(
        "meeting_created",
        False,
    ):
        st.success(
            "Reunião cadastrada com sucesso."
        )

    st.markdown(
        (
            '<div class="meetings-header">'
            "<h1>👥 Reuniões</h1>"
            "<p>"
            "Planejamento, registro e acompanhamento "
            "das reuniões do projeto."
            "</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    scheduled = MeetingService.get_scheduled()
    completed = MeetingService.get_completed()

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Reuniões agendadas",
        len(scheduled),
    )

    metric2.metric(
        "Reuniões realizadas",
        len(completed),
    )

    meetings_this_month = [
        meeting
        for meeting in scheduled + completed
        if date.fromisoformat(
            meeting["meeting_date"]
        ).month == date.today().month
        and date.fromisoformat(
            meeting["meeting_date"]
        ).year == date.today().year
    ]

    metric3.metric(
        "Reuniões neste mês",
        len(meetings_this_month),
    )

    st.write("")

    if st.button(
        "➕ Agendar nova reunião",
        type="primary",
        use_container_width=True,
    ):
        create_meeting_dialog()

    st.write("")

    st.markdown(
    '<div class="section-title">'
    "✅ Reuniões realizadas"
    "</div>",
    unsafe_allow_html=True,
    )
    if completed:
        with st.expander(
            "🔎 Filtrar reuniões realizadas",
            expanded=False,):
                filtered_completed = (
                    filter_completed_meetings(
                        completed
                    )
                )
    
        st.caption(
            f"{len(filtered_completed)} de "
            f"{len(completed)} reunião(ões) exibida(s)."
        )
    
        if filtered_completed:
            completed_columns = st.columns(2)
    
            for index, meeting in enumerate(
                filtered_completed
            ):
                with completed_columns[index % 2]:
                    render_completed_meeting(meeting)
    
        else:
            st.info(
                "Nenhuma reunião encontrada para "
                "os filtros selecionados."
            )
    
    else:
        st.info(
            "Nenhuma reunião realizada cadastrada."
        )

    if scheduled:
        scheduled_columns = st.columns(2)

        for index, meeting in enumerate(scheduled):
            with scheduled_columns[index % 2]:
                render_scheduled_meeting(meeting)

    else:
        st.info(
            "Nenhuma reunião futura agendada."
        )

    st.divider()

