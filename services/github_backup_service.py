import base64
import hashlib
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

from database.database import DB_PATH


class GitHubBackupError(Exception):
    """Erro relacionado ao backup do SQLite no GitHub."""


class GitHubBackupService:
    API_BASE_URL = "https://api.github.com"
    API_VERSION = "2022-11-28"

    @staticmethod
    def _get_settings() -> dict[str, str]:
        try:
            settings = st.secrets["github_backup"]

            required_keys = [
                "token",
                "owner",
                "repo",
                "branch",
                "database_path",
            ]

            missing_keys = [
                key
                for key in required_keys
                if not settings.get(key)
            ]

            if missing_keys:
                missing = ", ".join(missing_keys)

                raise GitHubBackupError(
                    f"Configurações ausentes nos Secrets: {missing}."
                )

            return {
                "token": str(settings["token"]),
                "owner": str(settings["owner"]),
                "repo": str(settings["repo"]),
                "branch": str(settings["branch"]),
                "database_path": str(
                    settings["database_path"]
                ),
            }

        except KeyError as error:
            raise GitHubBackupError(
                "A seção [github_backup] não foi encontrada "
                "nos Secrets do Streamlit."
            ) from error

    @staticmethod
    def _get_headers(token: str) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": (
                GitHubBackupService.API_VERSION
            ),
        }

    @staticmethod
    def _get_contents_url(
        owner: str,
        repo: str,
        database_path: str,
    ) -> str:
        normalized_path = database_path.strip("/")

        return (
            f"{GitHubBackupService.API_BASE_URL}"
            f"/repos/{owner}/{repo}/contents/{normalized_path}"
        )

    @staticmethod
    def _create_consistent_database_copy() -> Path:
        """
        Cria uma cópia consistente do banco usando a API
        de backup do SQLite.

        Isso é mais seguro do que simplesmente ler o arquivo
        enquanto o aplicativo pode estar escrevendo nele.
        """
        if not DB_PATH.exists():
            raise GitHubBackupError(
                f"Banco não encontrado em: {DB_PATH}"
            )

        temporary_file = tempfile.NamedTemporaryFile(
            suffix=".db",
            delete=False,
        )

        temporary_path = Path(temporary_file.name)
        temporary_file.close()

        source_connection = None
        backup_connection = None

        try:
            source_connection = sqlite3.connect(
                str(DB_PATH),
                timeout=30,
            )

            backup_connection = sqlite3.connect(
                str(temporary_path),
                timeout=30,
            )

            source_connection.backup(
                backup_connection,
                pages=100,
            )

            backup_connection.commit()

            return temporary_path

        except sqlite3.Error as error:
            temporary_path.unlink(missing_ok=True)

            raise GitHubBackupError(
                f"Não foi possível criar a cópia do banco: "
                f"{error}"
            ) from error

        finally:
            if backup_connection:
                backup_connection.close()

            if source_connection:
                source_connection.close()

    @staticmethod
    def _get_remote_file() -> dict[str, Any] | None:
        settings = GitHubBackupService._get_settings()

        url = GitHubBackupService._get_contents_url(
            owner=settings["owner"],
            repo=settings["repo"],
            database_path=settings["database_path"],
        )

        response = requests.get(
            url,
            headers=GitHubBackupService._get_headers(
                settings["token"]
            ),
            params={
                "ref": settings["branch"],
            },
            timeout=30,
        )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            GitHubBackupService._raise_api_error(
                response=response,
                operation="consultar o banco no GitHub",
            )

        return response.json()

    @staticmethod
    def _raise_api_error(
        response: requests.Response,
        operation: str,
    ) -> None:
        try:
            response_data = response.json()
            github_message = response_data.get(
                "message",
                response.text,
            )
        except ValueError:
            github_message = response.text

        if response.status_code == 401:
            explanation = (
                "Token inválido ou expirado."
            )

        elif response.status_code == 403:
            explanation = (
                "O token não possui permissão de escrita ou "
                "a branch está protegida."
            )

        elif response.status_code == 404:
            explanation = (
                "Repositório, branch ou caminho não encontrado."
            )

        elif response.status_code == 409:
            explanation = (
                "Houve um conflito ao atualizar o arquivo. "
                "Tente novamente."
            )

        elif response.status_code == 422:
            explanation = (
                "O GitHub rejeitou os dados enviados. Confira "
                "o repositório, a branch e o SHA do arquivo."
            )

        else:
            explanation = "Erro retornado pela API do GitHub."

        raise GitHubBackupError(
            f"Não foi possível {operation}. "
            f"{explanation} "
            f"GitHub: {github_message}"
        )

    @staticmethod
    def get_local_database_info() -> dict[str, Any]:
        if not DB_PATH.exists():
            return {
                "exists": False,
                "path": str(DB_PATH),
                "size_bytes": 0,
                "modified_at": None,
                "hash": None,
            }

        database_bytes = DB_PATH.read_bytes()

        modified_at = datetime.fromtimestamp(
            DB_PATH.stat().st_mtime
        )

        return {
            "exists": True,
            "path": str(DB_PATH),
            "size_bytes": len(database_bytes),
            "modified_at": modified_at,
            "hash": hashlib.sha256(
                database_bytes
            ).hexdigest(),
        }


