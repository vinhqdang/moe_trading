import numpy as np
import pandas as pd
from typing import Dict, List, Any
from expert import Expert
import random

class TrendFollowingExpert(Expert):
    """Expert that focuses on following trends in the data."""
    
    def __init__(self, name: str = "Trend Follower"):
        super().__init__(name)
        self.lookback_period = 10
        self.trend_threshold = 0.01
        
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data using trend following strategy."""
        if len(data) < self.lookback_period:
            return {"action": "hold", "confidence": 0.5, "reason": "Not enough data for trend analysis"}
        
        # Simple trend analysis using moving averages
        recent_avg = data['close'].tail(self.lookback_period).mean()
        older_avg = data['close'].iloc[-(2*self.lookback_period):-self.lookback_period].mean()
        
        pct_change = (recent_avg - older_avg) / older_avg
        
        confidence = min(abs(pct_change) * 10, 0.9)  # Scale confidence by trend strength
        
        if pct_change > self.trend_threshold:
            action = "buy"
            reason = f"Upward trend detected: {pct_change:.2%} increase"
        elif pct_change < -self.trend_threshold:
            action = "sell"
            reason = f"Downward trend detected: {pct_change:.2%} decrease"
        else:
            action = "hold"
            reason = f"No significant trend: {pct_change:.2%} change"
            confidence = 0.5
            
        return {
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "parameters": {
                "lookback_period": self.lookback_period,
                "trend_threshold": self.trend_threshold
            }
        }
    
    def update_strategy(self, performance: float, meeting_outcome: Dict[str, Any]) -> None:
        """Update strategy parameters based on performance."""
        # Record performance
        self.record_performance(performance)
        
        # If performance is good, slightly adjust parameters
        if performance > 0.05:  # Good performance threshold
            # Keep parameters similar
            self.lookback_period = max(5, min(20, self.lookback_period + random.randint(-1, 1)))
            self.trend_threshold = max(0.005, min(0.02, self.trend_threshold * (1 + random.uniform(-0.1, 0.1))))
        else:
            # More significant adjustments for poor performance
            self.lookback_period = max(5, min(20, self.lookback_period + random.randint(-3, 3)))
            self.trend_threshold = max(0.005, min(0.02, self.trend_threshold * (1 + random.uniform(-0.2, 0.2))))


class MeanReversionExpert(Expert):
    """Expert that focuses on mean reversion strategies."""
    
    def __init__(self, name: str = "Mean Reverter"):
        super().__init__(name)
        self.window_size = 20
        self.std_dev_threshold = 1.5
        
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data using mean reversion strategy."""
        if len(data) < self.window_size:
            return {"action": "hold", "confidence": 0.5, "reason": "Not enough data for mean reversion analysis"}
            
        # Calculate z-score (how many standard deviations from mean)
        rolling_mean = data['close'].rolling(window=self.window_size).mean()
        rolling_std = data['close'].rolling(window=self.window_size).std()
        
        current_price = data['close'].iloc[-1]
        current_mean = rolling_mean.iloc[-1]
        current_std = rolling_std.iloc[-1]
        
        if current_std == 0:
            z_score = 0
        else:
            z_score = (current_price - current_mean) / current_std
        
        confidence = min(abs(z_score) / 3, 0.9)  # Scale confidence by z-score
        
        if z_score < -self.std_dev_threshold:
            action = "buy"  # Price is below mean, expect reversion upward
            reason = f"Price significantly below mean (z-score: {z_score:.2f})"
        elif z_score > self.std_dev_threshold:
            action = "sell"  # Price is above mean, expect reversion downward
            reason = f"Price significantly above mean (z-score: {z_score:.2f})"
        else:
            action = "hold"
            reason = f"Price near mean (z-score: {z_score:.2f})"
            confidence = 0.5
            
        return {
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "parameters": {
                "window_size": self.window_size,
                "std_dev_threshold": self.std_dev_threshold
            }
        }
    
    def update_strategy(self, performance: float, meeting_outcome: Dict[str, Any]) -> None:
        """Update strategy parameters based on performance."""
        # Record performance
        self.record_performance(performance)
        
        # If performance is good, slightly adjust parameters
        if performance > 0.05:  # Good performance threshold
            # Keep parameters similar
            self.window_size = max(10, min(30, self.window_size + random.randint(-1, 1)))
            self.std_dev_threshold = max(1.0, min(2.5, self.std_dev_threshold * (1 + random.uniform(-0.05, 0.05))))
        else:
            # More significant adjustments for poor performance
            self.window_size = max(10, min(30, self.window_size + random.randint(-3, 3)))
            self.std_dev_threshold = max(1.0, min(2.5, self.std_dev_threshold * (1 + random.uniform(-0.2, 0.2))))


