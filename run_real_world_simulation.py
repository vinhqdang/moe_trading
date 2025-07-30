#!/usr/bin/env python3
"""
Real World MOE Trading Simulation (2014-2024)
Using historical context and events for expert decision making
"""

import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import os
import argparse

# Import our enhanced modules
from enhanced_expert import ContextAwareTrendExpert, ContextAwareVolatilityExpert, ContextAwareSentimentExpert
from strategies import MeanReversionExpert  # Use original for mean reversion
from meeting import ExpertMeeting
from backtester import Backtester

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("real_world_moe_system.log"),
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

def run_real_world_moe_system(start_year: int = 2014, end_year: int = 2024, 
                              n_rounds: int = 11, test_duration_days: int = 365, 
                              training_duration_days: int = 365, leader: str = None):
    """
    Run the MOE system with real-world data and historical context.
    
    Args:
        start_year: Starting year for simulation
        end_year: Ending year for simulation  
        n_rounds: Number of yearly rounds
        test_duration_days: Days per testing period
        training_duration_days: Days for training data
        leader: Name of expert to act as leader
    """
    logger.info(f"Starting Real-World MOE system simulation {start_year}-{end_year}")
    
    # Load config
    config = load_config()
    
    # Create context-aware experts
    experts = [
        ContextAwareTrendExpert("Context-Aware Trend Expert"),
        MeanReversionExpert("Mean Reversion Expert"),  # Keep original
        ContextAwareVolatilityExpert("Context-Aware Volatility Expert"), 
        ContextAwareSentimentExpert("Context-Aware Sentiment Expert")
    ]
    
    # Create meeting facilitator
    meeting = ExpertMeeting(experts, max_rounds=3, 
                           openai_key=config.get('openai_api_key'),
                           gemini_key=None,  # Disabled
                           leader=leader)
    
    # Create backtester with real market data
    backtester = Backtester(initial_capital=10000, transaction_cost=0.001)
    
    # Override reset method to start with some initial holdings
    original_reset = backtester.reset
    
    def modified_reset():
        original_reset()
        # Start with half in holdings to allow sell recommendations
        backtester.holdings = 50.0  # 50 shares
        backtester.capital = 5000.0  # Half cash, half holdings
    
    # Replace reset method
    backtester.reset = modified_reset
    
    # Track performance across years
    round_performances = []
    annual_results = {}
    
    # Run simulation year by year
    for year in range(start_year, end_year + 1):
        round_num = year - start_year + 1
        logger.info(f"\n{'=' * 60}\nStarting Year {year} (Round {round_num}/{n_rounds})\n{'=' * 60}")
        
        # Calculate date ranges for this year
        start_date = f"{year-1}-01-01"  # Use previous year for training
        train_end_date = f"{year-1}-12-31"
        test_start_date = f"{year}-01-01"
        test_end_date = f"{year}-12-31"
        
        # Get training data (previous year)
        logger.info(f"Getting training data from {start_date} to {train_end_date}")
        try:
            training_data = backtester.get_market_data(start_date=start_date, end_date=train_end_date)
            logger.info(f"Training data: {len(training_data)} days")
        except Exception as e:
            logger.error(f"Failed to get training data: {e}")
            continue
        
        # Get test data (current year)
        logger.info(f"Getting test data from {test_start_date} to {test_end_date}")
        try:
            test_data = backtester.get_market_data(start_date=test_start_date, end_date=test_end_date)
            logger.info(f"Test data: {len(test_data)} days")
        except Exception as e:
            logger.error(f"Failed to get test data: {e}")
            continue
        
        # Generate strategy decisions - make quarterly decisions
        strategy_decisions = []
        
        # Make decisions quarterly (4 times per year)
        quarters = [
            (f"{year}-01-01", f"{year}-03-31"),
            (f"{year}-04-01", f"{year}-06-30"), 
            (f"{year}-07-01", f"{year}-09-30"),
            (f"{year}-10-01", f"{year}-12-31")
        ]
        
        for q_num, (q_start, q_end) in enumerate(quarters, 1):
            logger.info(f"\nAnalyzing Q{q_num} {year}: {q_start} to {q_end}")
            
            # Get data up to current quarter
            q_start_dt = pd.to_datetime(q_start)
            analysis_end_date = min(pd.to_datetime(q_end), pd.to_datetime(test_data['date'].max()))
            
            # Combine training data with test data up to current quarter
            current_test_data = test_data[test_data['date'] <= analysis_end_date]
            
            if len(current_test_data) == 0:
                continue
                
            analysis_data = pd.concat([training_data, current_test_data], ignore_index=True)
            
            # Current analysis date (end of quarter)
            current_date = analysis_end_date
            logger.info(f"Analyzing data up to: {current_date}")
            
            # Hold expert meeting with historical context
            consensus = meeting.hold_meeting(analysis_data)
            
            # Save meeting log
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            meeting_log_file = f"real_world_meeting_log_{year}_Q{q_num}_{timestamp}.json"
            meeting.save_meeting_log(meeting_log_file)
            logger.info(f"Meeting log saved to {meeting_log_file}")
            
            # Add decision to strategy decisions
            decision = consensus.copy()
            decision['date'] = current_date.strftime('%Y-%m-%d')
            decision['quarter'] = f"{year}-Q{q_num}"
            strategy_decisions.append(decision)
            
            logger.info(f"Q{q_num} {year} decision: {decision['action']} (confidence: {decision['confidence']:.2f})")
        
        # Run backtest on the full year
        logger.info(f"\nRunning backtest for year {year}...")
        try:
            backtest_results = backtester.run_backtest(
                test_data, strategy_decisions,
                start_date=test_start_date,
                end_date=test_end_date
            )
            
            # Save backtest results
            results_file = f"real_world_backtest_results_{year}.json"
            backtester.save_results(backtest_results, results_file)
            
            # Log performance  
            performance = backtest_results['total_return']
            round_performances.append(performance)
            annual_results[year] = {
                "performance": performance,
                "final_equity": backtest_results['final_equity'],
                "sharpe_ratio": backtest_results['sharpe_ratio'],
                "max_drawdown": backtest_results['max_drawdown'],
                "n_trades": backtest_results['n_trades']
            }
            
            logger.info(f"\nYear {year} Performance:")
            logger.info(f"Total Return: {performance:.2%}")
            logger.info(f"Final Equity: ${backtest_results['final_equity']:.2f}")
            logger.info(f"Sharpe Ratio: {backtest_results['sharpe_ratio']:.2f}")
            logger.info(f"Max Drawdown: {backtest_results['max_drawdown']:.2%}")
            logger.info(f"Number of Trades: {backtest_results['n_trades']}")
            
        except Exception as e:
            logger.error(f"Error running backtest for year {year}: {e}")
            continue
        
        # Update experts based on performance
        logger.info(f"Updating expert strategies based on {year} performance...")
        for expert in experts:
            try:
                expert.update_strategy(performance, strategy_decisions[-1] if strategy_decisions else {})
                logger.info(f"Updated {expert.name}'s strategy parameters")
            except Exception as e:
                logger.warning(f"Failed to update {expert.name}: {e}")
    
    # Final performance summary
    logger.info(f"\n{'=' * 60}\nFinal Performance Summary ({start_year}-{end_year})\n{'=' * 60}")
    
    if round_performances:
        avg_annual_return = np.mean(round_performances)
        total_return = np.prod([1 + r for r in round_performances]) - 1
        volatility = np.std(round_performances)
        sharpe_ratio = avg_annual_return / volatility if volatility > 0 else 0
        
        logger.info(f"Annual returns: {[f'{p:.2%}' for p in round_performances]}")
        logger.info(f"Average annual return: {avg_annual_return:.2%}")
        logger.info(f"Total cumulative return: {total_return:.2%}")
        logger.info(f"Annual volatility: {volatility:.2%}")
        logger.info(f"Sharpe ratio: {sharpe_ratio:.2f}")
        logger.info(f"Best year: {max(round_performances):.2%}")
        logger.info(f"Worst year: {min(round_performances):.2%}")
        
        # Save comprehensive summary
        leader_suffix = f"_leader_{leader.replace(' ', '_')}" if leader else "_equal_weights"
        summary = {
            "period": f"{start_year}-{end_year}",
            "annual_performances": round_performances,
            "annual_results": annual_results,
            "summary_stats": {
                "average_annual_return": float(avg_annual_return),
                "total_return": float(total_return),
                "annual_volatility": float(volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "best_year": float(max(round_performances)),
                "worst_year": float(min(round_performances))
            },
            "run_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "config": {
                "start_year": start_year,
                "end_year": end_year,
                "leader": leader,
                "experts": [expert.name for expert in experts]
            }
        }
        
        summary_file = f"real_world_summary{leader_suffix}_{start_year}_{end_year}.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Comprehensive summary saved to {summary_file}")
        return summary
    else:
        logger.error("No performance data collected!")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Real-World MOE System (2014-2024)")
    parser.add_argument("--start-year", type=int, default=2014, help="Starting year")
    parser.add_argument("--end-year", type=int, default=2024, help="Ending year")
    parser.add_argument("--leader", type=str, default=None, help="Expert to act as leader")
    
    args = parser.parse_args()
    
    # Run the simulation
    result = run_real_world_moe_system(
        start_year=args.start_year,
        end_year=args.end_year,
        leader=args.leader
    )
    
    if result:
        print(f"\n{'='*60}")
        print(f"REAL-WORLD SIMULATION COMPLETE ({args.start_year}-{args.end_year})")
        print(f"{'='*60}")
        print(f"Average Annual Return: {result['summary_stats']['average_annual_return']:.2%}")
        print(f"Total Return: {result['summary_stats']['total_return']:.2%}")
        print(f"Sharpe Ratio: {result['summary_stats']['sharpe_ratio']:.2f}")
        print(f"Best Year: {result['summary_stats']['best_year']:.2%}")
        print(f"Worst Year: {result['summary_stats']['worst_year']:.2%}")
    else:
        print("Simulation failed!")