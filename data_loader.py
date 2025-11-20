import pandas as pd
from datetime import datetime
from typing import Union
import re # Necessário para extrair a data

# Define o tipo de retorno para as funções de processamento
DataFrameOrNone = Union[pd.DataFrame, None]

# --- FUNÇÃO 1 (Sem alteração) ---
def processar_dados_vendas(df_vendas: pd.DataFrame) -> DataFrameOrNone:
    """Processa a base de vendas (Relatorio.xlsx), limpando e adicionando colunas de tempo."""
    try:
        df_vendas_clean = df_vendas.copy()
        df_vendas_clean.columns = ['venda', 'cliente', 'vendedor', 'data', 'pagamento', 'valor']
        df_vendas_clean['data'] = pd.to_datetime(df_vendas_clean['data'], format='%d/%m/%Y %H:%M', errors='coerce')
        df_vendas_clean['valor'] = df_vendas_clean['valor'].astype(str).str.replace(',', '.').astype(float)
        df_vendas_clean['venda'] = pd.to_numeric(df_vendas_clean['venda'], errors='coerce')
        df_vendas_clean['hora'] = df_vendas_clean['data'].dt.hour
        df_vendas_clean['dia_semana'] = df_vendas_clean['data'].dt.day_name()
        df_vendas_clean['mes'] = df_vendas_clean['data'].dt.month_name()
        return df_vendas_clean
    except Exception as e:
        print(f"Erro ao processar vendas: {str(e)}")
        return None

# --- FUNÇÃO 2 (Sem alteração) ---
def processar_dados_estoque(df_estoque: pd.DataFrame) -> DataFrameOrNone:
    """Processa a base de estoque (RelatorioProd.xlsx), limpando e categorizando produtos."""
    try:
        df_estoque_clean = df_estoque.copy()
        df_estoque_clean.columns = ['codigo', 'descricao', 'unidade', 'estoque', 'valor_estoque', 
                                    'qtd_devolvida', 'valor_devolvida', 'qtd', 'saldo']
        for col in ['estoque', 'valor_estoque', 'qtd_devolvida', 'valor_devolvida', 'qtd', 'saldo']:
            if col in df_estoque_clean.columns:
                df_estoque_clean[col] = df_estoque_clean[col].astype(str).str.replace(',', '.').astype(float)
        df_estoque_clean['tipo_produto'] = df_estoque_clean['descricao'].apply(
            lambda x: 'CARNE' if 'CARNE' in str(x).upper() or 'AGEM' in str(x).upper() else 'OUTROS'
        )
        return df_estoque_clean
    except Exception as e:
        print(f"Erro ao processar estoque: {str(e)}")
        return None

# --- FUNÇÃO 3 (NOVA FUNÇÃO) ---
def processar_dados_caixa(df_caixa_raw: pd.DataFrame) -> DataFrameOrNone:
    """Processa o Relatório de Movimentação de Caixa (Movimentacao_Caixa.xlsx)."""
    try:
        dados_processados = []
        data_negociacao = None
        
        # Expressão regular para encontrar a data (ex: "Date: 02/01/2024 08:29:23")
        date_pattern = re.compile(r"Date: (\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})")

        # Lê o dataframe sem cabeçalho
        df = df_caixa_raw
        
        headers = ['Codigo', 'Produto', 'Unidade', 'Quantidade', 'Desconto %', 'Valor R$']
        coletando_dados = False

        for index, row in df.iterrows():
            # Converte a linha para string para verificar
            row_str = str(row.iloc[0])
            
            # 1. Encontra a data da negociação
            if "Negociação" in row_str:
                match = date_pattern.search(str(row.iloc[1]))
                if match:
                    data_negociacao = pd.to_datetime(match.group(1), format='%d/%m/%Y %H:%M:%S')
                coletando_dados = False # Para de coletar ao achar uma nova negociação
            
            # 2. Encontra o cabeçalho dos produtos
            elif str(row.iloc[0]).strip() == "Codigo" and str(row.iloc[1]).strip() == "Produto":
                coletando_dados = True
                continue # Pula a linha do cabeçalho
            
            # 3. Para de coletar ao encontrar o total
            elif "Total:" in row_str:
                coletando_dados = False
                continue

            # 4. Coleta os dados
            if coletando_dados and data_negociacao:
                try:
                    # Tenta converter o código para número para garantir que é uma linha de dados
                    pd.to_numeric(row.iloc[0]) 
                    
                    dados_linha = {
                        'Data': data_negociacao,
                        'Codigo': row.iloc[0],
                        'Produto': row.iloc[1],
                        'Unidade': row.iloc[2],
                        'Quantidade': pd.to_numeric(str(row.iloc[3]).replace(',', '.')),
                        'Desconto %': pd.to_numeric(str(row.iloc[4]).replace(',', '.')),
                        'Valor R$': pd.to_numeric(str(row.iloc[5]).replace(',', '.'))
                    }
                    dados_processados.append(dados_linha)
                except ValueError:
                    # Se não for um número no código, ignora (provavelmente linha em branco ou lixo)
                    continue

        df_final = pd.DataFrame(dados_processados)
        return df_final

    except Exception as e:
        print(f"Erro ao processar caixa: {str(e)}")
        return None