import pandas as pd

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['is_anomaly'] = False
    df['anomaly_reason'] = None

    # Rule 1: amount > 3 * account median amount
    if 'account_id' in df.columns and 'amount' in df.columns:
        # Calculate median per account
        account_medians = df.groupby('account_id')['amount'].transform('median')
        mask_rule_1 = df['amount'] > (3 * account_medians)
        
        df.loc[mask_rule_1, 'is_anomaly'] = True
        df.loc[mask_rule_1, 'anomaly_reason'] = "Amount exceeds 3x account median"

    # Rule 2: currency = USD and merchant in [Swiggy, Ola, IRCTC]
    if 'currency' in df.columns and 'merchant' in df.columns:
        target_merchants = ['SWIGGY', 'OLA', 'IRCTC']
        mask_rule_2 = (df['currency'] == 'USD') & (df['merchant'].astype(str).str.upper().isin(target_merchants))
        
        # For rows that hit both rules, we can append or overwrite the reason.
        # Let's append if there's already a reason.
        existing_reason_mask = mask_rule_2 & df['is_anomaly']
        new_reason_mask = mask_rule_2 & ~df['is_anomaly']

        df.loc[new_reason_mask, 'is_anomaly'] = True
        df.loc[new_reason_mask, 'anomaly_reason'] = "USD currency used for domestic merchant"

        df.loc[existing_reason_mask, 'anomaly_reason'] += " | USD currency used for domestic merchant"

    return df

def get_anomaly_statistics(df: pd.DataFrame) -> dict:
    if 'is_anomaly' not in df.columns:
        return {"total_anomalies": 0}
    
    total_anomalies = int(df['is_anomaly'].sum())
    return {
        "total_anomalies": total_anomalies
    }