@staticmethod
def _calculate_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

@staticmethod
def _calculate_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


@staticmethod
def get_remote_database_info() -> dict[str, Any]:
    """
    Consulta o banco salvo no GitHub e retorna
    informações para comparação com o banco local.
    """
    settings = GitHubBackupService._get_settings()

    url = GitHubBackupService._get_contents_url(
        owner=settings["owner"],
        repo=settings["repo"],
        database_path=settings["database_path"],
    )

    try:
        response = requests.get(
            url,
            headers=GitHubBackupService._get_headers(
                settings["token"]
            ),
            params={
                "ref": settings["branch"],
            },
            timeout=30,
        )

        if response.status_code == 404:
            return {
                "exists": False,
                "hash": None,
                "size_bytes": 0,
                "sha": None,
            }

        if response.status_code != 200:
            GitHubBackupService._raise_api_error(
                response=response,
                operation="consultar o banco no GitHub",
            )

        response_data = response.json()

        encoded_content = response_data.get("content")

        if not encoded_content:
            raise GitHubBackupError(
                "O GitHub não retornou o conteúdo do banco."
            )

        normalized_content = encoded_content.replace(
            "\n",
            "",
        )

        database_bytes = base64.b64decode(
            normalized_content
        )

        return {
            "exists": True,
            "hash": GitHubBackupService._calculate_hash(
                database_bytes
            ),
            "size_bytes": len(database_bytes),
            "sha": response_data.get("sha"),
            "html_url": response_data.get("html_url"),
        }

    except requests.RequestException as error:
        raise GitHubBackupError(
            "Não foi possível consultar o banco no GitHub. "
            f"Detalhes: {error}"
        ) from error


@staticmethod
def get_synchronization_status() -> dict[str, Any]:
    """
    Compara o banco local com o banco salvo no GitHub.
    """
    local_info = (
        GitHubBackupService.get_local_database_info()
    )

    if not local_info["exists"]:
        return {
            "status": "local_missing",
            "is_synced": False,
            "message": "Banco local não encontrado",
            "local": local_info,
            "remote": None,
        }

    remote_info = (
        GitHubBackupService.get_remote_database_info()
    )

    if not remote_info["exists"]:
        return {
            "status": "remote_missing",
            "is_synced": False,
            "message": "Banco ainda não salvo no GitHub",
            "local": local_info,
            "remote": remote_info,
        }

    is_synced = (
        local_info["hash"]
        == remote_info["hash"]
    )

    return {
        "status": (
            "synced"
            if is_synced
            else "not_synced"
        ),
        "is_synced": is_synced,
        "message": (
            "Banco sincronizado"
            if is_synced
            else "Alterações não sincronizadas"
        ),
        "local": local_info,
        "remote": remote_info,
    }
    
