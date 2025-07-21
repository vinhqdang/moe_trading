from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("meeting_logs.log"), 
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

class Expert(ABC):
    """
    Abstract base class for all experts in the MoE system.
    Each expert has its own strategy for making predictions/decisions.
    """
    def __init__(self, name: str):
        self.name = name
        self.performance_history = []
        self.learning_rate = 0.1
        
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the data and return a strategy recommendation.
        
        Args:
            data: Historical data to analyze
            
        Returns:
            Dictionary containing the strategy details
        """
        pass
    
    @abstractmethod
    def update_strategy(self, performance: float, meeting_outcome: Dict[str, Any]) -> None:
        """
        Update the expert's strategy based on performance and meeting outcome.
        
        Args:
            performance: Performance metric from backtesting
            meeting_outcome: The consensus strategy from the meeting
        """
        pass
    
    def record_performance(self, performance: float) -> None:
        """
        Record the performance of the expert's strategy.
        
        Args:
            performance: Performance metric
        """
        self.performance_history.append(performance)
    
    def get_confidence(self) -> float:
        """
        Calculate the expert's confidence based on past performance.
        
        Returns:
            Confidence score between 0 and 1
        """
        if not self.performance_history:
            return 0.5  # Default confidence
        
        # Simple confidence calculation based on recent performance
        recent_perfs = self.performance_history[-3:]
        if len(recent_perfs) < 3:
            return 0.5
        
        # Scale to 0-1 range
        avg_perf = np.mean(recent_perfs)
        confidence = min(max(0.2 + avg_perf * 0.6, 0), 1)
        return confidence