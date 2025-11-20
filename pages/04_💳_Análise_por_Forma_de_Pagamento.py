import streamlit as st
import pandas as pd
import plotly.express as px

try:
    # A função agora retorna os nomes renomeados (ex: 'dinheiro', 'pix', etc.)
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
        margin-bottom: 10px;
        font-size: 1.05rem;
    }
    .info-box b {
        color: #FFFFFF;
        font-weight: 700;
    }
    .metric-highlight {
        color: #4FD1C5;
        font-weight: bold;
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
    .stDateInput > div {
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

if 'df_vendas' not in st.session_state or st.session_state.df_vendas is None:
    st.warning("⚠️ Dados não carregados. Verifique a página inicial (app).")
    st.stop()

# Dados completos
df_vendas_total = st.session_state.df_vendas.copy()

# =============================================
# 📅 FILTRO NA BARRA LATERAL (SIDEBAR)
# =============================================
with st.sidebar:
    st.header("Filtros")
    st.info("O filtro de data abaixo aplica-se **somente** ao gráfico de Ticket Médio (Esquerda).")
    
    # Garante formato de data
    df_vendas_total['data'] = pd.to_datetime(df_vendas_total['data'])
    
    if not df_vendas_total.empty:
        min_date = df_vendas_total['data'].min().date()
        max_date = df_vendas_total['data'].max().date()
    else:
        from datetime import date
        min_date = date.today()
        max_date = date.today()

    data_selecionada = st.date_input(
        "Período de Análise:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filtro_pagamento_sidebar"
    )

# Cria o dataframe filtrado (para o gráfico de Ticket Médio)
df_vendas_filtrado = df_vendas_total
if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
    inicio, fim = data_selecionada
    mask = (df_vendas_total['data'].dt.date >= inicio) & (df_vendas_total['data'].dt.date <= fim)
    df_vendas_filtrado = df_vendas_total.loc[mask]


# =============================================
# CÁLCULOS
# =============================================

# 1. Dados GERAIS (Para o gráfico de Popularidade)
if not df_vendas_total.empty:
    pagamento_stats_total = calcular_preferencias_pagamento(df_vendas_total)
else:
    pagamento_stats_total = pd.DataFrame()

# 2. Dados FILTRADOS (Para o gráfico de Ticket Médio)
if not df_vendas_filtrado.empty:
    pagamento_stats_filtrado = calcular_preferencias_pagamento(df_vendas_filtrado)
else:
    pagamento_stats_filtrado = pd.DataFrame()


# =============================================
# RENDERIZAÇÃO
# =============================================

st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💳 Performance de Pagamentos</div>', unsafe_allow_html=True)

# Verifica se há dados para exibir
if pagamento_stats_total.empty and pagamento_stats_filtrado.empty:
    st.warning("Sem dados disponíveis para visualização.")
else:
    # Criar duas colunas com espaçamento (GAP)
    col1, col2 = st.columns(2, gap="large")
    
    # --- GRÁFICO 1: TICKET MÉDIO (BARRAS VERTICAIS - FILTRADO) ---
    with col1:
        st.subheader("📅 Ticket Médio (Filtro de Data)")
        st.caption("Qual o valor médio por venda neste período?")
        
        if not pagamento_stats_filtrado.empty:
            # Ordenar do MAIOR para o MENOR valor
            pagamento_stats_ticket_sorted = pagamento_stats_filtrado.sort_values('Ticket Médio', ascending=False)
            
            fig_ticket = px.bar(pagamento_stats_ticket_sorted.reset_index(), 
                                    x='pagamento', 
                                    y='Ticket Médio',
                                    color='Ticket Médio',
                                    color_continuous_scale='reds',
                                    text='Ticket Médio',
                                    labels={'pagamento': 'Forma', 'Ticket Médio': 'Valor (R$)'}
                                    )
            # Formatação de dinheiro e layout limpo
            fig_ticket.update_traces(texttemplate='R$ %{y:.2f}', textposition='outside')
            fig_ticket.update_layout(template='plotly_dark', showlegend=False, margin=dict(t=30, b=30))
            st.plotly_chart(fig_ticket, use_container_width=True)
        else:
            st.info("Sem vendas no período selecionado.")


    # --- GRÁFICO 2: POPULARIDADE (BARRAS HORIZONTAIS - GLOBAL) ---
    with col2:
        st.subheader("🌐 Popularidade (Histórico Geral)")
        st.caption("Ranking das formas de pagamento mais utilizadas.")

        if not pagamento_stats_total.empty:
            # Ordenar do MAIOR para o MENOR (para barras horizontais, a ordem é invertida no código para aparecer certo na tela)
            pagamento_stats_popular_sorted = pagamento_stats_total.sort_values('Total Vendas', ascending=True)

            fig_popular = px.bar(pagamento_stats_popular_sorted.reset_index(), 
                                    x='Total Vendas', 
                                    y='pagamento', 
                                    orientation='h', # Barras Horizontais
                                    color='Total Vendas',
                                    color_continuous_scale='Blues', # Cor diferente para contrastar
                                    text='Total Vendas',
                                    labels={'pagamento': 'Forma', 'Total Vendas': 'Transações'}
                                   )
            
            fig_popular.update_traces(textposition='outside')
            fig_popular.update_layout(template='plotly_dark', showlegend=False, margin=dict(t=30, b=30))
            st.plotly_chart(fig_popular, use_container_width=True)
        else:
            st.warning("Sem dados históricos.")

    st.markdown("---")

    # --- INSIGHTS INTELIGENTES E ESTRATÉGICOS ---
    try:
        # Preparação dos dados
        if not pagamento_stats_total.empty:
            forma_mais_popular = pagamento_stats_total['Total Vendas'].idxmax()
        else:
            forma_mais_popular = "N/A"

        if not pagamento_stats_filtrado.empty:
            forma_maior_ticket = pagamento_stats_filtrado['Ticket Médio'].idxmax()
            val_ticket = pagamento_stats_filtrado['Ticket Médio'].max()
            texto_ticket = f"{forma_maior_ticket} (R$ {val_ticket:.2f})"
        else:
            texto_ticket = "N/A"
            forma_maior_ticket = "N/A"

        # GERAÇÃO DE RECOMENDAÇÃO AUTOMÁTICA
        recomendacao_estrategica = ""
        if forma_mais_popular == forma_maior_ticket:
            recomendacao_estrategica = f"🏆 <b>Cenário Ideal:</b> O método <b>{forma_mais_popular}</b> é o campeão tanto em volume quanto em valor. Mantenha o foco na qualidade do atendimento neste canal."
        elif 'credito' in forma_maior_ticket.lower():
            recomendacao_estrategica = f"🚀 <b>Estratégia:</b> O <b>Crédito</b> traz clientes que gastam mais. Tente converter o fluxo do <b>{forma_mais_popular}</b> oferecendo parcelamento facilitado no cartão."
        elif 'pix' in forma_maior_ticket.lower():
            recomendacao_estrategica = f"💡 <b>Oportunidade:</b> O <b>Pix</b> tem um ticket alto e custo menor. Crie uma campanha '5% OFF no Pix' para migrar clientes do <b>{forma_mais_popular}</b>."
        else:
            recomendacao_estrategica = f"📊 <b>Ação:</b> Use o alto volume do <b>{forma_mais_popular}</b> para fazer 'upsell' (oferecer produtos adicionais no caixa) e tentar aproximar o ticket médio do nível do <b>{forma_maior_ticket}</b>."

        st.markdown(f"""
        <div class="info-box">
            <h3>🎯 Diagnóstico e Estratégia:</h3>
            <ul>
                <li><b>Líder de Volume (Frequência):</b> <span class="metric-highlight">{forma_mais_popular}</span> - Traz movimento à loja.</li>
                <li><b>Líder de Valor (Ticket Médio):</b> <span class="metric-highlight">{texto_ticket}</span> - Traz rentabilidade.</li>
            </ul>
            <br>
            <p>{recomendacao_estrategica}</p>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        pass

st.markdown('</div>', unsafe_allow_html=True)