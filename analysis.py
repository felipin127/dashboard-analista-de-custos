import pandas as pd
from typing import Union
import numpy as np

# =============================================
# ANÁLISE GERAL (Para a página Visão Geral)
# =============================================
def calcular_metricas_gerais(df_vendas: pd.DataFrame, df_estoque: pd.DataFrame) -> dict:
    """Calcula as principais métricas do negócio."""
    
    receita_total = df_vendas['valor'].sum()
    ticket_medio = df_vendas['valor'].mean()
    total_vendas = len(df_vendas)
    
    # Métricas de estoque
    valor_estoque_total = df_estoque['valor_estoque'].sum() if 'valor_estoque' in df_estoque.columns else None
    produtos_carne = len(df_estoque[df_estoque['tipo_produto'] == 'CARNE'])

    return {
        'receita_total': receita_total,
        'ticket_medio': ticket_medio,
        'total_vendas': total_vendas,
        'valor_estoque_total': valor_estoque_total,
        'produtos_carne': produtos_carne
    }


# =============================================
# ANÁLISE DE SAZONALIDADE (Para a página Sazonalidade)
# =============================================
def calcular_vendas_por_hora(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Calcula o faturamento agregado por hora do dia."""
    
    vendas_hora = df_vendas.dropna(subset=['hora']).copy()
    
    vendas_hora = vendas_hora.groupby('hora')['valor'].sum().reset_index()
    
    vendas_hora['hora'] = vendas_hora['hora'].astype(int) 
    vendas_hora['hora'] = vendas_hora['hora'].astype(str) # Tratar hora como categoria
    
    return vendas_hora

def calcular_vendas_por_dia_semana(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Calcula o faturamento agregado por dia da semana."""
    dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_portugues = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    
    vendas_dia = df_vendas.groupby('dia_semana')['valor'].sum().reset_index()
    vendas_dia['dia_pt'] = vendas_dia['dia_semana'].map(dias_portugues)
    vendas_dia['dia_ordem'] = pd.Categorical(vendas_dia['dia_semana'], categories=dias_ordem, ordered=True)
    vendas_dia = vendas_dia.sort_values('dia_ordem')
    
    return vendas_dia


# =============================================
# ANÁLISE DE PAGAMENTO (Para a página Pagamentos)
# =============================================

def calcular_preferencias_pagamento(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Calcula a receita, ticket médio e total de vendas por forma de pagamento."""
    
    df_pag = df_vendas.copy()
    
    # --- CORREÇÃO (V11) ---
    # 1. Remove linhas onde o pagamento é nulo ANTES de agrupar
    df_pag = df_pag.dropna(subset=['pagamento'])
    
    # 2. Cria uma coluna limpa (sem espaços) para agrupar
    df_pag['pagamento_limpo'] = df_pag['pagamento'].astype(str).str.strip()
    
    # 3. Agrupa pela coluna limpa
    pagamento_stats = df_pag.groupby('pagamento_limpo').agg({
        'valor': ['sum', 'mean', 'count']
    }).round(2)
    # --- FIM DA CORREÇÃO (V11) ---
    
    pagamento_stats.columns = ['Receita Total', 'Ticket Médio', 'Total Vendas']
    pagamento_stats = pagamento_stats.sort_values('Receita Total', ascending=False)
    
    # 4. Define o mapa de nomes que você pediu
    mapa_nomes = {
        'A VISTA': 'dinheiro',
        '1x': 'debito',
        'ENT. + 1x': 'pix', # <-- ALTERAÇÃO FEITA AQUI (V13)
        '2x': 'credito',
        'ENT. + 2x': 'credito parcelado'
    }
    
    # 5. Renomeia o índice
    # .fillna() causava TypeError, .combine_first() é mais robusto
    original_series = pagamento_stats.index.to_series()
    mapped_series = original_series.map(mapa_nomes)
    # Combina os nomes mapeados (ex: 'dinheiro') com os originais que não foram mapeados
    novos_nomes = mapped_series.combine_first(original_series)
    pagamento_stats.index = novos_nomes
    
    # --- CORREÇÃO (V12) - Corrige o 'ValueError' ---
    # Renomeia o índice de 'pagamento_limpo' de volta para 'pagamento'
    # para que a página (que busca x='pagamento') funcione
    pagamento_stats.index.name = 'pagamento'
    # --- FIM DA CORREÇÃO (V12) ---
    
    return pagamento_stats

# =============================================
# ANÁLISE DE ESTOQUE (Para a página Estoque)
# =============================================
def calcular_saude_estoque(df_estoque: pd.DataFrame) -> dict:
    """Calcula as métricas de saúde e devolução do estoque."""
    
    metricas = {}
    
    metricas['valor_total'] = df_estoque['valor_estoque'].sum() if 'valor_estoque' in df_estoque.columns else None
    metricas['total_carnes'] = len(df_estoque[df_estoque['tipo_produto'] == 'CARNE'])
    metricas['total_devolvido'] = df_estoque['qtd_devolvida'].sum() if 'qtd_devolvida' in df_estoque.columns else None
    metricas['produtos_negativos'] = len(df_estoque[df_estoque['estoque'] < 0]) if 'estoque' in df_estoque.columns else None
        
    return metricas

# =============================================
# HIPÓTESE 2: ANÁLISE DE CAPITAL (NOVA FUNÇÃO)
# =============================================
def calcular_analise_capital(df_estoque: pd.DataFrame):
    """Calcula o capital alocado e devoluções por tipo de produto."""
    
    colunas_capital = ['tipo_produto', 'descricao', 'valor_estoque', 'percentual_total']
    
    # --- CORREÇÃO (V14) ---
    # Corrigindo o erro de digitação ('colunas_devolucao' e não 'colunas_devoluvao')
    colunas_devolucao = ['tipo_produto', 'valor_devolvida']
    # --- FIM DA CORREÇÃO ---
    
    capital_full_df = pd.DataFrame(columns=colunas_capital)
    devolucao_df = pd.DataFrame(columns=colunas_devolucao)
    
    # (Para o gráfico de barras simples)
    capital_simplificado_df = pd.DataFrame(columns=['tipo_produto', 'valor_estoque'])

    # 1. Capital Alocado
    if all(col in df_estoque.columns for col in ['tipo_produto', 'valor_estoque', 'descricao']):
        
        capital_df = df_estoque.groupby('tipo_produto')['valor_estoque'].sum().reset_index()
        total_capital = capital_df['valor_estoque'].sum()
        
        # Dataframe para o gráfico de barras
        capital_simplificado_df = capital_df.sort_values('valor_estoque', ascending=False)

        if total_capital > 0:
            capital_df['percentual_total'] = (capital_df['valor_estoque'] / total_capital)
        else:
            capital_df['percentual_total'] = 0.0
        
        # Dataframe para o Treemap (se necessário no futuro)
        capital_full_df_temp = df_estoque[['tipo_produto', 'descricao', 'valor_estoque']].copy()
        capital_full_df = capital_full_df_temp.merge(capital_df[['tipo_produto', 'percentual_total']], on='tipo_produto')
        
        # --- CORREÇÃO (CAPITAL V2) ---
        # Resolve o erro 'ValueError: (Non-leaves rows are not permitted...)'
        capital_full_df['descricao'] = capital_full_df['descricao'].astype(str)
        capital_full_df = capital_full_df.dropna(subset=['descricao'])
        capital_full_df['descricao'] = capital_full_df['descricao'].str.strip()
        capital_full_df = capital_full_df[capital_full_df['descricao'] != '']
        # --- FIM DA CORREÇÃO (CAPITAL V2) ---

    # 2. Análise de Devolução
    if all(col in df_estoque.columns for col in ['tipo_produto', 'valor_devolvida']):
        
        devolucao_df = df_estoque.groupby('tipo_produto')['valor_devolvida'].sum().reset_index()
        devolucao_df = devolucao_df.sort_values('valor_devolvida', ascending=False)
    
    # Retorna os 3 dataframes
    return capital_full_df, devolucao_df, capital_simplificado_df

# =============================================
# HIPÓTESE 3: ANÁLISE DE RETENÇÃO (NOVA FUNÇÃO)
# =============================================
def calcular_analise_retencao(df_vendas: pd.DataFrame):
    """Calcula o heatmap de retenção (coortes) e KPIs de retenção."""
    
    # --- INÍCIO DA ALTERAÇÃO (V15) ---
    # Inicializar os dataframes de retorno para garantir que a função não quebre
    # se os dados de entrada forem insuficientes.
    colunas_heatmap = ['Coorte (Mês da 1ª Compra)', 'Meses Desde a Primeira Compra', 'Taxa de Retenção']
    retencao_pivot_final = pd.DataFrame(columns=colunas_heatmap)
    
    colunas_media = ['Meses Desde a Primeira Compra', 'Taxa Média de Retenção']
    media_retencao_df = pd.DataFrame(columns=colunas_media)
    
    kpi_novos = 0
    kpi_retidos = 0
    # --- FIM DA ALTERAÇÃO (V15) ---

    df = df_vendas[['cliente', 'data']].copy()
    df = df.dropna(subset=['data'])
    
    if df.empty:
        # Retorna os dataframes vazios e KPIs zerados (agora 4 valores)
        return retencao_pivot_final, kpi_novos, kpi_retidos, media_retencao_df

    df['mes_compra'] = df['data'].dt.to_period('M')
    df['mes_coorte'] = df.groupby('cliente')['data'].transform('min').dt.to_period('M')
    
    df_coorte = df.groupby(['mes_coorte', 'mes_compra'])['cliente'].nunique().reset_index()
    df_coorte = df_coorte.dropna(subset=['mes_compra', 'mes_coorte'])

    # Evitar erro se não houver dados suficientes para calcular 'periodo_mes'
    if df_coorte.empty:
       return retencao_pivot_final, kpi_novos, kpi_retidos, media_retencao_df

    df_coorte['periodo_mes'] = (df_coorte['mes_compra'] - df_coorte['mes_coorte']).apply(lambda x: x.n)
    
    coorte_pivot = df_coorte.pivot_table(index='mes_coorte',
                                         columns='periodo_mes',
                                         values='cliente')
    
    # Se o pivot falhar ou estiver vazio
    if coorte_pivot.empty:
        return retencao_pivot_final, kpi_novos, kpi_retidos, media_retencao_df

    coorte_tamanho = coorte_pivot.iloc[:, 0]
    retencao_matrix = coorte_pivot.divide(coorte_tamanho, axis=0)
    
    # --- INÍCIO DA ALTERAÇÃO (V15) ---
    # Calcular a média de retenção para o gráfico de linha
    media_retencao = retencao_matrix.mean(axis=0)
    media_retencao_df = media_retencao.reset_index()
    media_retencao_df.columns = ['Meses Desde a Primeira Compra', 'Taxa Média de Retenção']
    # Manter apenas os meses 1 em diante (o mês 0 é sempre 100%)
    media_retencao_df = media_retencao_df[media_retencao_df['Meses Desde a Primeira Compra'] > 0].copy()
    # --- FIM DA ALTERAÇÃO (V15) ---

    # Formatar para o gráfico de heatmap
    retencao_heatmap = retencao_matrix.rename_axis('Coorte (Mês da 1ª Compra)').reset_index()
    retencao_heatmap = retencao_heatmap.melt(id_vars='Coorte (Mês da 1ª Compra)', 
                                             var_name='Meses Desde a Primeira Compra', 
                                             value_name='Taxa de Retenção')
    
    if len(retencao_heatmap['Coorte (Mês da 1ª Compra)'].unique()) > 12:
        top_12_coortes = retencao_heatmap['Coorte (Mês da 1ª Compra)'].unique()[-12:]
        retencao_heatmap = retencao_heatmap[retencao_heatmap['Coorte (Mês da 1ª Compra)'].isin(top_12_coortes)]
        
    retencao_heatmap = retencao_heatmap.dropna(subset=['Taxa de Retenção'])
    retencao_heatmap = retencao_heatmap[retencao_heatmap['Meses Desde a Primeira Compra'] > 0] # Remover o Mês 0
    
    # Pivotar novamente para o Plotly imshow
    if not retencao_heatmap.empty:
        retencao_pivot_final = retencao_heatmap.pivot_table(index='Coorte (Mês da 1ª Compra)', 
                                                            columns='Meses Desde a Primeira Compra', 
                                                            values='Taxa de Retenção')
        retencao_pivot_final.index = retencao_pivot_final.index.astype(str)
    else:
        # Se após os filtros o heatmap ficar vazio, retorna o DF vazio inicializado
        retencao_pivot_final = pd.DataFrame(columns=colunas_heatmap)


    # 5. KPIs de Retenção/Aquisição (para o último mês)
    try:
        if not df.empty and not df['mes_compra'].empty:
            ultimo_mes = df['mes_compra'].max()
            penultimo_mes = ultimo_mes - 1
            
            clientes_ultimo_mes = set(df[df['mes_compra'] == ultimo_mes]['cliente'].unique())
            clientes_penultimo_mes = set(df[df['mes_compra'] == penultimo_mes]['cliente'].unique())
            
            kpi_novos = len(clientes_ultimo_mes - clientes_penultimo_mes)
            kpi_retidos = len(clientes_ultimo_mes.intersection(clientes_penultimo_mes))
        else:
            kpi_novos = 0
            kpi_retidos = 0
    except Exception:
        # Se houver qualquer erro (ex: dados de apenas 1 mês), zera os KPIs
        kpi_novos = 0
        kpi_retidos = 0

    # Retorna o heatmap, os kpis E o novo dataframe de média
    return retencao_pivot_final, kpi_novos, kpi_retidos, media_retencao_df  