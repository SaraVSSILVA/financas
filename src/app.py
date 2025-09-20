import streamlit as st
import pandas as pd
import plotly.express as px
import shutil
from pathlib import Path

# Configurar pandas para evitar warnings de depreciação
pd.set_option('future.no_silent_downcasting', True)

# Inicializar session state
if 'refresh_data' not in st.session_state:
    st.session_state.refresh_data = False

# Função para criar backup antes de modificações
def criar_backup():
    """Cria backup dos arquivos CSV antes de modificações"""
    try:
        backup_dir = Path("data/backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        arquivos_backup = []
        
        for arquivo in ["horas.csv", "familia.csv", "despesas.csv", "investimentos.csv", "emprestimos.csv"]:
            arquivo_path = Path(f"data/{arquivo}")
            if arquivo_path.exists():
                backup_path = backup_dir / f"{arquivo.replace('.csv', '')}_{timestamp}.csv"
                shutil.copy2(arquivo_path, backup_path)
                arquivos_backup.append(arquivo)
        
        if arquivos_backup:
            st.info(f"✅ Backup criado para: {', '.join(arquivos_backup)}")
        return True
    except Exception as e:
        st.error(f"❌ Erro ao criar backup: {e}")
        return False

# Função para carregar dados sem cache agressivo
def load_csv_data(file_path, default_columns=None):
    try:
        if Path(file_path).exists():
            df = pd.read_csv(file_path)
            
            # Verificação de integridade
            if df.empty and default_columns:
                st.warning(f"⚠️ Arquivo {file_path} estava vazio, recriando estrutura padrão.")
                df = pd.DataFrame(columns=default_columns)
                df.to_csv(file_path, index=False)
            
            # Verificar se as colunas estão corretas
            if default_columns and not df.empty:
                colunas_faltantes = set(default_columns) - set(df.columns)
                if colunas_faltantes:
                    st.warning(f"⚠️ Colunas faltantes em {file_path}: {colunas_faltantes}")
                    for col in colunas_faltantes:
                        df[col] = None
                    df.to_csv(file_path, index=False)
            
            return df
        else:
            # Criar arquivo se não existir
            columns = default_columns or get_default_columns(file_path)
            df = pd.DataFrame(columns=columns)
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(file_path, index=False)
            st.info(f"📄 Arquivo {file_path} criado com estrutura padrão.")
            return df
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar {file_path}: {e}")
        columns = default_columns or get_default_columns(file_path)
        return pd.DataFrame(columns=columns)

def get_default_columns(file_path):
    """Retorna colunas padrão baseadas no nome do arquivo"""
    if 'horas' in file_path:
        return ['Data', 'Horas', 'Cotacao', 'Semana', 'Nota', 'Valor_USD', 'Valor_BRL', 'Valor_Ajustado_USD', 'Valor_Ajustado_BRL', 'Pago']
    elif 'familia' in file_path:
        return ['Membro', 'Tipo', 'Valor', 'Data']
    elif 'despesas' in file_path:
        return ['Membro', 'Categoria', 'Valor', 'Data']
    elif 'investimentos' in file_path:
        return ['Membro', 'Tipo', 'Valor', 'Data', 'Rendimento']
    elif 'emprestimos' in file_path:
        return ['Nome', 'Tipo', 'Valor_Original', 'Valor_Com_Juros', 'Parcelas_Total', 'Parcelas_Pagas', 'Valor_Parcela', 'Data_Emprestimo', 'Status', 'Observacoes']
    else:
        return []

# Função para salvar dados com verificação e backup
def save_csv_data(df, file_path, success_message="Dados salvos com sucesso!"):
    try:
        # Criar backup do arquivo atual se existir
        file_path_obj = Path(file_path)
        if file_path_obj.exists():
            backup_temp = file_path.replace('.csv', '_temp_backup.csv')
            shutil.copy2(file_path, backup_temp)
        
        # Salvar novos dados
        df.to_csv(file_path, index=False)
        
        # Verificar se foi salvo corretamente
        verificacao = pd.read_csv(file_path)
        if len(verificacao) == len(df) and not verificacao.empty:
            # Remover backup temporário se salvamento foi bem-sucedido
            backup_temp = file_path.replace('.csv', '_temp_backup.csv')
            if Path(backup_temp).exists():
                Path(backup_temp).unlink()
            st.success(success_message)
            return True
        else:
            raise Exception("Verificação de integridade falhou")
            
    except Exception as e:
        st.error(f"❌ Erro ao salvar dados: {str(e)}")
        
        # Restaurar backup se algo deu errado
        backup_temp = file_path.replace('.csv', '_temp_backup.csv')
        if Path(backup_temp).exists():
            shutil.copy2(backup_temp, file_path)
            Path(backup_temp).unlink()
            st.warning("⚠️ Dados restaurados do backup devido ao erro")
        
        return False

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
emprestimos_path = 'data/emprestimos.csv'


# ============================
# Título e Controles
# ============================
col_title, col_backup, col_refresh = st.columns([3, 1, 1])
with col_title:
    st.title("Registro Financeiro")
with col_backup:
    if st.button("💾 Backup", help="Criar backup dos dados"):
        if criar_backup():
            st.balloons()
with col_refresh:
    if st.button("🔄 Atualizar", help="Atualizar dados exibidos"):
        st.session_state.refresh_data = True
        st.success("Dados atualizados! ✅")

# Informações de backup e exportação
backup_dir = Path("data/backups")
if backup_dir.exists():
    backups = list(backup_dir.glob("*.csv"))
    if backups:
        with st.expander("📋 Gerenciamento de Backup e Dados"):
            col_info, col_export = st.columns(2)
            
            with col_info:
                st.info(f"💾 **{len(backups)} backups disponíveis** na pasta `data/backups/`")
                st.write("📌 **Dica**: Os backups são criados automaticamente a cada modificação.")
                
                # Mostrar últimos 3 backups
                backups_recentes = sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
                for backup in backups_recentes:
                    timestamp = pd.Timestamp.fromtimestamp(backup.stat().st_mtime)
                    st.text(f"📄 {backup.name} - {timestamp.strftime('%d/%m/%Y %H:%M')}")
            
            with col_export:
                st.write("**📤 Exportar Dados Completos**")
                
                if st.button("📦 Exportar Todos os Dados"):
                    try:
                        # Criar ZIP com todos os dados
                        import zipfile
                        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                        zip_name = f"dados_completos_{timestamp}.zip"
                        
                        with zipfile.ZipFile(zip_name, 'w') as zipf:
                            for arquivo in ["horas.csv", "familia.csv", "despesas.csv", "investimentos.csv", "emprestimos.csv"]:
                                arquivo_path = f"data/{arquivo}"
                                if Path(arquivo_path).exists():
                                    zipf.write(arquivo_path, arquivo)
                        
                        with open(zip_name, "rb") as file:
                            st.download_button(
                                label="⬇️ Baixar Dados Exportados",
                                data=file.read(),
                                file_name=zip_name,
                                mime="application/zip"
                            )
                        
                        # Remover arquivo temporário
                        Path(zip_name).unlink()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao exportar dados: {e}")
                
                st.write("**📥 Restaurar Dados**")
                st.info("⚠️ Para restaurar dados, substitua manualmente os arquivos CSV na pasta `data/`")
else:
    with st.expander("📋 Gerenciamento de Backup"):
        st.info("💡 Crie seu primeiro backup clicando no botão 'Backup' acima.")
    
st.divider()

# ============================
# Abas do Dashboard
# ============================
abas = st.tabs(["Ganhos", "Renda", "Despesas", "Investimentos", "Empréstimos"])

# ============================
# Aba 1 – Ganhos Profissionais
# ============================

with abas[0]:
    subabas = st.tabs(["Freelancer", "CLT"])

    # --- Freelancer ---
    with subabas[0]:
        st.subheader(" Ganhos Freelancer")
        
        df_horas = load_csv_data('data/horas.csv')
        # Garantir que a coluna 'Pago' existe
        if 'Pago' not in df_horas.columns:
            df_horas['Pago'] = False
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
                    "Valor_Ajustado_BRL": [valor_ajustado_brl],
                    "Pago": [False]
                })
                df_horas = pd.concat([df_horas, novo], ignore_index=True)
                save_csv_data(df_horas, 'data/horas.csv', "✅ Ganho registrado e salvo!")
        
        if not df_horas.empty and 'Valor_Ajustado_BRL' in df_horas.columns:
            # Métricas de Efetivo vs Projeção
            st.subheader("📊 Resumo Financeiro")
            total_recebido = df_horas[df_horas['Pago'] == True]['Valor_Ajustado_BRL'].sum()
            total_projecao = df_horas[df_horas['Pago'] == False]['Valor_Ajustado_BRL'].sum()
            total_geral = total_recebido + total_projecao
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total Recebido", f"R$ {total_recebido:,.2f}")
            with col2:
                st.metric("📈 Projeção Pendente", f"R$ {total_projecao:,.2f}")
            with col3:
                st.metric("🎯 Total Geral", f"R$ {total_geral:,.2f}")
            
            # Resumo semanal
            df_horas['Data'] = pd.to_datetime(df_horas['Data'])
            resumo = df_horas.groupby('Semana').agg(
                Periodo=('Data', lambda x: f"{x.min().date()} a {x.max().date()}"),
                Total_Horas=('Horas', 'sum'),
                Total_USD=('Valor_USD', 'sum'),
                Total_Ajustado_USD=('Valor_Ajustado_USD', 'sum'),
                Total_BRL=('Valor_BRL', 'sum'),
                Total_Ajustado_BRL=('Valor_Ajustado_BRL', 'sum')
            ).reset_index()
            # Gráfico de barras: ganhos semanais em BRL (considerando nota)
            st.subheader(" Ganhos Semanais Ajustados por Qualidade")
            fig_barras = px.bar(resumo, x='Semana', y='Total_Ajustado_BRL', color='Total_Ajustado_BRL',
                               color_continuous_scale='turbo',
                               title='Ganhos Semanais Ajustados por Qualidade (BRL)', text_auto=True)
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
            # Formatação condicional - usar valor ajustado para destacar maior ganho
            semana_maior_ganho = resumo.loc[resumo['Total_Ajustado_BRL'].idxmax(), 'Semana'] if not resumo.empty else None
            def highlight_maior_ganho(row):
                color = 'background-color: #1DE9B6; color: #181C2F; font-weight: bold;' if row['Semana'] == semana_maior_ganho else ''
                return [color]*len(row)
            st.dataframe(resumo.style.apply(highlight_maior_ganho, axis=1).format({
                'Total_Horas': '{:.1f}h',
                'Total_USD': 'US$ {:.2f}',
                'Total_Ajustado_USD': 'US$ {:.2f}',
                'Total_BRL': 'R$ {:.2f}',
                'Total_Ajustado_BRL': 'R$ {:.2f}'
            }))
            st.subheader("Detalhamento dos Lançamentos")
            def highlight_nota_4(row):
                return ['background-color: #1DE9B6; color: #181C2F; font-weight: bold;' if row.get('Nota',0)==4 else '' for _ in row]
            st.dataframe(df_horas.style.apply(highlight_nota_4, axis=1).format({
                'Horas': '{:.1f}h',
                'Cotacao': 'R$ {:.2f}',
                'Valor_USD': 'US$ {:.2f}',
                'Valor_BRL': 'R$ {:.2f}',
                'Valor_Ajustado_USD': 'US$ {:.2f}',
                'Valor_Ajustado_BRL': 'R$ {:.2f}',
                'Pago': lambda x: '💰 Recebido' if x else '📈 Projeção'
            }))
            
            # Controles de pagamento e exclusão
            st.subheader("🔧 Gerenciar Registros")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**💰 Marcar como Recebido com Nota Real:**")
                if not df_horas.empty:
                    opcoes_pagamento = []
                    indices_pagamento = []
                    for idx, row in df_horas.iterrows():
                        status = "💰 Recebido" if row.get('Pago', False) else "📈 Projeção"
                        opcoes_pagamento.append(f"Semana {row['Semana']} - {row['Data']} - Nota: {row['Nota']} ({status})")
                        indices_pagamento.append(idx)
                    
                    registro_pagamento = st.selectbox("Selecione o registro:", opcoes_pagamento, key="select_pagamento")
                    idx_selecionado = indices_pagamento[opcoes_pagamento.index(registro_pagamento)]
                    registro_atual = df_horas.loc[idx_selecionado]
                    
                    # Mostrar informações atuais
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.info(f"Nota atual: **{registro_atual['Nota']}**")
                    with col_info2:
                        valor_atual = registro_atual.get('Valor_Ajustado_BRL', 0)
                        st.info(f"Valor atual: **R$ {valor_atual:.2f}**")
                    
                    # Interface para ajustar
                    if not registro_atual.get('Pago', False):  # Só mostrar se for projeção
                        st.write("**Ajustar nota real recebida:**")
                        nova_nota = st.selectbox("Nota real recebida:", [4, 3, 2, 1], 
                                                index=[4, 3, 2, 1].index(int(registro_atual['Nota'])), 
                                                key="nova_nota",
                                                help="4=Excelente (+20%), 3=Bom (normal), 2=Regular (-50%), 1=Ruim (R$0)")
                        
                        # Calcular novo valor
                        def ajustar_nota(valor_base, nota):
                            return valor_base * 1.2 if nota == 4 else valor_base if nota == 3 else valor_base * 0.5 if nota == 2 else 0
                        
                        valor_base_usd = registro_atual['Valor_USD']
                        cotacao = registro_atual['Cotacao']
                        novo_valor_usd = ajustar_nota(valor_base_usd, nova_nota)
                        novo_valor_brl = novo_valor_usd * cotacao
                        
                        # Mostrar preview do novo valor
                        if nova_nota != registro_atual['Nota']:
                            diferenca = novo_valor_brl - valor_atual
                            if diferenca > 0:
                                st.success(f"💰 Novo valor: R$ {novo_valor_brl:.2f} (+R$ {diferenca:.2f})")
                            else:
                                st.warning(f"📉 Novo valor: R$ {novo_valor_brl:.2f} ({diferenca:.2f})")
                        
                        if st.button("✅ Confirmar Recebimento", key="btn_confirmar_recebimento"):
                            # Atualizar nota e valores
                            df_horas.loc[idx_selecionado, 'Nota'] = nova_nota
                            df_horas.loc[idx_selecionado, 'Valor_Ajustado_USD'] = novo_valor_usd
                            df_horas.loc[idx_selecionado, 'Valor_Ajustado_BRL'] = novo_valor_brl
                            df_horas.loc[idx_selecionado, 'Pago'] = True
                            save_csv_data(df_horas, 'data/horas.csv', f"✅ Marcado como recebido com nota {nova_nota} e salvo!")
                    
                    else:  # Se já está pago
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("📈 Voltar para Projeção", key="btn_voltar_projecao"):
                                df_horas.loc[idx_selecionado, 'Pago'] = False
                                save_csv_data(df_horas, 'data/horas.csv', "✅ Voltou para projeção e salvo!")
                        
                        with col_btn2:
                            st.write("*Já recebido*")
            
            with col2:
                st.write("**🔧 Outras Opções:**")
                
                # Seção para editar notas de registros já pagos
                st.write("*Editar Nota de Registro Recebido:*")
                if not df_horas.empty:
                    registros_pagos = df_horas[df_horas['Pago'] == True]
                    if not registros_pagos.empty:
                        opcoes_edicao = []
                        indices_edicao = []
                        for idx, row in registros_pagos.iterrows():
                            opcoes_edicao.append(f"Semana {row['Semana']} - Nota: {row['Nota']}")
                            indices_edicao.append(idx)
                        
                        if opcoes_edicao:
                            registro_edicao = st.selectbox("Editar nota:", opcoes_edicao, key="select_edicao")
                            idx_edicao = indices_edicao[opcoes_edicao.index(registro_edicao)]
                            
                            nova_nota_edicao = st.selectbox("Nova nota:", [4, 3, 2, 1], 
                                                          index=[4, 3, 2, 1].index(int(df_horas.loc[idx_edicao, 'Nota'])), 
                                                          key="nova_nota_edicao")
                            
                            if st.button("✏️ Atualizar Nota", key="btn_editar_nota"):
                                # Recalcular valores com nova nota
                                valor_base_usd = df_horas.loc[idx_edicao, 'Valor_USD']
                                cotacao = df_horas.loc[idx_edicao, 'Cotacao']
                                novo_valor_usd = ajustar(valor_base_usd, nova_nota_edicao)
                                novo_valor_brl = novo_valor_usd * cotacao
                                
                                df_horas.loc[idx_edicao, 'Nota'] = nova_nota_edicao
                                df_horas.loc[idx_edicao, 'Valor_Ajustado_USD'] = novo_valor_usd
                                df_horas.loc[idx_edicao, 'Valor_Ajustado_BRL'] = novo_valor_brl
                                save_csv_data(df_horas, 'data/horas.csv', f"✏️ Nota atualizada para {nova_nota_edicao} e salvo!")
                    else:
                        st.info("Nenhum registro recebido para editar")
                
                st.divider()
                
                # Seção de exclusão
                st.write("*Excluir Registro:*")
                if not df_horas.empty:
                    opcoes_exclusao = []
                    for idx, row in df_horas.iterrows():
                        opcoes_exclusao.append(f"Semana {row['Semana']} - {row['Data']} - {row['Horas']}h")
                    
                    registro_exclusao = st.selectbox("Selecione para excluir:", opcoes_exclusao, key="exclusao_horas")
                    
                    if st.button("🗑️ Excluir Registro", type="secondary", key="btn_excluir_horas"):
                        idx_excluir = opcoes_exclusao.index(registro_exclusao)
                        df_horas = df_horas.drop(df_horas.index[idx_excluir]).reset_index(drop=True)
                        save_csv_data(df_horas, 'data/horas.csv', "✅ Registro excluído e salvo!")
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
        
        # Botão para registrar os ganhos CLT na renda familiar
        if st.button("💼 Registrar Ganhos CLT na Renda Familiar", key="btn_registrar_clt"):
            df_familia = load_csv_data(renda_path)
            
            # Mapeamento de mês
            meses_map = {
                "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
                "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08", 
                "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
            }
            
            mes_num = meses_map[mes]
            data_salario = f"{ano}-{mes_num}-05"
            data_vale = f"{ano}-{mes_num}-20"
            
            # Verificar se já existem registros CLT para este mês/ano
            df_familia['Data'] = pd.to_datetime(df_familia['Data'], errors='coerce')
            ja_existe_salario = any(
                (df_familia['Data'].dt.year == ano) & 
                (df_familia['Data'].dt.month == int(mes_num)) & 
                (df_familia['Tipo'].str.lower() == 'salário')
            )
            ja_existe_vale = any(
                (df_familia['Data'].dt.year == ano) & 
                (df_familia['Data'].dt.month == int(mes_num)) & 
                (df_familia['Tipo'].str.lower() == 'vale')
            )
            
            if ja_existe_salario or ja_existe_vale:
                st.warning(f"⚠️ Já existem registros CLT para {mes}/{ano}. Verifique na aba Renda.")
            else:
                # Adicionar registros CLT
                novos_registros = pd.DataFrame({
                    "Membro": ["Breno", "Breno"],
                    "Tipo": ["Salário", "Vale"],
                    "Valor": [salario, vale],
                    "Data": [data_salario, data_vale]
                })
                
                df_familia = pd.concat([df_familia, novos_registros], ignore_index=True)
                save_csv_data(df_familia, renda_path, f"✅ Ganhos CLT de {mes}/{ano} registrados na renda familiar e salvos!")
            
        st.info("💡 **Dica**: Clique no botão acima para incluir automaticamente o salário e vale na Renda Familiar.")
        
        # Seção para excluir ganhos CLT
        st.divider()
        st.subheader("🗑️ Excluir Ganhos CLT")
        
        # Filtrar registros CLT existentes na renda familiar
        df_familia_temp = load_csv_data(renda_path)
        if not df_familia_temp.empty:
            df_familia_temp['Data'] = pd.to_datetime(df_familia_temp['Data'], errors='coerce')
            registros_clt = df_familia_temp[
                (df_familia_temp['Membro'] == 'Breno') & 
                (df_familia_temp['Tipo'].isin(['Salário', 'Vale']))
            ].copy()
            
            if not registros_clt.empty:
                st.write("**Registros CLT existentes:**")
                opcoes_clt = []
                for idx, row in registros_clt.iterrows():
                    data_formatada = row['Data'].strftime('%m/%Y') if pd.notna(row['Data']) else 'Data inválida'
                    opcoes_clt.append(f"{row['Tipo']} - R$ {row['Valor']:.2f} - {data_formatada}")
                
                if opcoes_clt:
                    registro_clt_exclusao = st.selectbox("Selecione o registro CLT para excluir:", opcoes_clt, key="exclusao_clt")
                    
                    if st.button("🗑️ Excluir Registro CLT", type="secondary", key="btn_excluir_clt"):
                        idx_excluir = opcoes_clt.index(registro_clt_exclusao)
                        idx_real = registros_clt.index[idx_excluir]
                        df_familia_temp = df_familia_temp.drop(idx_real).reset_index(drop=True)
                        save_csv_data(df_familia_temp, renda_path, "✅ Registro CLT excluído e salvo!")
            else:
                st.info("Nenhum registro CLT encontrado para excluir.")
        else:
            st.info("Nenhum dado de renda familiar encontrado.")

 # ============================
 # Aba 2 – Renda Familiar
 # ============================
