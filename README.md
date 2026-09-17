# Personal Finance Manager - Web Application

A comprehensive personal finance management web application built as a college mini project. This application helps users manage their finances by tracking income, expenses, and providing insights through reports and visualizations.

## Features

- **User Authentication**: Secure registration and login system
- **Multi-currency Support**: Choose your preferred currency and change it anytime
- **Transaction Management**: Add, view, and track income and expenses
- **Dashboard**: Visual overview of your financial status with charts and summaries
- **Reports**: Monthly financial reports and spending analysis
- **Responsive Design**: Works well on desktop and mobile devices
- **Real-time Currency Exchange**: Up-to-date currency conversion rates

## Technologies Used

### Backend
- **Python** (3.8+)
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database (easily configurable to other databases)

### Frontend
- **HTML5 / CSS3 / JavaScript**
- **Bootstrap 5**: Responsive design framework
- **Chart.js**: Interactive charts and visualizations

### External APIs
- Exchange Rate API for currency conversion

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd personal-finance-manager
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the application:
```
python app.py
```

5. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Project Structure

```
personal-finance-manager/
├── app.py                  # Main application file
├── currency_utils.py       # Currency utilities
├── requirements.txt        # Dependencies
├── static/                 # Static files
│   ├── css/
│   │   └── styles.css      # Custom styles
│   └── js/
│       └── main.js         # Custom JavaScript
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # Dashboard
│   ├── add_transaction.html # Add transaction form
│   ├── transactions.html   # Transaction history
│   ├── reports.html        # Financial reports
│   └── change_currency.html # Currency settings
└── README.md               # This file
```

## Database Schema

- **Users Table**: Stores user information and preferences
  - id, username, email, password_hash, preferred_currency

- **Transactions Table**: Stores financial transactions
  - id, user_id, amount, type, category, description, date

## Usage Guide

1. **Register** a new account and select your preferred currency
2. **Login** to access your personal dashboard
3. **Add transactions** (income or expenses) with categories and descriptions
4. **View reports** to analyze your spending patterns
5. **Change currency** if needed, with automatic conversion of all amounts

## Contributing

This is a college mini project. For educational purposes only.

## License

This project is available for educational purposes. Feel free to use it for learning web development and personal finance management concepts. 

## database info showing
locate to directly = cd "C:\Users\Aditya Sagar\OneDrive\Desktop\important\miniproject1\mini project"
run this  = python show_db.py