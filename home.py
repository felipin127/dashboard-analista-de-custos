import streamlit as st
import pandas as pd
import warnings
import os 
warnings.filterwarnings('ignore')

# IMPORTANDO FUNÇÕES (Apenas as 2 necessárias)
try:
    from data_loader import processar_dados_vendas, processar_dados_estoque
except ImportError:
    st.error("Erro crítico: Não foi possível encontrar 'data_loader.py'. Verifique se o arquivo está na pasta raiz.")
    st.stop()

# =============================================
# CONFIGURAÇÃO DA PÁGINA E CSS
# =============================================
st.set_page_config(
    page_title="Martins Analytics",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS PROFISSIONAL
st.markdown("""
<style>
    /* Estilos do App (Header, Seções, etc.) */
    .main-header {
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 100%);
        padding: 2.5rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        text-align: center;
        border: 1px solid #FF6B6B;
    }
    .header-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #FFFFFF, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .analysis-section {
        background: linear-gradient(135deg, #1E293B 0%, #2D3748 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #4A5568;
        margin-bottom: 2rem;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: #FFD700;
        text-align: center;
        border-bottom: 2px solid #DC143C;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background: #2D3748;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4299E1;
        margin: 1rem 0;
    }

    /* --- ESTILOS DA SIDEBAR --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A202C 0%, #0E1117 100%);
        border-right: 2px solid #DC143C; /* Borda vermelha */
    }
    [data-testid="stSidebarUserContent"] h1 {
        color: #FFD700; /* Dourado */
        text-align: center;
        font-size: 1.8rem;
    }
    [data-testid="stSidebarNav"] a {
        color: #FAFAFA; /* Branco */
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    [data-testid="stSidebarNav"] a:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: #FFD700; /* Dourado no hover */
    }
    /* Estilo da Página Ativa (Qualquer página) */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #DC143C;
        color: #FFFFFF;
        font-weight: bold;
    }
    [data-testid="stNotification"][data-st-notification-type="success"] {
        background-color: #1a422a;
        color: #b3ffb3;
        border-radius: 10px;
        border: 1px solid #00C851;
        font-weight: bold;
        text-align: center;
    }
    [data-testid="stNotification"][data-st-notification-type="error"] {
        background-color: #4d1c1c;
        color: #ffb3b3;
        border-radius: 10px;
        border: 1px solid #DC143C;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# =============================================
# FUNÇÃO DE CARREGAMENTO (COM CACHE - 2 ARQUIVOS)
# =============================================
@st.cache_data
def carregar_dados_automaticamente():
    """Carrega os dados da pasta /data e processa."""
    
    # Nomes dos arquivos na pasta data/
    CAMINHO_VENDAS = os.path.join('data', 'Relatorio.xlsx')
    CAMINHO_ESTOQUE = os.path.join('data', 'RelatorioProd.xlsx')
    
    df_vendas, df_estoque, erro_carregamento = None, None, None
    
    try:
        # Carregar dados
        df_vendas_raw = pd.read_excel(CAMINHO_VENDAS)
        df_estoque_raw = pd.read_excel(CAMINHO_ESTOQUE)
        
        # Processar dados
        df_vendas = processar_dados_vendas(df_vendas_raw)
        df_estoque = processar_dados_estoque(df_estoque_raw)
        
        if df_vendas is None or df_estoque is None:
             erro_carregamento = "❌ Erro no processamento dos dados. Verifique a formatação dos arquivos."
             
    except FileNotFoundError:
        erro_carregamento = f"🚨 Erro: Arquivos não encontrados na pasta 'data/'. Verifique os nomes: {CAMINHO_VENDAS} e {CAMINHO_ESTOQUE}."
    except Exception as e:
        erro_carregamento = f"❌ Erro ao ler ou processar os arquivos: {str(e)}"
        
    return df_vendas, df_estoque, erro_carregamento

# =============================================
# EXECUÇÃO PRINCIPAL (APP.PY)
# =============================================

# 1. CARREGAMENTO DOS DADOS (Sempre roda primeiro)
df_vendas, df_estoque, erro_carregamento = carregar_dados_automaticamente()

# 2. ARMAZENAMENTO NA SESSION STATE (Para as outras páginas)
st.session_state.df_vendas = df_vendas
st.session_state.df_estoque = df_estoque
# (df_caixa foi removido)
    
# 3. SIDEBAR (APENAS LOGO E STATUS)
with st.sidebar:
    st.title("🥩 Martins Carnes")
    st.markdown("---")
    
    # Status do Carregamento
    if erro_carregamento:
        st.error("Falha ao carregar dados.")
    elif st.session_state.df_vendas is not None:
        st.success("Dados carregados!")
    
    # A NAVEGAÇÃO (as 4 páginas) APARECE AUTOMATICAMENTE AQUI

# 4. HEADER (Conteúdo Principal)
st.markdown("""
<div class='main-header'>
    <h1 class='header-title'>MARTINS ANALYTICS</h1>
    <p class='header-subtitle'>Análise Inteligente do Setor de Carnes</p>
</div>
""", unsafe_allow_html=True)

# 5. CONTEÚDO PRINCIPAL (Apenas Boas-vindas)
st.markdown("<div class='analysis-section'>", unsafe_allow_html=True)
st.markdown("## 📊 Bem-vindo ao Martins Analytics!")
st.markdown("Selecione uma das análises na barra lateral à esquerda para começar.")

if erro_carregamento:
    st.error(erro_carregamento) # Mostra o erro detalhado

st.markdown("</div>", unsafe_allow_html=True)
    
# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #A0A0A0;'>🥩 <b>Martins Analytics</b> • © 2024</div>", unsafe_allow_html=True)

