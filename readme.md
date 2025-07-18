DeFi Wallet Credit Scoring
Project Overview
This project addresses the challenge of assigning a credit score to decentralized finance (DeFi) wallets based solely on their historical transaction behavior within the Aave V2 protocol. The objective is to develop a robust system that identifies reliable and responsible wallet usage, distinguishing it from risky, bot-like, or exploitative activities, and quantifies this behavior with a score ranging from 0 to 1000.

Problem Statement
As provided by Zeru Finance, the core problem is to evaluate the creditworthiness of DeFi wallets using transaction-level data from the Aave V2 protocol. Each transaction record corresponds to a wallet's interaction with the protocol (e.g., deposit, borrow, repay, redeemunderlying, liquidationcall). The final output should be a credit score (0-1000) for each unique wallet, where higher scores indicate more reliable behavior.

Methodology and Architecture
The solution is implemented as a one-step Python script (main.py) that handles data ingestion, preprocessing, feature engineering, and credit score calculation.

1. Data Acquisition
   The raw transaction-level data (approximately 100K records from the Aave V2 protocol on Polygon network) was sourced from the provided Google Drive link. For efficiency, the compressed ZIP file was downloaded and extracted.

Raw Data Source: https://drive.google.com/file/d/1ISFbAXxadMrt7ZI96rmzzzZmEKZnyW7FS/view?usp=sharing

Compressed ZIP (Used): https://drive.google.com/file/d/14ceBCLQ-BTCydDrFJauVA_PKAZ7VtDor/view?usp=sharing

The extracted file is named user-wallet-transactions.json.

2. Data Preprocessing
   The initial JSON data required several cleaning and flattening steps to make it suitable for analysis and feature engineering:

JSON Normalization: Nested fields within the \_id, createdAt, updatedAt, and especially the actionData columns were flattened. pd.json_normalize() was used for actionData to extract details like amount, assetSymbol, assetPriceUSD, and other action-specific parameters into separate columns.

Column Renaming: The userWallet column was renamed to wallet_address for clarity and consistency. The amount column from actionData was renamed to amount_raw, and assetSymbol to asset_symbol.

Data Type Conversion:

createdAt and updatedAt fields were converted from nested dictionaries to UTC datetime objects.

The timestamp column (already datetime) was confirmed.

Crucially, amount_raw (representing token amounts in their smallest unit, e.g., wei) was converted to human-readable float values. This involved:

Identifying the asset_symbol for each transaction.

Using a predefined token_decimals mapping (e.g., WETH=18, USDC=6, WBTC=8, WPOL=18) to divide the raw integer amount by 10
textdecimals
.

Robust error handling ensured conversion even for irregular entries.

Other relevant numeric fields (e.g., assetPriceUSD, borrowRate, collateralAmount) were converted to float64 and NaN values were filled with 0.

3. Feature Engineering
   After preprocessing, the transaction-level data was aggregated to generate a comprehensive set of features for each unique wallet. These features aim to capture various aspects of a wallet's engagement and risk profile. The wallet_address column was used for groupby operations.

Key Features Engineered (per wallet):

total_transactions: Total number of unique transactions initiated by the wallet.

first_tx_date / last_tx_date: The earliest and latest transaction timestamps, respectively.

activity_duration_days: The total duration in days between the first and last transaction, indicating how long the wallet has been active.

num_unique_assets: The count of distinct crypto assets the wallet has interacted with (deposited, borrowed, repaid).

total_deposit_value: Sum of all deposited amounts across all assets (in human-readable values).

total_borrow_value: Sum of all borrowed amounts across all assets.

total_repay_value: Sum of all repaid amounts across all assets.

net_borrow_value: total_borrow_value - total_repay_value, indicating outstanding debt if positive.

deposit_count / borrow_count / repay_count: Number of each specific action type.

liquidation_call_count: Number of times the wallet was subject to a liquidation call. This is a critical indicator of risky behavior.

total_liquidation_amount: The total principal amount that was liquidated from the wallet.

total_collateral_liquidated: The total collateral amount that was liquidated from the wallet.

repay_ratio: total_repay_value / total_borrow_value. Capped at 1.0; a higher ratio indicates better repayment discipline. (If total_borrow_value is 0, this is 0).

borrow_to_deposit_ratio: total_borrow_value / total_deposit_value. Capped at 10.0 to handle edge cases with very small deposits; a higher ratio might indicate higher leverage. (If total_deposit_value is 0, this is 0).

was_liquidated: A binary flag (1 if liquidation_call_count > 0, else 0).

avg_tx_amount: Average transaction amount across deposits, borrows, and repays.

