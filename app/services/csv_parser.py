import pandas as pd
from typing import IO
from fastapi import HTTPException

REQUIRED_COLUMNS = [
    "txn_id",
    "date",
    "merchant",
    "amount",
    "currency",
    "status",
    "category",
    "account_id",
    "notes",
]

def parse_csv(file_obj: IO) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_obj)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required columns: {', '.join(missing_cols)}"
        )
    
    return df