with abas[1]:
    st.header(" Renda Familiar")
    df_familia = load_csv_data(renda_path)
    
    # Separar valores CLT (já recebidos) dos outros
    valores_clt = df_familia[df_familia['Tipo'].str.lower().isin(['salário', 'salario', 'vale'])]['Valor'].sum()
    valores_outros = df_familia[~df_familia['Tipo'].str.lower().isin(['salário', 'salario', 'vale'])]['Valor'].sum()
    
    # Ganhos freelancer automatizados
    try:
        df_horas = load_csv_data('data/horas.csv')
        # Garantir que a coluna 'Pago' existe
        if 'Pago' not in df_horas.columns:
            df_horas['Pago'] = False
        
        # Calcular totais
        total_freela_pendente = 0
        total_freela_pago = 0
        if 'Valor_Ajustado_BRL' in df_horas.columns:
            total_freela_pago = df_horas[df_horas['Pago'] == True]['Valor_Ajustado_BRL'].sum()
            total_freela_pendente = df_horas[df_horas['Pago'] == False]['Valor_Ajustado_BRL'].sum()
        
        total_freela = total_freela_pago + total_freela_pendente
    except Exception:
        total_freela_pago = 0
        total_freela_pendente = 0
        total_freela = 0
    
    # Calcular renda total (CLT + Outros + Freelancer)
    renda_total_efetiva = valores_clt + valores_outros + total_freela_pago  # CLT sempre efetivo + outros + freelancer pago
    renda_total_projetada = renda_total_efetiva + total_freela_pendente  # Incluindo projeções freelancer
    
    st.metric("💰 Renda Familiar Efetiva", f"R$ {renda_total_efetiva:,.2f}")
    st.metric("📈 Renda Familiar Projetada", f"R$ {renda_total_projetada:,.2f}", 
              delta=f"+R$ {total_freela_pendente:,.2f} (pendente)")
    
    # Breakdown detalhado
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💼 CLT (Efetivo)", f"R$ {valores_clt:,.2f}")
    with col2:
        st.metric("🏠 Outras Rendas", f"R$ {valores_outros:,.2f}")
    with col3:
        st.metric("✅ Freelancer Recebido", f"R$ {total_freela_pago:,.2f}")
    with col4:
        st.metric("📊 Freelancer Projeção", f"R$ {total_freela_pendente:,.2f}")

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
    
    # Separar valores filtrados
    valores_clt_filtrados = df_filtrado[df_filtrado['Tipo'].str.lower().isin(['salário', 'salario', 'vale'])]['Valor'].sum()
    valores_outros_filtrados = df_filtrado[~df_filtrado['Tipo'].str.lower().isin(['salário', 'salario', 'vale'])]['Valor'].sum()
    renda_total_filtrada = valores_clt_filtrados + valores_outros_filtrados + total_freela_pago

    st.metric("💰 Renda Família Filtrada (Efetiva)", f"R$ {renda_total_filtrada:,.2f}")
    
    # Breakdown do filtro
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.caption(f"💼 CLT Filtrado: R$ {valores_clt_filtrados:,.2f}")
    with col_f2:
        st.caption(f"🏠 Outras Rendas: R$ {valores_outros_filtrados:,.2f}")
    with col_f3:
        st.caption(f"✅ Freelancer Pago: R$ {total_freela_pago:,.2f}")

    # Gráfico resumo mensal Freelancer e CLT
    try:
        # Freelancer
        df_horas = pd.read_csv('data/horas.csv')
        if 'Data' in df_horas.columns and 'Valor_Ajustado_BRL' in df_horas.columns:
            # Garantir que a coluna 'Pago' existe
            if 'Pago' not in df_horas.columns:
                df_horas['Pago'] = False
            
            df_horas['Data'] = pd.to_datetime(df_horas['Data'])
            df_horas['MesAno'] = df_horas['Data'].dt.strftime('%Y-%m')
            
            # Separar pagos e pendentes
            resumo_freela_pago = df_horas[df_horas['Pago'] == True].groupby('MesAno')['Valor_Ajustado_BRL'].sum().reset_index()
            resumo_freela_pago = resumo_freela_pago.rename(columns={'Valor_Ajustado_BRL': 'Freelancer_Pago'})
            
            resumo_freela_pendente = df_horas[df_horas['Pago'] == False].groupby('MesAno')['Valor_Ajustado_BRL'].sum().reset_index()
            resumo_freela_pendente = resumo_freela_pendente.rename(columns={'Valor_Ajustado_BRL': 'Freelancer_Pendente'})
        else:
            resumo_freela_pago = pd.DataFrame(columns=['MesAno', 'Freelancer_Pago'])
            resumo_freela_pendente = pd.DataFrame(columns=['MesAno', 'Freelancer_Pendente'])
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
        # Primeiro merge dos dados de freelancer
        resumo_freelancer = pd.merge(resumo_freela_pago, resumo_freela_pendente, on='MesAno', how='outer').fillna(0).infer_objects(copy=False)
        
        # Depois merge com CLT
        resumo = pd.merge(resumo_freelancer, resumo_clt, on='MesAno', how='outer').fillna(0).infer_objects(copy=False)
        resumo = resumo.sort_values('MesAno')
        if not resumo.empty:
            fig_mensal = px.bar(resumo, x='MesAno', y=['Freelancer_Pago', 'Freelancer_Pendente', 'CLT'], barmode='group',
                               title='💰 Ganhos Efetivos vs 📈 Projeções Mensais',
                               labels={'value':'Total (R$)','MesAno':'Mês/Ano','variable':'Tipo'},
                               color_discrete_map={
                                   'Freelancer_Pago': '#1DE9B6',
                                   'Freelancer_Pendente': '#FFA726', 
                                   'CLT': '#42A5F5'
                               })
            
            # Personalizar legendas
            fig_mensal.for_each_trace(lambda t: t.update(name={
                'Freelancer_Pago': '✅ Freelancer Recebido',
                'Freelancer_Pendente': '📊 Freelancer Projeção',
                'CLT': '💼 CLT'
            }[t.name]))
            
            st.plotly_chart(fig_mensal, use_container_width=True)
    except Exception as e:
        st.info(f"Não foi possível gerar o gráfico mensal: {e}")

    fig2 = px.pie(df_filtrado, names='Tipo', values='Valor', title='Distribuição da Renda Filtrada')
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(df_filtrado)

    # Funcionalidade de exclusão para renda
    st.subheader("🗑️ Excluir Registro de Renda")
    if not df_familia.empty:
        opcoes_exclusao_renda = []
        for idx, row in df_familia.iterrows():
            opcoes_exclusao_renda.append(f"{row['Membro']} - {row['Tipo']} - R$ {row['Valor']:.2f} - {row['Data']}")
        
        registro_exclusao_renda = st.selectbox("Selecione para excluir:", opcoes_exclusao_renda, key="exclusao_renda")
        
        if st.button("🗑️ Excluir Registro de Renda", type="secondary", key="btn_excluir_renda"):
            idx_excluir = opcoes_exclusao_renda.index(registro_exclusao_renda)
            df_familia = df_familia.drop(df_familia.index[idx_excluir]).reset_index(drop=True)
            save_csv_data(df_familia, renda_path, "✅ Registro de renda excluído e salvo!")

    st.subheader("➕ Adicionar nova renda familiar")
    with st.form("form_renda"):
        membro = st.selectbox("Nome do membro", ["Breno", "Sara", "Adhara", "Outro"], key="membro_renda")
        if membro == "Outro":
            membro = st.text_input("Digite o nome do membro")
        tipo = st.selectbox("Tipo de renda", ["Salário", "Freelance", "Investimento", "Vale", "Outro"])
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
            save_csv_data(df_familia, renda_path, f"✅ Renda de {membro} adicionada e salva com sucesso!")



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
            save_csv_data(df_despesas, despesas_path, f"✅ Despesa de {membro_d} adicionada e salva com sucesso!")

    # Funcionalidade de exclusão para despesas
    st.subheader("🗑️ Excluir Registro de Despesa")
    if not df_despesas.empty:
        opcoes_exclusao_despesa = []
        for idx, row in df_despesas.iterrows():
            opcoes_exclusao_despesa.append(f"{row['Membro']} - {row['Categoria']} - R$ {row['Valor']:.2f} - {row['Data']}")
        
        registro_exclusao_despesa = st.selectbox("Selecione para excluir:", opcoes_exclusao_despesa, key="exclusao_despesa")
        
        if st.button("🗑️ Excluir Registro de Despesa", type="secondary", key="btn_excluir_despesa"):
            idx_excluir = opcoes_exclusao_despesa.index(registro_exclusao_despesa)
            df_despesas = df_despesas.drop(df_despesas.index[idx_excluir]).reset_index(drop=True)
            save_csv_data(df_despesas, despesas_path, "✅ Registro de despesa excluído e salvo!")



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
            save_csv_data(df_invest, invest_path, f"✅ Investimento de {membro_i} adicionado e salvo com sucesso!")

    # Funcionalidade de exclusão para investimentos
    st.subheader("🗑️ Excluir Registro de Investimento")
    if not df_invest.empty:
        opcoes_exclusao_invest = []
        for idx, row in df_invest.iterrows():
            opcoes_exclusao_invest.append(f"{row['Membro']} - {row['Tipo']} - R$ {row['Valor']:.2f} - {row['Data']}")
        
        registro_exclusao_invest = st.selectbox("Selecione para excluir:", opcoes_exclusao_invest, key="exclusao_invest")
        
        if st.button("🗑️ Excluir Registro de Investimento", type="secondary", key="btn_excluir_invest"):
            idx_excluir = opcoes_exclusao_invest.index(registro_exclusao_invest)
            df_invest = df_invest.drop(df_invest.index[idx_excluir]).reset_index(drop=True)
            save_csv_data(df_invest, invest_path, "✅ Registro de investimento excluído e salvo!")


