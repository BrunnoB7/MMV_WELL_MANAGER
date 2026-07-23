from datetime import date, datetime

from repositories.meeting_repository import (
    MeetingRepository,
)


class MeetingService:

    VALID_STATUSES = [
        "Agendada",
        "Realizada",
        "Cancelada",
    ]

    @staticmethod
    def get_all():
        return MeetingRepository.get_all()

    @staticmethod
    def get_scheduled():
        meetings = MeetingRepository.get_scheduled()

        today = date.today()

        return [
            meeting
            for meeting in meetings
            if MeetingService.parse_date(
                meeting.get("meeting_date")
            ) >= today
        ]

    @staticmethod
    def get_completed():
        return MeetingRepository.get_completed()

    @staticmethod
    def get_by_date(meeting_date):
        if isinstance(meeting_date, date):
            meeting_date = meeting_date.isoformat()

        return MeetingRepository.get_by_date(
            meeting_date
        )

    @staticmethod
    def create_meeting(
        title,
        meeting_date,
        start_time,
        duration_minutes,
        participants,
        description,
        recording_link,
        status,
    ):
        MeetingService.validate(
            title=title,
            meeting_date=meeting_date,
            start_time=start_time,
            duration_minutes=duration_minutes,
            status=status,
        )

        return MeetingRepository.insert(
            title=title.strip(),
            meeting_date=MeetingService.normalize_date(
                meeting_date
            ),
            start_time=MeetingService.normalize_time(
                start_time
            ),
            duration_minutes=int(duration_minutes),
            participants=participants.strip(),
            description=description.strip(),
            recording_link=recording_link.strip(),
            status=status,
        )

    @staticmethod
    def update_meeting(
        meeting_id,
        title,
        meeting_date,
        start_time,
        duration_minutes,
        participants,
        description,
        recording_link,
        status,
    ):
        MeetingService.validate(
            title=title,
            meeting_date=meeting_date,
            start_time=start_time,
            duration_minutes=duration_minutes,
            status=status,
        )

        MeetingRepository.update(
            meeting_id=meeting_id,
            title=title.strip(),
            meeting_date=MeetingService.normalize_date(
                meeting_date
            ),
            start_time=MeetingService.normalize_time(
                start_time
            ),
            duration_minutes=int(duration_minutes),
            participants=participants.strip(),
            description=description.strip(),
            recording_link=recording_link.strip(),
            status=status,
        )

    @staticmethod
    def delete_meeting(meeting_id):
        MeetingRepository.delete(meeting_id)

    @staticmethod
    def validate(
        title,
        meeting_date,
        start_time,
        duration_minutes,
        status,
    ):
        if not str(title).strip():
            raise ValueError(
                "Informe o título da reunião."
            )

        if not meeting_date:
            raise ValueError(
                "Informe a data da reunião."
            )

        if not start_time:
            raise ValueError(
                "Informe o horário da reunião."
            )

        if int(duration_minutes) <= 0:
            raise ValueError(
                "A duração deve ser maior que zero."
            )

        if status not in MeetingService.VALID_STATUSES:
            raise ValueError(
                "Status da reunião inválido."
            )

    @staticmethod
    def normalize_date(value):
        if isinstance(value, datetime):
            return value.date().isoformat()

        if isinstance(value, date):
            return value.isoformat()

        return str(value)

    @staticmethod
    def normalize_time(value):
        if hasattr(value, "strftime"):
            return value.strftime("%H:%M")

        return str(value)[:5]

    @staticmethod
    def parse_date(value):
        if isinstance(value, date):
            return value

        return date.fromisoformat(str(value))
