import pandas as pd
from typing import Union

# =============================================
# ANÁLISE GERAL (Mantida)
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
# ANÁLISE DE PAGAMENTO (Mantida - Usada pela pág. Clientes)
# =============================================
def calcular_preferencias_pagamento(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Calcula a receita, ticket médio e total de vendas por forma de pagamento."""
    
    pagamento_stats = df_vendas.groupby('pagamento').agg({
        'valor': ['sum', 'mean', 'count']
    }).round(2)
    
    pagamento_stats.columns = ['Receita Total', 'Ticket Médio', 'Total Vendas']
    
    return pagamento_stats

# =============================================
# ANÁLISE DE ESTOQUE (Mantida)
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
# NOVAS ANÁLISE DE SAZONALIDADE (Para a pág. Vendas)
# =============================================

def calcular_vendas_por_hora(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Calcula o faturamento agregado por hora do dia."""
    vendas_hora = df_vendas.groupby('hora')['valor'].sum().reset_index()
    return vendas_hora

def calcular_vendas_por_dia_semana(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Calcula o faturamento agregado por dia da semana, ordenado."""
    
    # Ordem correta dos dias
    dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Mapeamento para português
    dias_portugues = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    
    # Agrupa os dados
    vendas_dia = df_vendas.groupby('dia_semana')['valor'].sum().reset_index()
    
    # Mapeia para português
    vendas_dia['dia_pt'] = vendas_dia['dia_semana'].map(dias_portugues)
    
    # Cria uma coluna categórica ordenada para garantir a ordem correta no gráfico
    vendas_dia['dia_semana_cat'] = pd.Categorical(vendas_dia['dia_semana'], categories=dias_ordem, ordered=True)
    
    # Ordena pela categoria
    vendas_dia = vendas_dia.sort_values('dia_semana_cat')
    
    return vendas_dia

