import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# ============================
# Estilo Futurista Customizado
# ============================
st.markdown(
    """
    <style>
    html, body, .stApp {
        background: linear-gradient(135deg, #181C2F 0%, #23272F 100%) !important;
        color: #E0F7FA !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #23272F !important;
        border-radius: 12px !important;
        border: 1.5px solid #1DE9B6 !important;
        box-shadow: 0 2px 16px 0 #1de9b633 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #E0F7FA !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border-radius: 8px 8px 0 0 !important;
        margin-right: 2px !important;
        background: #181C2F !important;
        transition: background 0.3s, color 0.3s !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #1DE9B6 0%, #181C2F 100%) !important;
        color: #181C2F !important;
        box-shadow: 0 2px 8px 0 #1de9b655 !important;
    }
    .stButton>button, .stForm button {
        background: linear-gradient(90deg, #1DE9B6 0%, #23272F 100%) !important;
        color: #181C2F !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        box-shadow: 0 2px 8px 0 #1de9b655 !important;
        transition: background 0.3s, color 0.3s !important;
    }
    .stButton>button:hover, .stForm button:hover {
        background: #1DE9B6 !important;
        color: #23272F !important;
    }
    .stDataFrame, .stTable {
        background: #23272F !important;
        color: #E0F7FA !important;
        border-radius: 8px !important;
        border: 1.5px solid #1DE9B6 !important;
    }
    .stMetric {
        background: #181C2F !important;
        border-radius: 8px !important;
        border: 1.5px solid #1DE9B6 !important;
        color: #1DE9B6 !important;
        box-shadow: 0 2px 8px 0 #1de9b655 !important;
    }
    .stPlotlyChart {
        background: #23272F !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 16px 0 #1de9b633 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1DE9B6 !important;
        letter-spacing: 1px !important;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important;
    }
   
    </style>
    """,
    unsafe_allow_html=True
)

# Caminhos dos arquivos
renda_path = 'data/familia.csv'
despesas_path = 'data/despesas.csv'
invest_path = 'data/investimentos.csv'


# ============================
# Título
# ============================
st.title("Registro Financeiro")

# ============================
# Abas do Dashboard
# ============================
abas = st.tabs(["Ganhos", "Renda", "Despesas", "Investimentos"])

# ============================
# Aba 1 – Ganhos Profissionais
# ============================