4. Credit Scoring Logic
   Given the absence of labeled data for "creditworthiness," a rule-based, weighted-sum approach was chosen for transparency and direct interpretability. The score ranges from 0 to 1000.

Base Score and Penalties/Rewards:

The scoring model starts with a base score and then adjusts it based on the engineered features:

Raw Score=Base Score−Penalties+Rewards
Base Score: 500 (A neutral starting point).

Penalties:

Liquidations (liquidation_call_count): Each liquidation event incurs a significant penalty.

Raw Score -= liquidation_call_count \* 100 (Example weight: -100 per liquidation)

High Leverage (borrow_to_deposit_ratio): Wallets taking excessive leverage are penalized.

Raw Score -= borrow_to_deposit_ratio \* 20 (Example weight: -20 per unit of ratio, capped at 10.0)

Rewards:

Repayment Discipline (repay_ratio): Wallets with good repayment habits are rewarded.

Raw Score += repay_ratio \* 200 (Example weight: +200 for a perfect repay ratio of 1.0)

Activity/Engagement (total_transactions): More active wallets generally receive a slight boost. A logarithmic scale is used to reduce the impact of extreme outliers.

Raw Score += \log(1 + \text{total_transactions}) \* 10

Total Deposits (total_deposit_value): Wallets with significant capital commitment are slightly rewarded (using a logarithmic scale).

Raw Score += \log(1 + \text{total_deposit_value}) \* 5

Normalization:

After applying all penalties and rewards, the raw scores can fall outside the 0-1000 range. To ensure the final score is within the required range, sklearn.preprocessing.MinMaxScaler is applied to the raw scores, scaling them linearly to fit between 0 and 1000. The final scores are then rounded to the nearest integer.

How to Run
To run the credit scoring script:

Clone the Repository:

Bash

git clone [Your GitHub Repo URL]
cd defi_credit_scoring
Create and Activate a Virtual Environment:

Bash

python -m venv venv

# On Windows:

.\venv\Scripts\activate

# On macOS/Linux:

source venv/bin/activate
Install Dependencies:

Bash

pip install -r requirements.txt
(Generate requirements.txt by running pip freeze > requirements.txt in your activated environment after installing pandas, numpy, and scikit-learn).

Place Data File:
Download the user-wallet-transactions.json file (from the compressed ZIP link above) and place it in the root directory of the project, next to main.py.

Run the Script:

Bash

python main.py
The script will print progress and final DataFrame information to the console. It will also generate a wallet_scores.csv file in the project directory, containing wallet_address and their final_credit_score.

Deliverables
main.py: The main Python script containing all the code for data processing, feature engineering, and credit scoring.

README.md: This document, explaining the project, methodology, and how to run the code.

analysis.md: (To be created separately) A detailed analysis of the score distribution and the behavior of wallets across different score ranges.

requirements.txt: A file listing all Python dependencies.

wallet_scores.csv: The output file generated by main.py, containing the final credit scores for each wallet.

Extensibility and Future Improvements
This foundational credit scoring model can be significantly expanded and refined:

More Advanced Feature Engineering:

Time-series features: Analyze trends over time (e.g., changes in debt-to-collateral ratio, frequency of transactions in recent periods).

Asset-specific metrics: Features for specific high-value or volatile assets.

Liquidity analysis: Features related to a wallet's ability to cover its positions.

External data: Incorporate data like gas fees paid, network congestion, or token price volatility.

Flash loan participation: A specific feature for wallets frequently engaging in flash loans, which can be benign or indicative of complex strategies.

Supervised Machine Learning: If labeled data (i.e., wallets explicitly marked as "good" or "bad" based on post-event behavior like defaults or successful liquidations) becomes available, a supervised model (e.g., Logistic Regression, Gradient Boosting, Neural Networks) could be trained for more accurate predictions.

Unsupervised Clustering Refinement: Use more sophisticated clustering algorithms (e.g., DBSCAN, HDBSCAN) or manifold learning (UMAP, t-SNE) for better identification of inherent groups within the wallet behavior, which could then inform score assignments.

Dynamic Scoring: Implement a system that updates scores periodically as new transactions occur.

Explainable AI (XAI): For production systems, integrate XAI techniques (e.g., SHAP, LIME) to explain why a particular wallet received a certain score, enhancing trust and auditability.

Optimization of Scoring Weights: Use optimization techniques (if a proxy for "ground truth" performance can be established) to automatically tune the weights for the rule-based system.

Technologies Used
Python 3.x
Pandas (for data manipulation and analysis)
NumPy (for numerical operations)
Scikit-learn (for MinMaxScaler)
