"""
Enhanced Expert Classes with Historical Context
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime
from expert import Expert
from strategies import TrendFollowingExpert, VolatilityExpert, SentimentExpert
from historical_context import HistoricalContext

class ContextAwareTrendExpert(TrendFollowingExpert):
    """
    Trend Expert that considers historical context and major events
    """
    
    def __init__(self, name: str = "Context-Aware Trend Expert"):
        super().__init__(name)
        self.historical_context = HistoricalContext()
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced analysis with historical context"""
        # Get basic trend analysis
        basic_analysis = super().analyze(data)
        
        # Get current date context
        if 'date' in data.columns and len(data) > 0:
            current_date = pd.to_datetime(data['date'].iloc[-1])
            context = self.historical_context.get_context_for_date(current_date)
            
            # Adjust confidence and reasoning based on historical context
            adjusted_analysis = self._adjust_for_context(basic_analysis, context, data)
            
            # Add context to reasoning
            adjusted_analysis['context'] = context
            adjusted_analysis['context_adjusted'] = True
            
            return adjusted_analysis
        
        return basic_analysis
    
    def _adjust_for_context(self, analysis: Dict[str, Any], context: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Adjust analysis based on historical context"""
        adjusted = analysis.copy()
        
        # Extract current trend strength
        if len(data) >= 20:
            recent_trend = (data['close'].iloc[-1] / data['close'].iloc[-20] - 1) * 100
        else:
            recent_trend = 0
        
        # Adjust based on regime and events
        regime = context['regime']
        risk_factors = context['risk_factors']
        
        # Crisis periods - be more defensive
        if any(factor in ' '.join(risk_factors).lower() for factor in ['crisis', 'crash', 'pandemic', 'war']):
            if analysis['action'] == 'buy':
                adjusted['confidence'] *= 0.7  # Reduce buy confidence in crisis
                adjusted['reason'] += f" (Reduced confidence due to crisis period: {context['regime']})"
            elif analysis['action'] == 'sell':
                adjusted['confidence'] = min(0.95, adjusted['confidence'] * 1.2)  # Increase sell confidence
                adjusted['reason'] += f" (Increased confidence due to crisis: {context['regime']})"
        
        # Bull market periods - be more aggressive
        elif any(phrase in regime.lower() for phrase in ['recovery', 'boom', 'rally', 'low volatility']):
            if analysis['action'] == 'buy':
                adjusted['confidence'] = min(0.95, adjusted['confidence'] * 1.15)
                adjusted['reason'] += f" (Bull market regime: {context['regime']})"
            elif analysis['action'] == 'sell':
                adjusted['confidence'] *= 0.8
                adjusted['reason'] += f" (Cautious selling in bull market: {context['regime']})"
        
        # Major events impact
        recent_events = [e for e in context['major_events'] if abs(e['days_ago']) <= 30]
        if recent_events:
            event_impact = len(recent_events) * 0.05  # 5% confidence adjustment per recent event
            if analysis['action'] in ['sell', 'hold']:
                adjusted['confidence'] = min(0.95, adjusted['confidence'] + event_impact)
                adjusted['reason'] += f" (Recent major events increase caution)"
        
        return adjusted

class ContextAwareVolatilityExpert(VolatilityExpert):
    """
    Volatility Expert that considers historical market regimes
    """
    
    def __init__(self, name: str = "Context-Aware Volatility Expert"):
        super().__init__(name)
        self.historical_context = HistoricalContext()
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced volatility analysis with regime awareness"""
        # Get basic volatility analysis
        basic_analysis = super().analyze(data)
        
        # Get current date context
        if 'date' in data.columns and len(data) > 0:
            current_date = pd.to_datetime(data['date'].iloc[-1])
            context = self.historical_context.get_context_for_date(current_date)
            
            # Adjust for historical volatility regimes
            adjusted_analysis = self._adjust_for_volatility_regime(basic_analysis, context, data)
            adjusted_analysis['context'] = context
            
            return adjusted_analysis
        
        return basic_analysis
    
    def _adjust_for_volatility_regime(self, analysis: Dict[str, Any], context: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Adjust based on known volatility regimes"""
        adjusted = analysis.copy()
        regime = context['regime'].lower()
        
        # High volatility periods (2008, 2020, 2022)
        if any(phrase in regime for phrase in ['crisis', 'crash', 'pandemic', 'bear market', 'tightening']):
            # In high vol regimes, volatility signals are more reliable
            adjusted['confidence'] = min(0.95, adjusted['confidence'] * 1.2)
            adjusted['reason'] += f" (High volatility regime: {context['regime']})"
        
        # Low volatility periods (2017, early 2021)
        elif any(phrase in regime for phrase in ['low volatility', 'synchronized growth', 'recovery']):
            # In low vol regimes, volatility breakouts are more significant
            if analysis['action'] == 'sell':  # Volatility spike in low vol regime
                adjusted['confidence'] = min(0.95, adjusted['confidence'] * 1.3)
                adjusted['reason'] += f" (Volatility spike in low-vol regime: {context['regime']})"
        
        return adjusted

class ContextAwareSentimentExpert(SentimentExpert):
    """
    Sentiment Expert that incorporates historical sentiment drivers
    """
    
    def __init__(self, name: str = "Context-Aware Sentiment Expert"):
        super().__init__(name)
        self.historical_context = HistoricalContext()
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced sentiment analysis with historical context"""
        # Get basic sentiment analysis
        basic_analysis = super().analyze(data)
        
        # Get current date context
        if 'date' in data.columns and len(data) > 0:
            current_date = pd.to_datetime(data['date'].iloc[-1])
            context = self.historical_context.get_context_for_date(current_date)
            
            # Adjust sentiment based on known drivers
            adjusted_analysis = self._adjust_for_sentiment_drivers(basic_analysis, context)
            adjusted_analysis['context'] = context
            
            return adjusted_analysis
        
        return basic_analysis
    
    def _adjust_for_sentiment_drivers(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust sentiment analysis based on historical drivers"""
        adjusted = analysis.copy()
        sentiment_drivers = context.get('market_sentiment_drivers', [])
        
        # Negative sentiment drivers
        negative_drivers = ['fear', 'crisis', 'uncertainty', 'recession', 'hawkish', 'contagion', 'war']
        positive_drivers = ['optimism', 'support', 'enthusiasm', 'recovery', 'stimulus', 'breakthrough']
        
        driver_text = ' '.join(sentiment_drivers).lower()
        
        negative_count = sum(1 for driver in negative_drivers if driver in driver_text)
        positive_count = sum(1 for driver in positive_drivers if driver in driver_text)
        
        # Adjust sentiment based on historical drivers
        if negative_count > positive_count:
            # Bearish sentiment environment
            if analysis['action'] == 'sell':
                adjusted['confidence'] = min(0.95, adjusted['confidence'] * 1.1)
                adjusted['reason'] += f" (Negative sentiment drivers: {negative_count})"
            elif analysis['action'] == 'buy':
                adjusted['confidence'] *= 0.9
                adjusted['reason'] += f" (Caution due to negative sentiment drivers)"
        
        elif positive_count > negative_count:
            # Bullish sentiment environment  
            if analysis['action'] == 'buy':
                adjusted['confidence'] = min(0.95, adjusted['confidence'] * 1.1)
                adjusted['reason'] += f" (Positive sentiment drivers: {positive_count})"
            elif analysis['action'] == 'sell':
                adjusted['confidence'] *= 0.9
                adjusted['reason'] += f" (Caution against selling in positive sentiment)"
        
        return adjusted