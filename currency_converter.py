import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self):
        self.cache_file = "currency_rates.json"
        self.cache_expiry_hours = 24  # Cache expiry time in hours
        self.base_currencies = {
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
        self.rates = self._load_rates()
        
    def _load_rates(self):
        """Load exchange rates from cache or fetch new rates if cache is expired."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as file:
                cache = json.load(file)
                
            # Check if cache is expired
            last_updated = datetime.fromisoformat(cache["timestamp"])
            now = datetime.now()
            hours_diff = (now - last_updated).total_seconds() / 3600
            
            if hours_diff < self.cache_expiry_hours:
                return cache["rates"]
                
        # Fetch new rates if cache doesn't exist or is expired
        return self._fetch_rates()
        
    def _fetch_rates(self):
        """Fetch the latest exchange rates from a public API."""
        try:
            # Using a free, no-API-key required service for demonstration
            response = requests.get("https://open.er-api.com/v6/latest/USD")
            data = response.json()
            
            if data["result"] == "success":
                # Save to cache
                cache = {
                    "timestamp": datetime.now().isoformat(),
                    "rates": data["rates"]
                }
                
                with open(self.cache_file, 'w') as file:
                    json.dump(cache, file, indent=4)
                    
                return data["rates"]
            else:
                # If API call fails, return hardcoded rates
                return self._get_fallback_rates()
        except Exception:
            # If there's any error with the API, use fallback rates
            return self._get_fallback_rates()
            
    def _get_fallback_rates(self):
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
        
    def get_available_currencies(self):
        """Return a dictionary of available currencies with their codes and names."""
        return self.base_currencies
        
    def get_conversion_rate(self, from_currency, to_currency):
        """Get the conversion rate from one currency to another."""
        if from_currency == to_currency:
            return 1.0
            
        # Get USD rate for both currencies
        if from_currency not in self.rates or to_currency not in self.rates:
            raise ValueError(f"Currency not supported: {from_currency if from_currency not in self.rates else to_currency}")
            
        # Calculate conversion rate (via USD)
        if from_currency == "USD":
            return self.rates[to_currency]
        elif to_currency == "USD":
            return 1 / self.rates[from_currency]
        else:
            # Convert via USD
            return self.rates[to_currency] / self.rates[from_currency]
            
    def convert(self, amount, from_currency, to_currency):
        """Convert an amount from one currency to another."""
        conversion_rate = self.get_conversion_rate(from_currency, to_currency)
        return round(amount * conversion_rate, 2) 