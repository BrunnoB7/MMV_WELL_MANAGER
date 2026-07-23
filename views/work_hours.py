from datetime import date, timedelta

import altair as alt
import pandas as pd
import streamlit as st
from config.team import TEAM_MEMBERS
from services.work_hours_service import (
    WorkHoursService,
)

SOURCE_LABELS = {
    "Deliverables": "Tarefas",
    "Reuniões": "Reuniões",
}

def format_hours(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0

    return (
        f"{value:.1f}"
        .replace(".", ",")
        + " h"
    )


def load_css():
    st.markdown(
        """
        <style>
            .hours-header {
                padding: 24px 28px;
                margin-bottom: 20px;
                border-radius: 14px;
                background: linear-gradient(
                    135deg,
                    #7f0000,
                    #d71920
                );
                color: white;
            }

            .documents-header h1 {
                margin: 0;
                font-size: 2rem;
            }

            .documents-header p {
                margin: 7px 0 0 0;
                opacity: 0.86;
            }

            .documents-summary {
                margin: 8px 0 18px 0;
                font-size: 0.88rem;
                opacity: 0.72;
            }

            .document-discipline {
                display: inline-block;
                padding: 4px 10px;
                margin-bottom: 10px;
                border-radius: 14px;
                background: rgba(215, 25, 32, 0.12);
                color: #d71920;
                font-size: 0.78rem;
                font-weight: 700;
            }

            .document-description {
                min-height: 70px;
                margin: 8px 0 14px 0;
                font-size: 0.90rem;
                line-height: 1.45;
                opacity: 0.78;
            }

            .document-info {
                padding-top: 12px;
                margin-top: 10px;
                border-top: 1px solid rgba(128, 128, 128, 0.25);
                font-size: 0.80rem;
                line-height: 1.6;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def format_date(value):
    if not value:
        return "-"

    try:
        return date.fromisoformat(
            str(value)
        ).strftime("%d/%m/%Y")
    except ValueError:
        return str(value)


def build_dataframe(entries):
    columns = [
        "entry_id",
        "source",
        "collaborator",
        "worked_hours",
        "work_date",
        "title",
        "discipline",
        "status",
        "description",
        "deliverable_id",
        "meeting_id",
    ]

    if not entries:
        return pd.DataFrame(
            columns=columns
        )

    dataframe = pd.DataFrame(entries)

    dataframe["worked_hours"] = (
        pd.to_numeric(
            dataframe["worked_hours"],
            errors="coerce",
        ).fillna(0)
    )

    dataframe["work_date"] = (
        pd.to_datetime(
            dataframe["work_date"],
            errors="coerce",
        )
    )

    return dataframe


def render_hours_by_collaborator_chart(
    dataframe
):
    if dataframe.empty:
        st.info(
            "Não existem dados para gerar "
            "o gráfico."
        )
        return

    chart_data = (
        dataframe.groupby(
            "collaborator",
            as_index=False,
        )["worked_hours"]
        .sum()
        .sort_values(
            "worked_hours",
            ascending=False,
        )
    )

    chart = (
        alt.Chart(chart_data)
        .mark_bar(
            cornerRadiusTopRight=5,
            cornerRadiusBottomRight=5,
        )
        .encode(
            x=alt.X(
                "worked_hours:Q",
                title="Horas trabalhadas",
            ),
            y=alt.Y(
                "collaborator:N",
                title=None,
                sort="-x",
            ),
            tooltip=[
                alt.Tooltip(
                    "collaborator:N",
                    title="Colaborador",
                ),
                alt.Tooltip(
                    "worked_hours:Q",
                    title="Horas",
                    format=".1f",
                ),
            ],
        )
        .properties(
            height=max(
                250,
                len(chart_data) * 45,
            )
        )
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )


def render_source_composition_chart(
    dataframe
):
    if dataframe.empty:
        st.info(
            "Não existem dados para gerar "
            "o gráfico."
        )
        return

    chart_data = (
        dataframe.groupby(
            [
                "collaborator",
                "source",
            ],
            as_index=False,
        )["worked_hours"]
        .sum()
    )

    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "collaborator:N",
                title="Colaborador",
                sort=TEAM_MEMBERS,
            ),
            y=alt.Y(
                "worked_hours:Q",
                title="Horas trabalhadas",
            ),
            color=alt.Color(
                "source:N",
                title="Origem",
            ),
            tooltip=[
                alt.Tooltip(
                    "collaborator:N",
                    title="Colaborador",
                ),
                alt.Tooltip(
                    "source:N",
                    title="Origem",
                ),
                alt.Tooltip(
                    "worked_hours:Q",
                    title="Horas",
                    format=".1f",
                ),
            ],
        )
        .properties(height=350)
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )


def render_time_evolution_chart(
    dataframe
):
    if dataframe.empty:
        st.info(
            "Não existem dados para gerar "
            "o gráfico."
        )
        return

    chart_data = dataframe.copy()

    chart_data = chart_data.dropna(
        subset=["work_date"]
    )

    chart_data["month"] = (
        chart_data["work_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    chart_data = (
        chart_data.groupby(
            "month",
            as_index=False,
        )["worked_hours"]
        .sum()
    )

    chart = (
        alt.Chart(chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "month:T",
                title="Mês",
                axis=alt.Axis(
                    format="%m/%Y"
                ),
            ),
            y=alt.Y(
                "worked_hours:Q",
                title="Horas trabalhadas",
            ),
            tooltip=[
                alt.Tooltip(
                    "month:T",
                    title="Mês",
                    format="%m/%Y",
                ),
                alt.Tooltip(
                    "worked_hours:Q",
                    title="Horas",
                    format=".1f",
                ),
            ],
        )
        .properties(height=320)
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )


def render_collaborator_details(
    dataframe,
    collaborator,
):
    collaborator_data = dataframe[
        dataframe["collaborator"]
        == collaborator
    ].copy()

    if collaborator_data.empty:
        st.info(
            "Não existem horas registradas "
            f"para {collaborator} no período."
        )
        return

    total_hours = collaborator_data[
        "worked_hours"
    ].sum()

    deliverable_data = collaborator_data[
        collaborator_data["source"]
        == "Deliverables"
    ]

    meeting_data = collaborator_data[
        collaborator_data["source"]
        == "Reuniões"
    ]

    deliverable_hours = deliverable_data[
        "worked_hours"
    ].sum()

    meeting_hours = meeting_data[
        "worked_hours"
    ].sum()

    deliverable_count = (
        deliverable_data[
            "deliverable_id"
        ]
        .dropna()
        .nunique()
    )

    meeting_count = (
        meeting_data[
            "meeting_id"
        ]
        .dropna()
        .nunique()
    )

    metric1, metric2, metric3 = (
        st.columns(3)
    )

    metric1.metric(
        "Horas totais",
        format_hours(total_hours),
    )

    metric2.metric(
        "Tarefas",
        (
            f"{format_hours(deliverable_hours)} "
            f"em {deliverable_count}"
        ),
    )

    metric3.metric(
        "Reuniões",
        (
            f"{format_hours(meeting_hours)} "
            f"em {meeting_count}"
        ),
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "📦 Tarefas",
            "👥 Reuniões",
            "📊 Estatísticas",
        ]
    )

    with tab1:
        if deliverable_data.empty:
            st.info(
                "Nenhuma hora registrada em "
                "Tarefas."
            )
        else:
            deliverable_table = (
                deliverable_data[
                    [
                        "work_date",
                        "title",
                        "discipline",
                        "worked_hours",
                        "description",
                    ]
                ]
                .copy()
                .sort_values(
                    "work_date",
                    ascending=False,
                )
            )

            deliverable_table[
                "work_date"
            ] = (
                deliverable_table[
                    "work_date"
                ]
                .dt.strftime("%d/%m/%Y")
            )

            deliverable_table.rename(
                columns={
                    "work_date": "Data",
                    "title": "Tarefa",
                    "discipline": "Disciplina",
                    "worked_hours": "Horas",
                    "description": "Descrição",
                },
                inplace=True,
            )

            st.dataframe(
                deliverable_table,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Horas": (
                        st.column_config
                        .NumberColumn(
                            format="%.2f h"
                        )
                    ),
                },
            )

    with tab2:
        if meeting_data.empty:
            st.info(
                "Nenhuma participação em "
                "reuniões."
            )
        else:
            meeting_table = (
                meeting_data[
                    [
                        "work_date",
                        "title",
                        "worked_hours",
                        "description",
                    ]
                ]
                .copy()
                .sort_values(
                    "work_date",
                    ascending=False,
                )
            )

            meeting_table[
                "work_date"
            ] = (
                meeting_table[
                    "work_date"
                ]
                .dt.strftime("%d/%m/%Y")
            )

            meeting_table.rename(
                columns={
                    "work_date": "Data",
                    "title": "Reunião",
                    "worked_hours": "Horas",
                    "description": "Descrição",
                },
                inplace=True,
            )

            st.dataframe(
                meeting_table,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Horas": (
                        st.column_config
                        .NumberColumn(
                            format="%.2f h"
                        )
                    ),
                },
            )

    with tab3:
        meeting_percentage = (
            meeting_hours / total_hours * 100
            if total_hours > 0
            else 0
        )

        deliverable_percentage = (
            deliverable_hours
            / total_hours
            * 100
            if total_hours > 0
            else 0
        )

        average_per_deliverable = (
            deliverable_hours
            / deliverable_count
            if deliverable_count > 0
            else 0
        )

        stat1, stat2, stat3 = (
            st.columns(3)
        )

        stat1.metric(
            "% em tarefas",
            (
                f"{deliverable_percentage:.1f}%"
                .replace(".", ",")
            ),
        )

        stat2.metric(
            "% em reuniões",
            (
                f"{meeting_percentage:.1f}%"
                .replace(".", ",")
            ),
        )

        stat3.metric(
            "Média por tarefa",
            format_hours(
                average_per_deliverable
            ),
        )

        if not deliverable_data.empty:
            deliverable_totals = (
                deliverable_data.groupby(
                    "title",
                    as_index=False,
                )["worked_hours"]
                .sum()
                .sort_values(
                    "worked_hours",
                    ascending=False,
                )
            )

            top_deliverable = (
                deliverable_totals.iloc[0]
            )

            st.markdown(
                (
                    "**Tarefa com maior "
                    "dedicação:** "
                    f"{top_deliverable['title']} "
                    f"— {format_hours(top_deliverable['worked_hours'])}"
                )
            )


def work_hours_page():
    load_css()

    st.markdown(
        (
            '<div class="hours-header">'
            '<h1>⏱️ Horas trabalhadas</h1>'
            '<p>'
            'Levantamento das horas trabalhadas pela equipe.'
            '</p>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    all_entries = (
        WorkHoursService.get_all_entries()
    )

    today = date.today()

    default_start_date = (
        today - timedelta(days=30)
    )

    with st.expander(
        "🔎 Filtros",
        expanded=True,
    ):
        filter_col1, filter_col2 = (
            st.columns(2)
        )

        with filter_col1:
            start_date = st.date_input(
                "Data inicial",
                value=default_start_date,
                format="DD/MM/YYYY",
                key="work_hours_start_date",
            )

        with filter_col2:
            end_date = st.date_input(
                "Data final",
                value=today,
                format="DD/MM/YYYY",
                key="work_hours_end_date",
            )

        filter_col3, filter_col4 = (
            st.columns(2)
        )

        with filter_col3:
            selected_collaborators = (
                st.multiselect(
                    "Colaboradores",
                    options=TEAM_MEMBERS,
                    placeholder=(
                        "Todos os colaboradores"
                    ),
                    key=(
                        "work_hours_collaborators"
                    ),
                )
            )

        with filter_col4:
            selected_sources = st.multiselect(
                "Origem das horas",
                options=[
                    "Deliverables",
                    "Reuniões",
                ],
                default=[
                    "Deliverables",
                    "Reuniões",
                ],
                format_func=lambda source: SOURCE_LABELS.get(
                    source,
                    source,
                ),
                key="work_hours_sources",
            )

    if end_date < start_date:
        st.warning(
            "A data final não pode ser "
            "anterior à data inicial."
        )
        return

    filtered_entries = (
        WorkHoursService.filter_entries(
            entries=all_entries,
            start_date=start_date,
            end_date=end_date,
            collaborators=(
                selected_collaborators
            ),
            sources=selected_sources,
        )
    )

    dataframe = build_dataframe(
        filtered_entries
    )

    total_hours = (
        dataframe["worked_hours"].sum()
        if not dataframe.empty
        else 0
    )

    deliverable_hours = (
        dataframe.loc[
            dataframe["source"]
            == "Deliverables",
            "worked_hours",
        ].sum()
        if not dataframe.empty
        else 0
    )

    meeting_hours = (
        dataframe.loc[
            dataframe["source"]
            == "Reuniões",
            "worked_hours",
        ].sum()
        if not dataframe.empty
        else 0
    )

    collaborator_totals = (
        dataframe.groupby(
            "collaborator"
        )["worked_hours"]
        .sum()
        if not dataframe.empty
        else pd.Series(dtype=float)
    )

    if collaborator_totals.empty:
        top_collaborator = "-"
    else:
        top_name = (
            collaborator_totals.idxmax()
        )

        top_value = (
            collaborator_totals.max()
        )

        top_collaborator = (
            f"{top_name} — "
            f"{format_hours(top_value)}"
        )

    metric1, metric2, metric3, metric4 = (
        st.columns(4)
    )

    metric1.metric(
        "Horas totais",
        format_hours(total_hours),
    )

    metric2.metric(
        "Tarefas",
        format_hours(deliverable_hours),
    )

    metric3.metric(
        "Reuniões",
        format_hours(meeting_hours),
    )

    metric4.metric(
        "Maior participação",
        top_collaborator,
    )

    st.caption(
        f"{len(filtered_entries)} lançamento(s) "
        "considerado(s) no período."
    )

    st.divider()

    st.subheader("Horas por colaborador")

    render_hours_by_collaborator_chart(
        dataframe
    )

    chart_col1, chart_col2 = (
        st.columns(2)
    )

    with chart_col1:
        st.subheader(
            "Composição das horas"
        )

        render_source_composition_chart(
            dataframe
        )

    with chart_col2:
        st.subheader(
            "Evolução das horas"
        )

        render_time_evolution_chart(
            dataframe
        )

    st.divider()

    st.subheader(
        "Detalhamento por colaborador"
    )

    available_collaborators = [
        member
        for member in TEAM_MEMBERS
        if (
            not dataframe.empty
            and member
            in dataframe[
                "collaborator"
            ].unique()
        )
    ]

    if not available_collaborators:
        st.info(
            "Não existem colaboradores com "
            "horas no período selecionado."
        )
        return

    detail_collaborator = st.selectbox(
        "Selecione o colaborador",
        options=available_collaborators,
        key="work_hours_detail_member",
    )

    render_collaborator_details(
        dataframe=dataframe,
        collaborator=detail_collaborator,
    )
