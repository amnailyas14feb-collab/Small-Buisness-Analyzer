# Small Business Supply and Cash Flow Analyzer 💰

A comprehensive, interactive tool designed for small businesses to monitor sales, manage inventory, and analyze financial health. Built with Python and Streamlit, this application provides data-driven insights to optimize business operations.

## 🔗 Live Demo
Check out the live application here: **[Small Business Analyzer](https://small-buisness-analyzer-2026.streamlit.app/)**

## 🚀 Key Features

### 1. Executive Dashboard
- **Top-Level Metrics**: View Filtered Revenue, Best Cash Inflow sources, Active Products, and Average Customer Ratings.
- **Seasonal Analysis**: Visualize revenue distribution across different seasons.
- **Category Insights**: Understand which product categories are driving sales.
- **Customer Deep-Dive**: Analyze payment method usage and customer age distribution.

### 2. Inventory Explorer
- **Stock Summary**: Track total units sold, revenue generated per item, and average unit prices.
- **Product Deep Dive**: Get detailed performance metrics for specific items in your inventory.

### 3. Financial Analytics
- **Profitability Tracking**: Monitor total revenue, estimated Cost of Goods Sold (COGS), and total profit margins.
- **Efficiency Analysis**: Identify "Costly vs. Return" products (high price but low volume) to optimize stock.
- **Cash Flow Sources**: Visualize the top products contributing to your cash inflow.

### 4. Operations Center
- **Transaction Recording**: Log new sales directly into the SQLite database.
- **Inventory Integration**: Automatically updates stock levels and creates new inventory entries for new items.
- **Data Export**: Generate and download filtered transaction reports in CSV format.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Matplotlib, Seaborn
- **Database**: SQLite3
- **Language**: Python 3.x

## 📁 Project Structure

- `app.py`: The main Streamlit application entry point.
- `finance_engine.py`: Core logic for data models, database management, and business calculations.
- `Visualizer.py`: Custom visualization module for generating charts and graphs.
- `check_data.py`: Utility script to quickly inspect the SQLite database tables.
- `store_sales.csv`: Initial dataset for sales analysis.
- `finance_analyzer.db`: SQLite database storing inventory and transaction records.

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Finance_project
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🖥️ Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Navigate the Dashboard**:
   - Use the **Control Panel** in the sidebar to switch between different analysis modules.
   - Adjust the **Revenue Weightage Threshold** to filter out low-impact products from your core analysis.
   - Apply **Global Filters** for specific categories or seasons.

3. **Record a Sale**:
   - Go to the **Operations Center**.
   - Fill in the item name, quantity, and price.
   - Submit to update the database and inventory levels.

4. **Verify Data**:
   - Run the check utility to see raw database entries:
     ```bash
     python check_data.py
     ```

## 📊 Data Requirements

The application expects a `store_sales.csv` file with the following columns:
- `CustomerID`, `Age`, `Gender`, `Category`, `ItemPurchased`, `Amount`, `Season`, `PaymentMethod`, `ItemRating`.

---
*Developed for Small Business Financial Optimization.*
