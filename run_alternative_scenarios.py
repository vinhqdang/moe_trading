#!/usr/bin/env python3
"""
Run MOE Trading System with Alternative Historical Scenarios
Testing system adaptability to different events
"""

import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import argparse
import os

# Import our modules
from enhanced_expert import ContextAwareTrendExpert, ContextAwareVolatilityExpert, ContextAwareSentimentExpert
from strategies import MeanReversionExpert
from meeting import ExpertMeeting
from backtester import Backtester
from alternative_scenarios import AlternativeScenarios
from alternative_historical_context import AlternativeHistoricalContext

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("alternative_scenarios.log"),
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

def create_alternative_experts(scenario_name: str):
    """Create experts using alternative historical context"""
    
    class AlternativeContextAwareTrendExpert(ContextAwareTrendExpert):
        def __init__(self, name: str, scenario: str):
            super().__init__(name)
            self.historical_context = AlternativeHistoricalContext(scenario)
    
    class AlternativeContextAwareVolatilityExpert(ContextAwareVolatilityExpert):
        def __init__(self, name: str, scenario: str):
            super().__init__(name)
            self.historical_context = AlternativeHistoricalContext(scenario)
    
    class AlternativeContextAwareSentimentExpert(ContextAwareSentimentExpert):
        def __init__(self, name: str, scenario: str):
            super().__init__(name)
            self.historical_context = AlternativeHistoricalContext(scenario)
    
    return [
        AlternativeContextAwareTrendExpert(f"Alt-Trend-{scenario_name}", scenario_name),
        MeanReversionExpert("Mean Reversion Expert"),  # Keep original
        AlternativeContextAwareVolatilityExpert(f"Alt-Volatility-{scenario_name}", scenario_name),
        AlternativeContextAwareSentimentExpert(f"Alt-Sentiment-{scenario_name}", scenario_name)
    ]

