import streamlit as st


def page_header(
    title: str,
    subtitle: str,
    color1: str = "#8B0000",
    color2: str = "#D71920",
):
    st.markdown(
    f"""
    <div style="
        background: linear-gradient(90deg, {color1}, {color2});
        padding: 34px;
        border-radius: 18px;
        color: white;
        margin-bottom: 30px;
    ">
        <h1 style="
            margin:0;
            font-size:2.2rem;
            font-weight:700;
        ">
            {title}
        </h1>

        <p style="
            margin-top:22px;
            margin-bottom:0;
            font-size:1rem;
            opacity:.95;
        ">
            {subtitle}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
