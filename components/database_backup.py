from datetime import datetime

import streamlit as st

from database.database import DB_PATH
from services.github_backup_service import (
    GitHubBackupError,
    GitHubBackupService,
)


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} bytes"

    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"

    return f"{size_bytes / (1024 * 1024):.1f} MB"


def validate_admin_password(password: str) -> bool:
    try:
        expected_password = str(
            st.secrets["github_backup"]["admin_password"]
        )
    except KeyError:
        return False

    return password == expected_password


def render_sync_indicator(
    synchronization_status: dict,
) -> None:
    status = synchronization_status["status"]

    if status == "synced":
        dot_class = "sync-dot-green"
        status_class = "sync-text-green"
        title = "Banco sincronizado"
        description = (
            "O sistema está atualizado "
        )

    elif status == "not_synced":
        dot_class = "sync-dot-red"
        status_class = "sync-text-red"
        title = "Atualização necessária"
        description = (
            "Existem alterações locais que ainda não "
            "atualizadas."
        )

    elif status == "remote_missing":
        dot_class = "sync-dot-red"
        status_class = "sync-text-red"
        title = "Backup não encontrado"
        description = (
            "O banco ainda não foi salvo no GitHub."
        )

    else:
        dot_class = "sync-dot-red"
        status_class = "sync-text-red"
        title = "Banco indisponível"
        description = (
            "Não foi possível encontrar o banco local."
        )

    html = (
        '<div class="database-sync-status">'
        '<div class="database-sync-header">'
        f'<span class="sync-dot {dot_class}"></span>'
        f'<span class="{status_class}">{title}</span>'
        '</div>'
        f'<div class="database-sync-description">'
        f'{description}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )

def render_database_backup():

    st.markdown(
    """
    <style>
    .database-sync-status {
        background: #F8F9FA;
        border: 1px solid #E4E7EB;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 12px;
    }

    .database-sync-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.88rem;
        font-weight: 600;
    }

    .sync-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }

    .sync-dot-green {
        background-color: #28A745;
        box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.14);
    }

    .sync-dot-red {
        background-color: #DC3545;
        box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.14);
    }

    .sync-text-green {
        color: #218838;
    }

    .sync-text-red {
        color: #C82333;
    }

    .database-sync-description {
        color: #6C757D;
        font-size: 0.74rem;
        line-height: 1.35;
        margin-top: 5px;
        padding-left: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    
    with st.sidebar.expander(
        "☁️ Atualizar banco de dados",
        expanded=False,
    ):
        st.markdown("#### Banco de dados")

        try:
            synchronization_status = (
                GitHubBackupService
                .get_synchronization_status()
            )
        
            render_sync_indicator(
                synchronization_status
            )

        except GitHubBackupError as error:
            st.warning(
                "Não foi possível verificar a sincronização."
            )
        
            st.caption(str(error))

        database_info = (
            GitHubBackupService.get_local_database_info()
        )

        if not database_info["exists"]:
            st.error("Banco de dados não encontrado.")
            st.caption(database_info["path"])
            return

        modified_at = database_info["modified_at"]

        st.caption(
            "Última atualização do banco: "
            f"{modified_at.strftime('%d/%m/%Y às %H:%M')}"
        )

        # st.caption(
        #     "Tamanho: "
        #     f"{format_file_size(database_info['size_bytes'])}"
        # )

        admin_password = st.text_input(
            "Senha administrativa",
            type="password",
            key="database_backup_admin_password",
            placeholder="Informe a senha",
        )

        password_is_valid = validate_admin_password(
            admin_password
        )

        if admin_password and not password_is_valid:
            st.error("Senha administrativa incorreta.")

        commit_message = st.text_input(
            "Descrição do backup",
            value=(
                "Backup do banco BECCS - "
                f"{datetime.now().strftime('%d/%m/%Y')}"
            ),
            disabled=not password_is_valid,
            key="database_backup_commit_message",
        )

        confirmation = st.checkbox(
            "Confirmo o envio do banco ao GitHub",
            disabled=not password_is_valid,
            key="database_backup_confirmation",
        )

        if st.button(
            "☁️ Salvar banco no GitHub",
            type="primary",
            use_container_width=True,
            disabled=(
                not password_is_valid
                or not confirmation
            ),
        ):
            try:
                with st.spinner(
                    "Criando backup e enviando ao GitHub..."
                ):
                    result = (
                        GitHubBackupService.upload_database(
                            commit_message=commit_message
                        )
                    )

                st.session_state[
                    "github_database_backup_success"
                ] = {
                    "date": result[
                        "backup_at"
                    ].strftime(
                        "%d/%m/%Y às %H:%M:%S"
                    ),
                    "commit_url": result[
                        "commit_url"
                    ],
                }

                st.success(
                    "Banco enviado ao GitHub. "
                    "O aplicativo poderá reiniciar para "
                    "realizar o novo deploy."
                )

                # if result["commit_url"]:
                #     st.link_button(
                #         "Ver commit no GitHub",
                #         result["commit_url"],
                #         use_container_width=True,
                #     )

            except GitHubBackupError as error:
                st.error(str(error))

            except Exception as error:
                st.error(
                    "Erro inesperado durante o backup: "
                    f"{error}"
                )

        # st.divider()

        # st.caption("Backup manual")

        # try:
        #     database_bytes = DB_PATH.read_bytes()

        #     st.download_button(
        #         "💾 Baixar arquivo .db",
        #         data=database_bytes,
        #         file_name=(
        #             "beccs_backup_"
        #             f"{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
        #             ".db"
        #         ),
        #         mime="application/octet-stream",
        #         use_container_width=True,
        #     )

        # except OSError as error:
        #     st.error(
        #         f"Não foi possível ler o banco: {error}"
        #     )

        # st.warning(
        #     "Faça a sincronização depois de cadastrar ou "
        #     "editar informações importantes."
        # )