@staticmethod
def get_remote_database_info() -> dict[str, Any]:
    """
    Consulta o banco salvo no GitHub e retorna
    informações para comparação com o banco local.
    """
    settings = GitHubBackupService._get_settings()

    url = GitHubBackupService._get_contents_url(
        owner=settings["owner"],
        repo=settings["repo"],
        database_path=settings["database_path"],
    )

    try:
        response = requests.get(
            url,
            headers=GitHubBackupService._get_headers(
                settings["token"]
            ),
            params={
                "ref": settings["branch"],
            },
            timeout=30,
        )

        if response.status_code == 404:
            return {
                "exists": False,
                "hash": None,
                "size_bytes": 0,
                "sha": None,
            }

        if response.status_code != 200:
            GitHubBackupService._raise_api_error(
                response=response,
                operation="consultar o banco no GitHub",
            )

        response_data = response.json()

        encoded_content = response_data.get("content")

        if not encoded_content:
            raise GitHubBackupError(
                "O GitHub não retornou o conteúdo do banco."
            )

        normalized_content = encoded_content.replace(
            "\n",
            "",
        )

        database_bytes = base64.b64decode(
            normalized_content
        )

        return {
            "exists": True,
            "hash": GitHubBackupService._calculate_hash(
                database_bytes
            ),
            "size_bytes": len(database_bytes),
            "sha": response_data.get("sha"),
            "html_url": response_data.get("html_url"),
        }

    except requests.RequestException as error:
        raise GitHubBackupError(
            "Não foi possível consultar o banco no GitHub. "
            f"Detalhes: {error}"
        ) from error
    
    @staticmethod
    def upload_database(
        commit_message: str | None = None,
    ) -> dict[str, Any]:
        settings = GitHubBackupService._get_settings()
        temporary_path = (
            GitHubBackupService
            ._create_consistent_database_copy()
        )

        try:
            database_bytes = temporary_path.read_bytes()
            encoded_content = base64.b64encode(
                database_bytes
            ).decode("utf-8")

            remote_file = (
                GitHubBackupService._get_remote_file()
            )

            now = datetime.now()

            payload: dict[str, Any] = {
                "message": (
                    commit_message.strip()
                    if commit_message
                    else (
                        "Backup automático do banco BECCS - "
                        f"{now.strftime('%d/%m/%Y %H:%M:%S')}"
                    )
                ),
                "content": encoded_content,
                "branch": settings["branch"],
            }

            if remote_file:
                payload["sha"] = remote_file["sha"]

            url = GitHubBackupService._get_contents_url(
                owner=settings["owner"],
                repo=settings["repo"],
                database_path=settings["database_path"],
            )

            response = requests.put(
                url,
                headers=GitHubBackupService._get_headers(
                    settings["token"]
                ),
                json=payload,
                timeout=120,
            )

            if response.status_code not in (200, 201):
                GitHubBackupService._raise_api_error(
                    response=response,
                    operation="salvar o banco no GitHub",
                )

            result = response.json()
            commit = result.get("commit", {})
            content = result.get("content", {})

            return {
                "success": True,
                "commit_sha": commit.get("sha"),
                "commit_url": commit.get("html_url"),
                "file_url": content.get("html_url"),
                "database_size_bytes": len(
                    database_bytes
                ),
                "backup_at": now,
                "created_file": remote_file is None,
            }

        except requests.RequestException as error:
            raise GitHubBackupError(
                "Não foi possível conectar à API do GitHub. "
                f"Detalhes: {error}"
            ) from error

        finally:
            temporary_path.unlink(missing_ok=True)
