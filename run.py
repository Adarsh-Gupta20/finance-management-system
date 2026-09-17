#!/usr/bin/env python
"""
Run script for Personal Finance Manager web application
"""
from app import app

if __name__ == '__main__':
    print("Starting Personal Finance Manager Web Application...")
    print("Open your browser and navigate to: http://127.0.0.1:5000")
    app.run(debug=True) 