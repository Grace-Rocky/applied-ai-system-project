"""
Agentic Workflow Module for Music Recommender.

This module implements an observable multi-step reasoning process where the AI agent:
1. Analyzes the user profile
2. Searches for matching songs
3. Evaluates and ranks results
4. Provides confidence scores
5. Verifies the recommendations
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStep(str, Enum):
    """Enumeration of agent workflow steps."""
    ANALYZE_PROFILE = "analyze_profile"
    RETRIEVE_CANDIDATES = "retrieve_candidates"
    SCORE_SONGS = "score_songs"
    RANK_RESULTS = "rank_results"
    VERIFY_RECOMMENDATIONS = "verify_recommendations"
    GENERATE_EXPLANATIONS = "generate_explanations"


@dataclass
class WorkflowAction:
    """Represents a single action in the agent workflow."""
    step: AgentStep
    input_data: Dict
    output_data: Dict
    confidence: float
    reasoning: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/display."""
        return {
            "step": self.step.value,
            "input": self.input_data,
            "output": self.output_data,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


class RecommendationAgent:
    """
    Agentic recommender with observable reasoning steps.
    
    This agent implements a transparent multi-step workflow that can be
    inspected and debugged, showing exactly what reasoning led to each recommendation.
    """
    
    def __init__(self, name: str = "MusicRecommender"):
        """Initialize the recommendation agent."""
        self.name = name
        self.workflow_history: List[WorkflowAction] = []
        logger.info(f"RecommendationAgent '{name}' initialized")
    
    def analyze_user_profile(self, user_prefs: Dict) -> WorkflowAction:
        """
        Step 1: Analyze the user profile to understand preferences.
        
        Args:
            user_prefs: User preference dictionary
            
        Returns:
            WorkflowAction describing the profile analysis
        """
        analysis = {
            "genre_preference": user_prefs.get("genre", "unknown"),
            "mood_preference": user_prefs.get("mood", "unknown"),
            "energy_level": user_prefs.get("energy", 0.5),
            "valence_expectation": user_prefs.get("valence", 0.5),
            "danceability_preference": user_prefs.get("danceability", 0.5),
            "acoustic_preference": user_prefs.get("likes_acoustic", False),
        }
        
        # Calculate confidence based on profile completeness
        provided_fields = sum(1 for k, v in user_prefs.items() if v is not None)
        total_fields = len(user_prefs)
        confidence = min(1.0, provided_fields / max(total_fields, 1))
        
        reasoning = (
            f"Analyzed user profile: prefers {analysis['genre_preference']} genre "
            f"with {analysis['mood_preference']} mood, "
            f"energy level {analysis['energy_level']:.2f}. "
            f"Acoustic preference: {'yes' if analysis['acoustic_preference'] else 'no'}"
        )
        
        action = WorkflowAction(
            step=AgentStep.ANALYZE_PROFILE,
            input_data=user_prefs,
            output_data=analysis,
            confidence=confidence,
            reasoning=reasoning
        )
        
        self.workflow_history.append(action)
        logger.info(f"Profile analysis: confidence={confidence:.2f}")
        return action
    
    def retrieve_candidate_songs(
        self,
        user_prefs: Dict,
        all_songs: List[Dict],
        rag_retriever=None
    ) -> WorkflowAction:
        """
        Step 2: Retrieve candidate songs matching user preferences.
        
        Args:
            user_prefs: User preference dictionary
            all_songs: List of all available songs
            rag_retriever: Optional RAG retriever for enhanced retrieval
            
        Returns:
            WorkflowAction describing the retrieval process
        """
        candidates = []
        selection_reasons = {}
        
        genre_pref = str(user_prefs.get("genre", "")).lower()
        mood_pref = str(user_prefs.get("mood", "")).lower()
        
        # Step 1: Filter by genre
        genre_matches = [s for s in all_songs 
                        if str(s.get("genre", "")).lower() == genre_pref]
        
        # Step 2: Filter by mood
        mood_matches = [s for s in all_songs 
                       if str(s.get("mood", "")).lower() == mood_pref]
        
        # Step 3: Combine and deduplicate
        # Step 3: Combine and deduplicate by song ID
        seen_ids = set()
        candidates = []
        for song in genre_matches + mood_matches:
            song_id = song.get("id")
            if song_id not in seen_ids:
                candidates.append(song)
                seen_ids.add(song_id)
        
        if not candidates:
            candidates = all_songs[:10]  # Fallback to first 10 if no matches
            selection_reasons["fallback"] = "No genre/mood matches found"
        else:
            selection_reasons["genre_matches"] = len(genre_matches)
            selection_reasons["mood_matches"] = len(mood_matches)
        
        # Enhance with RAG if available
        enhancements = 0
        if rag_retriever:
            rag_context = rag_retriever.get_retrieval_context_for_user(user_prefs)
            selection_reasons["rag_enhanced"] = True
            selection_reasons["rag_context"] = rag_context
            enhancements = len(rag_context.get("mood_based_suggestions", []))
        
        confidence = min(1.0, len(candidates) / 10.0)
        
        reasoning = (
            f"Retrieved {len(candidates)} candidate songs: "
            f"{len(genre_matches)} genre matches, {len(mood_matches)} mood matches. "
            f"{'RAG-enhanced with ' + str(enhancements) + ' contextual suggestions.' if enhancements else ''}"
        )
        
        action = WorkflowAction(
            step=AgentStep.RETRIEVE_CANDIDATES,
            input_data={"genres": genre_pref, "moods": mood_pref, "total_songs": len(all_songs)},
            output_data={
                "candidate_count": len(candidates),
                "candidate_ids": [c.get("id") for c in candidates[:5]],
                "selection_reasons": selection_reasons
            },
            confidence=confidence,
            reasoning=reasoning
        )
        
        self.workflow_history.append(action)
        logger.info(f"Candidate retrieval: {len(candidates)} candidates, confidence={confidence:.2f}")
        return action
    
    def score_and_rank(
        self,
        user_prefs: Dict,
        candidates: List[Dict],
        scoring_func
    ) -> WorkflowAction:
        """
        Step 3-4: Score and rank candidate songs.
        
        Args:
            user_prefs: User preference dictionary
            candidates: List of candidate songs
            scoring_func: Function to score a single song
            
        Returns:
            WorkflowAction describing scoring and ranking
        """
        scored_candidates = []
        
        for song in candidates:
            score, reasons = scoring_func(user_prefs, song)
            scored_candidates.append((song, score, reasons))
        
        # Rank by score
        ranked = sorted(scored_candidates, key=lambda x: x[1], reverse=True)
        
        # Calculate statistics
        scores = [s[1] for s in ranked]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        top_5_ids = [r[0].get("id") for r in ranked[:5]]
        
        confidence = min(1.0, max_score / 10.0)  # Normalize confidence
        
        reasoning = (
            f"Scored {len(candidates)} candidates. "
            f"Score range: {min_score:.2f} - {max_score:.2f}, "
            f"Average: {avg_score:.2f}. "
            f"Top 5 recommended: IDs {top_5_ids}"
        )
        
        action = WorkflowAction(
            step=AgentStep.SCORE_SONGS,
            input_data={"candidate_count": len(candidates)},
            output_data={
                "avg_score": avg_score,
                "max_score": max_score,
                "min_score": min_score,
                "top_ranked_ids": top_5_ids
            },
            confidence=confidence,
            reasoning=reasoning
        )
        
        self.workflow_history.append(action)
        logger.info(f"Scoring complete: avg={avg_score:.2f}, top_score={max_score:.2f}")
        
        return action
    
    def verify_recommendations(
        self,
        recommendations: List[Tuple],
        user_prefs: Dict
    ) -> WorkflowAction:
        """
        Step 5: Verify recommendations meet quality criteria.
        
        Args:
            recommendations: List of (song, score, explanation) tuples
            user_prefs: User preference dictionary
            
        Returns:
            WorkflowAction describing verification
        """
        verification_results = {
            "total_recommendations": len(recommendations),
            "all_different_songs": len(set(r[0].get("id") for r in recommendations)) == len(recommendations),
            "scores_in_range": all(0 <= r[1] <= 10 for r in recommendations),
            "has_explanations": all(len(r[2]) > 0 for r in recommendations),
            "genre_diversity": len(set(r[0].get("genre") for r in recommendations)),
            "mood_diversity": len(set(r[0].get("mood") for r in recommendations))
        }
        
        all_checks_passed = all(v for k, v in verification_results.items() 
                               if isinstance(v, bool))
        
        confidence = 1.0 if all_checks_passed else 0.7
        
        reasoning = (
            f"Verified {len(recommendations)} recommendations: "
            f"All unique songs ({verification_results['all_different_songs']}), "
            f"Scores in range ({verification_results['scores_in_range']}), "
            f"All explained ({verification_results['has_explanations']}), "
            f"Genre diversity: {verification_results['genre_diversity']}, "
            f"Mood diversity: {verification_results['mood_diversity']}"
        )
        
        action = WorkflowAction(
            step=AgentStep.VERIFY_RECOMMENDATIONS,
            input_data={"recommendation_count": len(recommendations)},
            output_data=verification_results,
            confidence=confidence,
            reasoning=reasoning
        )
        
        self.workflow_history.append(action)
        logger.info(f"Verification: all checks passed={all_checks_passed}")
        return action
    
    def run_workflow(
        self,
        user_prefs: Dict,
        all_songs: List[Dict],
        scoring_func,
        k: int = 5,
        rag_retriever=None
    ) -> Tuple[List[Tuple], List[WorkflowAction]]:
        """
        Run the complete agentic workflow.
        
        Args:
            user_prefs: User preference dictionary
            all_songs: List of all available songs
            scoring_func: Function to score a single song
            k: Number of recommendations to return
            rag_retriever: Optional RAG retriever for enhanced retrieval
            
        Returns:
            Tuple of (recommendations, workflow_actions)
        """
        # Reset workflow history
        self.workflow_history = []
        
        logger.info(f"Starting workflow for user with energy={user_prefs.get('energy')}")
        
        # Step 1: Analyze profile
        self.analyze_user_profile(user_prefs)
        
        # Step 2: Retrieve candidates
        self.retrieve_candidate_songs(user_prefs, all_songs, rag_retriever)
        
        # Step 3: Generate candidates for scoring
        genre_pref = str(user_prefs.get("genre", "")).lower()
        mood_pref = str(user_prefs.get("mood", "")).lower()
        candidates = [s for s in all_songs 
                     if str(s.get("genre", "")).lower() == genre_pref or 
                        str(s.get("mood", "")).lower() == mood_pref]
        
        if not candidates:
            candidates = all_songs
        
        # Step 4: Score and rank
        scored_candidates = []
        for song in candidates:
            score, reasons = scoring_func(user_prefs, song)
            scored_candidates.append((song, score, reasons))
        
        # Rank by score
        ranked = sorted(scored_candidates, key=lambda x: x[1], reverse=True)
        self.score_and_rank(user_prefs, candidates, scoring_func)
        
        # Step 5: Select top-k recommendations
        recommendations = ranked[:k]
        
        # Step 6: Verify recommendations
        self.verify_recommendations(recommendations, user_prefs)
        
        logger.info(f"Workflow complete: {len(recommendations)} recommendations generated")
        
        return recommendations, self.workflow_history
    
    def get_workflow_trace(self) -> List[Dict]:
        """Get the complete workflow trace for this agent."""
        return [action.to_dict() for action in self.workflow_history]
    
    def print_workflow_trace(self) -> None:
        """Print a human-readable workflow trace."""
        print("\n" + "="*80)
        print(f"AGENT WORKFLOW TRACE - {self.name}")
        print("="*80)
        
        for i, action in enumerate(self.workflow_history, 1):
            print(f"\nStep {i}: {action.step.value}")
            print(f"  Confidence: {action.confidence:.2f}")
            print(f"  Reasoning: {action.reasoning}")
            print(f"  Output Summary: {action.output_data}")
        
        print("\n" + "="*80 + "\n")
