import os
import json
from datetime import datetime

class FinanceManager:
    def __init__(self, currency):
        self.currency = currency
        self.data_file = "finance_data.json"
        self.data = self._load_data()
        
    def _load_data(self):
        """Load finance data from the JSON file or create a new data structure."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                # If the file is corrupted, create new data
                return self._create_new_data()
        else:
            return self._create_new_data()
            
    def _create_new_data(self):
        """Create a new data structure for storing financial information."""
        return {
            "currency": self.currency,
            "transactions": []
        }
        
    def _save_data(self):
        """Save the finance data to the JSON file."""
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file, indent=4)
            
    def add_income(self, amount, category, description):
        """Add an income transaction."""
        if amount <= 0:
            raise ValueError("Income amount must be positive")
            
        transaction = {
            "type": "income",
            "amount": amount,
            "category": category,
            "description": description,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.data["transactions"].append(transaction)
        self._save_data()
        
    def add_expense(self, amount, category, description):
        """Add an expense transaction."""
        if amount <= 0:
            raise ValueError("Expense amount must be positive")
            
        transaction = {
            "type": "expense",
            "amount": amount,
            "category": category,
            "description": description,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.data["transactions"].append(transaction)
        self._save_data()
        
    def get_balance(self):
        """Calculate and return the current balance."""
        total_income = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "income")
        total_expenses = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "expense")
        return round(total_income - total_expenses, 2)
        
    def get_transactions(self):
        """Return all transactions, sorted by date (newest first)."""
        return sorted(self.data["transactions"], key=lambda t: t["date"], reverse=True)
        
    def get_monthly_report(self, year, month):
        """Generate a monthly report of income, expenses, and savings."""
        try:
            year = int(year)
            month = int(month)
            if not (1 <= month <= 12 and year >= 2000):
                raise ValueError("Invalid year or month")
        except ValueError:
            raise ValueError("Year and month must be valid numbers")
            
        # Format the date prefix for comparison
        date_prefix = f"{year:04d}-{month:02d}"
        
        # Filter transactions for the given month
        monthly_transactions = [t for t in self.data["transactions"] if t["date"].startswith(date_prefix)]
        
        # Calculate totals
        total_income = sum(t["amount"] for t in monthly_transactions if t["type"] == "income")
        total_expenses = sum(t["amount"] for t in monthly_transactions if t["type"] == "expense")
        savings = total_income - total_expenses
        
        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "savings": round(savings, 2),
            "transactions": monthly_transactions
        }
        
    def get_expenses_by_category(self):
        """Calculate and return expenses grouped by category."""
        categories = {}
        for t in self.data["transactions"]:
            if t["type"] == "expense":
                if t["category"] in categories:
                    categories[t["category"]] += t["amount"]
                else:
                    categories[t["category"]] = t["amount"]
                    
        # Round all values to 2 decimal places
        return {category: round(amount, 2) for category, amount in categories.items()}
        
    def change_currency(self, new_currency, currency_converter):
        """Change the currency of all transactions."""
        old_currency = self.data["currency"]
        conversion_rate = currency_converter.get_conversion_rate(old_currency, new_currency)
        
        # Update all transaction amounts
        for transaction in self.data["transactions"]:
            transaction["amount"] = round(transaction["amount"] * conversion_rate, 2)
            
        # Update the currency
        self.currency = new_currency
        self.data["currency"] = new_currency
        
        # Save the updated data
        self._save_data() 