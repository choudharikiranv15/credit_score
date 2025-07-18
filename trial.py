import pandas as pd
import os

json_file_path = 'user-wallet-transactions.json'

if not os.path.exists(json_file_path):
    print(
        f"Error: '{json_file_path}' not found. Please make sure the JSON file is in the correct directory.")
    print("You can download the compressed ZIP file from: https://drive.google.com/file/d/14ceBCLQ-BTCydDrFJauVA_PKAZ7VtDor/view?usp=sharing")
    print("Extract 'transactions.json' from the ZIP file into your project directory.")
else:
    try:
        df = pd.read_json(json_file_path)
        print("Initial data loaded successfully.")

        # --- Data Cleaning and Flattening ---

        # 1. Flatten '_id' column (extract '$oid')
        if '_id' in df.columns and isinstance(df['_id'].iloc[0], dict):
            df['_id'] = df['_id'].apply(lambda x: x.get(
                '$oid') if isinstance(x, dict) else x)

        # 2. Flatten 'createdAt' and 'updatedAt' columns (extract '$date' and convert to datetime)
        for col in ['createdAt', 'updatedAt']:
            if col in df.columns and isinstance(df[col].iloc[0], dict):
                df[col] = df[col].apply(lambda x: x.get(
                    '$date') if isinstance(x, dict) else x)
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

        # 3. Rename 'userWallet' to 'wallet_address' for consistency
        if 'userWallet' in df.columns:
            df.rename(columns={'userWallet': 'wallet_address'}, inplace=True)

        # 4. Flatten 'actionData' column
        if 'actionData' in df.columns:
            action_data_df = pd.json_normalize(df['actionData'])

            # Rename columns if they exist after normalization
            if 'amount' in action_data_df.columns:
                action_data_df.rename(
                    columns={'amount': 'amount_raw'}, inplace=True)
            if 'asset' in action_data_df.columns:
                action_data_df.rename(
                    columns={'asset': 'asset_symbol'}, inplace=True)

            df = pd.concat(
                [df.drop('actionData', axis=1), action_data_df], axis=1)
        else:
            print(
                "Warning: 'actionData' column not found. Some features might be missing.")

        print("DataFrame after initial cleaning and flattening.")

        # --- Further Data Cleaning: Convert amount_raw to numeric and adjust for decimals ---

        # Define a mapping for common token decimals
        # This is an educated guess for Aave V2 main assets. You might need to refine this.
        # USDC and USDT typically have 6 decimals. WETH, DAI, AAVE usually have 18.
        token_decimals = {
            'WETH': 18, 'DAI': 18, 'USDC': 6, 'USDT': 6, 'WBTC': 8, 'AAVE': 18,
            'WMATIC': 18, 'LINK': 18, 'CRV': 18, 'BAL': 18, 'SUSHI': 18,
            # Add more as you discover them in assetSymbol unique values
        }
        # Default to 18 decimals if asset not found in mapping (common for many ERC-20s)
        default_decimals = 18

        def convert_amount(row):
            try:
                # Get the number of decimals for the specific asset
                decimals = token_decimals.get(
                    row['asset_symbol'], default_decimals)
                # Convert the raw amount (string) to integer and then to float
                return float(int(row['amount_raw'])) / (10**decimals)
            except (ValueError, TypeError, KeyError):
                # Handle cases where amount_raw isn't a valid number or asset_symbol is missing
                return pd.NA  # Use Pandas' nullable integer type

        # Apply the conversion
        print("Converting 'amount_raw' to 'amount' (adjusted for decimals)...")
        # Ensure 'amount_raw' is treated as string before conversion attempt
        df['amount'] = df.apply(lambda row: convert_amount(row), axis=1)

        # Convert 'assetPriceUSD' to numeric if it exists
        if 'assetPriceUSD' in df.columns:
            # Coerce errors to NaN, then fill NaN with a reasonable default (e.g., 0 or mean, depending on context)
            df['assetPriceUSD'] = pd.to_numeric(
                df['assetPriceUSD'], errors='coerce')
            # Or consider a more robust imputation strategy
            df['assetPriceUSD'].fillna(0, inplace=True)

        # Convert other relevant numeric-like columns that came from actionData
        # For columns that are 'object' but should be numeric, apply pd.to_numeric
        numeric_cols_to_convert = [
            'borrowRate', 'variableTokenDebt', 'stableTokenDebt',
            'collateralAmount', 'collateralAssetPriceUSD', 'principalAmount', 'borrowAssetPriceUSD'
        ]
        for col in numeric_cols_to_convert:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill NaNs with 0 for these columns, as their absence usually means 0 value for that specific transaction type
                df[col].fillna(0, inplace=True)

        print("\nDataFrame after all data type conversions:")
        print(df.head())
        print("\nDataFrame Info after all data type conversions:")
        df.info()

        # You might want to save this cleaned DataFrame for quicker loading later:
        # df.to_parquet('cleaned_transactions.parquet', index=False)
        # print("\nCleaned DataFrame saved to 'cleaned_transactions.parquet'")

    except Exception as e:
        print(f"An error occurred during data processing: {e}")
