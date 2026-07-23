from datetime import date, datetime

from config.team import TEAM_MEMBERS
from repositories.meeting_repository import (
    MeetingRepository,
)
from repositories.work_log_repository import (
    WorkLogRepository,
)


class WorkHoursService:

    @staticmethod
    def register_work_log(
        deliverable_id,
        collaborator,
        worked_hours,
        work_date,
        description="",
    ):
        if not deliverable_id:
            raise ValueError(
                "Deliverable não informado."
            )

        if collaborator not in TEAM_MEMBERS:
            raise ValueError(
                "Colaborador inválido."
            )

        try:
            worked_hours = float(worked_hours)
        except (TypeError, ValueError):
            raise ValueError(
                "Informe uma quantidade de horas válida."
            )

        if worked_hours <= 0:
            raise ValueError(
                "As horas devem ser maiores que zero."
            )

        normalized_date = (
            WorkHoursService.normalize_date(
                work_date
            )
        )

        return WorkLogRepository.create(
            deliverable_id=deliverable_id,
            collaborator=collaborator,
            worked_hours=worked_hours,
            work_date=normalized_date,
            description=str(
                description or ""
            ).strip(),
        )

    @staticmethod
    def delete_work_log(work_log_id):
        WorkLogRepository.delete(
            work_log_id
        )

    @staticmethod
    def get_deliverable_logs(
        deliverable_id
    ):
        return WorkLogRepository.get_by_deliverable(
            deliverable_id
        )

    @staticmethod
    def get_deliverable_summary(
        deliverable_id
    ):
        return (
            WorkLogRepository
            .get_summary_by_deliverable(
                deliverable_id
            )
        )

    @staticmethod
    def get_deliverable_total(
        deliverable_id
    ):
        return (
            WorkLogRepository
            .get_total_by_deliverable(
                deliverable_id
            )
        )

    @staticmethod
    def get_all_entries():
        entries = []

        entries.extend(
            WorkHoursService
            .get_deliverable_entries()
        )

        entries.extend(
            WorkHoursService
            .get_meeting_entries()
        )

        entries.sort(
            key=lambda item: (
                item.get("work_date") or "",
                item.get("collaborator") or "",
            ),
            reverse=True,
        )

        return entries

    @staticmethod
    def get_deliverable_entries():
        work_logs = (
            WorkLogRepository
            .get_all_with_deliverable()
        )

        entries = []

        for work_log in work_logs:
            entries.append(
                {
                    "entry_id": (
                        work_log.get("id")
                    ),
                    "source": "Deliverables",
                    "collaborator": (
                        work_log.get(
                            "collaborator"
                        )
                    ),
                    "worked_hours": float(
                        work_log.get(
                            "worked_hours"
                        ) or 0
                    ),
                    "work_date": (
                        work_log.get(
                            "work_date"
                        )
                    ),
                    "title": (
                        work_log.get(
                            "deliverable_title"
                        )
                        or "Sem título"
                    ),
                    "discipline": (
                        work_log.get(
                            "deliverable_discipline"
                        )
                        or "Não definida"
                    ),
                    "status": (
                        work_log.get(
                            "deliverable_status"
                        )
                        or ""
                    ),
                    "description": (
                        work_log.get(
                            "description"
                        )
                        or ""
                    ),
                    "deliverable_id": (
                        work_log.get(
                            "deliverable_id"
                        )
                    ),
                    "meeting_id": None,
                }
            )

        return entries

    @staticmethod
    def get_meeting_entries():
        meetings = MeetingRepository.get_completed()

        entries = []

        for meeting in meetings:
            status = str(
                meeting.get("status") or ""
            ).strip().lower()

            if status != "realizada":
                continue

            participants = (
                WorkHoursService
                .parse_participants(
                    meeting.get(
                        "participants"
                    )
                )
            )

            try:
                duration_minutes = int(
                    meeting.get(
                        "duration_minutes"
                    ) or 0
                )
            except (TypeError, ValueError):
                duration_minutes = 0

            worked_hours = (
                duration_minutes / 60
            )

            if worked_hours <= 0:
                continue

            for participant in participants:
                entries.append(
                    {
                        "entry_id": (
                            f"meeting_"
                            f"{meeting.get('id')}_"
                            f"{participant}"
                        ),
                        "source": "Reuniões",
                        "collaborator": participant,
                        "worked_hours": (
                            worked_hours
                        ),
                        "work_date": (
                            meeting.get(
                                "meeting_date"
                            )
                        ),
                        "title": (
                            meeting.get("title")
                            or "Sem título"
                        ),
                        "discipline": "Reunião",
                        "status": "Realizada",
                        "description": (
                            meeting.get(
                                "description"
                            )
                            or ""
                        ),
                        "deliverable_id": None,
                        "meeting_id": (
                            meeting.get("id")
                        ),
                    }
                )

        return entries

    @staticmethod
    def filter_entries(
        entries,
        start_date=None,
        end_date=None,
        collaborators=None,
        sources=None,
    ):
        collaborators = collaborators or []
        sources = sources or []

        filtered = []

        for entry in entries:
            entry_date = (
                WorkHoursService
                .parse_date(
                    entry.get("work_date")
                )
            )

            if entry_date is None:
                continue

            if (
                start_date
                and entry_date < start_date
            ):
                continue

            if (
                end_date
                and entry_date > end_date
            ):
                continue

            if (
                collaborators
                and entry.get("collaborator")
                not in collaborators
            ):
                continue

            if (
                sources
                and entry.get("source")
                not in sources
            ):
                continue

            filtered.append(entry)

        return filtered

    @staticmethod
    def parse_participants(value):
        if not value:
            return []

        participants = [
            participant.strip()
            for participant in str(value)
            .replace(";", ",")
            .split(",")
            if participant.strip()
        ]

        return [
            participant
            for participant in participants
            if participant in TEAM_MEMBERS
        ]

    @staticmethod
    def parse_date(value):
        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if not value:
            return None

        try:
            return date.fromisoformat(
                str(value)[:10]
            )
        except ValueError:
            return None

    @staticmethod
    def normalize_date(value):
        parsed_date = (
            WorkHoursService.parse_date(
                value
            )
        )

        if parsed_date is None:
            raise ValueError(
                "Informe uma data válida."
            )

        return parsed_date.isoformat()
