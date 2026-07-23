from datetime import datetime

import streamlit as st

from services.document_service import DocumentService
from components.page_header import page_header


DISCIPLINES = [
    "Geral",
    "Performance",
    "Integridade",
    "Reservatório",
    "MMV",
    "Operações",
    "Reuniões",
]


def format_datetime(value):
    if not value:
        return "-"

    try:
        date_value = datetime.strptime(
            value,
            "%Y-%m-%d %H:%M:%S",
        )

        return date_value.strftime("%d/%m/%Y às %H:%M")

    except ValueError:
        return value


@st.dialog("Adicionar pasta", width="large")
def create_folder_dialog():
    with st.form("create_document_folder"):
        name = st.text_input(
            "Nome da pasta",
            placeholder="Ex.: Performance dos Poços",
        )

        col1, col2 = st.columns(2)

        with col1:
            discipline = st.selectbox(
                "Disciplina",
                DISCIPLINES,
            )

        with col2:
            responsible = st.text_input(
                "Responsável",
            )

        description = st.text_area(
            "Descrição",
            placeholder=(
                "Explique quais documentos estão armazenados "
                "nesta pasta."
            ),
            height=110,
        )

        drive_link = st.text_input(
            "Link compartilhado do Google Drive",
            placeholder=(
                "https://drive.google.com/drive/folders/..."
            ),
        )

        submitted = st.form_submit_button(
            "Cadastrar pasta",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            try:
                DocumentService.create_folder(
                    name=name,
                    discipline=discipline,
                    description=description,
                    drive_link=drive_link,
                    responsible=responsible,
                )

                st.session_state["folder_created"] = True
                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    f"Erro ao cadastrar pasta: {error}"
                )


@st.dialog("Editar pasta", width="large")
def edit_folder_dialog(folder):
    current_discipline = (
        folder["discipline"]
        if folder["discipline"] in DISCIPLINES
        else "Geral"
    )

    discipline_index = DISCIPLINES.index(
        current_discipline
    )

    with st.form(f"edit_folder_{folder['id']}"):
        name = st.text_input(
            "Nome da pasta",
            value=folder["name"] or "",
        )

        col1, col2 = st.columns(2)

        with col1:
            discipline = st.selectbox(
                "Disciplina",
                DISCIPLINES,
                index=discipline_index,
            )

        with col2:
            responsible = st.text_input(
                "Responsável",
                value=folder["responsible"] or "",
            )

        description = st.text_area(
            "Descrição",
            value=folder["description"] or "",
            height=110,
        )

        drive_link = st.text_input(
            "Link compartilhado do Google Drive",
            value=folder["drive_link"] or "",
        )

        submitted = st.form_submit_button(
            "Salvar alterações",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            try:
                DocumentService.update_folder(
                    folder_id=folder["id"],
                    name=name,
                    discipline=discipline,
                    description=description,
                    drive_link=drive_link,
                    responsible=responsible,
                )

                st.session_state["folder_updated"] = True
                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    f"Erro ao atualizar pasta: {error}"
                )


def render_folder_card(folder):
    with st.container(border=True):
        st.subheader(f"📁 {folder['name']}")

        st.markdown(
            (
                '<span class="document-discipline">'
                f'{folder["discipline"] or "Geral"}'
                '</span>'
            ),
            unsafe_allow_html=True,
        )

        description = (
            folder["description"]
            or "Nenhuma descrição cadastrada."
        )

        st.markdown(
            (
                '<div class="document-description">'
                f'{description}'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<div class="document-info">'
                '<strong>Responsável:</strong> '
                f'{folder["responsible"] or "Não definido"}'
                '<br>'
                '<strong>Última atualização:</strong> '
                f'{format_datetime(folder["updated_at"])}'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

        st.link_button(
            "📂 Abrir no Google Drive",
            folder["drive_link"],
            use_container_width=True,
        )

        edit_col, delete_col = st.columns(2)

        with edit_col:
            if st.button(
                "✏️ Editar",
                key=f"edit_folder_{folder['id']}",
                use_container_width=True,
            ):
                edit_folder_dialog(folder)

        with delete_col:
            if st.button(
                "🗑️ Excluir",
                key=f"delete_folder_{folder['id']}",
                use_container_width=True,
            ):
                st.session_state[
                    "folder_pending_delete"
                ] = folder["id"]


def render_delete_confirmation():
    folder_id = st.session_state.get(
        "folder_pending_delete"
    )

    if not folder_id:
        return

    folder = DocumentService.get_folder(folder_id)

    if not folder:
        st.session_state.pop(
            "folder_pending_delete",
            None,
        )
        return

    st.warning(
        f"Confirma a exclusão do cadastro da pasta "
        f"**{folder['name']}**? "
        "A pasta no Google Drive não será apagada."
    )

    confirm_col, cancel_col = st.columns(2)

    with confirm_col:
        if st.button(
            "Confirmar exclusão",
            type="primary",
            use_container_width=True,
        ):
            DocumentService.delete_folder(folder_id)

            st.session_state.pop(
                "folder_pending_delete",
                None,
            )

            st.session_state["folder_deleted"] = True
            st.rerun()

    with cancel_col:
        if st.button(
            "Cancelar",
            use_container_width=True,
        ):
            st.session_state.pop(
                "folder_pending_delete",
                None,
            )

            st.rerun()


def documentos_page():
    page_header(
        title="📁 Documentos",
        subtitle="Acesso centralizado às pastas e documentos compartilhados no Google Drive.",
    )

    if st.session_state.pop("folder_created", False):
        st.toast(
            "Pasta cadastrada com sucesso.",
            icon="✅",
        )

    if st.session_state.pop("folder_updated", False):
        st.toast(
            "Pasta atualizada com sucesso.",
            icon="✅",
        )

    if st.session_state.pop("folder_deleted", False):
        st.toast(
            "Cadastro excluído.",
            icon="🗑️",
        )

    top_col1, top_col2 = st.columns([1, 4])

    with top_col1:
        if st.button(
            "➕ Adicionar pasta",
            type="primary",
            use_container_width=True,
        ):
            create_folder_dialog()

    render_delete_confirmation()

    folders = DocumentService.get_all_folders()

    disciplines = sorted(
        {
            folder["discipline"]
            for folder in folders
            if folder["discipline"]
        }
    )

    filter_col1, filter_col2 = st.columns([2, 1])

    with filter_col1:
        search = st.text_input(
            "Pesquisar",
            placeholder=(
                "Nome, descrição, responsável ou disciplina"
            ),
        )

    with filter_col2:
        selected_discipline = st.selectbox(
            "Disciplina",
            ["Todas"] + disciplines,
        )

    filtered = []

    for folder in folders:
        searchable = (
            f"{folder['name'] or ''} "
            f"{folder['description'] or ''} "
            f"{folder['responsible'] or ''} "
            f"{folder['discipline'] or ''}"
        ).lower()

        if search and search.lower() not in searchable:
            continue

        if (
            selected_discipline != "Todas"
            and folder["discipline"]
            != selected_discipline
        ):
            continue

        filtered.append(folder)

    st.markdown(
        (
            '<div class="documents-summary">'
            f'{len(filtered)} de {len(folders)} '
            'pastas exibidas'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    if not filtered:
        st.info(
            "Nenhuma pasta cadastrada para os filtros."
        )
        return

    columns = st.columns(3)

    for index, folder in enumerate(filtered):
        with columns[index % 3]:
            render_folder_card(folder)