class VolatilityExpert(Expert):
    """Expert that focuses on market volatility."""
    
    def __init__(self, name: str = "Volatility Expert"):
        super().__init__(name)
        self.vol_window = 15
        self.high_vol_threshold = 0.015  # 1.5% daily volatility
        self.low_vol_threshold = 0.005   # 0.5% daily volatility
        
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data using volatility-based strategy."""
        if len(data) < self.vol_window:
            return {"action": "hold", "confidence": 0.5, "reason": "Not enough data for volatility analysis"}
        
        # Calculate recent volatility (standard deviation of returns)
        returns = data['close'].pct_change().dropna()
        volatility = returns.tail(self.vol_window).std()
        
        # Get recent price action
        recent_return = returns.tail(3).mean()
        
        confidence = min(volatility * 50, 0.9)  # Higher confidence with higher volatility
        
        if volatility > self.high_vol_threshold:
            # High volatility regime
            if recent_return > 0:
                action = "sell"  # Fade the move in high volatility
                reason = f"High volatility ({volatility:.2%}) with recent upward movement"
            else:
                action = "buy"  # Fade the move in high volatility
                reason = f"High volatility ({volatility:.2%}) with recent downward movement"
        elif volatility < self.low_vol_threshold:
            # Low volatility regime
            if recent_return > 0:
                action = "buy"  # Follow the move in low volatility
                reason = f"Low volatility ({volatility:.2%}) with recent upward movement"
            else:
                action = "sell"  # Follow the move in low volatility
                reason = f"Low volatility ({volatility:.2%}) with recent downward movement"
        else:
            action = "hold"
            reason = f"Medium volatility ({volatility:.2%}), no clear signal"
            confidence = 0.5
            
        return {
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "parameters": {
                "vol_window": self.vol_window,
                "high_vol_threshold": self.high_vol_threshold,
                "low_vol_threshold": self.low_vol_threshold
            }
        }
    
    def update_strategy(self, performance: float, meeting_outcome: Dict[str, Any]) -> None:
        """Update strategy parameters based on performance."""
        # Record performance
        self.record_performance(performance)
        
        # If performance is good, slightly adjust parameters
        if performance > 0.05:  # Good performance threshold
            # Keep parameters similar
            self.vol_window = max(10, min(20, self.vol_window + random.randint(-1, 1)))
            self.high_vol_threshold = max(0.01, min(0.02, self.high_vol_threshold * (1 + random.uniform(-0.05, 0.05))))
            self.low_vol_threshold = max(0.003, min(0.008, self.low_vol_threshold * (1 + random.uniform(-0.05, 0.05))))
        else:
            # More significant adjustments for poor performance
            self.vol_window = max(10, min(20, self.vol_window + random.randint(-3, 3)))
            self.high_vol_threshold = max(0.01, min(0.02, self.high_vol_threshold * (1 + random.uniform(-0.15, 0.15))))
            self.low_vol_threshold = max(0.003, min(0.008, self.low_vol_threshold * (1 + random.uniform(-0.15, 0.15))))


class SentimentExpert(Expert):
    """Expert that makes decisions based on market sentiment analysis."""
    
    def __init__(self, name: str = "Sentiment Analyst"):
        super().__init__(name)
        self.sentiment_threshold = 0.6  # Threshold for strong sentiment
        
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data using sentiment-based approach."""
        if 'sentiment' not in data.columns:
            # Simulate sentiment if not available
            # In a real implementation, we would use actual sentiment data
            sentiment = np.mean([
                np.random.normal(0, 0.3),  # Random component
                np.sign(data['close'].diff().tail(5).mean()) * 0.2  # Trend component
            ])
            sentiment = max(min(sentiment, 1), -1)  # Clamp to [-1, 1]
        else:
            sentiment = data['sentiment'].iloc[-1]
        
        confidence = abs(sentiment) * 0.9  # Higher confidence with stronger sentiment
        
        if sentiment > self.sentiment_threshold:
            action = "buy"
            reason = f"Positive market sentiment detected: {sentiment:.2f}"
        elif sentiment < -self.sentiment_threshold:
            action = "sell"
            reason = f"Negative market sentiment detected: {sentiment:.2f}"
        else:
            action = "hold"
            reason = f"Neutral market sentiment: {sentiment:.2f}"
            confidence = 0.5
            
        return {
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "parameters": {
                "sentiment_threshold": self.sentiment_threshold
            }
        }
    
    def update_strategy(self, performance: float, meeting_outcome: Dict[str, Any]) -> None:
        """Update strategy parameters based on performance."""
        # Record performance
        self.record_performance(performance)
        
        # Adjust sentiment threshold based on performance
        if performance > 0.05:  # Good performance threshold
            # Smaller adjustment for good performance
            self.sentiment_threshold = max(0.4, min(0.8, self.sentiment_threshold * (1 + random.uniform(-0.05, 0.05))))
        else:
            # Larger adjustment for poor performance
            self.sentiment_threshold = max(0.4, min(0.8, self.sentiment_threshold * (1 + random.uniform(-0.15, 0.15))))