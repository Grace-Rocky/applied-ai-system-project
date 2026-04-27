"""
Reliability and Evaluation Framework for Music Recommender.

This module implements comprehensive testing and evaluation mechanisms
to assess the reliability, consistency, and accuracy of the recommendation system.
"""

import logging
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, asdict
import json
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Represents the result of a single recommendation evaluation."""
    user_profile_id: str
    recommendations: List[Dict]
    consistency_score: float
    coverage_score: float
    diversity_score: float
    overall_score: float
    timestamp: str


class ReliabilityEvaluator:
    """
    Comprehensive evaluation framework for measuring recommender reliability.
    
    Measures:
    - Consistency: Same user gets same/similar recommendations
    - Coverage: Recommends diverse parts of the catalog
    - Diversity: Recommendations are varied enough
    - Confidence: Model's confidence in its recommendations
    """
    
    def __init__(self):
        """Initialize the evaluator."""
        self.test_results: List[EvaluationResult] = []
        self.consistency_cache: Dict[str, List] = {}
        logger.info("Reliability Evaluator initialized")
    
    def evaluate_consistency(self, user_profile_id: str, recommendations: List[Tuple]) -> float:
        """
        Evaluate consistency: does the recommender give consistent results?
        
        Args:
            user_profile_id: Identifier for the user profile
            recommendations: List of (song, score, explanation) tuples
            
        Returns:
            Consistency score [0.0, 1.0]
        """
        rec_ids = [rec[0].get("id") if isinstance(rec[0], dict) else rec[0].id 
                   for rec in recommendations]
        
        if user_profile_id not in self.consistency_cache:
            self.consistency_cache[user_profile_id] = []
        
        self.consistency_cache[user_profile_id].append(rec_ids)
        
        if len(self.consistency_cache[user_profile_id]) < 2:
            return 1.0  # Perfect consistency on first run
        
        # Compare latest recommendations with average of previous ones
        latest = set(rec_ids)
        previous_sets = [set(ids) for ids in self.consistency_cache[user_profile_id][:-1]]
        
        if not previous_sets:
            return 1.0
        
        # Calculate Jaccard similarity with previous runs
        similarities = []
        for prev_set in previous_sets:
            if not prev_set:
                continue
            intersection = len(latest & prev_set)
            union = len(latest | prev_set)
            similarity = intersection / union if union > 0 else 0.0
            similarities.append(similarity)
        
        consistency = sum(similarities) / len(similarities) if similarities else 1.0
        logger.debug(f"Consistency for {user_profile_id}: {consistency:.3f}")
        return consistency
    
    def evaluate_coverage(self, recommendations: List[Tuple], total_catalog_size: int) -> float:
        """
        Evaluate coverage: what percentage of the catalog is represented?
        
        Args:
            recommendations: List of (song, score, explanation) tuples
            total_catalog_size: Total number of songs in catalog
            
        Returns:
            Coverage score [0.0, 1.0]
        """
        if total_catalog_size == 0:
            return 0.0
        
        unique_songs = len(set(rec[0].get("id") if isinstance(rec[0], dict) else rec[0].id 
                               for rec in recommendations))
        coverage = unique_songs / min(total_catalog_size, 10)  # Normalize against top 10
        coverage = min(1.0, coverage)  # Cap at 1.0
        logger.debug(f"Coverage: {coverage:.3f} ({unique_songs}/{total_catalog_size})")
        return coverage
    
    def evaluate_diversity(self, recommendations: List[Tuple], songs_data: List[Dict]) -> float:
        """
        Evaluate diversity: are recommendations varied (different genres, moods, etc.)?
        
        Args:
            recommendations: List of (song, score, explanation) tuples
            songs_data: Full list of available songs
            
        Returns:
            Diversity score [0.0, 1.0]
        """
        if not recommendations or len(recommendations) < 2:
            return 1.0
        
        # Extract genre diversity
        genres = []
        moods = []
        
        for rec in recommendations:
            song = rec[0]
            if isinstance(song, dict):
                genres.append(song.get("genre", ""))
                moods.append(song.get("mood", ""))
            else:
                genres.append(song.genre)
                moods.append(song.mood)
        
        # Calculate unique ratio
        unique_genres = len(set(g for g in genres if g))
        unique_moods = len(set(m for m in moods if m))
        
        genre_diversity = unique_genres / len(recommendations)
        mood_diversity = unique_moods / len(recommendations)
        
        diversity = (genre_diversity + mood_diversity) / 2
        logger.debug(f"Diversity: {diversity:.3f} (genres: {genre_diversity:.2f}, moods: {mood_diversity:.2f})")
        return diversity
    
    def evaluate_confidence(self, recommendations: List[Tuple]) -> float:
        """
        Evaluate confidence: how confident is the model in its recommendations?
        
        Args:
            recommendations: List of (song, score, explanation) tuples
            
        Returns:
            Average confidence score [0.0, 1.0]
        """
        if not recommendations:
            return 0.0
        
        scores = [rec[1] for rec in recommendations]
        # Normalize scores to [0, 1] range (assuming max score is ~10)
        confidences = [min(1.0, score / 10.0) for score in scores]
        avg_confidence = sum(confidences) / len(confidences)
        logger.debug(f"Confidence: {avg_confidence:.3f}")
        return avg_confidence
    
    def evaluate_recommendations(
        self,
        user_profile_id: str,
        recommendations: List[Tuple],
        songs_data: List[Dict]
    ) -> EvaluationResult:
        """
        Perform complete evaluation of a set of recommendations.
        
        Args:
            user_profile_id: Identifier for the user profile
            recommendations: List of (song, score, explanation) tuples
            songs_data: Full list of available songs
            
        Returns:
            EvaluationResult with comprehensive metrics
        """
        consistency = self.evaluate_consistency(user_profile_id, recommendations)
        coverage = self.evaluate_coverage(recommendations, len(songs_data))
        diversity = self.evaluate_diversity(recommendations, songs_data)
        confidence = self.evaluate_confidence(recommendations)
        
        # Weighted overall score
        overall = (consistency * 0.3 + coverage * 0.2 + diversity * 0.2 + confidence * 0.3)
        
        result = EvaluationResult(
            user_profile_id=user_profile_id,
            recommendations=[
                {
                    "title": rec[0].get("title") if isinstance(rec[0], dict) else rec[0].title,
                    "score": rec[1],
                    "explanation": rec[2]
                }
                for rec in recommendations
            ],
            consistency_score=consistency,
            coverage_score=coverage,
            diversity_score=diversity,
            overall_score=overall,
            timestamp=datetime.now().isoformat()
        )
        
        self.test_results.append(result)
        logger.info(f"Evaluation complete: {overall:.3f} (C:{consistency:.2f} Cv:{coverage:.2f} D:{diversity:.2f})")
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all evaluation results.
        
        Returns:
            Dictionary with overall statistics
        """
        if not self.test_results:
            return {"error": "No evaluation results yet"}
        
        overall_scores = [r.overall_score for r in self.test_results]
        consistency_scores = [r.consistency_score for r in self.test_results]
        coverage_scores = [r.coverage_score for r in self.test_results]
        diversity_scores = [r.diversity_score for r in self.test_results]
        
        return {
            "total_evaluations": len(self.test_results),
            "average_overall_score": sum(overall_scores) / len(overall_scores),
            "average_consistency": sum(consistency_scores) / len(consistency_scores),
            "average_coverage": sum(coverage_scores) / len(coverage_scores),
            "average_diversity": sum(diversity_scores) / len(diversity_scores),
            "min_overall_score": min(overall_scores),
            "max_overall_score": max(overall_scores),
            "test_results": [asdict(r) for r in self.test_results]
        }
    
    def export_results(self, filepath: str) -> None:
        """
        Export evaluation results to JSON file.
        
        Args:
            filepath: Path to save the results
        """
        summary = self.get_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Results exported to {filepath}")


