import streamlit as st

def render_sidebar() -> None:
    with st.sidebar:
        st.header("Tutor Controls")
        st.write("UI shell only (no logic yet).")
        st.divider()
        st.write("Steps will appear here (Upload → Learn → Quiz → Progress).")
