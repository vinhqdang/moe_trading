#!/usr/bin/env python3
"""
Alternative Synthetic Scenarios for MOE Trading System
Testing system adaptability to different historical events
"""

from historical_context import HistoricalContext
from typing import Dict, List, Any
from datetime import datetime

class AlternativeScenarios:
    """
    Generate alternative historical scenarios to test system adaptability
    """
    
    def __init__(self):
        self.base_context = HistoricalContext()
        self.scenarios = {}
    
    def create_scenario_1_ukraine_invades_russia(self):
        """Scenario 1: Ukraine invades Russia (reverse of reality)"""
        modified_events = self.base_context.major_events.copy()
        modified_regimes = self.base_context.market_regimes.copy()
        
        # Modify 2022 events
        modified_events["2022-02"] = "Ukraine launches surprise invasion of Russia, global energy crisis"
        modified_events["2022-03"] = "Western nations support Ukraine, Russia isolated economically"
        modified_events["2022-06"] = "Ukrainian forces advance, commodities spike due to supply disruption"
        modified_events["2022-11"] = "Russian government instability, energy markets in chaos"
        
        modified_regimes["2022"] = "Ukrainian invasion of Russia, energy crisis, Western military support"
        
        return {
            "name": "Ukraine Invades Russia",
            "description": "Alternative scenario where Ukraine is the aggressor",
            "major_events": modified_events,
            "market_regimes": modified_regimes,
            "expected_impact": "Similar energy crisis but different geopolitical dynamics"
        }
    
    def create_scenario_2_southeast_asia_conflicts(self):
        """Scenario 2: Thailand-Cambodia War & Laos attacks Vietnam"""
        modified_events = self.base_context.major_events.copy()
        modified_regimes = self.base_context.market_regimes.copy()
        
        # Add Southeast Asian conflicts
        modified_events["2019-08"] = "Thailand-Cambodia border dispute escalates to armed conflict"
        modified_events["2019-10"] = "ASEAN supply chains disrupted, manufacturing crisis begins"
        modified_events["2020-01"] = "Laos launches military offensive against Vietnam"
        modified_events["2020-02"] = "Regional war spreads, global electronics supply chain collapse"
        modified_events["2020-06"] = "UN peacekeeping intervention in Southeast Asia"
        
        modified_regimes["2019"] = "Southeast Asian conflicts emerge, supply chain disruption"
        modified_regimes["2020"] = "Regional war expansion, electronics shortage, no COVID pandemic"
        
        return {
            "name": "Southeast Asian Wars",
            "description": "Thailand-Cambodia conflict + Laos-Vietnam war",
            "major_events": modified_events,
            "market_regimes": modified_regimes,
            "expected_impact": "Supply chain crisis without pandemic, different risk factors"
        }
    
    def create_scenario_3_china_bans_chips_to_us(self):
        """Scenario 3: China bans chip exports to US (reverse of reality)"""
        modified_events = self.base_context.major_events.copy()
        modified_regimes = self.base_context.market_regimes.copy()
        
        # Modify trade war dynamics
        modified_events["2018-01"] = "China initiates tech export restrictions to US"
        modified_events["2018-06"] = "China bans semiconductor exports to US, tech crisis begins"
        modified_events["2019-01"] = "US tech companies scramble for alternative chip sources"
        modified_events["2019-07"] = "China expands tech export bans, US manufacturing disrupted"
        modified_events["2020-03"] = "Global chip shortage intensifies, automotive industry collapses"
        
        modified_regimes["2018"] = "Chinese tech export restrictions, US supply crisis"
        modified_regimes["2019"] = "Semiconductor embargo escalation, tech sector panic"
        modified_regimes["2020"] = "Global chip shortage, no pandemic, industrial disruption"
        
        return {
            "name": "China Chips Ban",
            "description": "China bans semiconductor exports to US",
            "major_events": modified_events,
            "market_regimes": modified_regimes,
            "expected_impact": "Technology sector crisis, different from COVID impact"
        }
    
    def create_scenario_4_no_covid_pandemic(self):
        """Scenario 4: No COVID-19 pandemic"""
        modified_events = self.base_context.major_events.copy()
        modified_regimes = self.base_context.market_regimes.copy()
        
        # Remove COVID events and replace with different 2020 events
        del modified_events["2020-01"]
        del modified_events["2020-03"]
        del modified_events["2020-04"]
        del modified_events["2020-11"]
        
        # Replace with alternative 2020 events
        modified_events["2020-02"] = "Global climate summit leads to massive green energy investment"
        modified_events["2020-05"] = "Breakthrough in quantum computing announced, tech rally begins"
        modified_events["2020-08"] = "Space exploration surge, private companies launch moon missions"
        modified_events["2020-11"] = "US election leads to infrastructure spending boom"
        
        modified_regimes["2020"] = "Green energy revolution, quantum computing breakthrough, space economy"
        modified_regimes["2021"] = "Infrastructure boom, technology advancement, continued expansion"
        
        return {
            "name": "No COVID Pandemic",
            "description": "2020 without pandemic, alternative positive events",
            "major_events": modified_events,
            "market_regimes": modified_regimes,
            "expected_impact": "Continued bull market, technology-driven growth"
        }
    
    def create_scenario_5_european_debt_crisis_2020(self):
        """Scenario 5: European sovereign debt crisis in 2020"""
        modified_events = self.base_context.major_events.copy()
        modified_regimes = self.base_context.market_regimes.copy()
        
        # Replace COVID with European crisis
        modified_events["2020-01"] = "Italy defaults on sovereign debt, eurozone crisis begins"
        modified_events["2020-03"] = "Spain and Portugal debt downgrades, contagion spreads"
        modified_events["2020-04"] = "European banking crisis, ECB emergency interventions"
        modified_events["2020-06"] = "Euro currency crisis, potential eurozone breakup fears"
        modified_events["2020-09"] = "Germany considers eurozone exit, political crisis"
        
        modified_regimes["2020"] = "European sovereign debt crisis, eurozone instability"
        modified_regimes["2021"] = "EU reconstruction efforts, currency reforms, banking consolidation"
        
        return {
            "name": "European Debt Crisis 2020",
            "description": "Major European sovereign debt crisis instead of COVID",
            "major_events": modified_events,
            "market_regimes": modified_regimes,
            "expected_impact": "Financial system crisis, currency instability"
        }
    
    def create_scenario_6_oil_discovery_boom(self):
        """Scenario 6: Massive oil discovery boom replaces 2014 crash"""
        modified_events = self.base_context.major_events.copy()
        modified_regimes = self.base_context.market_regimes.copy()
        
        # Replace oil crash with discovery boom
        modified_events["2014-10"] = "Massive oil discoveries in West Africa, production surge begins"
        modified_events["2015-01"] = "Global oil surplus leads to energy price collapse, deflation fears"
        modified_events["2015-08"] = "Energy companies struggle with oversupply, sector consolidation"
        modified_events["2016-01"] = "Renewable energy boom as oil becomes too cheap to compete"
        
        modified_regimes["2014"] = "Oil discovery boom, production surge, price volatility"
        modified_regimes["2015"] = "Energy deflation, sector transformation, oversupply crisis"
        modified_regimes["2016"] = "Renewable energy acceleration, traditional energy collapse"
        
        return {
            "name": "Oil Discovery Boom",
            "description": "Massive oil discoveries create oversupply instead of scarcity",
            "major_events": modified_events,
            "market_regimes": modified_regimes,
            "expected_impact": "Energy sector transformation, deflationary pressures"
        }
    
    def create_scenario_7_ai_bubble_burst_2023(self):
        """Scenario 7: AI bubble bursts in 2023 instead of banking crisis"""
        modified_events = self.base_context.major_events.copy()
        modified_regimes = self.base_context.market_regimes.copy()
        
        # Replace banking crisis with AI bubble burst
        modified_events["2023-03"] = "ChatGPT found to be largely fraudulent, AI bubble bursts"
        modified_events["2023-05"] = "Nvidia earnings miss badly, tech sector crashes 60%"
        modified_events["2023-07"] = "AI companies admit technology limitations, investors flee"
        modified_events["2023-11"] = "Congressional hearings on AI fraud, regulation crackdown"
        
        modified_regimes["2023"] = "AI bubble burst, technology sector collapse, fraud investigations"
        modified_regimes["2024"] = "Tech sector rebuilding, realistic AI expectations, regulatory oversight"
        
        return {
            "name": "AI Bubble Burst 2023",
            "description": "AI revolution revealed as overhyped bubble",
            "major_events": modified_events,
            "market_regimes": modified_regimes,
            "expected_impact": "Technology sector crash, growth expectations reset"
        }
    
    def get_all_scenarios(self):
        """Get all alternative scenarios"""
        return {
            "scenario_1": self.create_scenario_1_ukraine_invades_russia(),
            "scenario_2": self.create_scenario_2_southeast_asia_conflicts(), 
            "scenario_3": self.create_scenario_3_china_bans_chips_to_us(),
            "scenario_4": self.create_scenario_4_no_covid_pandemic(),
            "scenario_5": self.create_scenario_5_european_debt_crisis_2020(),
            "scenario_6": self.create_scenario_6_oil_discovery_boom(),
            "scenario_7": self.create_scenario_7_ai_bubble_burst_2023()
        }

if __name__ == "__main__":
    scenarios = AlternativeScenarios()
    all_scenarios = scenarios.get_all_scenarios()
    
    print("Alternative Historical Scenarios for MOE Trading System Testing")
    print("=" * 70)
    
    for scenario_id, scenario in all_scenarios.items():
        print(f"\n{scenario_id.upper()}: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Expected Impact: {scenario['expected_impact']}")
        print("-" * 50)