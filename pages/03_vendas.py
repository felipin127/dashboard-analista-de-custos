import streamlit as st
import pandas as pd
import plotly.express as px

try:
    # Importa as NOVAS funções de análise
    from analysis import calcular_vendas_por_hora, calcular_vendas_por_dia_semana
except ImportError:
    st.error("Erro: Não foi possível encontrar ou ler o arquivo 'analysis.py'. Verifique se ele foi atualizado com as novas funções de sazonalidade.")
    st.stop()

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(
    page_title="Análise de Sazonalidade",
    page_icon="⏰", # Ícone atualizado
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

# Validação: Checa se os dados (carregados pelo app.py) existem
if 'df_vendas' not in st.session_state or st.session_state.df_vendas is None:
    st.warning("⚠️ Dados não carregados. Verifique a página inicial (app).")
    st.stop()

# Recupera os dados
df_vendas = st.session_state.df_vendas
vendas_hora = calcular_vendas_por_hora(df_vendas)
vendas_dia = calcular_vendas_por_dia_semana(df_vendas)

# Renderização da página
st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⏰ Análise de Sazonalidade (Horários e Dias)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Gráfico 1: Vendas por Hora
with col1:
    fig_hora = px.bar(vendas_hora, x='hora', y='valor', 
                      title='Faturamento por Hora do Dia',
                      labels={'hora': 'Hora do Dia (0-23)', 'valor': 'Valor Total (R$)'},
                      color='valor',
                      color_continuous_scale='reds')
    fig_hora.update_layout(template='plotly_dark')
    st.plotly_chart(fig_hora, use_container_width=True)

# Gráfico 2: Vendas por Dia da Semana
with col2:
    fig_dia = px.line(vendas_dia, x='dia_pt', y='valor', 
                      title='Faturamento por Dia da Semana',
                      labels={'dia_pt': 'Dia da Semana', 'valor': 'Valor Total (R$)'},
                      markers=True)
    # Deixa a linha vermelha para combinar com o tema
    fig_dia.update_traces(line_color='#DC143C', line_width=3)
    fig_dia.update_layout(template='plotly_dark')
    st.plotly_chart(fig_dia, use_container_width=True)

# Insights
st.markdown("---")
hora_pico = vendas_hora.loc[vendas_hora['valor'].idxmax()]
dia_pico = vendas_dia.loc[vendas_dia['valor'].idxmax()]

st.markdown(f"""
<div class="info-box">
<h4>🎯 Insights de Sazonalidade:</h4>
<ul>
<li><b>Dia de Pico:</b> {dia_pico['dia_pt']} (Faturamento: R$ {dia_pico['valor']:,.2f})</li>
<li><b>Horário de Pico:</b> {int(hora_pico['hora'])}h (Faturamento: R$ {hora_pico['valor']:,.2f})</li>
<li><b>Recomendação:</b> Reforçar a equipe e o estoque para os horários e dias de maior movimento.</li>
</ul>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

