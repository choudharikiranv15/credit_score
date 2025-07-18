# 🏦 DeFi Wallet Credit Scoring with Aave V2 Data

This project computes and analyzes credit scores of DeFi wallets based on their interaction with the Aave V2 lending protocol. It uses behavioral features such as deposits, repayments, borrowings, and liquidations to assign risk-based credit scores.

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/github/license/choudharikiranv15/credit_score)

---

## 📌 Table of Contents

- [📊 Problem Statement](#-problem-statement)
- [🚀 Features](#-features)
- [🛠 Tech Stack](#-tech-stack)
- [⚙️ Installation](#-installation)
- [▶️ Usage](#-usage)
- [📁 Project Structure](#-project-structure)
- [📈 Results](#-results)
- [🧠 Future Improvements](#-future-improvements)
- [📄 License](#-license)

---

## 📊 Problem Statement

DeFi platforms lack traditional credit scoring mechanisms. This project proposes a decentralized credit scoring approach using DeFi on-chain activity, particularly from Aave V2, to assess the risk profile of wallets without relying on centralized data.

---

## 🚀 Features

- ✅ Extracts and processes wallet data from Aave V2
- 📈 Calculates credit scores based on financial behavior
- 🔎 Analyzes score distribution and wallet activity
- 📊 Visualizes score statistics
- 💾 Exports output to `wallet_scores.csv`

---

## 🛠 Tech Stack

- **Python 3.11**
- **Pandas**, **NumPy** – data handling
- **Matplotlib**, **Seaborn** – visualizations
- **Scikit-learn** – normalization and scaling

---

## ⚙️ Installation

1. **Clone the repository**

```bash
git clone https://github.com/choudharikiranv15/credit_score.git
cd credit_score
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the main script to generate credit scores:

```bash
python main.py
```

- This reads wallet data from `aave_wallet_data.csv`
- Processes and calculates a `credit_score` for each wallet
- Saves the results to `wallet_scores.csv`
- Also generates a score distribution plot as `credit_score_distribution.png`

---

## 📁 Project Structure

```plaintext
credit_score/
│
├── main.py                      # Main script to compute credit scores
├── aave_wallet_data.csv         # Raw wallet transaction data
├── wallet_scores.csv            # Output file with wallet addresses and scores
├── credit_score_distribution.png  # Score distribution plot
│
├── readme.md                    # Project documentation
├── analysis.md                  # In-depth analysis & visual insights
├── requirements.txt             # Python dependencies
```

### 🔍 Explanation of Key Files

- **main.py** – contains logic to clean, process, and score wallets.
- **aave_wallet_data.csv** – input dataset with wallet stats like total_deposits, borrows, etc.
- **wallet_scores.csv** – final output with wallet addresses and their calculated credit scores.
- **credit_score_distribution.png** – histogram plot showing how scores are distributed across wallets.
- **analysis.md** – detailed insights, observations, and recommendations based on the results.

---

## 📈 Results

After running the code:

- A new file named `wallet_scores.csv` will be created, with two columns:
  - `wallet_address`
  - `credit_score` (between 300 to 850)

Example:

```
wallet_address        credit_score
0xabc...123           745
0xdef...456           580
```

- A histogram showing the score distribution will be saved as:

```plaintext
credit_score_distribution.png
```

- For detailed visual and statistical analysis, refer to:
  👉 [`analysis.md`](analysis.md)

---

## 🧠 Future Improvements

- Add real-time Aave data extraction using The Graph or API
- Use supervised ML models to classify risk categories
- Include wallet metadata and token holdings
- Deploy as a web dashboard with wallet lookup

---

## 📄 License

This project is licensed under the MIT License.
