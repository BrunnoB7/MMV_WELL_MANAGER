import html
import streamlit as st


def page_header(title: str, subtitle: str) -> None:
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)

    st.markdown(
        """
        <style>
            .page-header {
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

            .page-header h1 {
                margin: 0;
                font-size: 2rem;
                font-weight: 700;
            }

            .page-header p {
                margin: 7px 0 0 0;
                opacity: 0.86;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""<div class="page-header">
<h1>{safe_title}</h1>
<p>{safe_subtitle}</p>
</div>""",
        unsafe_allow_html=True,
    )