with abas[0]:
    subabas = st.tabs(["Freelancer", "CLT"])

    # --- Freelancer ---
    with subabas[0]:
        st.subheader(" Ganhos Freelancer")
        df_horas = pd.read_csv('data/horas.csv')
        def ajustar(valor, nota):
            return valor * 1.2 if nota == 4 else valor if nota == 3 else valor * 0.5 if nota == 2 else 0
        with st.form("form_freela"):
            data = st.date_input("Data")
            horas = st.number_input("Horas Trabalhadas", min_value=0.0, step=0.5)
            cotacao = st.number_input("Cotação do Dólar", min_value=0.0, step=0.01)
            semana = st.text_input("Semana")
            nota = st.selectbox("Nota de Qualidade (1 a 4)", [4,3,2,1])
            enviar = st.form_submit_button("Registrar ganho semanal")
            if enviar:
                valor_usd = horas * 30
                valor_brl = valor_usd * cotacao
                valor_ajustado_usd = ajustar(valor_usd, nota)
                valor_ajustado_brl = valor_ajustado_usd * cotacao
                novo = pd.DataFrame({
                    "Data": [data],
                    "Horas": [horas],
                    "Valor_USD": [valor_usd],
                    "Cotacao": [cotacao],
                    "Valor_BRL": [valor_brl],
                    "Semana": [semana],
                    "Nota": [nota],
                    "Valor_Ajustado_USD": [valor_ajustado_usd],
                    "Valor_Ajustado_BRL": [valor_ajustado_brl]
                })
                df_horas = pd.concat([df_horas, novo], ignore_index=True)
                df_horas.to_csv('data/horas.csv', index=False)
                st.success("Ganho registrado!")
        if not df_horas.empty and 'Valor_Ajustado_BRL' in df_horas.columns:
            # Resumo semanal
            df_horas['Data'] = pd.to_datetime(df_horas['Data'])
            resumo = df_horas.groupby('Semana').agg(
                Periodo=('Data', lambda x: f"{x.min().date()} a {x.max().date()}"),
                Total_Horas=('Horas', 'sum'),
                Total_USD=('Valor_USD', 'sum'),
                Total_Ajustado_USD=('Valor_Ajustado_USD', 'sum'),
                Total_BRL=('Valor_BRL', 'sum')
            ).reset_index()
            # Gráfico de barras: ganhos semanais em BRL
            st.subheader(" Ganhos Semanais em BRL")
            fig_barras = px.bar(resumo, x='Semana', y='Total_BRL', color='Total_BRL',
                               color_continuous_scale='turbo',
                               title='Ganhos Semanais em BRL', text_auto=True)
            st.plotly_chart(fig_barras, use_container_width=True)
            # Gráfico de linha: evolução da qualidade
            st.subheader(" Evolução da Qualidade (Nota Média)")
            media_nota = df_horas.groupby('Semana')['Nota'].mean().reset_index()
            fig_qualidade = px.line(media_nota, x='Semana', y='Nota', markers=True,
                                    title='Média das Notas por Semana')
            fig_qualidade.update_traces(line_color='#1DE9B6', marker_color='#1DE9B6')
            st.plotly_chart(fig_qualidade, use_container_width=True)
            # Formatação condicional
            st.subheader("Resumo Semanal")
            semana_maior_ganho = resumo.loc[resumo['Total_BRL'].idxmax(), 'Semana'] if not resumo.empty else None
            def highlight_maior_ganho(row):
                color = 'background-color: #1DE9B6; color: #181C2F; font-weight: bold;' if row['Semana'] == semana_maior_ganho else ''
                return [color]*len(row)
            st.dataframe(resumo.style.apply(highlight_maior_ganho, axis=1))
            st.subheader("Detalhamento dos Lançamentos")
            def highlight_nota_4(row):
                return ['background-color: #1DE9B6; color: #181C2F; font-weight: bold;' if row.get('Nota',0)==4 else '' for _ in row]
            st.dataframe(df_horas.style.apply(highlight_nota_4, axis=1))
        elif not df_horas.empty:
            st.info("Ainda não há dados completos para exibir o gráfico. Registre um ganho para visualizar.")

    # --- CLT ---
    with subabas[1]:
        st.subheader("Ganhos CLT")
        salario = st.number_input("Salário Mensal (R$)", min_value=0.0, step=100.0, value=3000.0)
        vale = st.number_input("Vale Mensal (R$)", min_value=0.0, step=50.0, value=800.0)
        mes = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        ano = st.number_input("Ano", min_value=2000, max_value=2100, value=2025)
        st.write(f"Salário será pago dia 05/{mes}/{ano} e vale dia 20/{mes}/{ano}.")
        ganhos_clt = pd.DataFrame({
            "Tipo": ["Salário", "Vale"],
            "Data": [f"05/{mes}/{ano}", f"20/{mes}/{ano}"],
            "Valor": [salario, vale]
        })
        st.dataframe(ganhos_clt)

 # ============================
 # Aba 2 – Renda Familiar
 # ============================
