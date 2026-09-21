import streamlit as st

st.set_page_config(
    page_title="Painel ODS - Educação Brasil", page_icon="📚", layout="wide"
)

pg = st.navigation(
    [
        st.Page("pages/home.py", title="Início", icon="🏠"),
        st.Page("pages/alfabetizacao.py", title="Alfabetização", icon="📖"),
        st.Page("pages/escolarizacao.py", title="Escolarização", icon="📚"),
        st.Page("pages/frequencia.py", title="Frequência", icon="📅"),
        st.Page("pages/conclusao.py", title="Conclusão", icon="🎓"),
        st.Page("pages/noticias.py", title="Notícias", icon="📰"),
    ]
)

pg.run()
