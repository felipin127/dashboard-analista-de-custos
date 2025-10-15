import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# =============================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(
    page_title="Martins Analytics | Análise de Carnes",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# CSS PERSONALIZADO
# =============================================
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
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
    .upload-section {
        background: #1A202C;
        padding: 3rem;
        border-radius: 15px;
        border: 3px dashed #4A5568;
        margin-bottom: 2rem;
        text-align: center;
    }
    .info-box {
        background: #2D3748;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4299E1;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# FUNÇÕES DE PROCESSAMENTO
# =============================================

def processar_dados_vendas(df_vendas):
    """Processa a base de vendas"""
    try:
        # Renomear colunas para padrão
        df_vendas_clean = df_vendas.copy()
        df_vendas_clean.columns = ['venda', 'cliente', 'vendedor', 'data', 'pagamento', 'valor']
        
        # Converter tipos
        df_vendas_clean['data'] = pd.to_datetime(df_vendas_clean['data'], format='%d/%m/%Y %H:%M', errors='coerce')
        df_vendas_clean['valor'] = df_vendas_clean['valor'].astype(str).str.replace(',', '.').astype(float)
        df_vendas_clean['venda'] = pd.to_numeric(df_vendas_clean['venda'], errors='coerce')
        
        # Extrair informações de tempo
        df_vendas_clean['hora'] = df_vendas_clean['data'].dt.hour
        df_vendas_clean['dia_semana'] = df_vendas_clean['data'].dt.day_name()
        df_vendas_clean['mes'] = df_vendas_clean['data'].dt.month_name()
        
        return df_vendas_clean
        
    except Exception as e:
        st.error(f"❌ Erro ao processar vendas: {str(e)}")
        return None

def processar_dados_estoque(df_estoque):
    """Processa a base de estoque/custos"""
    try:
        df_estoque_clean = df_estoque.copy()
        df_estoque_clean.columns = ['codigo', 'descricao', 'unidade', 'estoque', 'valor_estoque', 
                                  'qtd_devolvida', 'valor_devolvida', 'qtd', 'saldo']
        
        # Converter valores numéricos
        for col in ['estoque', 'valor_estoque', 'qtd_devolvida', 'valor_devolvida', 'qtd', 'saldo']:
            if col in df_estoque_clean.columns:
                df_estoque_clean[col] = df_estoque_clean[col].astype(str).str.replace(',', '.').astype(float)
        
        # Identificar produtos de carne
        df_estoque_clean['tipo_produto'] = df_estoque_clean['descricao'].apply(
            lambda x: 'CARNE' if 'CARNE' in str(x).upper() or 'AGEM' in str(x).upper() else 'OUTROS'
        )
        
        return df_estoque_clean
        
    except Exception as e:
        st.error(f"❌ Erro ao processar estoque: {str(e)}")
        return None

# =============================================
# FUNÇÕES DE VISUALIZAÇÃO
# =============================================

def criar_metricas_principais(df_vendas, df_estoque):
    """Cria os cards com as métricas principais"""
    st.markdown('## 📊 Visão Geral do Negócio')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        receita_total = df_vendas['valor'].sum()
        st.metric("💰 Receita Total", f"R$ {receita_total:,.0f}")
    
    with col2:
        ticket_medio = df_vendas['valor'].mean()
        st.metric("🎫 Ticket Médio", f"R$ {ticket_medio:.2f}")
    
    with col3:
        total_vendas = len(df_vendas)
        st.metric("📈 Total de Vendas", f"{total_vendas}")
    
    with col4:
        if 'valor_estoque' in df_estoque.columns:
            valor_estoque_total = df_estoque['valor_estoque'].sum()
            st.metric("📦 Valor em Estoque", f"R$ {valor_estoque_total:,.0f}")
        else:
            st.metric("📦 Itens no Estoque", f"{len(df_estoque)}")
    
    with col5:
        produtos_carne = len(df_estoque[df_estoque['tipo_produto'] == 'CARNE'])
        st.metric("🥩 Produtos de Carne", f"{produtos_carne}")

# =============================================
# ANÁLISES PRINCIPAIS
# =============================================

def analise_horarios_pico(df_vendas):
    """Análise de Melhores Horários de Venda"""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⏰ Melhores Horários de Venda</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Vendas por hora do dia
        vendas_hora = df_vendas.groupby('hora')['valor'].sum().reset_index()
        
        fig_hora = px.bar(vendas_hora, x='hora', y='valor', 
                         title='Faturamento por Hora do Dia',
                         labels={'hora': 'Hora do Dia', 'valor': 'Valor Total (R$)'},
                         color='valor',
                         color_continuous_scale='reds')
        
        fig_hora.update_layout(template='plotly_dark', showlegend=False)
        st.plotly_chart(fig_hora, use_container_width=True)
    
    with col2:
        # Vendas por dia da semana
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_portugues = {'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 
                         'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        
        vendas_dia = df_vendas.groupby('dia_semana')['valor'].sum().reset_index()
        vendas_dia['dia_pt'] = vendas_dia['dia_semana'].map(dias_portugues)
        vendas_dia['dia_ordem'] = vendas_dia['dia_semana'].map({dia: i for i, dia in enumerate(dias_ordem)})
        vendas_dia = vendas_dia.sort_values('dia_ordem')
        
        fig_dia = px.line(vendas_dia, x='dia_pt', y='valor', 
                         title='Faturamento por Dia da Semana',
                         markers=True, line_shape='spline')
        fig_dia.update_layout(template='plotly_dark', showlegend=False)
        st.plotly_chart(fig_dia, use_container_width=True)
    
    # Insights
    hora_pico = vendas_hora.loc[vendas_hora['valor'].idxmax(), 'hora']
    dia_pico = vendas_dia.loc[vendas_dia['valor'].idxmax(), 'dia_pt']
    
    st.markdown(f"""
    <div class="info-box">
    <h4>💡 Insights Descobertos:</h4>
    <ul>
    <li><b>Horário de Pico:</b> {hora_pico}h - Maior movimento de vendas</li>
    <li><b>Dia Mais Rentável:</b> {dia_pico} - Melhor desempenho semanal</li>
    <li><b>Recomendação:</b> Reforçar equipe nesses períodos para melhor atendimento</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def analise_desempenho_vendedores(df_vendas):
    """Análise de Desempenho da Equipe"""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👥 Desempenho da Equipe de Vendas</div>', unsafe_allow_html=True)
    
    # Métricas por vendedor
    perf_vendedores = df_vendas.groupby('vendedor').agg({
        'valor': ['sum', 'mean', 'count']
    }).round(2)
    
    perf_vendedores.columns = ['Receita Total', 'Ticket Médio', 'Total Vendas']
    perf_vendedores = perf_vendedores.sort_values('Receita Total', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras - Receita por vendedor
        fig_vendedores = px.bar(perf_vendedores.reset_index(), 
                               x='vendedor', y='Receita Total',
                               title='Performance - Receita por Vendedor',
                               color='Receita Total',
                               color_continuous_scale='reds')
        
        fig_vendedores.update_layout(template='plotly_dark', showlegend=False)
        st.plotly_chart(fig_vendedores, use_container_width=True)
    
    with col2:
        # Gráfico de pizza - Distribuição de vendas
        fig_distribuicao = px.pie(perf_vendedores.reset_index(), 
                                 values='Receita Total', names='vendedor',
                                 title='Distribuição de Receita entre Vendedores',
                                 hole=0.4)
        
        fig_distribuicao.update_layout(template='plotly_dark')
        st.plotly_chart(fig_distribuicao, use_container_width=True)
    
    # Tabela de performance SIMPLIFICADA
    st.subheader("📋 Ranking de Desempenho")
    
    # Criar tabela simples sem formatação complexa
    tabela_simples = perf_vendedores.reset_index()
    tabela_simples['Posição'] = range(1, len(tabela_simples) + 1)
    tabela_simples = tabela_simples[['Posição', 'vendedor', 'Receita Total', 'Ticket Médio', 'Total Vendas']]
    
    # Formatar valores
    tabela_simples['Receita Total'] = tabela_simples['Receita Total'].apply(lambda x: f'R$ {x:,.2f}')
    tabela_simples['Ticket Médio'] = tabela_simples['Ticket Médio'].apply(lambda x: f'R$ {x:,.2f}')
    
    st.dataframe(tabela_simples, use_container_width=True)
    
    # Melhor vendedor
    melhor_vendedor = perf_vendedores.index[0]
    receita_melhor = perf_vendedores.iloc[0]['Receita Total']
    
    st.markdown(f"""
    <div class="info-box">
    <h4>🏆 Destaque da Equipe:</h4>
    <p><b>{melhor_vendedor}</b> lidera com R$ {receita_melhor:,.2f} em vendas</p>
    <p><b>Sugestão:</b> Estude as estratégias do vendedor top para replicar na equipe</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def analise_preferencias_clientes(df_vendas):
    """Análise de Comportamento do Cliente"""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💳 Como Seus Clientes Preferem Pagar</div>', unsafe_allow_html=True)
    
    # Análise por forma de pagamento
    pagamento_stats = df_vendas.groupby('pagamento').agg({
        'valor': ['sum', 'mean', 'count']
    }).round(2)
    
    pagamento_stats.columns = ['Receita Total', 'Ticket Médio', 'Total Vendas']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pizza - Distribuição de receita
        fig_pizza = px.pie(pagamento_stats.reset_index(), 
                          values='Receita Total', names='pagamento',
                          title='Distribuição por Forma de Pagamento',
                          hole=0.4,
                          color_discrete_sequence=px.colors.sequential.Reds)
        
        fig_pizza.update_layout(template='plotly_dark')
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col2:
        # Barras - Ticket médio
        fig_ticket = px.bar(pagamento_stats.reset_index(), 
                           x='pagamento', y='Ticket Médio',
                           title='Ticket Médio por Forma de Pagamento',
                           color='Ticket Médio',
                           color_continuous_scale='reds')
        
        fig_ticket.update_layout(template='plotly_dark', showlegend=False)
        st.plotly_chart(fig_ticket, use_container_width=True)
    
    forma_mais_popular = pagamento_stats['Total Vendas'].idxmax()
    forma_maior_ticket = pagamento_stats['Ticket Médio'].idxmax()
    
    st.markdown(f"""
    <div class="info-box">
    <h4>🎯 Comportamento do Cliente:</h4>
    <ul>
    <li><b>Forma Mais Popular:</b> {forma_mais_popular} - Mais utilizada pelos clientes</li>
    <li><b>Maior Ticket Médio:</b> {forma_maior_ticket} - Clientes gastam mais</li>
    <li><b>Oportunidade:</b> Incentivar formas de pagamento com maior ticket médio</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def analise_gestao_estoque(df_estoque):
    """Análise Inteligente de Estoque"""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📦 Gestão Inteligente de Estoque</div>', unsafe_allow_html=True)
    
    # Filtrar apenas produtos de carne para análise focada
    produtos_carne = df_estoque[df_estoque['tipo_produto'] == 'CARNE']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top produtos (usando as colunas disponíveis)
        if not produtos_carne.empty:
            # Usar a primeira coluna numérica disponível para o gráfico
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
            st.info("📊 Não há produtos de carne no estoque")
    
    with col2:
        # Distribuição por tipo de produto
        dist_tipo = df_estoque['tipo_produto'].value_counts()
        fig_dist = px.pie(values=dist_tipo.values, names=dist_tipo.index,
                         title='Distribuição de Produtos por Tipo')
        fig_dist.update_layout(template='plotly_dark')
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Métricas de estoque
    st.subheader("📊 Saúde do Estoque")
    
    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
    
    with col_met1:
        if 'valor_estoque' in df_estoque.columns:
            total_estoque = df_estoque['valor_estoque'].sum()
            st.metric("💰 Valor Total", f"R$ {total_estoque:,.0f}")
        else:
            st.metric("📊 Total Itens", f"{len(df_estoque)}")
    
    with col_met2:
        total_carnes = len(produtos_carne)
        st.metric("🥩 Itens de Carne", f"{total_carnes}")
    
    with col_met3:
        if 'qtd_devolvida' in df_estoque.columns:
            total_devolvido = df_estoque['qtd_devolvida'].sum()
            st.metric("🔄 Devoluções", f"{total_devolvido:.0f}")
        else:
            st.metric("📈 Tipos", f"{len(df_estoque['tipo_produto'].unique())}")
    
    with col_met4:
        if 'estoque' in df_estoque.columns:
            produtos_negativos = len(df_estoque[df_estoque['estoque'] < 0])
            st.metric("⚠️ Negativos", f"{produtos_negativos}")
        else:
            st.metric("📋 Categorias", f"{len(df_estoque)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# LAYOUT PRINCIPAL
# =============================================

def main():
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1 class='header-title'>MARTINS ANALYTICS</h1>
        <p class='header-subtitle'>Análise Inteligente do Setor de Carnes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://i.imgur.com/rLgn6yr.png", width=100)
        st.title("🥩 Martins Carnes")
        st.markdown("---")
        
        st.header("📁 Upload de Arquivos")
        
        st.subheader("🗃️ Base de Vendas")
        arquivo_vendas = st.file_uploader("Selecione...", type=['xlsx', 'xls'], key='vendas')
        
        st.subheader("📦 Base de Estoque")
        arquivo_estoque = st.file_uploader("Selecione...", type=['xlsx', 'xls'], key='estoque')
        
        st.markdown("---")
        
        if st.button("🔄 Recarregar Análise", use_container_width=True):
            st.rerun()
    
    # Processamento dos dados
    if arquivo_vendas is not None and arquivo_estoque is not None:
        try:
            with st.spinner('🔍 Analisando seus dados...'):
                # Carregar dados
                df_vendas_raw = pd.read_excel(arquivo_vendas)
                df_estoque_raw = pd.read_excel(arquivo_estoque)
                
                # Processar dados
                df_vendas = processar_dados_vendas(df_vendas_raw)
                df_estoque = processar_dados_estoque(df_estoque_raw)
            
            if df_vendas is not None and df_estoque is not None:
                st.success("✅ Dados carregados com sucesso!")
                
                # Métricas principais
                criar_metricas_principais(df_vendas, df_estoque)
                
                st.markdown("---")
                st.markdown('## 🎯 Análises Inteligentes')
                
                # Executar todas as análises
                analise_horarios_pico(df_vendas)
                analise_desempenho_vendedores(df_vendas)
                analise_preferencias_clientes(df_vendas)
                analise_gestao_estoque(df_estoque)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar os arquivos: {str(e)}")
    
    else:
        # Tela inicial
        st.markdown("""
        <div class='upload-section'>
            <h2 style='color: #FFD700; margin-bottom: 1rem;'>📊 Bem-vindo ao Martins Analytics</h2>
            <p style='font-size: 1.2rem; margin-bottom: 2rem;'>
            Faça o upload das planilhas para descobrir insights valiosos sobre seu negócio.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #A0A0A0;'>
        🥩 <b>Martins Analytics</b> • Análise Especializada • © 2024
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()