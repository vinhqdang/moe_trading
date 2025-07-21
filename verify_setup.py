#!/usr/bin/env python3
"""
MOE Trading System - Setup Verification Script
This script checks if all required packages are installed and API keys are set up.
"""

import sys
import os
import json
import importlib

# ANSI colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
END = '\033[0m'

def check_package(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        print(f"{GREEN}✓{END} {package_name} is installed")
        return True
    except ImportError:
        print(f"{RED}✗{END} {package_name} is NOT installed")
        return False

def check_config():
    """Check if config.json exists and API keys are set."""
    if not os.path.exists("config.json"):
        if os.path.exists("config.json.example"):
            print(f"{YELLOW}⚠{END} config.json does not exist, but config.json.example found")
            print(f"    Run: cp config.json.example config.json and add your API keys")
        else:
            print(f"{RED}✗{END} config.json and config.json.example do not exist")
        return False
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        openai_key = config.get("openai_api_key")
        gemini_key = config.get("gemini_api_key")
        
        if not openai_key or openai_key == "your_openai_api_key_here":
            print(f"{YELLOW}⚠{END} OpenAI API key is missing or not set")
            return False
            
        if not gemini_key or gemini_key == "your_gemini_api_key_here":
            print(f"{YELLOW}⚠{END} Gemini API key is missing or not set")
            return False
            
        print(f"{GREEN}✓{END} API keys are configured")
        return True
    except Exception as e:
        print(f"{RED}✗{END} Error reading config.json: {e}")
        return False

def check_files():
    """Check if required files exist."""
    required_files = [
        "expert.py", "strategies.py", "meeting.py", "backtester.py", "main.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"{RED}✗{END} Missing required files: {', '.join(missing_files)}")
        return False
    else:
        print(f"{GREEN}✓{END} All required files exist")
        return True

def main():
    """Run all checks."""
    print(f"{YELLOW}MOE Trading System - Setup Verification{END}")
    print("-" * 40)
    
    # Check required packages
    print("\nChecking required packages:")
    packages = ["pandas", "numpy", "openai", "google.generativeai", "yfinance", "matplotlib"]
    missing_packages = []
    
    for package in packages:
        if not check_package(package):
            missing_packages.append(package)
    
    # Check config
    print("\nChecking configuration:")
    config_ok = check_config()
    
    # Check files
    print("\nChecking required files:")
    files_ok = check_files()
    
    # Summary
    print("\n" + "-" * 40)
    if missing_packages:
        print(f"{RED}Missing packages:{END} {', '.join(missing_packages)}")
        print(f"Install with: pip install {' '.join(missing_packages)}")
    
    if not config_ok:
        print(f"{YELLOW}Please update your API keys in config.json{END}")
    
    if not files_ok:
        print(f"{RED}Some required files are missing. Please check your installation.{END}")
    
    if not missing_packages and config_ok and files_ok:
        print(f"{GREEN}All checks passed! Your MOE Trading System is ready to use.{END}")
        print(f"\nRun the system with: {YELLOW}python main.py{END}")
    else:
        print(f"\n{YELLOW}Please fix the issues above to use the MOE Trading System.{END}")

if __name__ == "__main__":
    main()