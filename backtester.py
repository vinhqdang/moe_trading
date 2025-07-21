import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class Backtester:
    """
    Backtesting framework for evaluating expert strategies.
    """
    def __init__(self, initial_capital: float = 10000, transaction_cost: float = 0.001):
        """
        Initialize the backtester.
        
        Args:
            initial_capital: Initial capital for backtesting
            transaction_cost: Transaction cost as a percentage of trade value
        """
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.reset()
        
    def reset(self):
        """Reset the backtester state."""
        self.capital = self.initial_capital
        self.holdings = 0
        self.trade_history = []
        self.equity_curve = []
        self.current_date = None
        
    def run_backtest(self, data: pd.DataFrame, strategy_decisions: List[Dict[str, Any]],
                    start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Run backtest on historical data with a list of strategy decisions.
        
        Args:
            data: Historical price data (must have 'date', 'open', 'high', 'low', 'close')
            strategy_decisions: List of dictionaries with strategy decisions and dates
            start_date: Start date for backtest (if None, uses first date in data)
            end_date: End date for backtest (if None, uses last date in data)
            
        Returns:
            Dictionary of backtest results including performance metrics
        """
        # Reset the backtester
        self.reset()
        
        # Ensure data is sorted by date
        data = data.sort_values('date').copy()
        data['date'] = pd.to_datetime(data['date'])
        
        # Filter data by date range if specified
        if start_date:
            start_date = pd.to_datetime(start_date)
            data = data[data['date'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            data = data[data['date'] <= end_date]
            
        if len(data) == 0:
            logger.error("No data available for the specified date range")
            return {"error": "No data available for the specified date range"}
        
        # Map decisions to dates
        decision_map = {}
        for decision in strategy_decisions:
            if isinstance(decision['date'], pd.Series):
                decision_date = pd.to_datetime(decision['date'].iloc[0])
            else:
                decision_date = pd.to_datetime(decision['date'])
            decision_map[decision_date] = decision
        
        # Iterate through each day in the data
        for i, row in data.iterrows():
            current_date = row['date']
            self.current_date = current_date
            
            # Get decision for this date if exists
            try:
                decision = decision_map.get(current_date, None)
            except Exception as e:
                logger.warning(f"Error getting decision for {current_date}: {e}")
                decision = None
            
            # Execute trade based on decision
            if decision:
                self._execute_trade(decision, row)
            
            # Update equity value at the end of each day
            current_value = self.capital + (self.holdings * row['close'])
            self.equity_curve.append({
                'date': current_date,
                'equity': current_value,
                'price': row['close'],
                'holdings': self.holdings,
                'cash': self.capital
            })
        
        # Calculate performance metrics
        results = self._calculate_performance_metrics()
        results['trades'] = self.trade_history
        results['equity_curve'] = self.equity_curve
        
        return results
    
    def _execute_trade(self, decision: Dict[str, Any], price_data: pd.Series) -> None:
        """
        Execute a trade based on a strategy decision.
        
        Args:
            decision: Strategy decision (action, confidence, etc.)
            price_data: Price data for the trading day
        """
        action = decision['action']
        confidence = decision.get('confidence', 1.0)
        close_price = price_data['close']
        
        # Calculate trade size based on confidence and current capital/holdings
        if action == 'buy':
            # Use confidence to determine position size (as a % of available capital)
            position_size = self.capital * min(confidence, 0.9)  # Cap at 90% of available capital
            
            # Calculate shares to buy
            shares_to_buy = position_size / close_price
            
            # Adjust for transaction costs
            transaction_fee = position_size * self.transaction_cost
            adjusted_position = position_size - transaction_fee
            actual_shares = adjusted_position / close_price
            
            # Update holdings and capital
            self.holdings += actual_shares
            self.capital -= position_size
            
            # Record trade
            self.trade_history.append({
                'date': self.current_date,
                'action': 'buy',
                'price': close_price,
                'shares': actual_shares,
                'value': position_size,
                'fee': transaction_fee,
                'confidence': confidence,
                'reason': decision.get('reason', '')
            })
            
            logger.info(f"BUY: {actual_shares:.4f} shares @ ${close_price:.2f} (value: ${position_size:.2f}, fee: ${transaction_fee:.2f})")
            
        elif action == 'sell':
            if self.holdings > 0:
                # Use confidence to determine what percentage of holdings to sell
                shares_to_sell = self.holdings * min(confidence, 0.9)  # Cap at 90% of holdings
                
                # Calculate value
                position_value = shares_to_sell * close_price
                
                # Adjust for transaction costs
                transaction_fee = position_value * self.transaction_cost
                adjusted_value = position_value - transaction_fee
                
                # Update holdings and capital
                self.holdings -= shares_to_sell
                self.capital += adjusted_value
                
                # Record trade
                self.trade_history.append({
                    'date': self.current_date,
                    'action': 'sell',
                    'price': close_price,
                    'shares': shares_to_sell,
                    'value': position_value,
                    'fee': transaction_fee,
                    'confidence': confidence,
                    'reason': decision.get('reason', '')
                })
                
                logger.info(f"SELL: {shares_to_sell:.4f} shares @ ${close_price:.2f} (value: ${position_value:.2f}, fee: ${transaction_fee:.2f})")
        
        # For 'hold' we do nothing
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """
        Calculate performance metrics based on equity curve.
        
        Returns:
            Dictionary of performance metrics
        """
        if not self.equity_curve:
            return {'error': 'No equity data available'}
        
        # Extract equity values and dates
        equity = pd.DataFrame(self.equity_curve)
        
        # Calculate returns
        initial_equity = equity['equity'].iloc[0]
        final_equity = equity['equity'].iloc[-1]
        
        total_return = (final_equity / initial_equity) - 1
        
        # Calculate daily returns
        equity['daily_return'] = equity['equity'].pct_change()
        
        # Annualized return (assuming 252 trading days per year)
        n_days = len(equity)
        if n_days > 1:
            ann_return = ((1 + total_return) ** (252 / n_days)) - 1
        else:
            ann_return = 0
        
        # Volatility (annualized)
        if n_days > 1:
            volatility = equity['daily_return'].std() * np.sqrt(252)
        else:
            volatility = 0
        
        # Sharpe ratio (assuming risk-free rate of 0)
        sharpe_ratio = ann_return / volatility if volatility != 0 else 0
        
        # Maximum drawdown
        equity['cummax'] = equity['equity'].cummax()
        equity['drawdown'] = (equity['equity'] / equity['cummax']) - 1
        max_drawdown = equity['drawdown'].min()
        
        # Win rate
        trades_df = pd.DataFrame(self.trade_history) if self.trade_history else pd.DataFrame()
        if len(trades_df) > 0:
            # Calculate profit/loss for each trade
            buy_trades = trades_df[trades_df['action'] == 'buy'].copy()
            sell_trades = trades_df[trades_df['action'] == 'sell'].copy()
            
            # Simple P&L based on sells
            if len(sell_trades) > 0:
                win_count = len(sell_trades[sell_trades['price'] > sell_trades['price'].shift(1)])
                win_rate = win_count / len(sell_trades) if len(sell_trades) > 0 else 0
            else:
                win_rate = 0
        else:
            win_rate = 0
        
        return {
            'initial_equity': initial_equity,
            'final_equity': final_equity,
            'total_return': total_return,
            'annual_return': ann_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'n_trades': len(self.trade_history),
            'start_date': self.equity_curve[0]['date'] if self.equity_curve else None,
            'end_date': self.equity_curve[-1]['date'] if self.equity_curve else None
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """
        Save backtest results to a file.
        
        Args:
            results: Backtest results dictionary
            filename: Filename to save to (if None, generates one)
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_results_{timestamp}.json"
        
        # Convert complex objects to serializable format
        serializable_results = results.copy()
        
        # Convert dates to strings
        if 'equity_curve' in serializable_results:
            for point in serializable_results['equity_curve']:
                if isinstance(point['date'], (datetime, pd.Timestamp)):
                    point['date'] = point['date'].strftime('%Y-%m-%d')
                    
        if 'trades' in serializable_results:
            for trade in serializable_results['trades']:
                if isinstance(trade['date'], (datetime, pd.Timestamp)):
                    trade['date'] = trade['date'].strftime('%Y-%m-%d')
        
        # Handle other specific datetime conversions
        for key in ['start_date', 'end_date']:
            if key in serializable_results and isinstance(serializable_results[key], (datetime, pd.Timestamp)):
                serializable_results[key] = serializable_results[key].strftime('%Y-%m-%d')
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
            
        return filename
    
    @staticmethod
    def load_results(filename: str) -> Dict[str, Any]:
        """
        Load backtest results from a file.
        
        Args:
            filename: Path to the results file
            
        Returns:
            Dictionary of backtest results
        """
        with open(filename, 'r') as f:
            results = json.load(f)
        return results

    @staticmethod
    def get_market_data(symbol: str = 'SPY', start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Helper method to get market data for backtesting.
        In a real implementation, this would connect to a data provider.
        For this example, we'll generate some simulated data.
        
        Args:
            symbol: Trading symbol
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            
        Returns:
            DataFrame with OHLCV data
        """
        # Parse dates
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
            
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Generate date range (only business days)
        date_range = pd.date_range(start=start, end=end, freq='B')
        
        # Base price and daily volatility
        base_price = 100.0
        daily_vol = 0.015
        
        # Generate price series with random walk
        np.random.seed(42)  # For reproducibility
        returns = np.random.normal(0.0005, daily_vol, size=len(date_range))
        
        # Add some trends and patterns
        trend_cycles = 3
        trend = 0.1 * np.sin(np.linspace(0, trend_cycles * 2 * np.pi, len(date_range)))
        returns = returns + trend
        
        # Calculate price series
        log_returns = np.log(1 + returns)
        log_price_series = np.cumsum(log_returns)
        price_series = base_price * np.exp(log_price_series)
        
        # Create OHLCV data
        data = pd.DataFrame(index=date_range)
        data['date'] = data.index
        data['close'] = price_series
        
        # Generate OHLC based on close prices
        data['open'] = data['close'].shift(1) * (1 + np.random.normal(0, 0.003, size=len(data)))
        data['high'] = data[['open', 'close']].max(axis=1) * (1 + abs(np.random.normal(0, 0.005, size=len(data))))
        data['low'] = data[['open', 'close']].min(axis=1) * (1 - abs(np.random.normal(0, 0.005, size=len(data))))
        data['volume'] = np.random.normal(1000000, 200000, size=len(data))
        data['volume'] = data['volume'].clip(lower=100000)
        
        # Fill first row NaN values
        data['open'].iloc[0] = price_series[0] * 0.995
        
        return data.reset_index(drop=True)