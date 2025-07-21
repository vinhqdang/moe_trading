import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def get_spy_returns(start_date, end_date):
    """Get S&P 500 returns for a specific date range."""
    try:
        spy_data = yf.download("SPY", start=start_date, end=end_date)
        if len(spy_data) < 2:
            print(f"Not enough SPY data between {start_date} and {end_date}")
            return 0.0
        first_price = float(spy_data['Close'].iloc[0])
        last_price = float(spy_data['Close'].iloc[-1])
        return (last_price / first_price) - 1
    except Exception as e:
        print(f"Error getting SPY data: {e}")
        return 0.0

def load_moe_results():
    """Load MOE results from the summary file."""
    try:
        with open("moe_summary_results.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading MOE results: {e}")
        return {}

def compare_performance():
    """Compare MOE performance with S&P 500."""
    moe_results = load_moe_results()
    
    if not moe_results:
        print("No MOE results found")
        return
    
    # Get MOE performance
    round_performances = moe_results.get("round_performances", [])
    if not round_performances:
        print("No round performances found")
        return
    
    # Get run timestamp
    run_timestamp = moe_results.get("run_timestamp")
    if not run_timestamp:
        run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    run_date = datetime.strptime(run_timestamp.split(" ")[0], "%Y-%m-%d")
    
    # Get config
    config = moe_results.get("config", {})
    test_days = config.get("test_duration_days", 10)
    
    # Calculate SPY returns for each round
    spy_returns = []
    
    # Dates from backtest results
    backtest_files = [f"backtest_results_round{i+1}.json" for i in range(len(round_performances))]
    
    for i, file in enumerate(backtest_files):
        try:
            with open(file, "r") as f:
                backtest = json.load(f)
                start_date = backtest.get("start_date")
                end_date = backtest.get("end_date")
                if start_date and end_date:
                    spy_return = get_spy_returns(start_date, end_date)
                    spy_returns.append(spy_return)
                else:
                    print(f"No dates found in {file}")
                    spy_returns.append(0.0)
        except Exception as e:
            print(f"Error loading {file}: {e}")
            spy_returns.append(0.0)
    
    # If no backtest files, use estimated dates
    if len(spy_returns) == 0:
        base_date = run_date - timedelta(days=test_days*len(round_performances))
        for i in range(len(round_performances)):
            start_date = (base_date + timedelta(days=i*test_days)).strftime("%Y-%m-%d")
            end_date = (base_date + timedelta(days=(i+1)*test_days)).strftime("%Y-%m-%d")
            spy_return = get_spy_returns(start_date, end_date)
            spy_returns.append(spy_return)
    
    # Print summary
    print("\nPerformance Summary:")
    print(f"{'Round':<10} {'MOE':<10} {'S&P 500':<10} {'Difference':<10}")
    print("-" * 40)
    
    for i in range(len(round_performances)):
        moe_return = round_performances[i]
        spy_return = spy_returns[i] if i < len(spy_returns) else 0.0
        diff = moe_return - spy_return
        print(f"{i+1:<10} {moe_return:.2%} {spy_return:.2%} {diff:.2%}")
    
    print("-" * 40)
    avg_moe = sum(round_performances) / len(round_performances)
    avg_spy = sum(spy_returns) / len(spy_returns) if spy_returns else 0.0
    print(f"{'Average':<10} {avg_moe:.2%} {avg_spy:.2%} {avg_moe - avg_spy:.2%}")
    
    # Check for improvement in MOE performance
    if len(round_performances) > 1:
        print("\nMOE Learning Progress:")
        for i in range(1, len(round_performances)):
            change = round_performances[i] - round_performances[i-1]
            print(f"Round {i} to {i+1}: {change:.2%} change in performance")

if __name__ == "__main__":
    compare_performance()