# Predefined test scenarios
TEST_SCENARIOS = {
    "high_energy_pop_lover": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "valence": 0.8,
        "danceability": 0.85,
        "likes_acoustic": False,
    },
    "chill_lofi_student": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "valence": 0.55,
        "danceability": 0.5,
        "likes_acoustic": True,
    },
    "intense_rock_fan": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.9,
        "valence": 0.45,
        "danceability": 0.55,
        "likes_acoustic": False,
    },
    "ambient_meditator": {
        "genre": "ambient",
        "mood": "calm",
        "energy": 0.2,
        "valence": 0.5,
        "danceability": 0.2,
        "likes_acoustic": True,
    },
    "workout_enthusiast": {
        "genre": "pop",
        "mood": "intense",
        "energy": 0.9,
        "valence": 0.7,
        "danceability": 0.85,
        "likes_acoustic": False,
    },
}


def run_reliability_tests(
    recommend_func,
    songs_data: List[Dict],
    evaluator: ReliabilityEvaluator = None
) -> Dict[str, EvaluationResult]:
    """
    Run a full reliability test suite on the recommender.
    
    Args:
        recommend_func: The recommendation function to test
        songs_data: List of available songs
        evaluator: ReliabilityEvaluator instance (created if None)
        
    Returns:
        Dictionary mapping scenario names to evaluation results
    """
    if evaluator is None:
        evaluator = ReliabilityEvaluator()
    
    results = {}
    
    for scenario_name, user_prefs in TEST_SCENARIOS.items():
        logger.info(f"Testing scenario: {scenario_name}")
        
        # Run recommendation twice to test consistency
        recs1 = recommend_func(user_prefs, songs_data, k=5)
        recs2 = recommend_func(user_prefs, songs_data, k=5)
        
        # Evaluate
        result = evaluator.evaluate_recommendations(
            user_profile_id=scenario_name,
            recommendations=recs1,
            songs_data=songs_data
        )
        results[scenario_name] = result
    
    return results
