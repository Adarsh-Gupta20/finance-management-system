import requests
import json
import os
from datetime import datetime

# Cache file for exchange rates
CACHE_FILE = 'currency_rates.json'
CACHE_EXPIRY_HOURS = 24

# Currency list
CURRENCIES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",
    "INR": "Indian Rupee",
    "MXN": "Mexican Peso",
    "BRL": "Brazilian Real",
    "ZAR": "South African Rand",
    "SGD": "Singapore Dollar"
}

def get_currency_list():
    """Return a dictionary of available currencies with their codes and names."""
    return CURRENCIES

def _load_rates():
    """Load exchange rates from cache or fetch new rates if cache is expired."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as file:
                cache = json.load(file)
                
            # Check if cache is expired
            last_updated = datetime.fromisoformat(cache["timestamp"])
            now = datetime.now()
            hours_diff = (now - last_updated).total_seconds() / 3600
            
            if hours_diff < CACHE_EXPIRY_HOURS:
                return cache["rates"]
        except (json.JSONDecodeError, KeyError, ValueError):
            # If cache is corrupted, fetch new rates
            pass
                
    # Fetch new rates if cache doesn't exist or is expired
    return _fetch_rates()

def _fetch_rates():
    """Fetch the latest exchange rates from a public API."""
    try:
        # Using a free, no-API-key required service for demonstration
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        data = response.json()
        
        if data.get("result") == "success":
            # Save to cache
            cache = {
                "timestamp": datetime.now().isoformat(),
                "rates": data["rates"]
            }
            
            with open(CACHE_FILE, 'w') as file:
                json.dump(cache, file, indent=4)
                
            return data["rates"]
    except Exception:
        pass
        
    # If API call fails, return hardcoded rates
    return _get_fallback_rates()

def _get_fallback_rates():
    """Return hardcoded exchange rates as a fallback."""
    # These rates are fixed and might not be accurate
    return {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 149.82,
        "AUD": 1.52,
        "CAD": 1.36,
        "CHF": 0.91,
        "CNY": 7.22,
        "INR": 83.42,
        "MXN": 16.87,
        "BRL": 5.05,
        "ZAR": 18.37,
        "SGD": 1.34
    }

def get_exchange_rate(from_currency, to_currency):
    """Get the conversion rate from one currency to another."""
    if from_currency == to_currency:
        return 1.0
        
    # Get rates (USD is base)
    rates = _load_rates()
    
    # Check if currencies are supported
    if from_currency not in rates or to_currency not in rates:
        raise ValueError(f"Currency not supported: {from_currency if from_currency not in rates else to_currency}")
        
    # Calculate conversion rate (via USD)
    if from_currency == "USD":
        return rates[to_currency]
    elif to_currency == "USD":
        return 1 / rates[from_currency]
    else:
        # Convert via USD
        return rates[to_currency] / rates[from_currency]

def convert_amount(amount, from_currency, to_currency):
    """Convert an amount from one currency to another."""
    conversion_rate = get_exchange_rate(from_currency, to_currency)
    return round(amount * conversion_rate, 2) 