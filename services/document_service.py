from datetime import datetime

from repositories.document_repository import DocumentRepository


class DocumentService:

    @staticmethod
    def get_all_folders():
        return DocumentRepository.get_all()

    @staticmethod
    def get_folder(folder_id):
        return DocumentRepository.get_by_id(folder_id)

    @staticmethod
    def get_disciplines():
        return DocumentRepository.get_disciplines()

    @staticmethod
    def validate_drive_link(drive_link):
        valid_prefixes = (
            "https://drive.google.com/",
            "https://docs.google.com/",
        )

        return drive_link.startswith(valid_prefixes)

    @staticmethod
    def create_folder(
        name,
        discipline,
        description,
        drive_link,
        responsible,
    ):
        name = name.strip()
        drive_link = drive_link.strip()

        if not name:
            raise ValueError("Informe o nome da pasta.")

        if not drive_link:
            raise ValueError("Informe o link do Google Drive.")

        if not DocumentService.validate_drive_link(drive_link):
            raise ValueError(
                "Informe um link válido do Google Drive."
            )

        return DocumentRepository.insert(
            name=name,
            discipline=discipline.strip(),
            description=description.strip(),
            drive_link=drive_link,
            responsible=responsible.strip(),
            updated_at=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )

    @staticmethod
    def update_folder(
        folder_id,
        name,
        discipline,
        description,
        drive_link,
        responsible,
    ):
        name = name.strip()
        drive_link = drive_link.strip()

        if not name:
            raise ValueError("Informe o nome da pasta.")

        if not DocumentService.validate_drive_link(drive_link):
            raise ValueError(
                "Informe um link válido do Google Drive."
            )

        DocumentRepository.update(
            folder_id=folder_id,
            name=name,
            discipline=discipline.strip(),
            description=description.strip(),
            drive_link=drive_link,
            responsible=responsible.strip(),
            updated_at=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )

    @staticmethod
    def delete_folder(folder_id):
        DocumentRepository.delete(folder_id)