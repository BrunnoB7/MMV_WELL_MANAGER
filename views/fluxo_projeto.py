import streamlit as st


# =========================================================
# CONFIGURAÇÕES EDITÁVEIS
# =========================================================

# Altere este número para definir a etapa atual do projeto.
CURRENT_PHASE_ID = 1

PROJECT_FLOW = [
    {
        "id": 1,
        "title": "Baseline e Indicadores",
        "short_title": "Baseline",
        "group": "Antes da injeção",
        "description": (
            "Estabelecimento da baseline técnica e definição dos "
            "indicadores de performance e integridade dos poços."
        ),
        "responsible": "Equipe de Performance e Integridade",
        "deliverable": "Relatório de Baseline e matriz de indicadores do MMV para poço",
    },
    {
        "id": 2,
        "title": "Dashboard de acompanhamento",
        "short_title": "Dashboard",
        "group": "Antes da injeção",
        "description": (
            "Desenvolvimento do painel para acompanhamento dos "
            "parâmetros operacionais, de performance e de injeção."
        ),
        "responsible": "Coordenação do projeto",
        "deliverable": "Dashboard de acompanhamento operacional",
    },
    {
        "id": 3,
        "title": "Ações de contingência",
        "short_title": "Contingência",
        "group": "Antes da injeção",
        "description": (
            "Definição das ações e procedimentos de contingência "
            "aplicáveis aos possíveis desvios operacionais."
        ),
        "responsible": "Equipe técnica",
        "deliverable": "Plano de ações de contingência",
    },
    {
        "id": 4,
        "title": "Integridade das barreiras",
        "short_title": "Integridade",
        "group": "Antes da injeção",
        "description": (
            "Definição dos critérios para avaliação da integridade "
            "das barreiras de segurança dos poços."
        ),
        "responsible": "Equipe de Integridade",
        "deliverable": "Critérios de avaliação das barreiras",
    },
    {
        "id": 5,
        "title": "Programa de monitoramento",
        "short_title": "Monitoramento",
        "group": "Antes da injeção",
        "description": (
            "Elaboração do programa de monitoramento dos poços "
            "injetor e monitor."
        ),
        "responsible": "Equipe de Monitoramento",
        "deliverable": "Programa de monitoramento dos poços",
    },
]

OPERATION_FLOW = [
    {
        "id": 6,
        "title": "Atividades diárias",
        "frequency": "Diária",
        "description": (
            "Recebimento, armazenamento, avaliação e validação "
            "dos dados dos sensores."
        ),
        "responsible": "Equipe operacional",
    },
    {
        "id": 7,
        "title": "Atividades semanais",
        "frequency": "Semanal",
        "description": (
            "Acompanhamento dos parâmetros de injeção, análise "
            "da operação e recomendação de ações."
        ),
        "responsible": "Equipe de Performance",
    },
    {
        "id": 8,
        "title": "Atividades mensais",
        "frequency": "Mensal",
        "description": (
            "Consolidação das evidências técnicas e elaboração "
            "do relatório de performance e integridade."
        ),
        "responsible": "Coordenação técnica",
    },
    {
        "id": 9,
        "title": "Avaliações periódicas",
        "frequency": "Periódica",
        "description": (
            "Avaliação da integridade dos poços, intervenções "
            "e emissão dos relatórios aplicáveis."
        ),
        "responsible": "Equipe de Integridade",
    },
]


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def get_status(phase_id: int) -> str:
    if phase_id < CURRENT_PHASE_ID:
        return "Concluído"

    if phase_id == CURRENT_PHASE_ID:
        return "Em andamento"

    return "Não iniciado"


def get_status_class(phase_id: int) -> str:
    status = get_status(phase_id)

    classes = {
        "Concluído": "completed",
        "Em andamento": "current",
        "Não iniciado": "pending",
    }

    return classes[status]


