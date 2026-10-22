import streamlit as st

st.set_page_config(
    page_title="AI Development Concentration Dashboard",
    layout="wide"
)

# =====================================
# Custom Styles
# =====================================

st.markdown(
    """
    <style>

    div.stButton > button {
        min-height: 120px;
        font-size: 22px;
        font-weight: 600;

        background-color: rgba(128, 128, 128, 0.12);
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 12px;

        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: rgba(128, 128, 128, 0.22);
        border: 1px solid rgba(128, 128, 128, 0.45);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# Header
# =====================================

st.markdown(
    """
    <h2>
    Is AI Development Becoming Concentrated in Fewer Countries?
    </h2>
    """,
    unsafe_allow_html=True
)

st.write(
    """
    This dashboard investigates whether global AI development is becoming
    increasingly concentrated among a small number of countries.
    """
)

st.info(
    "Persona: Policy Analysts and Government Decision Makers"
)

# =====================================
# Navigation
# =====================================

st.markdown("## Explore the Dashboard")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "Publications",
        use_container_width=True
    ):
        st.switch_page("pages/publications.py")

    if st.button(
        "Patents",
        use_container_width=True
    ):
        st.switch_page("pages/patents.py")

with col2:

    if st.button(
        "Investments",
        use_container_width=True
    ):
        st.switch_page("pages/investments.py")

    if st.button(
        "Concentration Analysis",
        use_container_width=True
    ):
        st.switch_page("pages/concentration.py")