def run_scenario_simulation(scenario_name: str, start_year: int = 2014, end_year: int = 2024):
    """
    Run simulation with alternative scenario
    """
    logger.info(f"Starting scenario simulation: {scenario_name}")
    
    # Get scenario description
    scenarios = AlternativeScenarios()
    all_scenarios = scenarios.get_all_scenarios()
    scenario_info = all_scenarios.get(scenario_name, {"description": "Unknown scenario"})
    
    logger.info(f"Scenario: {scenario_info['description']}")
    
    # Load config
    config = load_config()
    
    # Create alternative experts
    experts = create_alternative_experts(scenario_name)
    
    # Create meeting facilitator
    meeting = ExpertMeeting(experts, max_rounds=3,
                           openai_key=config.get('openai_api_key'),
                           gemini_key=None,  # Disabled
                           leader=None)  # Use equal weights for scenarios
    
    # Create backtester
    backtester = Backtester(initial_capital=10000, transaction_cost=0.001)
    
    # Override reset method to start with mixed holdings
    original_reset = backtester.reset
    def modified_reset():
        original_reset()
        backtester.holdings = 50.0  # 50 shares
        backtester.capital = 5000.0  # Half cash, half holdings
    backtester.reset = modified_reset
    
    # Track performance
    round_performances = []
    annual_results = {}
    
    # Run simulation year by year
    for year in range(start_year, end_year + 1):
        round_num = year - start_year + 1
        logger.info(f"\\n{'=' * 60}\\nScenario {scenario_name} - Year {year} (Round {round_num}/{end_year-start_year+1})\\n{'=' * 60}")
        
        # Calculate date ranges
        start_date = f"{year-1}-01-01"
        train_end_date = f"{year-1}-12-31"
        test_start_date = f"{year}-01-01"
        test_end_date = f"{year}-12-31"
        
        # Get training and test data
        try:
            training_data = backtester.get_market_data(start_date=start_date, end_date=train_end_date)
            test_data = backtester.get_market_data(start_date=test_start_date, end_date=test_end_date)
            logger.info(f"Training: {len(training_data)} days, Test: {len(test_data)} days")
        except Exception as e:
            logger.error(f"Failed to get data for year {year}: {e}")
            continue
        
        # Generate quarterly decisions
        strategy_decisions = []
        quarters = [
            (f"{year}-01-01", f"{year}-03-31"),
            (f"{year}-04-01", f"{year}-06-30"),
            (f"{year}-07-01", f"{year}-09-30"),
            (f"{year}-10-01", f"{year}-12-31")
        ]
        
        for q_num, (q_start, q_end) in enumerate(quarters, 1):
            logger.info(f"Analyzing Q{q_num} {year}: {q_start} to {q_end}")
            
            # Get data up to current quarter
            q_start_dt = pd.to_datetime(q_start)
            analysis_end_date = min(pd.to_datetime(q_end), pd.to_datetime(test_data['date'].max()))
            
            current_test_data = test_data[test_data['date'] <= analysis_end_date]
            if len(current_test_data) == 0:
                continue
            
            analysis_data = pd.concat([training_data, current_test_data], ignore_index=True)
            
            # Hold expert meeting
            try:
                consensus = meeting.hold_meeting(analysis_data)
                
                # Save meeting log
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                meeting_log_file = f"scenario_{scenario_name}_meeting_log_{year}_Q{q_num}_{timestamp}.json"
                meeting.save_meeting_log(meeting_log_file)
                
                # Add decision
                decision = consensus.copy()
                decision['date'] = analysis_end_date.strftime('%Y-%m-%d')
                decision['quarter'] = f"{year}-Q{q_num}"
                strategy_decisions.append(decision)
                
                logger.info(f"Q{q_num} {year} decision: {decision['action']} (confidence: {decision['confidence']:.2f})")
                
            except Exception as e:
                logger.error(f"Error in expert meeting for Q{q_num} {year}: {e}")
                continue
        
        # Run backtest for the year
        try:
            backtest_results = backtester.run_backtest(
                test_data, strategy_decisions,
                start_date=test_start_date,
                end_date=test_end_date
            )
            
            # Save results
            results_file = f"scenario_{scenario_name}_backtest_{year}.json"
            backtester.save_results(backtest_results, results_file)
            
            # Track performance
            performance = backtest_results['total_return']
            round_performances.append(performance)
            annual_results[year] = {
                "performance": performance,
                "final_equity": backtest_results['final_equity'],
                "sharpe_ratio": backtest_results['sharpe_ratio'],
                "max_drawdown": backtest_results['max_drawdown'],
                "n_trades": backtest_results['n_trades']
            }
            
            logger.info(f"Year {year} Performance: {performance:.2%}")
            
        except Exception as e:
            logger.error(f"Error running backtest for year {year}: {e}")
            continue
        
        # Update experts
        for expert in experts:
            try:
                expert.update_strategy(performance, strategy_decisions[-1] if strategy_decisions else {})
            except Exception as e:
                logger.warning(f"Failed to update {expert.name}: {e}")
    
    # Final summary
    if round_performances:
        avg_annual_return = np.mean(round_performances)
        total_return = np.prod([1 + r for r in round_performances]) - 1
        volatility = np.std(round_performances)
        sharpe_ratio = avg_annual_return / volatility if volatility > 0 else 0
        
        logger.info(f"\\n{'=' * 60}\\nScenario {scenario_name} Results ({start_year}-{end_year})\\n{'=' * 60}")
        logger.info(f"Average annual return: {avg_annual_return:.2%}")
        logger.info(f"Total return: {total_return:.2%}")
        logger.info(f"Sharpe ratio: {sharpe_ratio:.2f}")
        logger.info(f"Best year: {max(round_performances):.2%}")
        logger.info(f"Worst year: {min(round_performances):.2%}")
        
        # Save comprehensive summary
        summary = {
            "scenario": scenario_name,
            "scenario_description": scenario_info['description'],
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
            "run_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        summary_file = f"scenario_{scenario_name}_summary_{start_year}_{end_year}.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Summary saved to {summary_file}")
        return summary
    else:
        logger.error("No performance data collected!")
        return None

def run_all_scenarios():
    """Run all alternative scenarios"""
    scenarios = AlternativeScenarios()
    all_scenarios = scenarios.get_all_scenarios()
    
    results_comparison = {}
    
    for scenario_id in all_scenarios.keys():
        logger.info(f"\\n\\n{'*' * 80}\\nSTARTING SCENARIO: {scenario_id.upper()}\\n{'*' * 80}")
        try:
            result = run_scenario_simulation(scenario_id, 2014, 2024)
            if result:
                results_comparison[scenario_id] = result['summary_stats']
        except Exception as e:
            logger.error(f"Failed to run scenario {scenario_id}: {e}")
    
    # Save comparison results
    comparison_file = "all_scenarios_comparison.json"
    with open(comparison_file, "w") as f:
        json.dump(results_comparison, f, indent=2)
    
    logger.info(f"\\n\\nAll scenarios completed. Comparison saved to {comparison_file}")
    
    # Print summary comparison
    print("\\n" + "="*80)
    print("ALTERNATIVE SCENARIOS PERFORMANCE COMPARISON")
    print("="*80)
    for scenario_id, stats in results_comparison.items():
        print(f"\\n{scenario_id.upper()}:")
        print(f"  Total Return: {stats['total_return']:.2%}")
        print(f"  Annual Return: {stats['average_annual_return']:.2%}")
        print(f"  Sharpe Ratio: {stats['sharpe_ratio']:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Alternative Scenario Simulations")
    parser.add_argument("--scenario", type=str, default="all", 
                       help="Scenario to run (scenario_1, scenario_2, etc. or 'all')")
    parser.add_argument("--start-year", type=int, default=2014, help="Starting year")
    parser.add_argument("--end-year", type=int, default=2024, help="Ending year")
    
    args = parser.parse_args()
    
    if args.scenario == "all":
        run_all_scenarios()
    else:
        result = run_scenario_simulation(args.scenario, args.start_year, args.end_year)
        if result:
            print(f"\\nScenario {args.scenario} completed successfully!")
        else:
            print(f"\\nScenario {args.scenario} failed!")