def load_css():
    st.markdown(
        """
        <style>
            .flow-page-header {
                padding: 24px 28px;
                margin-bottom: 22px;
                border-radius: 14px;
                background: linear-gradient(135deg, #8f0000, #d71920);
                color: white;
            }

            .flow-page-header h1 {
                margin: 0;
                font-size: 2rem;
            }

            .flow-page-header p {
                margin: 8px 0 0 0;
                opacity: 0.88;
            }

            .phase-section {
                margin-top: 18px;
                padding: 18px 22px;
                border: 1px solid rgba(128, 128, 128, 0.25);
                border-radius: 14px;
                background: rgba(128, 128, 128, 0.04);
            }

            .phase-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 15px;
                margin-bottom: 28px;
            }

            .phase-title {
                font-size: 1.15rem;
                font-weight: 750;
            }

            .phase-duration {
                padding: 6px 13px;
                border-radius: 18px;
                background: rgba(215, 25, 32, 0.12);
                color: #d71920;
                font-size: 0.82rem;
                font-weight: 700;
            }

            .timeline {
                display: flex;
                align-items: flex-start;
                width: 100%;
                overflow-x: auto;
                padding: 12px 4px 20px 4px;
            }

            .timeline-step {
                position: relative;
                flex: 1;
                min-width: 145px;
                text-align: center;
            }

            .timeline-step:not(:last-child)::after {
                content: "";
                position: absolute;
                top: 20px;
                left: 50%;
                width: 100%;
                height: 4px;
                background: #bdbdbd;
                z-index: 0;
            }

            .timeline-step.completed:not(:last-child)::after {
                background: #555555;
            }

            .timeline-step.current:not(:last-child)::after {
                background: linear-gradient(
                    90deg,
                    #d71920 0%,
                    #d71920 50%,
                    #bdbdbd 50%,
                    #bdbdbd 100%
                );
            }

            .timeline-circle {
                position: relative;
                z-index: 2;
                display: flex;
                width: 42px;
                height: 42px;
                margin: 0 auto 12px auto;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                border: 4px solid #bdbdbd;
                background: white;
                color: #888888;
                font-weight: 800;
            }

            .timeline-step.completed .timeline-circle {
                border-color: #555555;
                background: #555555;
                color: white;
            }

            .timeline-step.current .timeline-circle {
                border-color: #d71920;
                background: #d71920;
                color: white;
                box-shadow: 0 0 0 7px rgba(215, 25, 32, 0.14);
            }

            .timeline-label {
                padding: 0 8px;
                font-size: 0.88rem;
                font-weight: 700;
                line-height: 1.3;
            }

            .timeline-status {
                margin-top: 6px;
                font-size: 0.72rem;
                font-weight: 700;
                color: #999999;
            }

            .timeline-step.completed .timeline-status {
                color: #555555;
            }

            .timeline-step.current .timeline-status {
                color: #d71920;
            }

            .current-phase-panel {
                padding: 20px 22px;
                margin-top: 22px;
                border-left: 6px solid #d71920;
                border-radius: 10px;
                background: rgba(215, 25, 32, 0.07);
            }

            .current-phase-label {
                color: #d71920;
                font-size: 0.78rem;
                font-weight: 800;
                text-transform: uppercase;
            }

            .current-phase-title {
                margin-top: 5px;
                font-size: 1.35rem;
                font-weight: 750;
            }

            .detail-label {
                margin-bottom: 3px;
                font-size: 0.75rem;
                font-weight: 700;
                opacity: 0.65;
                text-transform: uppercase;
            }

            .detail-value {
                font-size: 0.92rem;
                line-height: 1.5;
            }

            .operation-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 14px;
            }

            .operation-card {
                min-height: 235px;
                padding: 18px;
                border-radius: 12px;
                border-top: 5px solid #d71920;
                border-left: 1px solid rgba(128, 128, 128, 0.22);
                border-right: 1px solid rgba(128, 128, 128, 0.22);
                border-bottom: 1px solid rgba(128, 128, 128, 0.22);
                background: rgba(128, 128, 128, 0.06);
            }

            .operation-frequency {
                display: inline-block;
                padding: 4px 9px;
                margin-bottom: 12px;
                border-radius: 14px;
                background: rgba(215, 25, 32, 0.12);
                color: #d71920;
                font-size: 0.75rem;
                font-weight: 750;
            }

            .operation-title {
                min-height: 52px;
                margin-bottom: 10px;
                font-size: 1rem;
                font-weight: 750;
            }

            .operation-description {
                min-height: 92px;
                font-size: 0.84rem;
                line-height: 1.5;
                opacity: 0.78;
            }

            .operation-responsible {
                padding-top: 12px;
                margin-top: 12px;
                border-top: 1px solid rgba(128, 128, 128, 0.22);
                font-size: 0.78rem;
            }

            @media (max-width: 1050px) {
                .operation-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }

            @media (max-width: 650px) {
                .operation-grid {
                    grid-template-columns: 1fr;
                }

                .phase-header {
                    align-items: flex-start;
                    flex-direction: column;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_pre_injection_timeline():
    steps_html = ""

    for phase in PROJECT_FLOW:
        status = get_status(phase["id"])
        css_class = get_status_class(phase["id"])

        circle_content = (
            "✓"
            if status == "Concluído"
            else str(phase["id"])
        )

        steps_html += (
            f'<div class="timeline-step {css_class}">'
            f'<div class="timeline-circle">{circle_content}</div>'
            f'<div class="timeline-label">{phase["short_title"]}</div>'
            f'<div class="timeline-status">{status}</div>'
            '</div>'
        )

    timeline_html = (
        '<div class="phase-section">'
        '<div class="phase-header">'
        '<div class="phase-title">Antes da injeção</div>'
        '<div class="phase-duration">Duração total estimada: 2 meses</div>'
        '</div>'
        f'<div class="timeline">{steps_html}</div>'
        '</div>'
    )

    st.markdown(
        timeline_html,
        unsafe_allow_html=True,
    )


def render_current_phase_details():
    current_phase = next(
        (
            phase
            for phase in PROJECT_FLOW
            if phase["id"] == CURRENT_PHASE_ID
        ),
        None,
    )

    if not current_phase:
        return

    panel_html = (
        '<div class="current-phase-panel">'
        '<div class="current-phase-label">Etapa atual</div>'
        f'<div class="current-phase-title">'
        f'{current_phase["id"]}. {current_phase["title"]}'
        '</div>'
        '</div>'
    )

    st.markdown(
        panel_html,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1.5, 1, 1.2])

    with col1:
        with st.container(border=True):
            st.markdown(
                '<div class="detail-label">Descrição</div>',
                unsafe_allow_html=True,
            )
            st.write(current_phase["description"])

    with col2:
        with st.container(border=True):
            st.markdown(
                '<div class="detail-label">Responsável</div>',
                unsafe_allow_html=True,
            )
            st.write(current_phase["responsible"])

    with col3:
        with st.container(border=True):
            st.markdown(
                '<div class="detail-label">Entregável esperado</div>',
                unsafe_allow_html=True,
            )
            st.write(current_phase["deliverable"])


def render_operation_flow():
    cards_html = ""

    for phase in OPERATION_FLOW:
        cards_html += (
            '<div class="operation-card">'
            f'<div class="operation-frequency">'
            f'{phase["frequency"]}'
            '</div>'
            f'<div class="operation-title">{phase["title"]}</div>'
            f'<div class="operation-description">'
            f'{phase["description"]}'
            '</div>'
            '<div class="operation-responsible">'
            '<strong>Responsável:</strong><br>'
            f'{phase["responsible"]}'
            '</div>'
            '</div>'
        )

    operation_html = (
        '<div class="phase-section">'
        '<div class="phase-header">'
        '<div class="phase-title">Durante a injeção</div>'
        '<div class="phase-duration">'
        'Execução cíclica durante aproximadamente 5 anos'
        '</div>'
        '</div>'
        f'<div class="operation-grid">{cards_html}</div>'
        '</div>'
    )

    st.markdown(
        operation_html,
        unsafe_allow_html=True,
    )


# =========================================================
# PÁGINA
# =========================================================

def fluxo_projeto_page():
    load_css()

    st.markdown(
        (
            '<div class="flow-page-header">'
            '<h1>🧩 Fluxo do Projeto</h1>'
            '<p>'
            'Acompanhamento da performance, integridade dos poços '
            'e suporte à operação segura.'
            '</p>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    completed_steps = len(
        [
            phase
            for phase in PROJECT_FLOW
            if phase["id"] < CURRENT_PHASE_ID
        ]
    )

    total_steps = len(PROJECT_FLOW)
    progress = completed_steps / total_steps

    st.progress(progress)

    st.caption(
        f"{completed_steps} de {total_steps} etapas preparatórias concluídas."
    )

    render_pre_injection_timeline()
    render_current_phase_details()
    render_operation_flow()

    st.divider()

    # st.caption(
    #     "Para alterar a etapa atual, edite CURRENT_PHASE_ID "
    #     "no início do arquivo views/fluxo_projeto.py."
    # )
