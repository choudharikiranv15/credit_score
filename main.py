import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np  # Import numpy for np.inf

json_file_path = 'user-wallet-transactions.json'

if not os.path.exists(json_file_path):
    print(
        f"Error: '{json_file_path}' not found. Please make sure the JSON file is in the correct directory.")
    print("You can download the compressed ZIP file from: https://drive.google.com/file/d/14ceBCLQ-BTCydDrFJauVA_PKAZ7VtDor/view?usp=sharing")
    print("Extract 'user-wallet-transactions.json' from the ZIP file into your project directory.")
else:
    try:
        df = pd.read_json(json_file_path)
        print("Initial data loaded successfully.")

        # --- Data Cleaning and Flattening ---
        if '_id' in df.columns and isinstance(df['_id'].iloc[0], dict):
            df['_id'] = df['_id'].apply(lambda x: x.get(
                '$oid') if isinstance(x, dict) else x)
            # print("Flattened '_id' column.") # Commented out for cleaner output

        for col in ['createdAt', 'updatedAt']:
            if col in df.columns and isinstance(df[col].iloc[0], dict):
                df[col] = df[col].apply(lambda x: x.get(
                    '$date') if isinstance(x, dict) else x)
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
                # print(f"Flattened and converted '{col}' to datetime.") # Commented out

        if 'userWallet' in df.columns:
            df.rename(columns={'userWallet': 'wallet_address'}, inplace=True)
            # print("Renamed 'userWallet' to 'wallet_address'.") # Commented out

        if 'actionData' in df.columns:
            # print("Flattening 'actionData' column...") # Commented out
            action_data_df = pd.json_normalize(df['actionData'])

            # print(f"Columns in action_data_df after json_normalize: {action_data_df.columns.tolist()}") # Commented out

            rename_map = {}
            if 'amount' in action_data_df.columns:
                rename_map['amount'] = 'amount_raw'
            if 'assetSymbol' in action_data_df.columns:
                rename_map['assetSymbol'] = 'asset_symbol'

            if rename_map:
                action_data_df.rename(columns=rename_map, inplace=True)
                # print(f"Columns in action_data_df after renaming: {action_data_df.columns.tolist()}") # Commented out

            df = df.drop('actionData', axis=1)
            df = pd.concat([df.reset_index(drop=True),
                           action_data_df.reset_index(drop=True)], axis=1)
            # print("Flattened 'actionData' column and integrated into DataFrame.") # Commented out
        else:
            print(
                "Warning: 'actionData' column not found. Some features might be missing.")

        print("DataFrame after initial cleaning and flattening.")

        token_decimals = {
            'WETH': 18, 'DAI': 18, 'USDC': 6, 'USDT': 6, 'WBTC': 8, 'AAVE': 18,
            'WMATIC': 18, 'LINK': 18, 'CRV': 18, 'BAL': 18, 'SUSHI': 18,
            'USDC.e': 6, 'EURT': 6, 'stETH': 18, 'FRAX': 18, 'CRVUSD': 18, 'LUSD': 18,
            'WPOL': 18,
        }
        default_decimals = 18

        def convert_amount(row):
            if 'amount_raw' not in row.index or 'asset_symbol' not in row.index:
                return pd.NA

            raw_amount_str = str(row['amount_raw'])
            asset_sym = str(row['asset_symbol'])

            if not raw_amount_str.isdigit():
                return pd.NA

            try:
                decimals = token_decimals.get(asset_sym, default_decimals)
                return float(int(raw_amount_str)) / (10**decimals)
            except (ValueError, TypeError, KeyError) as e:
                # print(f"Error converting amount: raw='{raw_amount_str}', asset='{asset_sym}', Error: {e}") # Commented out
                return pd.NA

        print("Converting 'amount_raw' to 'amount' (adjusted for decimals)...")
        if 'amount_raw' in df.columns and 'asset_symbol' in df.columns:
            df['amount'] = df.apply(convert_amount, axis=1)
        else:
            df['amount'] = pd.NA
            print(
                "Warning: 'amount_raw' or 'asset_symbol' columns not found. 'amount' column will be all <NA>.")

        if 'assetPriceUSD' in df.columns:
            df['assetPriceUSD'] = pd.to_numeric(
                df['assetPriceUSD'], errors='coerce').fillna(0)

        numeric_cols_to_convert = [
            'borrowRate', 'variableTokenDebt', 'stableTokenDebt',
            'collateralAmount', 'collateralAssetPriceUSD', 'principalAmount', 'borrowAssetPriceUSD'
        ]
        for col in numeric_cols_to_convert:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        print("\nDataFrame after all data type conversions:")
        print(df.head())
        print("\nDataFrame Info after all data type conversions:")
        df.info()

        print("\nUnique asset symbols to check for decimal mapping:")
        if 'asset_symbol' in df.columns:
            print(df['asset_symbol'].unique())
        else:
            print("Cannot check unique asset symbols: 'asset_symbol' column not found.")

        print(f"\nNaN count in 'amount' column: {df['amount'].isna().sum()}")

        # --- Feature Engineering ---
        print("\nStarting Feature Engineering...")

        wallet_features = df.groupby('wallet_address').agg(
            total_transactions=('txHash', 'nunique'),
            first_tx_date=('timestamp', 'min'),
            last_tx_date=('timestamp', 'max'),
            num_unique_assets=('asset_symbol', 'nunique'),

            total_deposit_value=(
                'amount', lambda x: x[df.loc[x.index, 'action'] == 'deposit'].sum()),
            total_borrow_value=(
                'amount', lambda x: x[df.loc[x.index, 'action'] == 'borrow'].sum()),
            total_repay_value=(
                'amount', lambda x: x[df.loc[x.index, 'action'] == 'repay'].sum()),
            total_liquidation_amount=(
                'principalAmount', lambda x: x[df.loc[x.index, 'action'] == 'liquidationcall'].sum()),
            total_collateral_liquidated=(
                'collateralAmount', lambda x: x[df.loc[x.index, 'action'] == 'liquidationcall'].sum()),

            deposit_count=('action', lambda x: (x == 'deposit').sum()),
            borrow_count=('action', lambda x: (x == 'borrow').sum()),
            repay_count=('action', lambda x: (x == 'repay').sum()),
            liquidation_call_count=('action', lambda x: (
                x == 'liquidationcall').sum()),
        )

        wallet_features['activity_duration_days'] = (
            wallet_features['last_tx_date'] - wallet_features['first_tx_date']).dt.days

        wallet_features['net_borrow_value'] = wallet_features['total_borrow_value'] - \
            wallet_features['total_repay_value']

        wallet_features['repay_ratio'] = wallet_features.apply(
            lambda row: row['total_repay_value'] / row['total_borrow_value'] if row['total_borrow_value'] > 0 else 0, axis=1
        )
        wallet_features['repay_ratio'] = wallet_features['repay_ratio'].clip(
            upper=1.0)

        wallet_features['borrow_to_deposit_ratio'] = wallet_features.apply(
            lambda row: row['total_borrow_value'] / row['total_deposit_value'] if row['total_deposit_value'] > 0 else 0, axis=1
        )
        wallet_features['borrow_to_deposit_ratio'] = wallet_features['borrow_to_deposit_ratio'].clip(
            upper=10.0)

        wallet_features['was_liquidated'] = (
            wallet_features['liquidation_call_count'] > 0).astype(int)

        wallet_features['avg_tx_amount'] = wallet_features.apply(
            lambda row: (row['total_deposit_value'] + row['total_borrow_value'] + row['total_repay_value']) / row['total_transactions'] if row['total_transactions'] > 0 else 0, axis=1
        )

        wallet_features.fillna(0, inplace=True)

        print("\nWallet Features DataFrame Head:")
        print(wallet_features.head())
        print("\nWallet Features DataFrame Info:")
        wallet_features.info()

        # --- Saving engineered features (UNCOMMENTED HERE) ---
        # index=True saves wallet_address
        wallet_features.to_csv('wallet_features.csv', index=True)
        print("\nWallet features saved to 'wallet_features.csv'")

        # --- START OF NEW CODE FOR SCORING LOGIC ---
        print("\nApplying Credit Scoring Logic...")

        features_for_scoring = wallet_features[[
            'total_transactions',
            'activity_duration_days',
            'num_unique_assets',
            'total_deposit_value',
            'total_borrow_value',
            'total_repay_value',
            'repay_ratio',
            'borrow_to_deposit_ratio',
            'liquidation_call_count',
            'was_liquidated',
            'net_borrow_value',
            'avg_tx_amount'
        ]].copy()

        features_for_scoring.replace([np.inf, -np.inf], np.nan, inplace=True)
        features_for_scoring.fillna(0, inplace=True)

        wallet_features['credit_score'] = 500

        wallet_features['credit_score'] -= (
            features_for_scoring['liquidation_call_count'] * 100)

        wallet_features['credit_score'] -= (
            features_for_scoring['borrow_to_deposit_ratio'] * 20)

        wallet_features['credit_score'] += (
            features_for_scoring['repay_ratio'] * 200)

        wallet_features['credit_score'] += (
            np.log1p(features_for_scoring['total_transactions']) * 10)

        wallet_features['credit_score'] += (
            np.log1p(features_for_scoring['total_deposit_value']) * 5)

        temp_scores = wallet_features['credit_score'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1000))
        wallet_features['final_credit_score'] = scaler.fit_transform(
            temp_scores)

        wallet_features['final_credit_score'] = wallet_features['final_credit_score'].round(
        ).astype(int)

        print("\nWallet Features with Final Credit Score Head:")
        print(wallet_features[['total_transactions', 'repay_ratio', 'borrow_to_deposit_ratio',
                              'liquidation_call_count', 'was_liquidated', 'final_credit_score']].head())
        print("\nCredit Score Distribution (example ranges):")
        print(wallet_features['final_credit_score'].value_counts(
            bins=5).sort_index())
        print(f"\nMax Score: {wallet_features['final_credit_score'].max()}")
        print(f"Min Score: {wallet_features['final_credit_score'].min()}")
        print(f"Average Score: {wallet_features['final_credit_score'].mean()}")

        output_df = wallet_features[['final_credit_score']].copy()
        output_df.index.name = 'wallet_address'
        output_df.to_csv('wallet_scores.csv')
        print("\nWallet scores saved to 'wallet_scores.csv'")

    except Exception as e:
        print(f"An unexpected error occurred during data processing: {e}")
