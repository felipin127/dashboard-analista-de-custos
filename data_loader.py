# data_loader.py (CÓDIGO CORRETO E COMPLETO)

import pandas as pd
from datetime import datetime
from typing import Union

# Define o tipo de retorno para as funções de processamento
DataFrameOrNone = Union[pd.DataFrame, None]


def processar_dados_vendas(df_vendas: pd.DataFrame) -> DataFrameOrNone:
    """Processa a base de vendas, limpando e adicionando colunas de tempo."""
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
        print(f"Erro ao processar vendas: {str(e)}")
        return None


def processar_dados_estoque(df_estoque: pd.DataFrame) -> DataFrameOrNone:
    """Processa a base de estoque/custos, limpando e categorizando produtos."""
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
        print(f"Erro ao processar estoque: {str(e)}")
        return None