"""Reliability and fact-checking framework for recommendation quality."""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Represents the result of a single recommendation evaluation."""

    user_profile_id: str
    recommendations: List[Dict]
    consistency_score: float
    coverage_score: float
    diversity_score: float
    confidence_score: float
    fact_check_score: float
    baseline_overlap_score: float
    overall_score: float
    verification_details: List[Dict]
    timestamp: str


class ReliabilityEvaluator:
    """Measures reliability and verifies recommendation claims with evidence."""

    def __init__(self):
        self.test_results: List[EvaluationResult] = []
        self.consistency_cache: Dict[str, List[List[int]]] = {}
        logger.info("Reliability Evaluator initialized")

    @staticmethod
    def _song_id(song_like: Any) -> int:
        return int(song_like.get("id") if isinstance(song_like, dict) else song_like.id)

    def evaluate_consistency(self, user_profile_id: str, recommendations: List[Tuple]) -> float:
        rec_ids = [self._song_id(rec[0]) for rec in recommendations]
        self.consistency_cache.setdefault(user_profile_id, []).append(rec_ids)

        if len(self.consistency_cache[user_profile_id]) < 2:
            return 1.0

        latest = set(rec_ids)
        previous_sets = [set(ids) for ids in self.consistency_cache[user_profile_id][:-1] if ids]
        if not previous_sets:
            return 1.0

        similarities: List[float] = []
        for prev_set in previous_sets:
            union = len(latest | prev_set)
            if union == 0:
                continue
            similarities.append(len(latest & prev_set) / union)

        return sum(similarities) / len(similarities) if similarities else 1.0

    def evaluate_coverage(self, recommendations: List[Tuple], total_catalog_size: int) -> float:
        if total_catalog_size <= 0:
            return 0.0
        unique_songs = len({self._song_id(rec[0]) for rec in recommendations})
        return min(1.0, unique_songs / min(total_catalog_size, 20))

    def evaluate_diversity(self, recommendations: List[Tuple], songs_data: List[Dict]) -> float:
        if len(recommendations) < 2:
            return 1.0

        genres: List[str] = []
        moods: List[str] = []
        artists: List[str] = []

        for rec in recommendations:
            song = rec[0]
            if isinstance(song, dict):
                genres.append(str(song.get("genre", "")))
                moods.append(str(song.get("mood", "")))
                artists.append(str(song.get("artist", "")))
            else:
                genres.append(str(song.genre))
                moods.append(str(song.mood))
                artists.append(str(song.artist))

        n = len(recommendations)
        genre_diversity = len(set(g for g in genres if g)) / n
        mood_diversity = len(set(m for m in moods if m)) / n
        artist_diversity = len(set(a for a in artists if a)) / n
        return (genre_diversity + mood_diversity + artist_diversity) / 3.0

    def evaluate_confidence(self, recommendations: List[Tuple]) -> float:
        if not recommendations:
            return 0.0
        confidences = [min(1.0, float(rec[1]) / 10.0) for rec in recommendations]
        return sum(confidences) / len(confidences)

    @staticmethod
    def _extract_explanation_text(explanation: Any) -> str:
        if isinstance(explanation, str):
            return explanation.lower()
        if isinstance(explanation, list):
            return "; ".join(str(item) for item in explanation).lower()
        return str(explanation).lower()

    def fact_check_recommendations(
        self,
        recommendations: List[Tuple],
        user_profile: Dict,
    ) -> Tuple[float, List[Dict]]:
        """Cross-verify explanation claims against structured song facts."""
        if not recommendations:
            return 0.0, []

        checks: List[Dict] = []
        passed = 0
        total = 0

        target_genre = str(user_profile.get("genre", "")).lower()
        target_mood = str(user_profile.get("mood", "")).lower()
        target_energy = float(user_profile.get("energy", 0.5))

        for rec in recommendations:
            song = rec[0]
            explanation = self._extract_explanation_text(rec[2])
            genre = str(song.get("genre", "") if isinstance(song, dict) else song.genre).lower()
            mood = str(song.get("mood", "") if isinstance(song, dict) else song.mood).lower()
            energy = float(song.get("energy", 0.5) if isinstance(song, dict) else song.energy)
            title = str(song.get("title", "unknown") if isinstance(song, dict) else song.title)

            song_checks = []

            if "genre match" in explanation:
                total += 1
                ok = genre == target_genre
                passed += int(ok)
                song_checks.append({"claim": "genre_match", "passed": ok, "evidence": genre})

            if "mood match" in explanation:
                total += 1
                ok = mood == target_mood
                passed += int(ok)
                song_checks.append({"claim": "mood_match", "passed": ok, "evidence": mood})

            if "energy closeness" in explanation:
                total += 1
                ok = abs(energy - target_energy) <= 0.30
                passed += int(ok)
                song_checks.append(
                    {
                        "claim": "energy_closeness",
                        "passed": ok,
                        "evidence": f"target={target_energy:.2f}, song={energy:.2f}",
                    }
                )

            checks.append({"song": title, "checks": song_checks})

        if total == 0:
            return 1.0, checks
        return passed / total, checks

    def evaluate_baseline_overlap(self, recommendations: List[Tuple], baseline_recommendations: List[Tuple]) -> float:
        if not recommendations and not baseline_recommendations:
            return 1.0
        ids_main = {self._song_id(rec[0]) for rec in recommendations}
        ids_base = {self._song_id(rec[0]) for rec in baseline_recommendations}
        union = len(ids_main | ids_base)
        if union == 0:
            return 1.0
        return len(ids_main & ids_base) / union

    def evaluate_recommendations(
        self,
        user_profile_id: str,
        recommendations: List[Tuple],
        songs_data: List[Dict],
        user_profile: Dict = None,
        baseline_recommendations: List[Tuple] = None,
    ) -> EvaluationResult:
        consistency = self.evaluate_consistency(user_profile_id, recommendations)
        coverage = self.evaluate_coverage(recommendations, len(songs_data))
        diversity = self.evaluate_diversity(recommendations, songs_data)
        confidence = self.evaluate_confidence(recommendations)

        if user_profile is None:
            user_profile = {}
        fact_check_score, verification_details = self.fact_check_recommendations(recommendations, user_profile)

        if baseline_recommendations is None:
            baseline_recommendations = recommendations
        baseline_overlap = self.evaluate_baseline_overlap(recommendations, baseline_recommendations)

        overall = (
            consistency * 0.20
            + coverage * 0.15
            + diversity * 0.15
            + confidence * 0.20
            + fact_check_score * 0.20
            + baseline_overlap * 0.10
        )

        result = EvaluationResult(
            user_profile_id=user_profile_id,
            recommendations=[
                {
                    "title": rec[0].get("title") if isinstance(rec[0], dict) else rec[0].title,
                    "score": rec[1],
                    "explanation": rec[2],
                }
                for rec in recommendations
            ],
            consistency_score=consistency,
            coverage_score=coverage,
            diversity_score=diversity,
            confidence_score=confidence,
            fact_check_score=fact_check_score,
            baseline_overlap_score=baseline_overlap,
            overall_score=overall,
            verification_details=verification_details,
            timestamp=datetime.now().isoformat(),
        )

        self.test_results.append(result)
        logger.info(
            "Evaluation complete: %.3f (C:%.2f Cv:%.2f D:%.2f F:%.2f B:%.2f)",
            overall,
            consistency,
            coverage,
            diversity,
            fact_check_score,
            baseline_overlap,
        )
        return result

    def get_summary(self) -> Dict[str, Any]:
        if not self.test_results:
            return {"error": "No evaluation results yet"}

        overall_scores = [r.overall_score for r in self.test_results]
        consistency_scores = [r.consistency_score for r in self.test_results]
        coverage_scores = [r.coverage_score for r in self.test_results]
        diversity_scores = [r.diversity_score for r in self.test_results]
        confidence_scores = [r.confidence_score for r in self.test_results]
        fact_scores = [r.fact_check_score for r in self.test_results]
        baseline_scores = [r.baseline_overlap_score for r in self.test_results]

        return {
            "total_evaluations": len(self.test_results),
            "average_overall_score": sum(overall_scores) / len(overall_scores),
            "average_consistency": sum(consistency_scores) / len(consistency_scores),
            "average_coverage": sum(coverage_scores) / len(coverage_scores),
            "average_diversity": sum(diversity_scores) / len(diversity_scores),
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "average_fact_check": sum(fact_scores) / len(fact_scores),
            "average_baseline_overlap": sum(baseline_scores) / len(baseline_scores),
            "min_overall_score": min(overall_scores),
            "max_overall_score": max(overall_scores),
            "test_results": [asdict(r) for r in self.test_results],
        }

    def export_results(self, filepath: str) -> None:
        summary = self.get_summary()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        logger.info("Results exported to %s", filepath)


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
        "genre": "electronic",
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
    evaluator: ReliabilityEvaluator = None,
    baseline_func=None,
) -> Dict[str, EvaluationResult]:
    """Run reliability suite and baseline cross-verification across scenarios."""
    if evaluator is None:
        evaluator = ReliabilityEvaluator()
    if baseline_func is None:
        baseline_func = recommend_func

    results: Dict[str, EvaluationResult] = {}

    for scenario_name, user_prefs in TEST_SCENARIOS.items():
        logger.info("Testing scenario: %s", scenario_name)
        recs_main = recommend_func(user_prefs, songs_data, k=7)
        recs_repeat = recommend_func(user_prefs, songs_data, k=7)
        recs_base = baseline_func(user_prefs, songs_data, k=7)

        # Feed repeat run to consistency cache so score reflects actual repeatability.
        evaluator.evaluate_consistency(scenario_name, recs_repeat)

        result = evaluator.evaluate_recommendations(
            user_profile_id=scenario_name,
            recommendations=recs_main,
            songs_data=songs_data,
            user_profile=user_prefs,
            baseline_recommendations=recs_base,
        )
        results[scenario_name] = result

    return results
