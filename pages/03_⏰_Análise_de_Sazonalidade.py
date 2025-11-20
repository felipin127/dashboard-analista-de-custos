import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

try:
    from analysis import calcular_vendas_por_hora, calcular_vendas_por_dia_semana
except ImportError:
    st.error("Erro: Não foi possível encontrar ou ler o arquivo 'analysis.py'. Verifique se ele não tem erros de sintaxe.")
    st.stop()

# CONFIGURAÇÃO DE PÁGINA
st.set_page_config(
    page_title="Análise de Sazonalidade",
    page_icon="⏰",
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

# Recupera os dados originais
df_vendas_completo = st.session_state.df_vendas.copy()

# =============================================
# 📅 FILTROS NA BARRA LATERAL
# =============================================
with st.sidebar:
    st.header("Filtros de Tempo")
    st.info("Refine a análise para ver comportamentos em períodos específicos.")

    # 1. Limpeza de Dados (Correção do 'nan')
    df_vendas_completo['data'] = pd.to_datetime(df_vendas_completo['data'], errors='coerce')
    df_vendas_completo = df_vendas_completo.dropna(subset=['data'])

    if not df_vendas_completo.empty:
        min_date = df_vendas_completo['data'].min().date()
        max_date = df_vendas_completo['data'].max().date()
    else:
        min_date = date.today()
        max_date = date.today()

    data_selecionada = st.date_input(
        "📅 Intervalo de Datas:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filtro_sazonalidade_data"
    )


# --- LÓGICA DE FILTRAGEM ---
mask = pd.Series([True] * len(df_vendas_completo))

if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
    mask = mask & (df_vendas_completo['data'].dt.date >= data_selecionada[0]) & (df_vendas_completo['data'].dt.date <= data_selecionada[1])

df_vendas_filtrado = df_vendas_completo.loc[mask]


# =============================================
# CÁLCULOS E RENDERIZAÇÃO
# =============================================

st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⏰ Análise de Sazonalidade</div>', unsafe_allow_html=True)

if df_vendas_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

vendas_hora = calcular_vendas_por_hora(df_vendas_filtrado)
vendas_dia = calcular_vendas_por_dia_semana(df_vendas_filtrado)


# --- GRÁFICO 1: VENDAS POR HORA ---
st.markdown("### Vendas por Hora do Dia")

if not vendas_hora.empty:
    fig_hora = px.bar(vendas_hora, 
                      x='hora', 
                      y='valor',
                      labels={'hora': 'Hora do Dia', 'valor': 'Faturamento (R$)'},
                      color='valor',
                      color_continuous_scale='reds')
    
    fig_hora.update_layout(template='plotly_dark', xaxis={'type': 'category'})
    st.plotly_chart(fig_hora, use_container_width=True)
else:
    st.info("Sem dados de hora.")

st.markdown("---")

# --- GRÁFICO 2: VENDAS POR DIA DA SEMANA ---
st.markdown("### Vendas por Dia da Semana")

if not vendas_dia.empty:
    fig_dia = px.bar(vendas_dia, 
                     x='dia_pt', 
                     y='valor',
                     labels={'dia_pt': 'Dia da Semana', 'valor': 'Faturamento (R$)'},
                     color='valor',
                     color_continuous_scale='reds')
    
    fig_dia.update_layout(template='plotly_dark')
    st.plotly_chart(fig_dia, use_container_width=True)
else:
    st.info("Sem dados de dia.")


# --- INSIGHTS INTELIGENTES E PRESCRITIVOS ---
if not vendas_hora.empty and not vendas_dia.empty:
    # 1. Identifica os picos (Dados)
    melhor_hora_str = vendas_hora.loc[vendas_hora['valor'].idxmax(), 'hora']
    melhor_dia = vendas_dia.loc[vendas_dia['valor'].idxmax(), 'dia_pt']
    valor_dia_pico = vendas_dia['valor'].max()
    
    # 2. Lógica de Recomendação (Inteligência)
    
    # A) Lógica para HORA
    try:
        hora_int = int(melhor_hora_str)
    except:
        hora_int = 12 # Fallback

    if hora_int <= 10:
        analise_hora = "As vendas concentram-se no **início da manhã**."
        rec_hora = "💡 **Ação:** Garanta que a reposição de produtos frescos (padaria/açougue) seja feita na noite anterior ou de madrugada. Equipe de abertura deve estar completa."
    elif 11 <= hora_int <= 14:
        analise_hora = "O seu pico é no **horário de almoço**."
        rec_hora = "💡 **Ação:** Foco total em agilidade no atendimento. Evite trocas de turno ou reposições pesadas neste horário para não bloquear corredores."
    elif 17 <= hora_int <= 20:
        analise_hora = "O movimento explode no **final da tarde/noite**."
        rec_hora = "💡 **Ação:** Ideal para promoções de 'jantar' ou itens de conveniência rápida. Reforce os caixas para evitar filas na saída do trabalho."
    else:
        analise_hora = f"O horário de pico é às **{melhor_hora_str}h**."
        rec_hora = "💡 **Ação:** Monitore se este padrão se mantém e ajuste a escala de funcionários para este turno."

    # B) Lógica para DIA
    if melhor_dia in ['Sábado', 'Domingo']:
        analise_dia = "O **Fim de Semana** domina o seu faturamento."
        rec_dia = "💡 **Ação:** Excelente para 'Combos Família' ou ofertas de volume (ex: leve 3 pague 2) para churrasco e almoços de domingo."
    elif melhor_dia in ['Segunda', 'Terça', 'Quarta']:
        analise_dia = "Você tem força no **início/meio da semana**."
        rec_dia = "💡 **Ação:** Isso sugere um público que faz compras de abastecimento rotineiro. Mantenha o mix de produtos básicos sempre disponível."
    else:
        analise_dia = f"A **{melhor_dia}** é o seu dia mais forte."
        rec_dia = "💡 **Ação:** Concentre suas campanhas de marketing e ofertas relâmpago neste dia para maximizar o retorno."

    # Renderiza o HTML
    st.markdown(f"""
    <div class="info-box">
    <h3>🚀 Diagnóstico de Sazonalidade:</h3>
    <p>Com base nos dados do período selecionado, identificamos os seguintes padrões:</p>
    <ul>
        <li>
            <b>Horário ({melhor_hora_str}h):</b> {analise_hora}<br>
            {rec_hora}
        </li>
        <br>
        <li>
            <b>Dia ({melhor_dia}):</b> {analise_dia}<br>
            {rec_dia}
        </li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)