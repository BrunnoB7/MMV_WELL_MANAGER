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


def render_database_backup():
    with st.sidebar.expander(
        "☁️ Atualizar banco de dados",
        expanded=False,
    ):
        st.markdown("#### Banco de dados")

        database_info = (
            GitHubBackupService.get_local_database_info()
        )

        if not database_info["exists"]:
            st.error("Banco de dados não encontrado.")
            st.caption(database_info["path"])
            return

        modified_at = database_info["modified_at"]

        st.caption(
            "Última alteração local: "
            f"{modified_at.strftime('%d/%m/%Y às %H:%M')}"
        )

        st.caption(
            "Tamanho: "
            f"{format_file_size(database_info['size_bytes'])}"
        )

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

                if result["commit_url"]:
                    st.link_button(
                        "Ver commit no GitHub",
                        result["commit_url"],
                        use_container_width=True,
                    )

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
