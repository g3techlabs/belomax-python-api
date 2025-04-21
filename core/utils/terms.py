# core/utils/terms.py
def extract_unique_terms(df) -> list[str]:
    if 'Historico' not in df.columns:
        return []

    return df['Historico'].dropna().unique().tolist()