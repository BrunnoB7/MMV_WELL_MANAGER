import streamlit as st
from datetime import date
from components.deliverable_card import deliverable_card
from services.deliverable_service import DeliverableService


def load_css():
    st.markdown(
        """
        <style>
            .deliverables-header {
                padding: 22px 26px;
                margin-bottom: 20px;
                border-radius: 14px;
                background: linear-gradient(
                    135deg,
                    #7F0000,
                    #D71920
                );
                color: white;
            }

            .deliverables-header h1 {
                margin: 0;
                font-size: 2rem;
            }

            .deliverables-header p {
                margin: 7px 0 0 0;
                opacity: 0.85;
            }

            .deliverables-summary {
                margin-bottom: 15px;
                font-size: 0.90rem;
                opacity: 0.75;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Novo deliverable", width="large")
def create_deliverable_dialog():

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

    with st.form("create_deliverable_form"):

        title = st.text_input("Título")

        col1, col2 = st.columns(2)

        with col1:
            discipline = st.text_input("Disciplina")

            manager = st.text_input("Responsável")

            priority = st.selectbox(
                "Prioridade",
                priority_options,
                index=2,
            )

        with col2:
            status = st.selectbox(
                "Status",
                status_options,
                index=0,
            )

            progress = st.slider(
                "Progresso",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                format="%d%%",
            )

            deadline = st.date_input(
                "Prazo",
                value=date.today(),
                format="DD/MM/YYYY",
            )

        description = st.text_area(
            "Descrição",
            height=120,
        )

        google_drive = st.text_input(
            "Link do Google Drive",
            placeholder="https://drive.google.com/drive/folders/...",
        )

        submitted = st.form_submit_button(
            "Criar deliverable",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            try:
                DeliverableService.create_deliverable(
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

                st.session_state["deliverable_created"] = True
                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    f"Erro ao criar deliverable: {error}"
                )


def deliverables_page():
    load_css()

    if st.session_state.pop(
        "deliverable_updated",
        False,
    ):
        st.toast(
            "Tarefa atualizado com sucesso.",
            icon="✅",
        )

    st.markdown(
        (
            '<div class="deliverables-header">'
            '<h1>Tarefas</h1>'
            '<p>'
            'Acompanhamento das entregas técnicas, prazos, '
            'responsáveis e progresso.'
            '</p>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    deliverables = (
        DeliverableService.get_all_deliverables()
    )

    if st.session_state.pop(
            "deliverable_created",
            False,
    ):
        st.toast(
            "Tarefa criado com sucesso.",
            icon="✅",
        )

    button_col1, button_col2 = st.columns([1, 4])

    with button_col1:
        if st.button(
                "➕ Novo deliverable",
                type="primary",
                use_container_width=True,
        ):
            create_deliverable_dialog()

    disciplines = sorted(
        {
            deliverable["discipline"]
            for deliverable in deliverables
            if deliverable["discipline"]
        }
    )

    filter_col1, filter_col2, filter_col3 = st.columns(
        [2, 1, 1]
    )

    with filter_col1:
        search = st.text_input(
            "Pesquisar",
            placeholder="Nome, responsável ou disciplina",
        )

    with filter_col2:
        selected_discipline = st.selectbox(
            "Disciplina",
            ["Todas"] + disciplines,
        )

    with filter_col3:
        selected_status = st.selectbox(
            "Status",
            [
                "Todos",
                "Não iniciado",
                "Em andamento",
                "Concluído",
                "Atrasado",
                "Bloqueado",
            ],
        )

    filtered = []

    deliverables = sorted(deliverables,
                          key=lambda item: (str(item.get("status") or "").strip().lower()
                                            in {"concluído", "concluido"},
                                            item.get("deadline") or "9999-12-31",
                                            item.get("title") or "",),)

    for deliverable in deliverables:
        searchable = (
            f"{deliverable['title'] or ''} "
            f"{deliverable['manager'] or ''} "
            f"{deliverable['discipline'] or ''}"
        ).lower()

        if search and search.lower() not in searchable:
            continue

        if (
            selected_discipline != "Todas"
            and deliverable["discipline"]
            != selected_discipline
        ):
            continue

        if (
            selected_status != "Todos"
            and deliverable["status"]
            != selected_status
        ):
            continue

        filtered.append(deliverable)

    st.markdown(
        (
            '<div class="deliverables-summary">'
            f'{len(filtered)} de {len(deliverables)} '
            'deliverables exibidos'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    if not filtered:
        st.info(
            "Nenhuma tarefa encontrada para os filtros."
        )
        return

    columns = st.columns(2)

    for index, deliverable in enumerate(filtered):
        with columns[index % 2]:
            deliverable_card(deliverable)