with abas[1]:
    st.header(" Renda Familiar")
    df_familia = pd.read_csv(renda_path)
    # Ganhos freelancer automatizados
    try:
        df_horas = pd.read_csv('data/horas.csv')
        total_freela = df_horas['Valor_Ajustado_BRL'].sum() if 'Valor_Ajustado_BRL' in df_horas.columns else 0
    except Exception:
        total_freela = 0
    renda_total = df_familia['Valor'].sum() + total_freela
    st.metric("Renda Familiar Total", f"R$ {renda_total:,.2f}")
    st.caption(f"Inclui ganhos freelancer: R$ {total_freela:,.2f}")

    st.subheader("🔍 Filtros")
    membros = st.multiselect("Filtrar por membro", options=df_familia['Membro'].unique())
    tipos = st.multiselect("Filtrar por tipo de renda", options=df_familia['Tipo'].unique())
    meses = st.multiselect(
        "Filtrar por mês",
        options=df_familia['Data']
            .dropna()
            .apply(lambda x: pd.to_datetime(x).strftime('%Y-%m') if pd.notnull(x) and str(x).strip() != '' else None)
            .dropna()
            .unique(),
        key="meses_renda"
    )
    df_filtrado = df_familia.copy()
    if membros:
        df_filtrado = df_filtrado[df_filtrado['Membro'].isin(membros)]
    if tipos:
        df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipos)]
    if meses:
        df_filtrado['Mes'] = df_filtrado['Data'].apply(lambda x: pd.to_datetime(x).strftime('%Y-%m'))
        df_filtrado = df_filtrado[df_filtrado['Mes'].isin(meses)]
    renda_total_filtrada = df_filtrado['Valor'].sum() + total_freela

    st.metric("Renda Familiar Filtrada", f"R$ {renda_total_filtrada:,.2f}")
    st.caption(f"Inclui ganhos freelancer: R$ {total_freela:,.2f}")

    # Gráfico resumo mensal Freelancer e CLT
    try:
        # Freelancer
        df_horas = pd.read_csv('data/horas.csv')
        if 'Data' in df_horas.columns and 'Valor_Ajustado_BRL' in df_horas.columns:
            df_horas['Data'] = pd.to_datetime(df_horas['Data'])
            df_horas['MesAno'] = df_horas['Data'].dt.strftime('%Y-%m')
            resumo_freela = df_horas.groupby('MesAno')['Valor_Ajustado_BRL'].sum().reset_index()
            resumo_freela = resumo_freela.rename(columns={'Valor_Ajustado_BRL': 'Freelancer'})
        else:
            resumo_freela = pd.DataFrame(columns=['MesAno', 'Freelancer'])
        # CLT
        df_fam = pd.read_csv(renda_path)
        if 'Data' in df_fam.columns and 'Tipo' in df_fam.columns and 'Valor' in df_fam.columns:
            df_fam['Data'] = pd.to_datetime(df_fam['Data'])
            df_fam['MesAno'] = df_fam['Data'].dt.strftime('%Y-%m')
            clt_mask = df_fam['Tipo'].str.lower().isin(['salário', 'salario', 'vale'])
            resumo_clt = df_fam[clt_mask].groupby('MesAno')['Valor'].sum().reset_index()
            resumo_clt = resumo_clt.rename(columns={'Valor': 'CLT'})
        else:
            resumo_clt = pd.DataFrame(columns=['MesAno', 'CLT'])
        # Merge
        resumo = pd.merge(resumo_freela, resumo_clt, on='MesAno', how='outer').fillna(0)
        resumo = resumo.sort_values('MesAno')
        if not resumo.empty:
            fig_mensal = px.bar(resumo, x='MesAno', y=['Freelancer','CLT'], barmode='group',
                               title='Resumo Mensal dos Ganhos (Freelancer x CLT)',
                               labels={'value':'Total (R$)','MesAno':'Mês/Ano','variable':'Pessoa'})
            st.plotly_chart(fig_mensal, use_container_width=True)
    except Exception as e:
        st.info(f"Não foi possível gerar o gráfico mensal: {e}")

    fig2 = px.pie(df_filtrado, names='Tipo', values='Valor', title='Distribuição da Renda Filtrada')
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(df_filtrado)

    st.subheader("➕ Adicionar nova renda familiar")
    with st.form("form_renda"):
        membro = st.text_input("Nome do membro")
        tipo = st.selectbox("Tipo de renda", ["Salário", "Freelance", "Investimento", "Outro"])
        valor = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
        data = st.date_input("Data")
        enviar = st.form_submit_button("Adicionar")
        if enviar:
            novo_dado = pd.DataFrame({
                "Membro": [membro],
                "Tipo": [tipo],
                "Valor": [valor],
                "Data": [data]
            })
            df_familia = pd.concat([df_familia, novo_dado], ignore_index=True)
            df_familia.to_csv(renda_path, index=False)
            st.success(f"Renda de {membro} adicionada com sucesso!")



 # ============================
 # Aba 3 – Despesas
 # ============================
