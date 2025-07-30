"""
Alternative Historical Context Module
Supports different synthetic scenarios for MOE Trading System testing
"""

from datetime import datetime
from typing import Dict, List, Any
from alternative_scenarios import AlternativeScenarios

class AlternativeHistoricalContext:
    """
    Historical context provider that can use alternative scenarios
    """
    
    def __init__(self, scenario_name: str = "baseline"):
        """
        Initialize with specific scenario
        
        Args:
            scenario_name: Name of scenario to use (baseline, scenario_1, etc.)
        """
        self.scenario_name = scenario_name
        self.scenarios = AlternativeScenarios()
        
        if scenario_name == "baseline":
            # Use original historical context
            from historical_context import HistoricalContext
            original = HistoricalContext()
            self.major_events = original.major_events
            self.market_regimes = original.market_regimes
        else:
            # Use alternative scenario
            all_scenarios = self.scenarios.get_all_scenarios()
            if scenario_name in all_scenarios:
                scenario_data = all_scenarios[scenario_name]
                self.major_events = scenario_data["major_events"]
                self.market_regimes = scenario_data["market_regimes"]
                self.scenario_description = scenario_data["description"]
            else:
                raise ValueError(f"Unknown scenario: {scenario_name}")
    
    def get_context_for_date(self, date: datetime) -> Dict[str, Any]:
        """
        Get relevant historical context for a specific date
        """
        year = str(date.year)
        month_key = f"{date.year}-{date.month:02d}"
        
        context = {
            "year": year,
            "regime": self.market_regimes.get(year, "Unknown period"),
            "major_events": [],
            "risk_factors": self._get_risk_factors(date),
            "market_sentiment_drivers": self._get_sentiment_drivers(date),
            "scenario": self.scenario_name
        }
        
        # Get events for this month and nearby months
        for key, event in self.major_events.items():
            event_parts = key.split("-")
            if len(event_parts) >= 2:
                event_year, event_month = event_parts[0], event_parts[1]
                if event_year == year:
                    event_date = datetime(int(event_year), int(event_month), 1)
                    days_diff = abs((date - event_date).days)
                    if days_diff <= 90:  # Include events within 3 months
                        context["major_events"].append({
                            "date": key,
                            "event": event,
                            "days_ago": (date - event_date).days
                        })
        
        return context
    
    def _get_risk_factors(self, date: datetime) -> List[str]:
        """Get main risk factors for the time period based on scenario"""
        year = date.year
        
        if self.scenario_name == "scenario_1":  # Ukraine invades Russia
            if year <= 2021:
                return ["Political uncertainty", "Trade policy changes", "Late cycle concerns"]
            elif year == 2022:
                return ["Ukrainian aggression", "Energy supply disruption", "Russian instability"]
            else:
                return ["Geopolitical realignment", "Energy transition", "Regional conflicts"]
                
        elif self.scenario_name == "scenario_2":  # Southeast Asian wars
            if year <= 2018:
                return ["Trade war escalation", "Brexit uncertainty", "Late cycle concerns"]
            elif year <= 2020:
                return ["Southeast Asian conflicts", "Supply chain collapse", "Electronics shortage"]
            else:
                return ["Regional instability", "Manufacturing relocation", "Supply diversification"]
                
        elif self.scenario_name == "scenario_3":  # China chips ban
            if year <= 2017:
                return ["Political uncertainty", "Trade policy changes", "Rising rates"]
            elif year <= 2020:
                return ["Chinese tech embargo", "Semiconductor shortage", "US tech crisis"]
            else:
                return ["Supply chain restructuring", "Technology decoupling", "Industrial disruption"]
                
        elif self.scenario_name == "scenario_4":  # No COVID
            if year <= 2019:
                return ["Trade war escalation", "Brexit uncertainty", "Late cycle concerns"]
            elif year == 2020:
                return ["Green energy transition", "Quantum computing breakthrough", "Space economy"]
            else:
                return ["Infrastructure spending", "Technology advancement", "Climate investment"]
                
        elif self.scenario_name == "scenario_5":  # European debt crisis 2020
            if year <= 2019:
                return ["Trade war escalation", "Brexit uncertainty", "Late cycle concerns"]
            elif year <= 2021:
                return ["European debt crisis", "Eurozone instability", "Currency crisis"]
            else:
                return ["EU reconstruction", "Banking consolidation", "Currency reform"]
                
        elif self.scenario_name == "scenario_6":  # Oil discovery boom
            if year <= 2016:
                return ["Energy oversupply", "Deflation fears", "Sector transformation"]
            else:
                return ["Renewable energy transition", "Traditional energy collapse", "Price volatility"]
                
        elif self.scenario_name == "scenario_7":  # AI bubble burst
            if year <= 2022:
                return ["Aggressive Fed tightening", "Ukraine war", "Energy crisis"]
            else:
                return ["AI bubble collapse", "Tech sector crash", "Fraud investigations"]
        
        # Default baseline factors
        if year <= 2015:
            return ["Oil price volatility", "China slowdown", "Fed policy normalization"]
        elif year <= 2017:
            return ["Political uncertainty", "Trade policy changes", "Rising rates"]
        elif year <= 2019:
            return ["Trade war escalation", "Brexit uncertainty", "Late cycle concerns"]
        elif year == 2020:
            return ["Pandemic impact", "Economic shutdown", "Unprecedented stimulus"]
        elif year == 2021:
            return ["Inflation emergence", "Supply chain disruption", "Policy normalization"]
        elif year == 2022:
            return ["Aggressive Fed tightening", "Ukraine war", "Energy crisis"]
        elif year == 2023:
            return ["Banking sector stress", "AI disruption", "Recession timing"]
        else:  # 2024
            return ["Election uncertainty", "Persistent inflation", "Geopolitical tensions"]
    
    def _get_sentiment_drivers(self, date: datetime) -> List[str]:
        """Get main sentiment drivers for the time period based on scenario"""
        year = date.year
        
        if self.scenario_name == "scenario_1":  # Ukraine invades Russia
            if year <= 2021:
                return ["Fed pivot hopes", "Growth concerns", "Policy uncertainty"]
            elif year == 2022:
                return ["Ukrainian aggression fears", "Energy crisis premium", "Russian instability"]
            else:
                return ["Geopolitical realignment", "Energy security concerns", "Regional stability"]
                
        elif self.scenario_name == "scenario_4":  # No COVID
            if year == 2020:
                return ["Green energy optimism", "Quantum computing enthusiasm", "Space economy excitement"]
            elif year == 2021:
                return ["Infrastructure optimism", "Technology advancement", "Climate investment enthusiasm"]
            else:
                return ["Continued expansion", "Innovation leadership", "Sustainable growth"]
        
        # Add other scenario-specific sentiment drivers as needed
        
        # Default baseline sentiment drivers
        if year <= 2015:
            return ["Central bank support", "Energy sector stress", "EM currency pressure"]
        elif year <= 2017:
            return ["Policy optimism", "Synchronized growth", "Low volatility regime"]
        elif year <= 2019:
            return ["Trade uncertainty", "Fed pivot hopes", "Growth concerns"]
        elif year == 2020:
            return ["Pandemic fear/hope cycles", "Fiscal/monetary response", "Vaccine developments"]
        elif year == 2021:
            return ["Reopening optimism", "Inflation concerns", "Meme stock mania"]
        elif year == 2022:
            return ["Hawkish Fed fears", "War premium", "Recession probability"]
        elif year == 2023:
            return ["Banking contagion fears", "AI enthusiasm", "Soft landing hopes"]
        else:  # 2024
            return ["Election positioning", "Fed pause expectations", "Earnings resilience"]