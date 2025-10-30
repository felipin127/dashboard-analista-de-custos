
import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from analysis import calcular_preferencias_pagamento
except ImportError:
    st.error("Erro: Não foi possível encontrar ou ler o arquivo 'analysis.py'. Verifique se ele não tem erros de sintaxe.")
    st.stop()

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(
    page_title="Formas de Pagamento",
    page_icon="💳",
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
    /* Estilos da Sidebar (copiados) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A202C 0%, #0E1117 100%);
        border-right: 2px solid #DC143C;
    }
    [data-testid="stSidebarUserContent"] h1 {
        color: #FFD700; text-align: center; font-size: 1.8rem;
    }
    [data-testid="stSidebarNav"] a {
        color: #FAFAFA; padding: 10px 15px; border-radius: 8px; margin-bottom: 5px;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    [data-testid="stSidebarNav"] a:hover {
        background-color: rgba(255, 255, 255, 0.1); color: #FFD700;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #DC143C; color: #FFFFFF; font-weight: bold;
    }
    [data-testid="stNotification"][data-st-notification-type="success"] {
        background-color: #1a422a; color: #b3ffb3; border-radius: 10px;
        border: 1px solid #00C851; font-weight: bold; text-align: center;
    }
    [data-testid="stNotification"][data-st-notification-type="error"] {
        background-color: #4d1c1c; color: #ffb3b3; border-radius: 10px;
        border: 1px solid #DC143C; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
# =============================================
# FIM DO CSS
# =============================================

if 'df_vendas' not in st.session_state or st.session_state.df_vendas is None:
    st.warning("⚠️ Dados não carregados. Verifique a página inicial (app).")
    st.stop()

# Recupera os dados
df_vendas = st.session_state.df_vendas
pagamento_stats = calcular_preferencias_pagamento(df_vendas)

# =============================================
# ANÁLISE DE PREFERÊNCIAS DO CLIENTE (RENDERIZAÇÃO)
# =============================================

st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💳 Análise por Forma de Pagamento</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig_pizza = px.pie(pagamento_stats.reset_index(), 
                        values='Receita Total', names='pagamento',
                        title='Distribuição por Forma de Pagamento',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Reds)
    fig_pizza.update_layout(template='plotly_dark')
    st.plotly_chart(fig_pizza, use_container_width=True)

with col2:
    fig_ticket = px.bar(pagamento_stats.reset_index(), 
                        x='pagamento', y='Ticket Médio',
                        title='Ticket Médio por Forma de Pagamento',
                        color='Ticket Médio',
                        color_continuous_scale='reds')
    fig_ticket.update_layout(template='plotly_dark', showlegend=False)
    st.plotly_chart(fig_ticket, use_container_width=True)

# Insights
st.markdown("---")
forma_mais_popular = pagamento_stats['Total Vendas'].idxmax()
forma_maior_ticket = pagamento_stats['Ticket Médio'].idxmax()

st.markdown(f"""
<div class="info-box">
<h4>🎯 Insights de Pagamento:</h4>
<ul>
<li><b>Forma Mais Popular:</b> {forma_mais_popular} (Mais utilizada pelos clientes)</li>
<li><b>Maior Ticket Médio:</b> {forma_maior_ticket} (Clientes gastam mais quando usam)</li>
<li><b>Oportunidade:</b> Incentivar formas de pagamento com maior ticket médio.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
