"""
Historical Context Module for MOE Trading System
Provides real-world events and context for 2014-2024 period
"""

from datetime import datetime
from typing import Dict, List, Any

class HistoricalContext:
    """
    Provides historical context and major events for trading decisions
    """
    
    def __init__(self):
        self.major_events = {
            # 2014
            "2014-01": "Oil price decline begins, Russia-Ukraine tensions (Crimea annexation)",
            "2014-07": "European Central Bank cuts rates to combat deflation",
            "2014-10": "Oil prices crash from $100+ to $60, affecting energy sector globally",
            
            # 2015
            "2015-01": "Swiss National Bank removes Euro peg, causing massive CHF spike",
            "2015-06": "Greece debt crisis peaks, threatens Eurozone stability",
            "2015-08": "China devalues Yuan, triggers global market selloff",
            "2015-12": "Fed raises rates for first time since 2008 financial crisis",
            
            # 2016
            "2016-01": "Oil hits 12-year lows below $30, market volatility spikes",
            "2016-06": "Brexit referendum shocks markets, GBP crashes 10%",
            "2016-11": "Trump election victory surprises markets, triggers 'Trump Rally'",
            
            # 2017
            "2017-01": "Trump inaugurated, promises tax cuts and deregulation",
            "2017-06": "Tech sector rally accelerates (FAANG stocks)",
            "2017-12": "Bitcoin reaches nearly $20,000, crypto bubble peaks",
            
            # 2018
            "2018-01": "Trade war with China begins, tariff threats",
            "2018-02": "Volatility spike ends low-vol regime, VIX hits 50",
            "2018-10": "Tech selloff intensifies, interest rate concerns grow",
            "2018-12": "Market correction continues, Fed pauses rate hikes",
            
            # 2019
            "2019-01": "Trade war escalation with China, supply chain concerns",
            "2019-07": "Fed cuts rates for first time since 2008",
            "2019-10": "Trade deal optimism boosts markets",
            
            # 2020
            "2020-01": "COVID-19 emerges in China, initial market complacency",
            "2020-03": "Global pandemic declared, markets crash 35% in weeks",
            "2020-03": "Fed cuts rates to zero, massive QE begins",
            "2020-04": "Oil goes negative for first time in history",
            "2020-11": "Vaccine breakthrough announcements, recovery rally begins",
            
            # 2021
            "2021-01": "Meme stock phenomenon (GameStop, AMC) disrupts markets",
            "2021-03": "Massive fiscal stimulus, inflation concerns emerge",
            "2021-11": "Supply chain crisis, inflation hits 6.8%",
            "2021-11": "Omicron variant discovered, market volatility returns",
            
            # 2022
            "2022-02": "Russia invades Ukraine, commodities spike",
            "2022-03": "Fed begins aggressive rate hiking cycle",
            "2022-06": "Inflation peaks at 9.1%, recession fears grow",
            "2022-11": "FTX crypto exchange collapses, contagion spreads",
            
            # 2023
            "2023-03": "Silicon Valley Bank fails, banking crisis emerges",
            "2023-03": "Credit Suisse rescued by UBS, systemic risk concerns",
            "2023-05": "Regional bank stress continues (First Republic fails)",
            "2023-11": "AI boom accelerates (ChatGPT, Nvidia surge)",
            
            # 2024
            "2024-01": "Election year uncertainty, political risk premium",
            "2024-03": "Fed maintains hawkish stance on inflation",
            "2024-06": "Economic data mixed, soft landing hopes persist"
        }
        
        self.market_regimes = {
            "2014": "Post-crisis recovery, low rates, oil crash",
            "2015": "Emerging market stress, China slowdown, first Fed hike",
            "2016": "Brexit shock, Trump surprise, reflation trade",
            "2017": "Synchronized global growth, low volatility, tax reform hopes",
            "2018": "Trade war escalation, rising rates, tech selloff",
            "2019": "Trade tensions peak, Fed pivots dovish, late cycle",
            "2020": "Pandemic crash and recovery, massive stimulus, zero rates",
            "2021": "Reopening boom, meme stocks, inflation emergence",
            "2022": "Aggressive Fed tightening, Ukraine war, bear market",
            "2023": "Banking crisis, AI revolution, resilient economy",
            "2024": "Election year, persistent inflation, Fed pause"
        }
    
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
            "market_sentiment_drivers": self._get_sentiment_drivers(date)
        }
        
        # Get events for this month and nearby months
        for key, event in self.major_events.items():
            event_year, event_month = key.split("-")
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
        """Get main risk factors for the time period"""
        year = date.year
        
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
        """Get main sentiment drivers for the time period"""
        year = date.year
        
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