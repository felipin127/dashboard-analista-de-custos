import streamlit as st
import pandas as pd
import plotly.express as px

try:
    # A função agora retorna 3 dataframes:
    from analysis import calcular_analise_capital
except ImportError:
    st.error("Erro: Não foi possível encontrar ou ler o arquivo 'analysis.py'. Verifique se ele contém a função 'calcular_analise_capital'.")
    st.stop()

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(
    page_title="Análise de Capital",
    page_icon="💰",
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
    
    /* CAIXA DE INSIGHTS */
    .info-box {
        background: #2D3748;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 6px solid #4299E1;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .info-box h3 {
        margin-top: 0;
        margin-bottom: 15px;
        color: #FAFAFA;
        font-size: 1.4rem;
        display: flex;
        align-items: center;
    }
    .info-box ul {
        margin-left: 20px;
        color: #E2E8F0;
    }
    .info-box li {
        margin-bottom: 12px; /* Espaçamento entre recomendações */
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .info-box b {
        color: #FFFFFF;
        font-weight: 700;
    }

    /* --- ESTILOS DA SIDEBAR (DESIGN RESTAURADO) --- */
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
</style>
""", unsafe_allow_html=True)

# Validação: Checa se os dados existem
if 'df_estoque' not in st.session_state or st.session_state.df_estoque is None:
    st.warning("⚠️ Dados não carregados. Verifique a página inicial (app).")
    st.stop()

# Recupera os dados completos
df_estoque_completo = st.session_state.df_estoque.copy()

# =============================================
# 🔍 FILTRO NA BARRA LATERAL (SIDEBAR)
# =============================================
with st.sidebar:
    st.header("Filtros")
    st.info("Este filtro aplica-se **apenas** ao gráfico de Devoluções (Direita).")
    
    # Pega as categorias únicas disponíveis
    categorias_disponiveis = df_estoque_completo['tipo_produto'].unique()

    # Cria o seletor
    categorias_selecionadas = st.multiselect(
        "Filtrar Categorias:",
        options=categorias_disponiveis,
        default=categorias_disponiveis, # Por padrão, seleciona tudo
        placeholder="Selecione..."
    )
    
# Aplica o filtro (apenas para o segundo conjunto de dados)
if not categorias_selecionadas:
    df_estoque_filtrado = pd.DataFrame(columns=df_estoque_completo.columns) # DF Vazio
    st.sidebar.warning("Selecione pelo menos uma categoria.")
else:
    df_estoque_filtrado = df_estoque_completo[df_estoque_completo['tipo_produto'].isin(categorias_selecionadas)]


# =============================================
# CÁLCULOS
# =============================================

# 1. DADOS GERAIS (Capital)
_, _, capital_simplificado_total = calcular_analise_capital(df_estoque_completo)

# 2. DADOS FILTRADOS (Devoluções)
_, devolucao_df_filtrado, _ = calcular_analise_capital(df_estoque_filtrado)


# =============================================
# RENDERIZAÇÃO
# =============================================

st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💰 Análise de Capital e Devoluções</div>', unsafe_allow_html=True)

# Cria duas colunas lado a lado com um espaçamento grande
col1, col2 = st.columns(2, gap="large")


# --- COLUNA 1: CAPITAL ALOCADO (AGORA PIZZA/DONUT) ---
with col1:
    st.subheader("Capital Alocado (Geral)")
    st.caption("Distribuição do valor parado em estoque (sem filtros).")

    if not capital_simplificado_total.empty:
        # Gráfico de Pizza (Donut)
        fig_capital = px.pie(capital_simplificado_total,
                            names='tipo_produto',
                            values='valor_estoque',
                            # title='Distribuição do Valor',
                            hole=0.4, # Faz o buraco no meio
                            color_discrete_sequence=px.colors.sequential.RdBu
                            )
        
        fig_capital.update_traces(textposition='inside', textinfo='percent+label')
        fig_capital.update_layout(template='plotly_dark', showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_capital, use_container_width=True)
    else:
        st.info("📊 Sem dados de estoque.")


# --- COLUNA 2: DEVOLUÇÕES (HORIZONTAL - FILTRADO) ---
with col2:
    st.subheader("Devoluções (Filtrado)")
    st.caption("Valor devolvido nas categorias selecionadas.")

    if not devolucao_df_filtrado.empty and devolucao_df_filtrado['valor_devolvida'].sum() > 0:
        
        # Ordenar para gráfico horizontal
        devolucao_sorted = devolucao_df_filtrado.sort_values('valor_devolvida', ascending=True)

        fig_devolucao = px.bar(devolucao_sorted,
                               x='valor_devolvida',
                               y='tipo_produto',
                               orientation='h',
                               # title='Valor Devolvido',
                               color='valor_devolvida',
                               color_continuous_scale='reds',
                               labels={'tipo_produto': 'Categoria', 'valor_devolvida': 'Valor Devolvido (R$)'})
        
        fig_devolucao.update_layout(template='plotly_dark', showlegend=False, yaxis_title=None, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_devolucao, use_container_width=True)
    else:
        st.info("📊 Sem devoluções para a seleção.")

st.markdown("---")

# --- INSIGHT INTELIGENTE ---
if not capital_simplificado_total.empty:
    # Encontra a categoria com maior valor em estoque
    maior_cap_row = capital_simplificado_total.loc[capital_simplificado_total['valor_estoque'].idxmax()]
    cat_maior_cap = maior_cap_row['tipo_produto']
    val_maior_cap = maior_cap_row['valor_estoque']
    
    # Verifica devolução da mesma categoria
    alerta_devolucao = ""
    if not devolucao_df_filtrado.empty:
        if cat_maior_cap in devolucao_df_filtrado['tipo_produto'].values:
             val_dev = devolucao_df_filtrado.loc[devolucao_df_filtrado['tipo_produto'] == cat_maior_cap, 'valor_devolvida'].sum()
             if val_dev > 0:
                 alerta_devolucao = f"<br><br>⚠️ <b>Atenção:</b> Esta categoria também possui R$ {val_dev:,.2f} em devoluções. Verifique a validade dos lotes, a temperatura de armazenamento ou renegocie com o fornecedor."

    st.markdown(f"""
    <div class="info-box">
    <h3>💡 Insight Financeiro:</h3>
    <p>A categoria <b>{cat_maior_cap}</b> imobiliza a maior parte do seu capital de giro (R$ {val_maior_cap:,.2f}). {alerta_devolucao}</p>
    <p><b>Recomendação:</b> Se o giro de estoque desta categoria for lento, considere fazer promoções para liberar caixa.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)