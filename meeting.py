import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from expert import Expert
import random
import openai
import os
from datetime import datetime

# For Gemini API
import google.generativeai as genai

logger = logging.getLogger(__name__)

class ExpertMeeting:
    """
    Facilitates meetings between experts to reach consensus on a strategy.
    """
    def __init__(self, experts: List[Expert], max_rounds: int = 3, openai_key: str = None, gemini_key: str = None):
        """
        Initialize the meeting with a list of experts.
        
        Args:
            experts: List of Expert objects
            max_rounds: Maximum number of discussion rounds
            openai_key: OpenAI API key for generating expert discussions
        """
        self.experts = experts
        self.max_rounds = max_rounds
        self.meeting_log = []
        self.round = 0
        
        # Load API keys
        self.openai_key = openai_key
        self.gemini_key = gemini_key
        
        if not self.openai_key or not self.gemini_key:
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    if not self.openai_key:
                        self.openai_key = config.get('openai_api_key')
                    if not self.gemini_key:
                        self.gemini_key = config.get('gemini_api_key')
            except Exception as e:
                logger.warning(f"Failed to load API keys: {e}")
                
        # Configure Gemini if available
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini API configured successfully")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini API: {e}")
                self.gemini_key = None
    
    def hold_meeting(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Conduct a meeting between experts to reach consensus on a strategy.
        
        Args:
            data: Historical data to analyze
            
        Returns:
            Dictionary containing the consensus strategy
        """
        logger.info(f"Starting expert meeting with {len(self.experts)} experts")
        self.meeting_log = []
        self.round = 0
        
        # Get initial analyses from all experts
        expert_analyses = {}
        for expert in self.experts:
            analysis = expert.analyze(data)
            expert_analyses[expert.name] = analysis
            logger.info(f"{expert.name} initial analysis: {analysis['action']} (confidence: {analysis['confidence']:.2f})")
        
        consensus = None
        current_round = 0
        
        while current_round < self.max_rounds:
            current_round += 1
            self.round = current_round
            logger.info(f"\n--- Meeting Round {current_round} ---")
            
            # Generate discussion between experts using their analyses
            discussion = self._generate_expert_discussion(expert_analyses, current_round)
            
            # Log the discussion
            self.meeting_log.append({
                "round": current_round,
                "discussion": discussion,
                "expert_analyses": expert_analyses.copy()
            })
            logger.info(f"Round {current_round} discussion:\n{discussion}")
            
            # Try to reach consensus
            consensus = self._reach_consensus(expert_analyses)
            if consensus:
                logger.info(f"Consensus reached in round {current_round}: {consensus['action']}")
                break
                
            # If no consensus, update expert opinions based on the discussion
            expert_analyses = self._update_opinions(expert_analyses, discussion)
        
        if not consensus:
            # If no consensus after max rounds, use weighted voting
            logger.info("No consensus reached, using weighted voting")
            consensus = self._weighted_voting(expert_analyses)
            
        # Add final result to meeting log
        self.meeting_log.append({
            "round": "final",
            "consensus": consensus
        })
        
        return consensus
    
    def _generate_expert_discussion(self, expert_analyses: Dict[str, Any], round_num: int) -> str:
        """
        Generate a discussion between experts based on their analyses.
        Uses OpenAI API if available, otherwise generates a simulated discussion.
        
        Args:
            expert_analyses: Dictionary mapping expert names to their analyses
            round_num: Current round number
            
        Returns:
            String containing the discussion text
        """
        # Try different APIs in order of preference
        if self.gemini_key:
            try:
                return self._generate_gemini_discussion(expert_analyses, round_num)
            except Exception as e:
                logger.error(f"Error with Gemini API: {e}, falling back to OpenAI")
                
        if self.openai_key:
            try:
                return self._generate_openai_discussion(expert_analyses, round_num)
            except Exception as e:
                logger.error(f"Error with OpenAI API: {e}, falling back to simulated discussion")
                
        return self._generate_simulated_discussion(expert_analyses)
    
    def _generate_gemini_discussion(self, expert_analyses: Dict[str, Any], round_num: int) -> str:
        """
        Generate a realistic discussion between experts using Google's Gemini API.
        
        Args:
            expert_analyses: Dictionary mapping expert names to their analyses
            round_num: Current round number
            
        Returns:
            String containing the discussion text
        """
        # Format experts' analyses for the prompt
        expert_info = ""
        for name, analysis in expert_analyses.items():
            expert_info += f"{name}: Recommends '{analysis['action']}' with confidence {analysis['confidence']:.2f}. "
            expert_info += f"Reasoning: {analysis['reason']}.\n"
        
        # Create prompt for the discussion
        prompt = f"""
        Round {round_num} of an expert discussion about investment strategy.
        
        The experts are discussing what action to take (buy, sell, or hold) based on market data.
        
        Expert analyses:
        {expert_info}
        
        Generate a realistic discussion between these experts where they debate their views and try to persuade others. 
        Some should defend their positions, some should be swayed by others' arguments.
        The discussion should include technical points about their strategies, and show how they consider others' viewpoints.
        
        Expert Discussion:
        """
        
        response = self.gemini_model.generate_content(prompt)
        discussion = response.text
        return discussion
    
    def _generate_openai_discussion(self, expert_analyses: Dict[str, Any], round_num: int) -> str:
        """Generate a realistic discussion between experts using OpenAI."""
        try:
            openai.api_key = self.openai_key
            
            # Format experts' analyses for the prompt
            expert_info = ""
            for name, analysis in expert_analyses.items():
                expert_info += f"{name}: Recommends '{analysis['action']}' with confidence {analysis['confidence']:.2f}. "
                expert_info += f"Reasoning: {analysis['reason']}.\n"
            
            # Create prompt for the discussion
            prompt = f"""
            Round {round_num} of an expert discussion about investment strategy.
            
            The experts are discussing what action to take (buy, sell, or hold) based on market data.
            
            Expert analyses:
            {expert_info}
            
            Generate a realistic discussion between these experts where they debate their views and try to persuade others. 
            Some should defend their positions, some should be swayed by others' arguments.
            The discussion should include technical points about their strategies, and show how they consider others' viewpoints.
            
            Expert Discussion:
            """
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are simulating a meeting between financial strategy experts."},
                          {"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            discussion = response.choices[0].message.content.strip()
            return discussion
            
        except Exception as e:
            logger.error(f"Error generating discussion with OpenAI: {e}")
            # Fall back to simulated discussion
            return self._generate_simulated_discussion(expert_analyses)
    
    def _generate_simulated_discussion(self, expert_analyses: Dict[str, Any]) -> str:
        """Generate a simulated discussion when OpenAI is not available."""
        discussion = []
        
        # Get list of experts
        expert_names = list(expert_analyses.keys())
        
        # Simple turn-based discussion
        for i in range(len(expert_names)):
            current_expert = expert_names[i]
            analysis = expert_analyses[current_expert]
            
            # Basic statement from current expert
            statement = f"{current_expert}: I recommend we should {analysis['action']} because {analysis['reason']}."
            discussion.append(statement)
            
            # Add a response from another expert
            if len(expert_names) > 1:
                responder_idx = (i + 1) % len(expert_names)
                responder = expert_names[responder_idx]
                responder_analysis = expert_analyses[responder]
                
                if analysis['action'] == responder_analysis['action']:
                    response = f"{responder}: I agree with {current_expert}'s {analysis['action']} recommendation, but for different reasons: {responder_analysis['reason']}"
                else:
                    response = f"{responder}: I disagree with {current_expert}. I think we should {responder_analysis['action']} because {responder_analysis['reason']}"
                
                discussion.append(response)
        
        return "\n".join(discussion)
    
    def _reach_consensus(self, expert_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Try to reach consensus among experts.
        
        Args:
            expert_analyses: Dictionary mapping expert names to their analyses
            
        Returns:
            Consensus dict if reached, None otherwise
        """
        # Count votes for each action
        action_votes = {"buy": 0, "sell": 0, "hold": 0}
        confidence_sum = {"buy": 0, "sell": 0, "hold": 0}
        
        for name, analysis in expert_analyses.items():
            action = analysis["action"]
            confidence = analysis["confidence"]
            
            action_votes[action] += 1
            confidence_sum[action] += confidence
        
        # Check if any action has a strong majority (>60% of experts)
        total_experts = len(expert_analyses)
        consensus_threshold = 0.6
        
        for action, votes in action_votes.items():
            if votes / total_experts >= consensus_threshold:
                # Consensus reached
                avg_confidence = confidence_sum[action] / votes if votes > 0 else 0
                
                # Collect reasons from experts who voted for this action
                supporting_experts = [name for name, analysis in expert_analyses.items() 
                                     if analysis["action"] == action]
                
                supporting_reasons = [expert_analyses[name]["reason"] for name in supporting_experts]
                
                consensus = {
                    "action": action,
                    "confidence": avg_confidence,
                    "supporting_experts": supporting_experts,
                    "reasons": supporting_reasons,
                    "vote_ratio": votes / total_experts
                }
                
                return consensus
        
        # No consensus reached
        return None
    
    def _update_opinions(self, expert_analyses: Dict[str, Dict[str, Any]], discussion: str) -> Dict[str, Dict[str, Any]]:
        """
        Update expert opinions based on the discussion.
        
        Args:
            expert_analyses: Current expert analyses
            discussion: The discussion text
            
        Returns:
            Updated expert analyses
        """
        # In a real implementation, we would parse the discussion and adjust
        # expert opinions based on persuasive arguments
        
        # For now, implement a simple model where experts slightly shift toward majority opinion
        action_counts = {}
        for _, analysis in expert_analyses.items():
            action = analysis["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Find majority action
        majority_action = max(action_counts, key=action_counts.get)
        
        # Updated analyses
        updated_analyses = {}
        
        for name, analysis in expert_analyses.items():
            # Copy original analysis
            updated_analysis = analysis.copy()
            
            # Small chance to be persuaded by majority (unless already agreeing)
            if analysis["action"] != majority_action and random.random() < 0.3:
                # Adjust confidence before changing action
                updated_analysis["confidence"] *= 0.8  # Reduced confidence in new opinion
                updated_analysis["action"] = majority_action
                updated_analysis["reason"] = f"Reconsidered based on discussion and now agrees with {majority_action} recommendation"
            
            updated_analyses[name] = updated_analysis
            
        return updated_analyses
    
    def _weighted_voting(self, expert_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Make a decision using weighted voting when consensus isn't reached.
        
        Args:
            expert_analyses: Dictionary mapping expert names to their analyses
            
        Returns:
            Decision dict with action, confidence, etc.
        """
        # Calculate weighted votes for each action
        weighted_votes = {"buy": 0, "sell": 0, "hold": 0}
        
        for name, analysis in expert_analyses.items():
            action = analysis["action"]
            confidence = analysis["confidence"]
            
            weighted_votes[action] += confidence
        
        # Select action with highest weighted votes
        best_action = max(weighted_votes, key=weighted_votes.get)
        
        # Supporters of this action
        supporting_experts = [name for name, analysis in expert_analyses.items() 
                             if analysis["action"] == best_action]
        
        supporting_reasons = [expert_analyses[name]["reason"] for name in supporting_experts]
        
        # Calculate average confidence of supporting experts
        if len(supporting_experts) > 0:
            avg_confidence = sum(expert_analyses[name]["confidence"] for name in supporting_experts) / len(supporting_experts)
        else:
            avg_confidence = 0.5  # Default
            
        decision = {
            "action": best_action,
            "confidence": avg_confidence,
            "supporting_experts": supporting_experts,
            "reasons": supporting_reasons,
            "weighted_votes": weighted_votes,
            "consensus": False  # Indicate this was not a true consensus
        }
        
        return decision
    
    def get_meeting_log(self) -> List[Dict[str, Any]]:
        """
        Get the complete meeting log.
        
        Returns:
            List of meeting rounds with discussions
        """
        return self.meeting_log
    
    def save_meeting_log(self, filename: str = None) -> None:
        """
        Save the meeting log to a file.
        
        Args:
            filename: Name of file to save to
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_log_{timestamp}.json"
            
        with open(filename, 'w') as f:
            json.dump(self.meeting_log, f, indent=2)