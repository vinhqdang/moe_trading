import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import argparse

def get_spy_returns(start_date, end_date):
    """Get S&P 500 returns for a specific date range."""
    try:
        spy_data = yf.download("SPY", start=start_date, end=end_date)
        if len(spy_data) < 2:
            print(f"Not enough SPY data between {start_date} and {end_date}")
            return 0.0
        first_price = spy_data['Close'].iloc[0]
        last_price = spy_data['Close'].iloc[-1]
        if isinstance(first_price, (pd.Series, np.ndarray)):
            first_price = first_price.item()
        if isinstance(last_price, (pd.Series, np.ndarray)):
            last_price = last_price.item()
        return float((last_price / first_price) - 1)
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
                    spy_returns.append(0)
        except Exception as e:
            print(f"Error loading {file}: {e}")
            spy_returns.append(0)
    
    # If no backtest files, use estimated dates
    if not spy_returns or all(r == 0 for r in spy_returns):
        base_date = run_date - timedelta(days=test_days*len(round_performances))
        for i in range(len(round_performances)):
            start_date = (base_date + timedelta(days=i*test_days)).strftime("%Y-%m-%d")
            end_date = (base_date + timedelta(days=(i+1)*test_days)).strftime("%Y-%m-%d")
            spy_return = get_spy_returns(start_date, end_date)
            spy_returns.append(spy_return)
    
    # Plot comparison
    plot_comparison(round_performances, spy_returns)
    
    # Print summary
    print("\nPerformance Summary:")
    print(f"{'Round':<10} {'MOE':<10} {'S&P 500':<10} {'Difference':<10}")
    print("-" * 40)
    
    for i in range(len(round_performances)):
        moe_return = round_performances[i]
        spy_return = spy_returns[i] if i < len(spy_returns) else 0
        diff = moe_return - spy_return
        print(f"{i+1:<10} {moe_return:.2%} {spy_return:.2%} {diff:.2%}")
    
    print("-" * 40)
    avg_moe = sum(round_performances) / len(round_performances)
    avg_spy = sum(spy_returns) / len(spy_returns) if spy_returns else 0
    print(f"{'Average':<10} {avg_moe:.2%} {avg_spy:.2%} {avg_moe - avg_spy:.2%}")
    
    # Check for improvement in MOE performance
    if len(round_performances) > 1:
        print("\nMOE Learning Progress:")
        for i in range(1, len(round_performances)):
            change = round_performances[i] - round_performances[i-1]
            print(f"Round {i} to {i+1}: {change:.2%} change in performance")

def plot_comparison(moe_returns, spy_returns):
    """Plot MOE performance vs S&P 500."""
    # Check if matplotlib is available
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not available for plotting")
        return
    
    rounds = list(range(1, len(moe_returns) + 1))
    
    plt.figure(figsize=(10, 6))
    
    # Plot returns
    plt.subplot(2, 1, 1)
    plt.bar([r - 0.2 for r in rounds], [r * 100 for r in moe_returns], width=0.4, label='MOE Strategy')
    plt.bar([r + 0.2 for r in rounds], [r * 100 for r in spy_returns[:len(moe_returns)]], width=0.4, label='S&P 500')
    plt.xlabel('Round')
    plt.ylabel('Return (%)')
    plt.title('MOE vs S&P 500 Performance by Round')
    plt.xticks(rounds)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot cumulative returns
    plt.subplot(2, 1, 2)
    cumulative_moe = [1 + r for r in moe_returns]
    for i in range(1, len(cumulative_moe)):
        cumulative_moe[i] = cumulative_moe[i] * cumulative_moe[i-1]
    
    cumulative_spy = [1 + r for r in spy_returns[:len(moe_returns)]]
    for i in range(1, len(cumulative_spy)):
        cumulative_spy[i] = cumulative_spy[i] * cumulative_spy[i-1]
    
    plt.plot(rounds, [(r - 1) * 100 for r in cumulative_moe], 'o-', label='MOE Strategy')
    plt.plot(rounds, [(r - 1) * 100 for r in cumulative_spy], 'o-', label='S&P 500')
    plt.xlabel('Round')
    plt.ylabel('Cumulative Return (%)')
    plt.title('Cumulative Performance')
    plt.xticks(rounds)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    try:
        plt.savefig('moe_vs_spy.png')
        print("Plot saved to moe_vs_spy.png")
    except Exception as e:
        print(f"Error saving plot: {e}")
    
    # Show plot
    try:
        plt.show()
    except Exception as e:
        print(f"Error showing plot: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare MOE performance with S&P 500")
    args = parser.parse_args()
    
    compare_performance()