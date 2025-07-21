import pandas as pd
import numpy as np
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Matplotlib not installed. Plotting will be disabled.")
    plt = None
import yfinance as yf
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any
import logging

# Import our modules
from expert import Expert
from strategies import TrendFollowingExpert, MeanReversionExpert, VolatilityExpert, SentimentExpert
from meeting import ExpertMeeting
from backtester import Backtester
from main import load_config, run_moe_system

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("benchmark_comparison.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

class BenchmarkComparison:
    """
    Compare MoE trading system performance against benchmarks like S&P 500.
    """
    def __init__(self):
        self.config = load_config()
        self.backtester = Backtester()
        
    def get_spy_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get S&P 500 ETF (SPY) data for a specific date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with OHLCV data for SPY
        """
        try:
            # Download SPY data
            spy_data = yf.download("SPY", start=start_date, end=end_date)
            
            # Format to match our backtester format
            spy_data = spy_data.reset_index()
            spy_data.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            
            return spy_data
            
        except Exception as e:
            logger.error(f"Error getting SPY data: {e}")
            # Fall back to simulated data if API fails
            return self.backtester.get_market_data(
                symbol='SPY', start_date=start_date, end_date=end_date
            )
    
    def run_buy_and_hold(self, data: pd.DataFrame, initial_capital: float = 10000) -> Dict[str, Any]:
        """
        Run a simple buy and hold strategy on the given data.
        
        Args:
            data: OHLCV price data
            initial_capital: Initial capital for backtesting
            
        Returns:
            Dictionary of backtest results
        """
        if len(data) == 0:
            return {"error": "No data available"}
            
        # Create decisions - buy at first day, hold for the rest
        decisions = [{
            'date': data['date'].iloc[0].strftime('%Y-%m-%d') if isinstance(data['date'].iloc[0], (pd.Timestamp, datetime)) else data['date'].iloc[0],
            'action': 'buy',
            'confidence': 1.0,
            'reason': 'Buy and hold strategy'
        }]
        
        # Run backtest
        results = self.backtester.run_backtest(data, decisions, 
                                              start_date=data['date'].iloc[0],
                                              end_date=data['date'].iloc[-1])
        
        return results
    
    def run_moe_with_initial_holdings(self, n_rounds: int = 3, k_meeting_rounds: int = 3,
                                     test_duration_days: int = 30, training_duration_days: int = 180,
                                     comparison_periods: List[str] = ['3mo', '6mo', '1y']) -> Dict[str, Any]:
        """
        Run the MoE system with initial holdings and compare to benchmarks.
        
        Args:
            n_rounds: Number of learning rounds
            k_meeting_rounds: Max discussion rounds per meeting
            test_duration_days: Days per test period
            training_duration_days: Days per training period
            comparison_periods: List of time periods for benchmark comparison
            
        Returns:
            Dictionary with results comparison
        """
        # Modify backtester to start with holdings
        original_reset = self.backtester.reset
        
        # Override reset method to start with holdings
        def modified_reset():
            original_reset()
            # Start with half of capital in holdings
            first_price = 100  # Approximate starting price
            self.backtester.holdings = (self.backtester.capital / 2) / first_price
            self.backtester.capital = self.backtester.capital / 2
        
        # Replace reset method
        self.backtester.reset = modified_reset
        
        # Run MoE system
        moe_results = run_moe_system(n_rounds, k_meeting_rounds, test_duration_days, training_duration_days)
        
        # Restore original reset method
        self.backtester.reset = original_reset
        
        # Get benchmark comparisons
        comparison_results = {}
        
        # Dates from MoE testing (from summary file)
        try:
            with open("moe_summary_results.json", "r") as f:
                summary = json.load(f)
                run_timestamp = summary.get("run_timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except:
            run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        run_date = datetime.strptime(run_timestamp.split(" ")[0], "%Y-%m-%d")
        
        # For each comparison period
        for period in comparison_periods:
            # Calculate date range
            if period == '3mo':
                months = 3
                period_name = "3 Months"
            elif period == '6mo':
                months = 6
                period_name = "6 Months"
            elif period == '1y':
                months = 12
                period_name = "1 Year"
            else:
                continue
                
            end_date = run_date
            start_date = end_date - timedelta(days=months*30)
            
            # Get SPY data
            spy_data = self.get_spy_data(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            # Run buy and hold strategy
            bh_results = self.run_buy_and_hold(spy_data)
            
            comparison_results[period] = {
                "period": period_name,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "spy_return": bh_results.get("total_return", 0),
                "spy_annualized_return": bh_results.get("annual_return", 0),
                "spy_sharpe": bh_results.get("sharpe_ratio", 0),
                "spy_max_drawdown": bh_results.get("max_drawdown", 0)
            }
        
        # Compare with MoE performance
        for i, perf in enumerate(moe_results.get("round_performances", [])):
            round_num = i + 1
            if round_num <= len(moe_results.get("round_performances", [])):
                for period in comparison_periods:
                    if period in comparison_results:
                        comparison_results[period][f"moe_round{round_num}_return"] = perf
        
        return comparison_results
    
    def plot_comparison(self, comparison_results: Dict[str, Any], output_file: str = "comparison_results.png"):
        """
        Plot the comparison results.
        
        Args:
            comparison_results: Results from run_moe_with_initial_holdings
            output_file: File to save the plot to
        """
        periods = list(comparison_results.keys())
        x = np.arange(len(periods))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        spy_returns = [comparison_results[p].get("spy_return", 0) * 100 for p in periods]
        
        # Get MOE returns for the last round (most learned)
        moe_returns = []
        for p in periods:
            # Find the highest round number in this period's results
            moe_keys = [k for k in comparison_results[p].keys() if k.startswith("moe_round")]
            if moe_keys:
                last_round_key = sorted(moe_keys)[-1]
                moe_returns.append(comparison_results[p].get(last_round_key, 0) * 100)
            else:
                moe_returns.append(0)
        
        rects1 = ax.bar(x - width/2, spy_returns, width, label='S&P 500 ETF (SPY)')
        rects2 = ax.bar(x + width/2, moe_returns, width, label='MoE Strategy (Last Round)')
        
        ax.set_ylabel('Return (%)')
        ax.set_title('MoE Strategy vs S&P 500 Returns')
        ax.set_xticks(x)
        ax.set_xticklabels([comparison_results[p].get("period", p) for p in periods])
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
        
        return output_file
    
    def run_comparison_and_plot(self, n_rounds: int = 3, k_meeting_rounds: int = 3,
                               test_days: int = 30, train_days: int = 90) -> str:
        """
        Run full comparison and generate plot.
        
        Args:
            n_rounds: Number of learning rounds
            k_meeting_rounds: Max discussion rounds per meeting
            test_days: Days per test period
            train_days: Days per training period
            
        Returns:
            Path to output plot file
        """
        # Run comparison
        comparison_results = self.run_moe_with_initial_holdings(
            n_rounds=n_rounds,
            k_meeting_rounds=k_meeting_rounds,
            test_duration_days=test_days,
            training_duration_days=train_days,
            comparison_periods=['3mo', '6mo', '1y']
        )
        
        # Save comparison results
        with open("comparison_results.json", "w") as f:
            json.dump(comparison_results, f, indent=2)
        
        # Generate and save plot
        plot_file = self.plot_comparison(comparison_results)
        
        return plot_file

def main():
    """Run the benchmark comparison."""
    parser = argparse.ArgumentParser(description="Compare MoE System to Benchmarks")
    parser.add_argument("--rounds", type=int, default=3, help="Number of learning rounds")
    parser.add_argument("--meeting-rounds", type=int, default=3, help="Max rounds per meeting")
    parser.add_argument("--test-days", type=int, default=30, help="Days for testing")
    parser.add_argument("--train-days", type=int, default=90, help="Days for training")
    
    args = parser.parse_args()
    
    comparison = BenchmarkComparison()
    plot_file = comparison.run_comparison_and_plot(
        n_rounds=args.rounds,
        k_meeting_rounds=args.meeting_rounds,
        test_days=args.test_days,
        train_days=args.train_days
    )
    
    logger.info(f"Comparison complete. Plot saved to {plot_file}")
    logger.info("Check comparison_results.json for detailed results")
    
if __name__ == "__main__":
    import argparse
    main()