import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import os
import argparse

# Import our modules
from expert import Expert
from strategies import TrendFollowingExpert, MeanReversionExpert, VolatilityExpert, SentimentExpert
from meeting import ExpertMeeting
from backtester import Backtester

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("moe_system.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from config.json."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def run_moe_system(n_rounds: int = 3, k_meeting_rounds: int = 3, 
                   test_duration_days: int = 30, training_duration_days: int = 180):
    """
    Run the Mixture of Experts system with multiple learning rounds.
    
    Args:
        n_rounds: Number of total learning rounds
        k_meeting_rounds: Maximum number of discussion rounds in each meeting
        test_duration_days: Number of days for backtesting
        training_duration_days: Number of days for training data
    """
    logger.info(f"Starting MOE system with {n_rounds} rounds")
    
    # Load config
    config = load_config()
    
    # Create experts
    experts = [
        TrendFollowingExpert("Trend Expert"),
        MeanReversionExpert("Mean Reversion Expert"),
        VolatilityExpert("Volatility Expert"),
        SentimentExpert("Sentiment Expert")
    ]
    
    # Create meeting facilitator
    meeting = ExpertMeeting(experts, max_rounds=k_meeting_rounds, 
                           openai_key=config.get('openai_api_key'),
                           gemini_key=config.get('gemini_api_key'))
    
    # Create backtester
    backtester = Backtester()
    
    # Override reset method to start with some initial holdings
    original_reset = backtester.reset
    
    def modified_reset():
        original_reset()
        # Start with half of capital in holdings at the beginning
        # This allows the system to execute sell recommendations
        first_price = 100  # Approximate starting price
        backtester.holdings = (backtester.capital / 2) / first_price
        backtester.capital = backtester.capital / 2
    
    # Replace reset method
    backtester.reset = modified_reset
    
    # Track performance across rounds
    round_performances = []
    
    # Current date for backtesting (we'll move this forward each round)
    end_date = datetime.now() - timedelta(days=30)  # Use data up to a month ago
    
    for round_num in range(1, n_rounds + 1):
        logger.info(f"\n{'=' * 50}\nStarting Round {round_num}/{n_rounds}\n{'=' * 50}")
        
        # Calculate date ranges for this round
        test_start = end_date - timedelta(days=test_duration_days)
        test_end = end_date
        
        training_start = test_start - timedelta(days=training_duration_days)
        training_end = test_start - timedelta(days=1)  # Day before test starts
        
        # Get market data
        logger.info(f"Getting training data from {training_start.strftime('%Y-%m-%d')} to {training_end.strftime('%Y-%m-%d')}")
        training_data = backtester.get_market_data(start_date=training_start.strftime('%Y-%m-%d'),
                                                  end_date=training_end.strftime('%Y-%m-%d'))
        
        logger.info(f"Getting test data from {test_start.strftime('%Y-%m-%d')} to {test_end.strftime('%Y-%m-%d')}")
        test_data = backtester.get_market_data(start_date=test_start.strftime('%Y-%m-%d'),
                                             end_date=test_end.strftime('%Y-%m-%d'))
        
        # Generate strategy decisions based on meetings
        strategy_decisions = []
        
        # Process each day in test period
        for i in range(0, len(test_data), len(test_data)-1):  # Make fewer decisions to speed up testing
            day_data = test_data.iloc[:i+1] if i > 0 else test_data.iloc[:1]
            
            # Combine with training data for analysis (excluding future data)
            analysis_data = pd.concat([training_data, day_data])
            
            # Current date
            current_date = day_data.iloc[-1]['date']
            logger.info(f"\nAnalyzing data for date: {current_date}")
            
            # Hold expert meeting
            consensus = meeting.hold_meeting(analysis_data)
            
            # Save meeting log with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            meeting_log_file = f"meeting_log_round{round_num}_{timestamp}.json"
            meeting.save_meeting_log(meeting_log_file)
            logger.info(f"Meeting log saved to {meeting_log_file}")
            
            # Add decision to strategy decisions
            decision = consensus.copy()
            decision['date'] = current_date
            strategy_decisions.append(decision)
            
            logger.info(f"Consensus decision: {decision['action']} with confidence {decision['confidence']:.2f}")
        
        # Run backtest on the test period
        logger.info("\nRunning backtest...")
        backtest_results = backtester.run_backtest(
            test_data, strategy_decisions,
            start_date=test_start.strftime('%Y-%m-%d'),
            end_date=test_end.strftime('%Y-%m-%d')
        )
        
        # Save backtest results
        results_file = f"backtest_results_round{round_num}.json"
        backtester.save_results(backtest_results, results_file)
        
        # Log performance
        performance = backtest_results['total_return']
        round_performances.append(performance)
        
        logger.info(f"\nRound {round_num} Performance:")
        logger.info(f"Total Return: {performance:.2%}")
        logger.info(f"Final Equity: ${backtest_results['final_equity']:.2f}")
        logger.info(f"Sharpe Ratio: {backtest_results['sharpe_ratio']:.2f}")
        logger.info(f"Max Drawdown: {backtest_results['max_drawdown']:.2%}")
        
        # Update experts based on performance
        logger.info("\nUpdating expert strategies based on performance...")
        for expert in experts:
            expert.update_strategy(performance, strategy_decisions[-1])
            logger.info(f"Updated {expert.name}'s strategy parameters")
        
        # Move end date forward for next round
        end_date = end_date + timedelta(days=test_duration_days)
        
    # Final performance summary
    logger.info(f"\n{'=' * 50}\nFinal Performance Summary\n{'=' * 50}")
    logger.info(f"Performance by round: {[f'{p:.2%}' for p in round_performances]}")
    logger.info(f"Average performance: {np.mean(round_performances):.2%}")
    logger.info(f"Best performance: {max(round_performances):.2%} (Round {round_performances.index(max(round_performances)) + 1})")
    
    # Save summary to file
    summary = {
        "round_performances": round_performances,
        "average_performance": float(np.mean(round_performances)),
        "best_performance": float(max(round_performances)),
        "best_round": round_performances.index(max(round_performances)) + 1,
        "run_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "config": {
            "n_rounds": n_rounds,
            "k_meeting_rounds": k_meeting_rounds,
            "test_duration_days": test_duration_days,
            "training_duration_days": training_duration_days
        }
    }
    
    with open("moe_summary_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info("Summary saved to moe_summary_results.json")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Mixture of Experts (MoE) System")
    parser.add_argument("--rounds", type=int, default=3, help="Number of learning rounds")
    parser.add_argument("--meeting-rounds", type=int, default=3, help="Max rounds per meeting")
    parser.add_argument("--test-days", type=int, default=10, help="Days for testing")
    parser.add_argument("--train-days", type=int, default=30, help="Days for training")
    
    args = parser.parse_args()
    
    run_moe_system(
        n_rounds=args.rounds,
        k_meeting_rounds=args.meeting_rounds,
        test_duration_days=args.test_days,
        training_duration_days=args.train_days
    )