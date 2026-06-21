import pandas as pd
import numpy as np
import uuid

def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
    return df

def clean_amounts(df: pd.DataFrame) -> pd.DataFrame:
    if df['amount'].dtype == object:
        df['amount'] = df['amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    return df

def uppercase_columns(df: pd.DataFrame) -> pd.DataFrame:
    if 'status' in df.columns:
        df['status'] = df['status'].astype(str).str.upper().replace('NAN', np.nan)
    if 'currency' in df.columns:
        df['currency'] = df['currency'].astype(str).str.upper().replace('NAN', np.nan)
    return df

def fill_missing_categories(df: pd.DataFrame) -> pd.DataFrame:
    if 'category' in df.columns:
        df['category'] = df['category'].replace('', np.nan).fillna('Uncategorised')
    return df

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()

def generate_missing_txn_ids(df: pd.DataFrame) -> pd.DataFrame:
    if 'txn_id' in df.columns:
        mask = df['txn_id'].isna() | (df['txn_id'] == '') | (df['txn_id'].astype(str).str.upper() == 'NAN')
        df.loc[mask, 'txn_id'] = [str(uuid.uuid4()) for _ in range(mask.sum())]
    return df

def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = normalize_dates(df)
    df = clean_amounts(df)
    df = uppercase_columns(df)
    df = fill_missing_categories(df)
    df = remove_duplicates(df)
    df = generate_missing_txn_ids(df)
    return df
