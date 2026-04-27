from __future__ import annotations

from pathlib import Path
from collections import Counter
from typing import Any, Dict, List, Tuple

from flask import Flask, jsonify, render_template, request

from src.agent import RecommendationAgent
from src.evaluation import ReliabilityEvaluator, run_reliability_tests
from src.rag_retriever import RAGRetriever
from src.recommender import load_songs, recommend_songs, score_song

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "songs.csv"

app = Flask(__name__)

songs_data = load_songs(str(DATA_PATH))
rag_retriever = RAGRetriever()
rag_retriever.hydrate_from_songs(songs_data)
agent = RecommendationAgent(name="MusicCommandCenter")
evaluator = ReliabilityEvaluator()


def _normalize_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "genre": str(payload.get("genre", "pop")).strip().lower(),
        "mood": str(payload.get("mood", "happy")).strip().lower(),
        "energy": float(payload.get("energy", 0.7)),
        "valence": float(payload.get("valence", 0.7)),
        "danceability": float(payload.get("danceability", 0.7)),
        "likes_acoustic": bool(payload.get("likes_acoustic", False)),
    }


def _serialize_recommendations(
    recommendations: List[Tuple[Dict, float, Any]],
    profile: Dict[str, Any],
    use_rag: bool,
) -> List[Dict[str, Any]]:
    serialized: List[Dict[str, Any]] = []
    for song, score, explanation in recommendations:
        explanation_list = explanation if isinstance(explanation, list) else str(explanation).split("; ")
        row: Dict[str, Any] = {
            "song": song,
            "score": round(float(score), 4),
            "confidence": round(min(1.0, float(score) / 10.0), 4),
            "explanation": [part.strip() for part in explanation_list if str(part).strip()],
        }
        if use_rag:
            row["rag"] = rag_retriever.enrich_recommendation(song, float(score), row["explanation"])
        serialized.append(row)
    return serialized


def _catalog_insights() -> Dict[str, Any]:
    genre_counts = Counter(str(song.get("genre", "unknown")).title() for song in songs_data)
    mood_counts = Counter(str(song.get("mood", "unknown")).title() for song in songs_data)

    energy_buckets = {
        "Low": sum(1 for song in songs_data if float(song.get("energy", 0)) < 0.35),
        "Balanced": sum(1 for song in songs_data if 0.35 <= float(song.get("energy", 0)) < 0.7),
        "High": sum(1 for song in songs_data if float(song.get("energy", 0)) >= 0.7),
    }

    featured = sorted(
        songs_data,
        key=lambda song: (
            float(song.get("energy", 0)) * 0.35
            + float(song.get("danceability", 0)) * 0.35
            + float(song.get("valence", 0)) * 0.30
        ),
        reverse=True,
    )[:6]

    return {
        "genres": [{"label": label, "value": count} for label, count in genre_counts.most_common(8)],
        "moods": [{"label": label, "value": count} for label, count in mood_counts.most_common(8)],
        "energy_buckets": energy_buckets,
        "featured": [
            {
                "title": song.get("title"),
                "artist": song.get("artist"),
                "genre": song.get("genre"),
                "mood": song.get("mood"),
                "energy": song.get("energy"),
                "danceability": song.get("danceability"),
            }
            for song in featured
        ],
    }


@app.get("/")
def index():
    genres = sorted({str(song.get("genre", "")).lower() for song in songs_data if song.get("genre")})
    moods = sorted({str(song.get("mood", "")).lower() for song in songs_data if song.get("mood")})

    catalog_stats = {
        "songs": len(songs_data),
        "genres": len(genres),
        "moods": len(moods),
        "artists": len({song.get("artist") for song in songs_data}),
    }
    return render_template(
        "index.html",
        genres=genres,
        moods=moods,
        catalog_stats=catalog_stats,
    )


@app.get("/api/catalog/insights")
def api_catalog_insights():
    return jsonify(_catalog_insights())


@app.post("/api/recommend")
def api_recommend():
    payload = request.get_json(silent=True) or {}
    profile = _normalize_profile(payload.get("profile", {}))
    k = max(1, min(20, int(payload.get("k", 8))))
    use_rag = bool(payload.get("use_rag", True))
    use_agent = bool(payload.get("use_agent", True))

    if use_agent:
        recs, workflow = agent.run_workflow(
            user_prefs=profile,
            all_songs=songs_data,
            scoring_func=score_song,
            k=k,
            rag_retriever=rag_retriever if use_rag else None,
        )
        workflow_trace = [step.to_dict() for step in workflow]
    else:
        recs = recommend_songs(
            user_prefs=profile,
            songs=songs_data,
            k=k,
            use_rag=use_rag,
            rag_retriever=rag_retriever if use_rag else None,
        )
        workflow_trace = []

    return jsonify(
        {
            "profile": profile,
            "recommendations": _serialize_recommendations(recs, profile, use_rag),
            "workflow": workflow_trace,
            "catalog_size": len(songs_data),
        }
    )


@app.post("/api/evaluate")
def api_evaluate():
    baseline_func = lambda user_prefs, songs, k=7: recommend_songs(  # noqa: E731
        user_prefs,
        songs,
        k=k,
        include_mood=False,
    )

    results = run_reliability_tests(
        recommend_func=recommend_songs,
        songs_data=songs_data,
        evaluator=evaluator,
        baseline_func=baseline_func,
    )
    summary = evaluator.get_summary()

    return jsonify(
        {
            "summary": summary,
            "scenarios": {
                key: {
                    "overall": value.overall_score,
                    "consistency": value.consistency_score,
                    "coverage": value.coverage_score,
                    "diversity": value.diversity_score,
                    "confidence": value.confidence_score,
                    "fact_check": value.fact_check_score,
                    "baseline_overlap": value.baseline_overlap_score,
                    "verification_details": value.verification_details,
                    "top_recommendations": value.recommendations[:5],
                }
                for key, value in results.items()
            },
        }
    )


@app.post("/api/rag/search")
def api_rag_search():
    payload = request.get_json(silent=True) or {}
    query = str(payload.get("query", "")).strip()
    mood = str(payload.get("mood", "")).strip().lower()

    matches = rag_retriever.semantic_search(query, limit=8) if query else []
    mood_matches = rag_retriever.retrieve_by_mood(mood, limit=8) if mood else []

    formatted_semantic = [
        {
            "song_id": song_id,
            "score": round(score, 4),
            "metadata": metadata,
        }
        for song_id, metadata, score in matches
    ]

    formatted_mood = [
        {
            "song_id": song_id,
            "metadata": metadata,
        }
        for song_id, metadata in mood_matches
    ]

    return jsonify(
        {
            "query": query,
            "mood": mood,
            "semantic_matches": formatted_semantic,
            "mood_matches": formatted_mood,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