with abas[2]:
    st.header("Despesas Familiares")
    df_despesas = pd.read_csv(despesas_path)
    df_despesas['Data'] = pd.to_datetime(df_despesas['Data'])
    df_despesas['Mes'] = df_despesas['Data'].dt.strftime('%Y-%m')
    meses_d = st.multiselect("Filtrar por mês", options=sorted(df_despesas['Mes'].unique()), key="meses_despesa")
    categorias_d = st.multiselect("Filtrar por categoria", options=df_despesas['Categoria'].unique())
    df_despesas_filtrado = df_despesas.copy()
    if meses_d:
        df_despesas_filtrado = df_despesas_filtrado[df_despesas_filtrado['Mes'].isin(meses_d)]
    if categorias_d:
        df_despesas_filtrado = df_despesas_filtrado[df_despesas_filtrado['Categoria'].isin(categorias_d)]
    total_despesas_filtrado = df_despesas_filtrado['Valor'].sum() if not df_despesas_filtrado.empty else 0
    st.metric("Total de Despesas Filtradas", f"R$ {total_despesas_filtrado:,.2f}")

    # Resumo geral por categoria
    st.subheader("Resumo Geral por Categoria")
    resumo_cat = df_despesas_filtrado.groupby('Categoria')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
    fig_cat = px.pie(resumo_cat, names='Categoria', values='Valor', title='Despesas por Categoria')
    st.plotly_chart(fig_cat, use_container_width=True)
    st.dataframe(resumo_cat)

    # Detalhamento por membro
    st.subheader("Detalhamento por Membro")
    membros = ['Adhara', 'Breno', 'Sara']
    resumo_membro = df_despesas_filtrado[df_despesas_filtrado['Membro'].isin(membros)]
    if not resumo_membro.empty:
        pivot = resumo_membro.pivot_table(index='Categoria', columns='Membro', values='Valor', aggfunc='sum', fill_value=0)
        st.dataframe(pivot.style.format("R$ {:.2f}"))
        fig_membro = px.bar(resumo_membro, x='Categoria', y='Valor', color='Membro', barmode='group',
                            title='Despesas por Categoria e Membro')
        st.plotly_chart(fig_membro, use_container_width=True)
    else:
        st.info("Nenhuma despesa registrada para Adhara, Breno ou Sara.")

    st.subheader("➕ Adicionar nova despesa")
    with st.form("form_despesa"):
        membro_d = st.text_input("Nome do membro")
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Saúde", "Educação", "Lazer", "Outro"])
        valor_d = st.number_input("Valor (R$)", min_value=0.0, step=50.0)
        data_d = st.date_input("Data da despesa")
        enviar_d = st.form_submit_button("Adicionar")
        if enviar_d:
            nova_despesa = pd.DataFrame({
                "Membro": [membro_d],
                "Categoria": [categoria],
                "Valor": [valor_d],
                "Data": [data_d]
            })
            df_despesas = pd.concat([df_despesas, nova_despesa], ignore_index=True)
            df_despesas.to_csv(despesas_path, index=False)
            st.success(f"Despesa de {membro_d} adicionada com sucesso!")



# ============================
# Aba 4 – Investimentos
# ============================
with abas[3]:
    st.header("Investimentos Familiares")
    try:
        df_invest = pd.read_csv(invest_path)
        df_invest['Data'] = pd.to_datetime(df_invest['Data'])
        df_invest['Mes'] = df_invest['Data'].dt.strftime('%Y-%m')
    except FileNotFoundError:
        df_invest = pd.DataFrame(columns=["Membro", "Tipo", "Valor", "Data", "Rendimento", "Mes"])
    df_invest_filtrado = df_invest.copy() if not df_invest.empty else pd.DataFrame(columns=df_invest.columns)
    total_investido = df_invest_filtrado['Valor'].sum() if not df_invest_filtrado.empty else 0
    total_rendimento = df_invest_filtrado['Rendimento'].sum() if not df_invest_filtrado.empty else 0
    saldo_invest = total_investido + total_rendimento
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Investido", f"R$ {total_investido:,.2f}")
    col2.metric("Rendimento Acumulado", f"R$ {total_rendimento:,.2f}")
    col3.metric("Saldo Atual", f"R$ {saldo_invest:,.2f}", delta=float(total_rendimento))
    if not df_invest_filtrado.empty:
        fig4 = px.bar(df_invest_filtrado, x='Tipo', y='Valor', color='Membro',
                      title='Investimentos por Tipo e Membro', text_auto=True)
        st.plotly_chart(fig4, use_container_width=True)
    st.subheader(" Detalhamento dos Investimentos")
    st.dataframe(df_invest_filtrado)
    st.subheader("➕ Adicionar novo investimento")
    with st.form("form_invest"):
        membro_i = st.text_input("Nome do membro")
        tipo_i = st.selectbox("Tipo de investimento", ["Ações", "Fundos", "Cripto", "Tesouro", "Outro"])
        valor_i = st.number_input("Valor investido (R$)", min_value=0.0, step=100.0)
        rendimento_i = st.number_input("Rendimento acumulado (R$)", step=50.0)
        data_i = st.date_input("Data do investimento")
        enviar_i = st.form_submit_button("Adicionar")
        if enviar_i:
            novo_invest = pd.DataFrame({
                "Membro": [membro_i],
                "Tipo": [tipo_i],
                "Valor": [valor_i],
                "Data": [data_i],
                "Rendimento": [rendimento_i]
            })
            df_invest = pd.concat([df_invest, novo_invest], ignore_index=True)
            df_invest.to_csv(invest_path, index=False)
            st.success(f"Investimento de {membro_i} adicionado com sucesso!")