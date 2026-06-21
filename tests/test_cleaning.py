import pandas as pd
from app.services.data_cleaner import clean_amounts, uppercase_columns

def test_clean_amounts():
    df = pd.DataFrame({'amount': ['$12.50', '10', 'invalid']})
    cleaned = clean_amounts(df)
    assert cleaned['amount'].iloc[0] == 12.50
    assert cleaned['amount'].iloc[1] == 10.0
    assert pd.isna(cleaned['amount'].iloc[2])

def test_uppercase_columns():
    df = pd.DataFrame({'status': ['pending', 'Success'], 'currency': ['inr', 'Usd']})
    cleaned = uppercase_columns(df)
    assert cleaned['status'].iloc[0] == 'PENDING'
    assert cleaned['currency'].iloc[1] == 'USD'
