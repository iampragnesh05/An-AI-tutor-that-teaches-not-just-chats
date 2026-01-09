import streamlit as st
from core.config.settings import settings
from core.config.logging import configure_logging
from core.utils.paths import ensure_data_dirs

configure_logging()
ensure_data_dirs()

st.set_page_config(
    page_title="AI Learning Tutor",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI Learning Tutor (Setup)")
st.caption("Scaffold + PDF upload plumbing. No tutor logic yet.")

with st.expander("✅ Environment Status", expanded=True):
    st.write("OpenAI API key loaded:", "✅" if settings.openai_api_key else "❌")
    st.write("Configured model:", settings.openai_model)

st.info("Go to the Upload PDFs page from the left sidebar.")
