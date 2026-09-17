import os
import json
from datetime import datetime
from finance_manager import FinanceManager
from currency_converter import CurrencyConverter

def clear_screen():
    """Clear the console screen based on the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("=" * 50)
    print("PERSONAL FINANCE MANAGEMENT SYSTEM")
    print("=" * 50)
    
    # Currency selection
    currency_converter = CurrencyConverter()
    available_currencies = currency_converter.get_available_currencies()
    
    print("\nAvailable currencies:")
    for i, (code, name) in enumerate(available_currencies.items(), 1):
        print(f"{i}. {code} - {name}")
    
    selected_currency = None
    while selected_currency is None:
        try:
            choice = input("\nSelect your preferred currency (enter the number): ")
            idx = int(choice) - 1
            if 0 <= idx < len(available_currencies):
                selected_currency = list(available_currencies.keys())[idx]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Initialize finance manager with selected currency
    finance_manager = FinanceManager(selected_currency)
    
    while True:
        clear_screen()
        print(f"\nPersonal Finance Manager - Currency: {selected_currency}")
        print("=" * 50)
        print("1. Add income")
        print("2. Add expense")
        print("3. View balance")
        print("4. View transaction history")
        print("5. View monthly report")
        print("6. View category-wise expenses")
        print("7. Change currency")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == '1':
            amount = float(input("Enter amount: "))
            category = input("Enter category (e.g., Salary, Freelance): ")
            description = input("Enter description: ")
            finance_manager.add_income(amount, category, description)
            input("\nIncome added successfully! Press Enter to continue...")
            
        elif choice == '2':
            amount = float(input("Enter amount: "))
            category = input("Enter category (e.g., Food, Transport): ")
            description = input("Enter description: ")
            finance_manager.add_expense(amount, category, description)
            input("\nExpense added successfully! Press Enter to continue...")
            
        elif choice == '3':
            balance = finance_manager.get_balance()
            print(f"\nCurrent Balance: {balance} {selected_currency}")
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            transactions = finance_manager.get_transactions()
            if not transactions:
                print("\nNo transactions found.")
            else:
                print("\nTransaction History:")
                print("-" * 80)
                print(f"{'Date':<12} {'Type':<10} {'Amount':<12} {'Category':<15} {'Description':<30}")
                print("-" * 80)
                for t in transactions:
                    amount_str = f"{t['amount']} {selected_currency}"
                    print(f"{t['date']:<12} {t['type']:<10} {amount_str:<12} {t['category']:<15} {t['description']:<30}")
            input("\nPress Enter to continue...")
            
        elif choice == '5':
            year = input("Enter year (YYYY): ")
            month = input("Enter month (MM): ")
            try:
                report = finance_manager.get_monthly_report(year, month)
                print(f"\nMonthly Report for {month}/{year}:")
                print(f"Total Income: {report['total_income']} {selected_currency}")
                print(f"Total Expenses: {report['total_expenses']} {selected_currency}")
                print(f"Net Savings: {report['savings']} {selected_currency}")
            except ValueError as e:
                print(f"\nError: {e}")
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            expenses_by_category = finance_manager.get_expenses_by_category()
            if not expenses_by_category:
                print("\nNo expense data found.")
            else:
                print("\nExpenses by Category:")
                print("-" * 40)
                for category, amount in expenses_by_category.items():
                    print(f"{category:<20} {amount} {selected_currency}")
            input("\nPress Enter to continue...")
            
        elif choice == '7':
            # Currency changing functionality
            print("\nAvailable currencies:")
            for i, (code, name) in enumerate(available_currencies.items(), 1):
                print(f"{i}. {code} - {name}")
            
            new_currency = None
            while new_currency is None:
                try:
                    choice = input("\nSelect new currency (enter the number): ")
                    idx = int(choice) - 1
                    if 0 <= idx < len(available_currencies):
                        new_currency = list(available_currencies.keys())[idx]
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
            if new_currency != selected_currency:
                finance_manager.change_currency(new_currency, currency_converter)
                selected_currency = new_currency
                print(f"\nCurrency changed to {selected_currency}")
            else:
                print("\nYou selected the same currency.")
            input("Press Enter to continue...")
            
        elif choice == '8':
            print("\nThank you for using the Personal Finance Manager!")
            break
            
        else:
            input("\nInvalid choice. Press Enter to try again...")

if __name__ == "__main__":
    main() 