import pandas as pd

def filter_df(df: pd.DataFrame, column_name: str, term: str) -> pd.DataFrame:
    """
    Filtra o DataFrame com base no termo passado e na coluna especificada.
    
    :param df: DataFrame a ser filtrado
    :param column_name: Nome da coluna para aplicar o filtro
    :param term: O valor/termo para filtrar
    :return: Um novo DataFrame apenas com as linhas que atendem à condição
    """
    try:
        # Realiza o filtro no DataFrame
        filtered_df = df[df[column_name].str.contains(term, case=False, na=False)].copy()
        # filtered_df['Historico'] = term
        return filtered_df
    except KeyError:
        print(f"Erro: A coluna '{column_name}' não existe no DataFrame.")
        return pd.DataFrame()  # Retorna um DataFrame vazio caso a coluna não exista
    except Exception as e:
        print(f"Ocorreu um erro ao filtrar o DataFrame: {e}")
        return pd.DataFrame()