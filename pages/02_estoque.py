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
# CSS (Deve ser adicionado em todas as páginas)
# =============================================
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

    /* --- NOVOS ESTILOS DA SIDEBAR --- */
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
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #DC143C; /* Vermelho na página ativa */
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
# FIM DO CSS
# =============================================

if 'df_estoque' not in st.session_state or st.session_state.df_estoque is None:
    st.warning("⚠️ Dados não carregados. Verifique a página inicial (app).")
    st.stop()

# Recupera os dados
df_estoque = st.session_state.df_estoque
produtos_carne = df_estoque[df_estoque['tipo_produto'] == 'CARNE']
saude_estoque = calcular_saude_estoque(df_estoque)

st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📦 Gestão Inteligente de Estoque</div>', unsafe_allow_html=True)

st.markdown("### Principais Produtos em Estoque")
if not produtos_carne.empty:
    coluna_valor = 'valor_estoque' if 'valor_estoque' in produtos_carne.columns else 'estoque'
    top_produtos = produtos_carne.nlargest(10, coluna_valor)
    fig_produtos = px.bar(top_produtos, 
                            x='descricao', y=coluna_valor,
                            title='Principais Produtos em Estoque',
                            color=coluna_valor,
                            color_continuous_scale='reds')
    fig_produtos.update_layout(template='plotly_dark', xaxis_tickangle=45, showlegend=False)
    st.plotly_chart(fig_produtos, use_container_width=True) 
else:
    st.info("📊 Não há produtos de carne no estoque para análise detalhada.")

st.markdown("---")
st.subheader("📊 Saúde do Estoque")
col_met1, col_met2, col_met3, col_met4 = st.columns(4)
with col_met1:
    valor_str = f"R$ {saude_estoque['valor_total']:,.0f}" if saude_estoque['valor_total'] is not None else "N/D"
    st.metric("💰 Valor Total", valor_str)
with col_met2:
    st.metric("🥩 Itens de Carne", f"{saude_estoque['total_carnes']}")
with col_met3:
    devolvido_str = f"{saude_estoque['total_devolvido']:.0f}" if saude_estoque['total_devolvido'] is not None else "N/D"
    st.metric("🔄 Devoluções", devolvido_str)
with col_met4:
    negativos_str = f"{saude_estoque['produtos_negativos']}" if saude_estoque['produtos_negativos'] is not None else "N/D"
    st.metric("⚠️ Negativos", negativos_str)
st.markdown('</div>', unsafe_allow_html=True)

