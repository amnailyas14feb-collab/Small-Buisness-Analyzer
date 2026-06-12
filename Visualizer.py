#Visualizer.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Visualizer:
    def __init__(self, cf_manager=None):
        self.cf_manager = cf_manager

    def plot_sales_by_season(self, df):
        if df.empty or 'Season' not in df.columns:
            return None
        
        seasonal_sales = df.groupby('Season')['Revenue'].sum().reindex(['Spring', 'Summer', 'Autumn', 'Winter']).fillna(0)
        fig, ax = plt.subplots(figsize=(10, 6))
        seasonal_sales.plot(kind='bar', color=['#2ecc71', '#f1c40f', '#e67e22', '#3498db'], ax=ax)
        ax.set_title("Total Revenue by Season", fontsize=14, pad=20)
        ax.set_xlabel("Season")
        ax.set_ylabel("Total Revenue ($)")
        plt.xticks(rotation=0)
        plt.tight_layout()
        return fig

    def plot_product_categories(self, df):
        if df.empty or 'Category' not in df.columns:
            return None
        counts = df["Category"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        counts.plot(kind="bar", color='#2ecc71', ax=ax)
        ax.set_title("Sales by Category", fontsize=14, pad=20)
        ax.set_xlabel("Category")
        ax.set_ylabel("Number of Sales")
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    def plot_product_weightage(self, df, top_n=10):
        if df.empty:
            return None
        # Calculate weightage if not present
        if 'weightage' not in df.columns:
            total_rev = df['Revenue'].sum()
            product_rev = df.groupby('Description')['Revenue'].sum().reset_index()
            product_rev['weightage'] = (product_rev['Revenue'] / total_rev) * 100
            df_viz = product_rev.sort_values("weightage", ascending=False).head(top_n)
        else:
            df_viz = df.sort_values("weightage", ascending=False).head(top_n)
            
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="weightage", y="Description" if "Description" in df_viz.columns else "product_name", data=df_viz, palette='viridis', ax=ax)
        ax.set_title(f"Top {top_n} Products by Revenue Weightage", fontsize=14, pad=20)
        ax.set_xlabel("Revenue Contribution (%)")
        ax.set_ylabel("Product Name")
        plt.tight_layout()
        return fig

    def plot_payment_methods(self, df):
        if df.empty or 'PaymentMethod' not in df.columns or 'Revenue' not in df.columns:
            return None
        
        # Calculate Total Revenue per Payment Method (More useful for business)
        revenue_data = df.groupby('PaymentMethod')['Revenue'].sum().sort_values(ascending=False)
        labels = revenue_data.index
        values = revenue_data.values
        total_revenue = values.sum()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # High Contrast Colors: Business Blue and Success Green
        colors = ['#1f77b4', '#2ca02c'] 
        
        # Percentage formatting function
        def func(pct, allvals):
            absolute = pct/100.*sum(allvals)
            return f"{pct:.1f}%\n(${absolute:,.0f})"

        # Plotting
        wedges, texts, autotexts = ax.pie(
            values, 
            autopct=lambda pct: func(pct, values),
            textprops=dict(color="w", fontsize=12, weight="bold"),
            colors=colors,
            startangle=140,
            pctdistance=0.75,
            explode=[0.05] * len(values),
            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
        )

        # Add a clear Legend
        ax.legend(wedges, labels,
                  title="Payment Methods",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=12)

        ax.set_title("Revenue Share by Payment Method", fontsize=16, pad=20, weight='bold')
        ax.axis('equal')  
        
        plt.tight_layout()
        return fig
