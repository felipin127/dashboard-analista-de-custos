import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from analysis import calcular_analise_retencao
except ImportError:
    st.error("Erro: Não foi possível encontrar ou ler o arquivo 'analysis.py'. Verifique se ele contém a função 'calcular_analise_retencao'.")
    st.stop()

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(
    page_title="Análise de Retenção",
    page_icon="🎯",
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

if 'df_vendas' not in st.session_state or st.session_state.df_vendas is None:
    st.warning("⚠️ Dados não carregados. Verifique a página inicial (app).")
    st.stop()

# Dados Completos
df_vendas_completo = st.session_state.df_vendas.copy()


# =============================================
# 📅 FILTRO NA BARRA LATERAL (SIDEBAR)
# =============================================
with st.sidebar:
    st.header("Filtros")
    st.write("Período de aquisição:")
    
    # Garante formato de data
    df_vendas_completo['data'] = pd.to_datetime(df_vendas_completo['data'])
    
    if not df_vendas_completo.empty:
        min_date = df_vendas_completo['data'].min().date()
        max_date = df_vendas_completo['data'].max().date()
    else:
        from datetime import date
        min_date = date.today()
        max_date = date.today()

    data_selecionada = st.date_input(
        "Selecione o intervalo:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filtro_retencao_sidebar"
    )
    
    st.info("Analise a retenção dos clientes que compraram neste período.")

# --- APLICAÇÃO DO FILTRO ---
df_vendas_filtrado = df_vendas_completo
if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
    inicio, fim = data_selecionada
    mask = (df_vendas_completo['data'].dt.date >= inicio) & (df_vendas_completo['data'].dt.date <= fim)
    df_vendas_filtrado = df_vendas_completo.loc[mask]


# =============================================
# CÁLCULOS COM DADOS FILTRADOS
# =============================================

if df_vendas_filtrado.empty:
    st.info("📊 Nenhum dado encontrado para o período selecionado.")
else:
    # Calcula tudo com base no filtro
    retencao_pivot_final, kpi_novos, kpi_retidos, media_retencao_df = calcular_analise_retencao(df_vendas_filtrado)

    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎯 Análise de Retenção de Clientes</div>', unsafe_allow_html=True)

    # --- KPIs ---
    st.markdown("### Aquisição vs. Retenção (No Período)")
    st.markdown("Clientes ativos no período filtrado: quantos são novos e quantos são recorrentes.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Aquisição (Clientes Novos)", f"{kpi_novos} Clientes")
    with col2:
        st.metric("Retenção (Clientes Recorrentes)", f"{kpi_retidos} Clientes")

    st.markdown("---")

    # --- GRÁFICO DE ÁREA ---
    st.markdown("### Retenção Média ao Longo do Tempo")
    st.markdown("Comportamento médio de retorno dos clientes neste período.")

    if not media_retencao_df.empty:
        fig_media = px.area(media_retencao_df, 
                            x='Meses Desde a Primeira Compra', 
                            y='Taxa Média de Retenção',
                            markers=True,
                            title='Curva de Retenção Média',
                            labels={'Taxa Média de Retenção': 'Taxa Média de Retenção (%)'})
        
        fig_media.update_layout(
            template='plotly_dark',
            yaxis_tickformat='.0%'
        )
        st.plotly_chart(fig_media, use_container_width=True)
    else:
        st.info("📊 Não há dados suficientes para calcular a curva de retenção média neste período.")

    st.markdown(f"""
    <div class="info-box">
    <h4>💡 Insight de Crescimento:</h4>
    <p>No período selecionado, você adquiriu <b>{kpi_novos} clientes novos</b> e manteve <b>{kpi_retidos} clientes existentes</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)