# ============================
# Aba 5 – Empréstimos
# ============================
with abas[4]:
    st.header("💳 Controle de Empréstimos")
    
    df_emprestimos = load_csv_data(emprestimos_path, ['Nome', 'Tipo', 'Valor_Original', 'Valor_Com_Juros', 'Parcelas_Total', 'Parcelas_Pagas', 'Valor_Parcela', 'Data_Emprestimo', 'Status', 'Observacoes'])
    
    # Função auxiliar para integrar com renda familiar
    def registrar_emprestimo_na_renda(nome, valor, tipo_transacao, data):
        """Registra empréstimo recebido na renda ou parcela paga como despesa"""
        renda_path = 'data/familia.csv'
        df_familia = load_csv_data(renda_path, ['Membro', 'Tipo', 'Valor', 'Data'])
        
        novo_registro = pd.DataFrame({
            'Membro': [nome],
            'Tipo': [tipo_transacao],
            'Valor': [valor],
            'Data': [data]
        })
        
        df_familia = pd.concat([df_familia, novo_registro], ignore_index=True)
        save_csv_data(df_familia, renda_path, f"✅ {tipo_transacao} registrado na renda familiar!")
    
    # Métricas gerais
    if not df_emprestimos.empty:
        # Calcular valores
        emprestimos_feitos = df_emprestimos[df_emprestimos['Tipo'] == 'Emprestado']['Valor_Com_Juros'].sum()
        emprestimos_recebidos = df_emprestimos[df_emprestimos['Tipo'] == 'Recebido']['Valor_Original'].sum()
        
        # Valores pendentes
        pendentes_receber = 0
        pendentes_pagar = 0
        
        for _, row in df_emprestimos.iterrows():
            parcelas_restantes = row['Parcelas_Total'] - row['Parcelas_Pagas']
            valor_restante = parcelas_restantes * row['Valor_Parcela']
            
            if row['Tipo'] == 'Emprestado' and row['Status'] == 'Ativo':
                pendentes_receber += valor_restante
            elif row['Tipo'] == 'Recebido' and row['Status'] == 'Ativo':
                pendentes_pagar += valor_restante
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💸 Total Emprestado", f"R$ {emprestimos_feitos:,.2f}")
        with col2:
            st.metric("💰 Total Recebido", f"R$ {emprestimos_recebidos:,.2f}")
        with col3:
            st.metric("⏳ A Receber", f"R$ {pendentes_receber:,.2f}")
        with col4:
            st.metric("📋 A Pagar", f"R$ {pendentes_pagar:,.2f}")
        
        # Saldo líquido
        saldo_liquido = pendentes_receber - pendentes_pagar
        if saldo_liquido > 0:
            st.metric("📊 Saldo Líquido", f"R$ {saldo_liquido:,.2f}", delta="Saldo positivo")
        elif saldo_liquido < 0:
            st.metric("📊 Saldo Líquido", f"R$ {abs(saldo_liquido):,.2f}", delta="Saldo negativo")
        else:
            st.metric("📊 Saldo Líquido", "R$ 0,00", delta="Equilibrado")
    
    # Exibir dados dos empréstimos
    if not df_emprestimos.empty:
        st.subheader("📋 Registros de Empréstimos")
        
        # Criar dados para exibição
        df_display = df_emprestimos.copy()
        df_display['Data_Emprestimo'] = pd.to_datetime(df_display['Data_Emprestimo']).dt.strftime('%d/%m/%Y')
        df_display['Parcelas_Restantes'] = df_display['Parcelas_Total'] - df_display['Parcelas_Pagas']
        df_display['Valor_Restante'] = df_display['Parcelas_Restantes'] * df_display['Valor_Parcela']
        df_display['Progresso'] = (df_display['Parcelas_Pagas'] / df_display['Parcelas_Total'] * 100).round(1)
        
        # Função para destacar por status
        def highlight_status_emp(row):
            if row['Status'] == 'Ativo':
                return ['background-color: #FFA726; color: #000000;' for _ in row]
            elif row['Status'] == 'Quitado':
                return ['background-color: #1DE9B6; color: #181C2F;' for _ in row]
            return ['' for _ in row]
        
        # Selecionar colunas para exibir
        colunas_exibir = ['Nome', 'Tipo', 'Valor_Original', 'Valor_Com_Juros', 'Valor_Parcela', 
                         'Parcelas_Pagas', 'Parcelas_Total', 'Parcelas_Restantes', 'Valor_Restante', 
                         'Progresso', 'Status', 'Data_Emprestimo']
        
        df_show = df_display[colunas_exibir]
        
        st.dataframe(df_show.style.apply(highlight_status_emp, axis=1).format({
            'Valor_Original': 'R$ {:.2f}',
            'Valor_Com_Juros': 'R$ {:.2f}',
            'Valor_Parcela': 'R$ {:.2f}',
            'Valor_Restante': 'R$ {:.2f}',
            'Progresso': '{:.1f}%'
        }), use_container_width=True)
        
        # Gráficos de acompanhamento
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            # Gráfico de progresso dos empréstimos
            if not df_emprestimos.empty:
                fig_progresso = px.bar(
                    df_display, 
                    x='Nome', 
                    y=['Parcelas_Pagas', 'Parcelas_Restantes'],
                    title='Progresso dos Empréstimos',
                    labels={'value': 'Parcelas', 'variable': 'Status'},
                    color_discrete_map={'Parcelas_Pagas': '#1DE9B6', 'Parcelas_Restantes': '#FFA726'}
                )
                st.plotly_chart(fig_progresso, use_container_width=True)
        
        with col_g2:
            # Gráfico de valores por tipo
            if not df_emprestimos.empty:
                resumo_tipo = df_emprestimos.groupby('Tipo').agg({
                    'Valor_Original': 'sum',
                    'Valor_Com_Juros': 'sum'
                }).reset_index()
                
                fig_valores = px.bar(
                    resumo_tipo, 
                    x='Tipo', 
                    y=['Valor_Original', 'Valor_Com_Juros'],
                    title='Valores por Tipo',
                    labels={'value': 'Valor (R$)', 'variable': 'Tipo de Valor'},
                    color_discrete_map={'Valor_Original': '#2196F3', 'Valor_Com_Juros': '#FF5722'}
                )
                st.plotly_chart(fig_valores, use_container_width=True)
        
        # Gráficos
        col_g1, col_g2 = st.columns(2)
        
    
    # Formulário para adicionar empréstimo
    st.subheader("➕ Adicionar Novo Empréstimo")
    with st.form("form_emprestimo"):
        col_form1, col_form2, col_form3 = st.columns(3)
        
        with col_form1:
            nome_emp = st.text_input("Nome da Pessoa:")
            tipo_emp = st.selectbox("Tipo:", ["Emprestado", "Recebido"], 
                                   help="Emprestado = Você emprestou para alguém | Recebido = Você pegou emprestado")
            valor_original = st.number_input("Valor Original (R$):", min_value=0.0, step=10.0)
        
        with col_form2:
            taxa_juros = st.number_input("Taxa de Juros (%):", min_value=0.0, max_value=100.0, step=0.1, value=0.0)
            parcelas_total = st.number_input("Total de Parcelas:", min_value=1, step=1, value=1)
            data_emprestimo = st.date_input("Data do Empréstimo:")
        
        with col_form3:
            # Cálculos automáticos
            if valor_original > 0 and parcelas_total > 0:
                valor_com_juros = valor_original * (1 + taxa_juros/100)
                valor_parcela = valor_com_juros / parcelas_total
                
                st.write(f"**Valor com Juros:** R$ {valor_com_juros:.2f}")
                st.write(f"**Valor da Parcela:** R$ {valor_parcela:.2f}")
            else:
                valor_com_juros = 0
                valor_parcela = 0
                
            observacoes_emp = st.text_area("Observações:", placeholder="Ex: condições especiais, etc.")
        
        enviar_emp = st.form_submit_button("💳 Registrar Empréstimo")
        
        if enviar_emp and nome_emp and valor_original > 0:
            novo_emprestimo = pd.DataFrame({
                "Nome": [nome_emp],
                "Tipo": [tipo_emp],
                "Valor_Original": [valor_original],
                "Valor_Com_Juros": [valor_com_juros],
                "Parcelas_Total": [parcelas_total],
                "Parcelas_Pagas": [0],
                "Valor_Parcela": [valor_parcela],
                "Data_Emprestimo": [data_emprestimo],
                "Status": ["Ativo"],
                "Observacoes": [observacoes_emp]
            })
            
            df_emprestimos = pd.concat([df_emprestimos, novo_emprestimo], ignore_index=True)
            save_csv_data(df_emprestimos, emprestimos_path, f"✅ Empréstimo {tipo_emp.lower()} para/de {nome_emp} registrado e salvo!")
            
            # Se é empréstimo recebido, adicionar na renda familiar
            if tipo_emp == "Recebido":
                registrar_emprestimo_na_renda(nome_emp, valor_original, "Empréstimo Recebido", data_emprestimo)
                
        elif enviar_emp:
            st.error("❌ Por favor, preencha todos os campos obrigatórios.")
    
    
    # Controles de gerenciamento
    if not df_emprestimos.empty:
        st.subheader("🔧 Gerenciar Empréstimos")
        
        # Seção de pagamento de parcelas
        st.write("**💳 Registrar Pagamento de Parcela:**")
        emprestimos_ativos = df_emprestimos[df_emprestimos['Status'] == 'Ativo']
        
        if not emprestimos_ativos.empty:
            opcoes_pagamento = []
            indices_pagamento = []
            
            for idx, row in emprestimos_ativos.iterrows():
                parcelas_restantes = row['Parcelas_Total'] - row['Parcelas_Pagas']
                if parcelas_restantes > 0:
                    opcoes_pagamento.append(f"{row['Nome']} - {row['Tipo']} - Parcela {row['Parcelas_Pagas']+1}/{row['Parcelas_Total']} - R$ {row['Valor_Parcela']:.2f}")
                    indices_pagamento.append(idx)
            
            if opcoes_pagamento:
                parcela_pagar = st.selectbox("Selecione a parcela:", opcoes_pagamento, key="pagar_parcela")
                data_pagamento = st.date_input("Data do Pagamento:", key="data_pagamento")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💰 Registrar Pagamento", key="btn_pagar_parcela"):
                        idx_pagar = indices_pagamento[opcoes_pagamento.index(parcela_pagar)]
                        row_atual = df_emprestimos.loc[idx_pagar]
                        
                        # Atualizar parcelas pagas
                        df_emprestimos.loc[idx_pagar, 'Parcelas_Pagas'] += 1
                        
                        # Verificar se foi quitado
                        if df_emprestimos.loc[idx_pagar, 'Parcelas_Pagas'] >= df_emprestimos.loc[idx_pagar, 'Parcelas_Total']:
                            df_emprestimos.loc[idx_pagar, 'Status'] = 'Quitado'
                            status_msg = "e empréstimo quitado"
                        else:
                            status_msg = ""
                        
                        # Registrar como despesa na renda familiar se for empréstimo recebido
                        if row_atual['Tipo'] == 'Recebido':
                            registrar_emprestimo_na_renda(row_atual['Nome'], row_atual['Valor_Parcela'], "Pagamento Empréstimo", data_pagamento)
                        
                        save_csv_data(df_emprestimos, emprestimos_path, f"✅ Parcela registrada {status_msg} e salvo!")
                
                with col_btn2:
                    if st.button("📋 Quitar Totalmente", key="btn_quitar_total"):
                        idx_quitar = indices_pagamento[opcoes_pagamento.index(parcela_pagar)]
                        row_atual = df_emprestimos.loc[idx_quitar]
                        
                        # Calcular parcelas restantes
                        parcelas_restantes = row_atual['Parcelas_Total'] - row_atual['Parcelas_Pagas']
                        valor_restante = parcelas_restantes * row_atual['Valor_Parcela']
                        
                        # Quitar totalmente
                        df_emprestimos.loc[idx_quitar, 'Parcelas_Pagas'] = row_atual['Parcelas_Total']
                        df_emprestimos.loc[idx_quitar, 'Status'] = 'Quitado'
                        
                        # Registrar valor restante como despesa se for empréstimo recebido
                        if row_atual['Tipo'] == 'Recebido':
                            registrar_emprestimo_na_renda(row_atual['Nome'], valor_restante, "Quitação Empréstimo", data_pagamento)
                        
                        save_csv_data(df_emprestimos, emprestimos_path, f"✅ Empréstimo quitado totalmente (R$ {valor_restante:.2f}) e salvo!")
            else:
                st.info("Nenhuma parcela pendente para pagamento")
        else:
            st.info("Nenhum empréstimo ativo")
            
        st.divider()
        
        # Seção de exclusão
        st.write("**🗑️ Excluir Registro:**")
        opcoes_exclusao_emp = []
        for idx, row in df_emprestimos.iterrows():
            opcoes_exclusao_emp.append(f"{row['Nome']} - {row['Tipo']} - R$ {row['Valor_Original']:.2f} - {row['Status']}")
        
        registro_exclusao_emp = st.selectbox("Selecione para excluir:", opcoes_exclusao_emp, key="exclusao_emprestimo")
        
        if st.button("🗑️ Excluir Registro de Empréstimo", type="secondary", key="btn_excluir_emprestimo"):
            idx_excluir = opcoes_exclusao_emp.index(registro_exclusao_emp)
            df_emprestimos = df_emprestimos.drop(df_emprestimos.index[idx_excluir]).reset_index(drop=True)
            save_csv_data(df_emprestimos, emprestimos_path, "✅ Registro de empréstimo excluído e salvo!")