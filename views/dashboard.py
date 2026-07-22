from datetime import date
import pandas as pd
import streamlit as st

from services.dashboard_service import DashboardService


def parse_date(value, fallback):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return fallback


def format_date(value):
    if not value:
        return "-"

    try:
        return date.fromisoformat(value).strftime("%d/%m/%Y")
    except ValueError:
        return value


def metric_card(title, value, subtitle, icon):
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="dashboard-metric">
                <div class="metric-icon">{icon}</div>
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-subtitle">{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def load_dashboard_css():
    st.markdown(
        """
        <style>
            .dashboard-header {
                padding: 24px 28px;
                border: 1px solid rgba(128, 128, 128, 0.20);
                border-radius: 16px;
                margin-bottom: 20px;
                background: linear-gradient(
                    135deg,
                    rgba(15, 52, 96, 0.95),
                    rgba(16, 86, 82, 0.88)
                );
            }

            .dashboard-header h1 {
                color: white;
                margin: 0;
                font-size: 2rem;
            }

            .dashboard-header p {
                color: rgba(255, 255, 255, 0.82);
                margin: 6px 0 0 0;
            }

            .project-badge {
                display: inline-block;
                padding: 5px 11px;
                margin-top: 12px;
                margin-right: 6px;
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.14);
                color: white;
                font-size: 0.82rem;
            }

            .dashboard-metric {
                min-height: 130px;
            }

            .metric-icon {
                font-size: 1.4rem;
                margin-bottom: 5px;
            }

            .metric-title {
                font-size: 0.85rem;
                opacity: 0.72;
            }

            .metric-value {
                font-size: 2rem;
                font-weight: 700;
                line-height: 1.2;
                margin-top: 5px;
            }

            .metric-subtitle {
                font-size: 0.78rem;
                opacity: 0.65;
                margin-top: 5px;
            }

            .section-title {
                font-size: 1.12rem;
                font-weight: 650;
                margin-bottom: 10px;
            }

            .pending-item {
                padding: 11px 13px;
                margin-bottom: 8px;
                border-radius: 9px;
                border-left: 4px solid #ef4444;
                background: rgba(239, 68, 68, 0.08);
            }

            .priority-item {
                padding: 11px 13px;
                margin-bottom: 8px;
                border-radius: 9px;
                border-left: 4px solid #f59e0b;
                background: rgba(245, 158, 11, 0.08);
            }

            .item-title {
                font-weight: 650;
            }

            .item-details {
                font-size: 0.80rem;
                opacity: 0.70;
                margin-top: 3px;
            }
            
            .days-remaining-box {
                position: absolute;
                top: 24px;
                right: 28px;
                min-width: 145px;
                padding: 14px 18px;
                border-radius: 14px;
                background: rgba(255, 255, 255, 0.14);
                border: 1px solid rgba(255, 255, 255, 0.18);
                text-align: center;
                backdrop-filter: blur(4px);
            }
            
            .days-remaining-number {
                color: white;
                font-size: 2.4rem;
                font-weight: 750;
                line-height: 1;
            }
            
            .days-remaining-label {
                color: rgba(255, 255, 255, 0.90);
                font-size: 0.82rem;
                font-weight: 600;
                margin-top: 6px;
            }
            
            .days-remaining-date {
                color: rgba(255, 255, 255, 0.68);
                font-size: 0.72rem;
                margin-top: 5px;
            }
            
            @media (max-width: 800px) {
                .dashboard-header {
                    padding-right: 28px;
                }
            
                .days-remaining-box {
                    position: static;
                    margin-top: 18px;
                    max-width: 180px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def project_configuration(settings):
    with st.expander("⚙️ Configurar informações do projeto"):
        with st.form("project_settings_form"):
            col1, col2 = st.columns(2)

            with col1:
                project_name = st.text_input(
                    "Nome do projeto",
                    value=settings.get(
                        "project_name",
                        "BECCS Baseline Manager",
                    ),
                )

                subtitle = st.text_input(
                    "Área ou subtítulo",
                    value=settings.get(
                        "subtitle",
                        "Performance & Well Integrity",
                    ),
                )

                client = st.text_input(
                    "Cliente",
                    value=settings.get("client", ""),
                )

                project_manager = st.text_input(
                    "Coordenador",
                    value=settings.get("project_manager", ""),
                )

            with col2:
                phase = st.text_input(
                    "Fase atual",
                    value=settings.get("phase", ""),
                )

                start_date = st.date_input(
                    "Data de início",
                    value=parse_date(
                        settings.get("start_date"),
                        date.today(),
                    ),
                    format="DD/MM/YYYY",
                )

                end_date = st.date_input(
                    "Data de término",
                    value=parse_date(
                        settings.get("end_date"),
                        date.today(),
                    ),
                    format="DD/MM/YYYY",
                )

                drive_link = st.text_input(
                    "Link da pasta principal do Google Drive",
                    value=settings.get("drive_link", ""),
                    placeholder="https://drive.google.com/drive/folders/...",
                )

            submitted = st.form_submit_button(
                "Salvar configurações",
                use_container_width=True,
            )

            if submitted:
                if end_date < start_date:
                    st.error(
                        "A data de término não pode ser anterior "
                        "à data de início."
                    )
                    return

                DashboardService.update_project_settings(
                    project_name=project_name.strip(),
                    subtitle=subtitle.strip(),
                    client=client.strip(),
                    project_manager=project_manager.strip(),
                    phase=phase.strip(),
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    drive_link=drive_link.strip(),
                )

                st.success("Configurações atualizadas.")
                st.rerun()


def dashboard():
    load_dashboard_css()

    settings = DashboardService.get_project_settings()
    kpis = DashboardService.get_kpis()

    days_remaining = DashboardService.get_days_remaining(
        settings.get("end_date")
    )

    in_progress_activities = (
    DashboardService.get_in_progress_activities()
)
    pending = DashboardService.get_critical_pending()
    priorities = DashboardService.get_priorities()

    # =====================================================
    # CABEÇALHO
    # =====================================================

    project_name = settings.get(
        "project_name",
        "BECCS Baseline Manager"
    )

    subtitle = settings.get(
        "subtitle",
        "Performance & Well Integrity"
    )

    client = settings.get("client") or "Não definido"
    phase = settings.get("phase") or "Não definida"

    project_manager = (
            settings.get("project_manager")
            or "Não definida"
    )
# format_date(settings.get('end_date'))
    header_html = (
        '<div class="dashboard-header">'

        '<div class="days-remaining-box">'
        f'<div class="days-remaining-number">{days_remaining}</div>'
        '<div class="days-remaining-label">dias restantes</div>'
        f'<div class="days-remaining-date">'
        f'Término em {format_date(settings.get("end_date"))}'
        '</div>'
        '</div>'
        f'<h1>🌱 {project_name}</h1>'
        f'<p>{subtitle}</p>'
        '<div class="project-badges">'
        f'<span class="project-badge">Cliente: {client}</span>'
        f'<span class="project-badge">Fase: {phase}</span>'
        f'<span class="project-badge">'
        f'Coordenação: {project_manager}'
        '</span>'
        '</div>'
        '</div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True
    )
    project_configuration(settings)

    # =====================================================
    # PROGRESSO GERAL
    # =====================================================

    progress = max(
        0,
        min(100, kpis["average_progress"]),
    )

    progress_col, dates_col = st.columns([3, 1])

    with st.container(border=True):
        st.markdown(
            '<div class="section-title">'
            "Progresso geral do projeto"
            "</div>",
            unsafe_allow_html=True,
        )

        st.progress(progress / 100)
        st.caption(
            f"{progress}% concluído com base na média "
            "dos deliverables."
        )

    # with dates_col:
    #     with st.container(border=True):
    #         if days_remaining is None:
    #             days_text = "-"
    #             days_caption = "Data final não configurada"
    #         elif days_remaining >= 0:
    #             days_text = str(days_remaining)
    #             days_caption = (
    #                 f"Término em "
    #                 f"{format_date(settings.get('end_date'))}"
    #             )
    #         else:
    #             days_text = str(abs(days_remaining))
    #             days_caption = "dias após o prazo previsto"
    #
    #         st.caption(days_caption)

    # =====================================================
    # KPIs
    # =====================================================

    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Tarefass",
            kpis["total"],
            "Total cadastrado",
            "📋",
        )

    with c2:
        metric_card(
            "Em andamento",
            kpis["in_progress"],
            "Trabalhos ativos",
            "🚧",
        )

    with c3:
        metric_card(
            "Concluídos",
            kpis["completed"],
            "Progresso de 100%",
            "✅",
        )

    with c4:
        metric_card(
            "Atrasados",
            kpis["delayed"],
            "Prazo vencido",
            "🔴",
        )

    st.write("")

    # =====================================================
    # MARCOS E PENDÊNCIAS
    # =====================================================

    esquerda, direita = st.columns([1.7, 1])

    with esquerda:
        with st.container(border=True):
            st.markdown(
                (
                    '<div class="section-title">'
                    "🚧 Atividades em andamento"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
    
            if in_progress_activities:
                activities_df = pd.DataFrame(
                    in_progress_activities
                )
    
                activities_df["deadline"] = (
                    activities_df["deadline"]
                    .apply(format_date)
                )
    
                activities_df["progress"] = (
                    pd.to_numeric(
                        activities_df["progress"],
                        errors="coerce",
                    )
                    .fillna(0)
                    .clip(0, 100)
                    .astype(int)
                )
    
                activities_df = activities_df[
                    [
                        "title",
                        "discipline",
                        "progress",
                        "manager",
                        "deadline",
                    ]
                ]
    
                activities_df.columns = [
                    "Atividade",
                    "Disciplina",
                    "Progresso",
                    "Responsável",
                    "Prazo",
                ]
    
                st.dataframe(
                    activities_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Atividade": st.column_config.TextColumn(
                            "Atividade",
                            width="large",
                        ),
                        "Disciplina": st.column_config.TextColumn(
                            "Disciplina",
                            width="medium",
                        ),
                        "Progresso": (
                            st.column_config.ProgressColumn(
                                "Progresso",
                                min_value=0,
                                max_value=100,
                                format="%d%%",
                            )
                        ),
                        "Responsável": (
                            st.column_config.TextColumn(
                                "Responsável",
                                width="medium",
                            )
                        ),
                        "Prazo": st.column_config.TextColumn(
                            "Prazo",
                            width="small",
                        ),
                    },
                )
    
                st.caption(
                    f"{len(in_progress_activities)} "
                    "atividade(s) em execução."
                )
    
            else:
                st.info(
                    "Nenhuma atividade está com o status "
                    "'Em andamento'."
                )

    with direita:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title">'
                "⚠️ Pendências críticas"
                "</div>",
                unsafe_allow_html=True,
            )

            if pending:
                for item in pending:
                    st.markdown(
                        (
                            '<div class="priority-item">'
                            f'<div class="item-title">{item["title"]}</div>'
                            '<div class="item-details">'
                            f'{item["discipline"]}<br>'
                            f'Responsável: {item["manager"]}<br>'
                            f'Prazo: {item["deadline"]}'
                            '</div>'
                            '</div>'
                        ),
                        unsafe_allow_html=True,
                    )
            else:
                st.success("Nenhuma pendência atrasada.")

    # =====================================================
    # PRIORIDADES
    # =====================================================

    st.write("")

    with st.container(border=True):
        st.markdown(
            '<div class="section-title">'
            "🎯 Próximas prioridades"
            "</div>",
            unsafe_allow_html=True,
        )

        if priorities:
            columns = st.columns(2)

            for index, item in enumerate(priorities):
                with columns[index % 2]:
                    title = item["title"]
                    priority = item["priority"] or "Não definida"
                    progress = item["progress"] or 0
                    deadline = format_date(item["deadline"])

                    priority_html = (
                        '<div class="priority-item">'
                        f'<div class="item-title">{title}</div>'
                        '<div class="item-details">'
                        f'<strong>Prioridade:</strong> {priority}<br>'
                        f'<strong>Progresso:</strong> {progress}%<br>'
                        f'<strong>Prazo:</strong> {deadline}'
                        '</div>'
                        '</div>'
                    )

                    st.markdown(
                        priority_html,
                        unsafe_allow_html=True
                    )
        else:
            st.info("Nenhum deliverable pendente.")

    # =====================================================
    # ACESSOS RÁPIDOS
    # =====================================================

    st.write("")

    with st.container(border=True):
        st.markdown(
            '<div class="section-title">'
            "🔗 Acessos rápidos"
            "</div>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if settings.get("drive_link"):
                st.link_button(
                    "📂 Abrir Google Drive",
                    settings["drive_link"],
                    use_container_width=True,
                )
            else:
                st.button(
                    "📂 Google Drive não configurado",
                    disabled=True,
                    use_container_width=True,
                )

        with col2:
            st.button(
                "📅 Cronograma disponível no menu",
                disabled=True,
                use_container_width=True,
            )

        with col3:
            st.button(
                "📦 Deliverables disponíveis no menu",
                disabled=True,
                use_container_width=True,
            )

    st.divider()

    st.caption(
        "BECCS Baseline Manager © 2026 · "
        "Dados atualizados automaticamente pelo SQLite"
    )
