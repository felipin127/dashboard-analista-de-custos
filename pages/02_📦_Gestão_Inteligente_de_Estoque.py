import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from analysis import calcular_saude_estoque
except ImportError:
    st.error("Erro: Não foi possível encontrar ou ler o arquivo 'analysis.py'. Verifique se ele não tem erros de sintaxe.")
    st.stop()

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(
    page_title="Gestão de Estoque",
    page_icon="📦",
    layout="wide"
)

# =============================================
# CSS (Bloco de Estilo Profissional - COM SIDEBAR)
# =============================================
st.markdown("""
<style>
    /* Estilos do App */
    .main-header {
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 100%);
        padding: 2.5rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        text-align: center;
        border: 1px solid #FF6B6B;
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
    
    /* --- ESTILOS DA SIDEBAR (RESTAURADOS) --- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A202C 0%, #0E1117 100%);
        border-right: 2px solid #DC143C; /* Borda vermelha */
    }
    [data-testid="stSidebarUserContent"] h1 {
        color: #FFD700;
        text-align: center;
        font-size: 1.8rem;
    }
    .stMultiSelect > div {
        background-color: #2D3748;
        border-radius: 5px;
    }
    [data-testid="stSidebarNav"] a {
        color: #FAFAFA;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    [data-testid="stSidebarNav"] a:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: #FFD700;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #DC143C;
        color: #FFFFFF;
        font-weight: bold;
    }

    /* Tabela */
    [data-testid="stDataFrame"] {
        border: 1px solid #4A5568;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

if 'df_estoque' not in st.session_state or st.session_state.df_estoque is None:
    st.warning("⚠️ Dados não carregados. Verifique a página inicial (app).")
    st.stop()

# Recupera os dados completos
df_estoque_completo = st.session_state.df_estoque.copy()

# =============================================
# LIMPEZA DE DADOS (CORREÇÃO DO 'nan')
# =============================================
# 1. Remove linhas onde a descrição é nula
df_estoque_completo = df_estoque_completo.dropna(subset=['descricao'])

# 2. Converte para string e remove espaços extras
df_estoque_completo['descricao'] = df_estoque_completo['descricao'].astype(str).str.strip()

# 3. Filtra palavras proibidas que aparecem como lixo no Excel (nan, total, etc)
filtros_lixo = ['nan', 'none', '', '0', 'total', 'grand total']
df_estoque_completo = df_estoque_completo[~df_estoque_completo['descricao'].str.lower().isin(filtros_lixo)]


# =============================================
# 🔍 FILTROS NA BARRA LATERAL (SIDEBAR)
# =============================================
with st.sidebar:
    st.header("Filtros de Estoque")
    st.info("Selecione produtos específicos para filtrar o gráfico e os indicadores.")
    
    # Lista de produtos ordenada (agora limpa)
    lista_produtos = sorted(df_estoque_completo['descricao'].unique())

    # Filtro Multiselect
    produtos_selecionados = st.multiselect(
        "Filtrar por Produto:",
        options=lista_produtos,
        placeholder="Selecione um ou mais produtos...",
        help="Se deixar vazio, mostraremos os Top 10 produtos por valor."
    )

# --- LÓGICA DE FILTRAGEM ---
if produtos_selecionados:
    # Se selecionou, mostra apenas os selecionados
    df_estoque_filtrado = df_estoque_completo[df_estoque_completo['descricao'].isin(produtos_selecionados)]
    titulo_grafico = "Produtos Selecionados em Estoque"
else:
    # Se NÃO selecionou, mostra tudo (mas o gráfico limitará aos Top 10)
    df_estoque_filtrado = df_estoque_completo
    titulo_grafico = "Principais Produtos em Estoque (Top 10)"


# =============================================
# RENDERIZAÇÃO DA PÁGINA
# =============================================

st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📦 Gestão Inteligente de Estoque</div>', unsafe_allow_html=True)

# --- GRÁFICO: VALOR EM ESTOQUE ---
st.markdown(f"### {titulo_grafico}")

if not df_estoque_filtrado.empty:
    # Prepara dados para o gráfico
    df_grafico = df_estoque_filtrado.sort_values('valor_estoque', ascending=False)
    
    # Se não houver filtro, pega só os top 10 para não travar o gráfico
    if not produtos_selecionados:
        df_grafico = df_grafico.head(10)

    fig_estoque = px.bar(df_grafico,
                        x='descricao',
                        y='valor_estoque',
                        color='valor_estoque',
                        color_continuous_scale='reds',
                        labels={'descricao': 'Produto', 'valor_estoque': 'Valor Total (R$)'}
                        )
    
    fig_estoque.update_layout(template='plotly_dark', showlegend=False)
    st.plotly_chart(fig_estoque, use_container_width=True)
else:
    st.info("Nenhum produto encontrado com os filtros atuais.")

st.markdown("---")

# --- KPIs: SAÚDE DO ESTOQUE (FILTRADO) ---
# Recalcula as métricas com base no filtro
metricas = calcular_saude_estoque(df_estoque_filtrado)

st.markdown("### 📊 Saúde do Estoque (Seleção)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    valor_formatado = f"R$ {metricas['valor_total']:,.2f}" if metricas['valor_total'] else "R$ 0,00"
    st.metric("Valor Total", valor_formatado)

with col2:
    st.metric("Itens de Carne", f"{metricas['total_carnes']}")

with col3:
    qtd_devolvida = f"{metricas['total_devolvido']:,.0f}" if metricas['total_devolvido'] else "0"
    st.metric("Devoluções (Qtd)", qtd_devolvida)

with col4:
    st.metric("Negativos", f"{metricas['produtos_negativos']}", 
              delta="-Crítico" if metricas['produtos_negativos'] > 0 else "Ok", delta_color="inverse")

st.markdown("---")

# --- TABELA DETALHADA ---
with st.expander("📋 Ver Tabela de Dados Detalhada"):
    st.dataframe(
        df_estoque_filtrado[['codigo', 'descricao', 'unidade', 'estoque', 'valor_estoque', 'tipo_produto']],
        use_container_width=True,
        hide_index=True
    )

st.markdown(f"""
<div class="info-box">
<h4>💡 Dica de Gestão:</h4>
<p>Use o filtro na barra lateral para auditar grupos específicos de produtos. Produtos com <b>estoque negativo</b> devem ser prioridade na contagem física.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)