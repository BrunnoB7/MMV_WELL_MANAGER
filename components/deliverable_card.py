from datetime import date

import streamlit as st

from services.deliverable_service import DeliverableService


STATUS_COLORS = {
    "Concluído": "#16A34A",      # Verde
    "Em andamento": "#EAB308",   # Amarelo
    "Não iniciado": "#9CA3AF",   # Cinza
    "Atrasado": "#DC2626",       # Vermelho
    "Bloqueado": "#111827",      # Preto
}

PRIORITY_COLORS = {
    "Crítica": "#DC2626",    # Vermelho
    "Alta": "#EA580C",       # Laranja escuro
    "Média": "#EAB308",      # Amarelo
    "Baixa": "#84CC16",      # Verde claro
}


def parse_date(value):
    if not value:
        return date.today()

    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.today()


def format_date(value):
    if not value:
        return "Não definido"

    try:
        return date.fromisoformat(value).strftime("%d/%m/%Y")
    except ValueError:
        return value


def safe_value(deliverable, key, default=""):
    value = deliverable[key]

    if value is None:
        return default

    return value


@st.dialog("Editar deliverable", width="large")
def edit_deliverable_dialog(deliverable):
    deliverable_id = deliverable["id"]

    current_status = safe_value(
        deliverable,
        "status",
        "Não iniciado",
    )

    current_priority = safe_value(
        deliverable,
        "priority",
        "Média",
    )

    status_options = [
        "Não iniciado",
        "Em andamento",
        "Concluído",
        "Atrasado",
        "Bloqueado",
    ]

    priority_options = [
        "Crítica",
        "Alta",
        "Média",
        "Baixa",
    ]

    status_index = (
        status_options.index(current_status)
        if current_status in status_options
        else 0
    )

    priority_index = (
        priority_options.index(current_priority)
        if current_priority in priority_options
        else 2
    )

    with st.form(f"edit_deliverable_{deliverable_id}"):
        title = st.text_input(
            "Título",
            value=safe_value(deliverable, "title"),
        )

        col1, col2 = st.columns(2)

        with col1:
            discipline = st.text_input(
                "Disciplina",
                value=safe_value(
                    deliverable,
                    "discipline",
                ),
            )

            manager = st.text_input(
                "Responsável",
                value=safe_value(
                    deliverable,
                    "manager",
                ),
            )

            priority = st.selectbox(
                "Prioridade",
                priority_options,
                index=priority_index,
            )

        with col2:
            status = st.selectbox(
                "Status",
                status_options,
                index=status_index,
            )

            progress = st.slider(
                "Progresso",
                min_value=0,
                max_value=100,
                value=int(
                    safe_value(
                        deliverable,
                        "progress",
                        0,
                    )
                ),
                step=5,
                format="%d%%",
            )

            deadline = st.date_input(
                "Prazo",
                value=parse_date(
                    safe_value(
                        deliverable,
                        "deadline",
                    )
                ),
                format="DD/MM/YYYY",
            )

        description = st.text_area(
            "Descrição",
            value=safe_value(
                deliverable,
                "description",
            ),
            height=120,
        )

        google_drive = st.text_input(
            "Link do Google Drive",
            value=safe_value(
                deliverable,
                "google_drive",
            ),
            placeholder="https://drive.google.com/drive/folders/...",
        )

        submitted = st.form_submit_button(
            "Salvar alterações",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            try:
                DeliverableService.update_deliverable(
                    deliverable_id=deliverable_id,
                    title=title,
                    discipline=discipline,
                    description=description,
                    manager=manager,
                    priority=priority,
                    status=status,
                    progress=progress,
                    deadline=deadline.isoformat(),
                    google_drive=google_drive,
                )

                st.session_state["deliverable_updated"] = True
                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    f"Erro ao atualizar deliverable: {error}"
                )


def deliverable_card(deliverable):
    status = safe_value(
        deliverable,
        "status",
        "Não iniciado",
    )

    priority = safe_value(
        deliverable,
        "priority",
        "Média",
    )

    progress = int(
        safe_value(
            deliverable,
            "progress",
            0,
        )
    )

    status_color = STATUS_COLORS.get(
        status,
        "#6B7280",
    )

    priority_color = PRIORITY_COLORS.get(
        priority,
        "#6B7280",
    )

    title = safe_value(
        deliverable,
        "title",
        "Sem título",
    )

    discipline = safe_value(
        deliverable,
        "discipline",
        "Sem disciplina",
    )

    manager = safe_value(
        deliverable,
        "manager",
        "Não definido",
    )

    deadline = format_date(
        safe_value(
            deliverable,
            "deadline",
        )
    )

    description = safe_value(
        deliverable,
        "description",
        "Sem descrição.",
    )

    google_drive = safe_value(
        deliverable,
        "google_drive",
    )

    with st.container(border=True):
        header_col, priority_col = st.columns([3, 1])

        with header_col:
            st.subheader(title)
            st.caption(f"📂 {discipline}")

        with priority_col:
            st.markdown(
                (
                    '<div style="text-align:right;">'
                    f'<span style="'
                    f'color:{priority_color};'
                    'font-weight:700;">'
                    f'{priority}'
                    '</span>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

        st.progress(progress / 100)

        progress_col, status_col = st.columns(2)

        with progress_col:
            st.caption(f"Progresso: **{progress}%**")

        with status_col:
            st.markdown(
                (
                    '<div style="text-align:right;">'
                    f'<span style="'
                    f'color:{status_color};'
                    'font-weight:700;">'
                    f'● {status}'
                    '</span>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

        st.write(description)

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.caption("Responsável")
            st.write(manager)

        with info_col2:
            st.caption("Prazo")
            st.write(deadline)

        button_col1, button_col2 = st.columns(2)

        with button_col1:
            if st.button(
                "✏️ Editar",
                key=f"edit_{deliverable['id']}",
                use_container_width=True,
            ):
                edit_deliverable_dialog(deliverable)

        with button_col2:
            if google_drive:
                st.link_button(
                    "📂 Google Drive",
                    google_drive,
                    use_container_width=True,
                )
            else:
                st.button(
                    "📂 Sem pasta",
                    key=f"no_drive_{deliverable['id']}",
                    disabled=True,
                    use_container_width=True,
                )
