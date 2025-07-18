import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

print("Starting analysis script...")

# --- Configuration ---
WALLET_FEATURES_FILE = 'wallet_features.csv'
WALLET_SCORES_FILE = 'wallet_scores.csv'  # Output from main.py
OUTPUT_PLOT_NAME = 'credit_score_distribution.png'

# --- Load Data ---
try:
    if not os.path.exists(WALLET_FEATURES_FILE):
        print(f"Error: '{WALLET_FEATURES_FILE}' not found.")
        print("Please ensure you've run 'main.py' and uncommented the line to save 'wallet_features.csv'.")
        # Fallback: if only wallet_scores.csv exists, load that.
        if os.path.exists(WALLET_SCORES_FILE):
            print(
                f"Attempting to load only '{WALLET_SCORES_FILE}'. Note: full feature analysis won't be possible.")
            wallet_features = pd.read_csv(
                WALLET_SCORES_FILE, index_col='wallet_address')
        else:
            raise FileNotFoundError(
                f"Neither {WALLET_FEATURES_FILE} nor {WALLET_SCORES_FILE} found.")
    else:
        wallet_features = pd.read_csv(
            WALLET_FEATURES_FILE, index_col='wallet_address')
        print(f"Successfully loaded {WALLET_FEATURES_FILE}.")

    # Ensure datetime columns are correct if loaded from CSV (as they might become object type)
    if 'first_tx_date' in wallet_features.columns:
        wallet_features['first_tx_date'] = pd.to_datetime(
            wallet_features['first_tx_date'])
    if 'last_tx_date' in wallet_features.columns:
        wallet_features['last_tx_date'] = pd.to_datetime(
            wallet_features['last_tx_date'])

    # If wallet_features.csv didn't contain 'final_credit_score' (e.g., if you saved it before scoring)
    # and wallet_scores.csv exists, merge the score in.
    if 'final_credit_score' not in wallet_features.columns and os.path.exists(WALLET_SCORES_FILE):
        wallet_scores = pd.read_csv(
            WALLET_SCORES_FILE, index_col='wallet_address')
        wallet_features = wallet_features.merge(
            wallet_scores, left_index=True, right_index=True, how='left')
        print(f"Merged 'final_credit_score' from {WALLET_SCORES_FILE}.")
    elif 'final_credit_score' not in wallet_features.columns:
        print("Warning: 'final_credit_score' not found in wallet_features. Cannot proceed with analysis.")
        exit()  # Exit if we don't have the score

    print("\nWallet Features DataFrame Head for analysis:")
    print(wallet_features.head())
    print("\nWallet Features DataFrame Info for analysis:")
    wallet_features.info()

except Exception as e:
    print(f"Error loading data for analysis: {e}")
    exit()

# --- 1. Credit Score Distribution Analysis and Plot ---
print(f"\nGenerating credit score distribution plot: {OUTPUT_PLOT_NAME}...")

plt.figure(figsize=(12, 7))
sns.histplot(wallet_features['final_credit_score'],
             bins=20, kde=True, color='skyblue', edgecolor='black')
plt.title('Distribution of Wallet Credit Scores (0-1000)', fontsize=16)
plt.xlabel('Credit Score', fontsize=14)
plt.ylabel('Number of Wallets', fontsize=14)
plt.xticks(range(0, 1001, 100))  # Set x-ticks for ranges like 0-100, 100-200
plt.grid(axis='y', alpha=0.75, linestyle='--')
plt.tight_layout()
plt.savefig(OUTPUT_PLOT_NAME)  # Save the plot as an image
print(f"Credit score distribution plot saved to {OUTPUT_PLOT_NAME}")
# plt.show() # Uncomment this line if you are running in an interactive environment (like Jupyter) and want to see the plot immediately.

# --- 2. Wallet Behavior Across Score Ranges ---
print("\nAnalyzing wallet behavior across score ranges...")

# Define score ranges for grouping
bins = [0, 200, 400, 600, 800, 1001]  # 1001 to include 1000
labels = ['0-200 (Very Low)', '201-400 (Low)', '401-600 (Medium)',
          '601-800 (High)', '801-1000 (Very High)']
wallet_features['score_range'] = pd.cut(
    wallet_features['final_credit_score'], bins=bins, labels=labels, right=False, include_lowest=True)

# Key features to analyze averages for
analysis_features = [
    'total_transactions', 'activity_duration_days', 'num_unique_assets',
    'total_deposit_value', 'total_borrow_value', 'total_repay_value',
    'repay_ratio', 'borrow_to_deposit_ratio', 'liquidation_call_count',
    'was_liquidated', 'net_borrow_value'
]

# Calculate mean values for each score range
avg_features_by_range = wallet_features.groupby(
    'score_range')[analysis_features].mean()

# Calculate count and percentage of wallets in each range
score_range_counts = wallet_features['score_range'].value_counts(sort=False)
score_range_percentages = wallet_features['score_range'].value_counts(
    sort=False, normalize=True) * 100

print("\n--- Score Range Summary ---")
for label in labels:
    count = score_range_counts.get(label, 0)
    percentage = score_range_percentages.get(label, 0.0)
    print(f"Range {label}: {count} wallets ({percentage:.2f}%)")

print("\n--- Average Feature Values by Score Range ---")
print(avg_features_by_range)

# --- Example Wallets ---
print("\n--- Example Wallets from Different Score Ranges ---")

# Function to safely get a sample wallet for a range


def get_sample_wallet(df_features, score_range_label):
    sample_wallets = df_features[df_features['score_range']
                                 == score_range_label]
    if not sample_wallets.empty:
        return sample_wallets.sample(min(3, len(sample_wallets)), random_state=42)[analysis_features + ['final_credit_score']]
    return pd.DataFrame()  # Return empty DataFrame if no wallets in range


# Low Score Examples
low_score_examples = get_sample_wallet(wallet_features, '0-200 (Very Low)')
if not low_score_examples.empty:
    print("\nExample Wallets from '0-200 (Very Low)' Score Range:")
    print(low_score_examples)
else:
    print("\nNo wallets found in '0-200 (Very Low)' range to display examples.")

# High Score Examples
high_score_examples = get_sample_wallet(
    wallet_features, '801-1000 (Very High)')
if not high_score_examples.empty:
    print("\nExample Wallets from '801-1000 (Very High)' Score Range:")
    print(high_score_examples)
else:
    print("\nNo wallets found in '801-1000 (Very High)' range to display examples.")

print("\nAnalysis script finished. Please use the output to fill your analysis.md.")
