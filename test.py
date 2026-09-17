from currency_converter import CurrencyConverter
from finance_manager import FinanceManager
import os

def test_currency_converter():
    print("Testing CurrencyConverter...")
    converter = CurrencyConverter()
    
    # Test getting available currencies
    currencies = converter.get_available_currencies()
    print(f"Available currencies: {len(currencies)}")
    
    # Test conversion rates
    usd_to_eur = converter.get_conversion_rate("USD", "EUR")
    print(f"USD to EUR rate: {usd_to_eur}")
    
    # Test amount conversion
    amount_usd = 100
    amount_eur = converter.convert(amount_usd, "USD", "EUR")
    print(f"{amount_usd} USD = {amount_eur} EUR")
    
    print("CurrencyConverter tests completed.\n")

def test_finance_manager():
    print("Testing FinanceManager...")
    
    # Clean up any existing test data
    if os.path.exists("test_finance_data.json"):
        os.remove("test_finance_data.json")
    
    # Create a finance manager with test data file
    fm = FinanceManager("USD")
    fm.data_file = "test_finance_data.json"
    fm.data = fm._create_new_data()
    
    # Test adding transactions
    print("Adding sample transactions...")
    fm.add_income(1000, "Salary", "Monthly salary")
    fm.add_income(500, "Freelance", "Client project")
    fm.add_expense(200, "Food", "Groceries")
    fm.add_expense(150, "Transport", "Gas")
    fm.add_expense(50, "Entertainment", "Movie tickets")
    
    # Test getting balance
    balance = fm.get_balance()
    print(f"Current balance: {balance} USD")
    
    # Test getting expenses by category
    expenses = fm.get_expenses_by_category()
    print("Expenses by category:")
    for category, amount in expenses.items():
        print(f"  {category}: {amount} USD")
    
    # Clean up test data
    if os.path.exists("test_finance_data.json"):
        os.remove("test_finance_data.json")
    
    print("FinanceManager tests completed.")

if __name__ == "__main__":
    print("=== Running tests for Personal Finance Manager ===\n")
    
    test_currency_converter()
    test_finance_manager()
    
    print("\n=== All tests completed ===") 