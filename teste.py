import streamlit as st
import pandas as pd
import numpy as np

st.title("Teste Simples")
st.write("Se você conseguir ver esta mensagem, o problema está resolvido!")

# Teste dos empréstimos
try:
    df_emp = pd.read_csv('data/emprestimos.csv')
    st.write("Dados dos empréstimos carregados com sucesso:")
    st.dataframe(df_emp)
except Exception as e:
    st.error(f"Erro ao carregar empréstimos: {e}")