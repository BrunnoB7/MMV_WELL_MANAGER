from repositories.deliverable_repository import DeliverableRepository


class DeliverableService:

    @staticmethod
    def get_all_deliverables():
        return DeliverableRepository.get_all()


    @staticmethod
    def get_deliverable(deliverable_id):
        return DeliverableRepository.get_by_id(deliverable_id)


    @staticmethod
    def create_deliverable(
        title,
        discipline,
        description,
        manager,
        priority,
        status,
        progress,
        deadline,
        google_drive
    ):

        DeliverableRepository.insert(
            title,
            discipline,
            description,
            manager,
            priority,
            status,
            progress,
            deadline,
            google_drive
        )


    @staticmethod
    def delete_deliverable(deliverable_id):
        DeliverableRepository.delete(deliverable_id)


    @staticmethod
    def total_deliverables():

        return len(
            DeliverableRepository.get_all()
        )


    @staticmethod
    def total_completed():

        data = DeliverableRepository.get_all()

        return len(
            [d for d in data if d["status"] == "Concluído"]
        )


    @staticmethod
    def total_in_progress():

        data = DeliverableRepository.get_all()

        return len(
            [d for d in data if d["status"] == "Em andamento"]
        )

    @staticmethod
    def create_deliverable(
            title,
            discipline,
            description,
            manager,
            priority,
            status,
            progress,
            deadline,
            google_drive,
    ):
        title = title.strip()

        if not title:
            raise ValueError("O título do deliverable é obrigatório.")

        progress = int(progress)
        progress = max(0, min(100, progress))

        if progress >= 100:
            progress = 100
            status = "Concluído"

        elif status == "Concluído":
            progress = 100

        elif progress > 0 and status == "Não iniciado":
            status = "Em andamento"

        DeliverableRepository.insert(
            title=title,
            discipline=discipline.strip(),
            description=description.strip(),
            manager=manager.strip(),
            priority=priority,
            status=status,
            progress=progress,
            deadline=deadline,
            google_drive=google_drive.strip(),
        )

    @staticmethod
    def update_deliverable(
        deliverable_id,
        title,
        discipline,
        description,
        manager,
        priority,
        status,
        progress,
        deadline,
        google_drive,
    ):
        title = title.strip()

        if not title:
            raise ValueError("O título do deliverable é obrigatório.")

        progress = int(progress)
        progress = max(0, min(100, progress))

        # Mantém status e progresso coerentes.
        if progress >= 100:
            progress = 100
            status = "Concluído"

        elif status == "Concluído":
            progress = 100

        elif progress > 0 and status == "Não iniciado":
            status = "Em andamento"

        DeliverableRepository.update(
            deliverable_id=deliverable_id,
            title=title,
            discipline=discipline.strip(),
            description=description.strip(),
            manager=manager.strip(),
            priority=priority,
            status=status,
            progress=progress,
            deadline=deadline,
            google_drive=google_drive.strip(),
        )


    @staticmethod
    def get_disciplines():
        return DeliverableRepository.get_disciplines()


    @staticmethod
    def total_not_started():

        data = DeliverableRepository.get_all()

        return len(
            [d for d in data if d["status"] == "Não iniciado"]
        )