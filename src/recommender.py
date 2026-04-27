import csv
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic with RAG and agentic workflow.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs
        self.rag_retriever = None
        self.agent = None

    def set_rag_retriever(self, retriever):
        """Set the RAG retriever for enhanced recommendations."""
        self.rag_retriever = retriever

    def set_agent(self, agent):
        """Set the agentic workflow engine."""
        self.agent = agent

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored: List[Tuple[Song, float, List[str]]] = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "valence": song.valence,
                "tempo_bpm": song.tempo_bpm,
                "danceability": song.danceability,
                "acousticness": song.acousticness,
            }
            user_prefs = {
                "genre": user.favorite_genre,
                "mood": user.favorite_mood,
                "energy": user.target_energy,
                "likes_acoustic": user.likes_acoustic,
            }
            score, reasons = score_song(user_prefs, song_dict)
            scored.append((song, score, reasons))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "valence": song.valence,
            "tempo_bpm": song.tempo_bpm,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _, reasons = score_song(user_prefs, song_dict)
        return "; ".join(reasons)


DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 2.0,
    "valence": 0.8,
    "tempo": 0.6,
    "danceability": 0.7,
    "acousticness": 0.5,
}


def _norm_str(value: Optional[str]) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _closeness_score(target: float, observed: float) -> float:
    """Returns a [0, 1] similarity score where 1 means perfect match."""
    gap = abs(target - observed)
    return max(0.0, 1.0 - gap)


def _tempo_similarity(target_energy: float, tempo_bpm: float) -> float:
    """Maps preferred energy to a rough preferred tempo, then scores closeness."""
    target_tempo = 60.0 + (target_energy * 100.0)
    gap = abs(target_tempo - tempo_bpm)
    return max(0.0, 1.0 - (gap / 80.0))


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
    include_mood: bool = True,
) -> Tuple[float, List[str]]:
    """Scores one song against a user profile and returns reasons for transparency."""
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w.update(weights)

    score = 0.0
    reasons: List[str] = []

    user_genre = _norm_str(user_prefs.get("genre"))
    song_genre = _norm_str(song.get("genre"))
    if user_genre and song_genre == user_genre:
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']:.2f})")

    if include_mood:
        user_mood = _norm_str(user_prefs.get("mood"))
        song_mood = _norm_str(song.get("mood"))
        if user_mood and song_mood == user_mood:
            score += w["mood"]
            reasons.append(f"mood match (+{w['mood']:.2f})")

    target_energy = float(user_prefs.get("energy", 0.5))
    song_energy = float(song.get("energy", 0.5))
    energy_points = _closeness_score(target_energy, song_energy) * w["energy"]
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    target_valence = float(user_prefs.get("valence", target_energy))
    song_valence = float(song.get("valence", 0.5))
    valence_points = _closeness_score(target_valence, song_valence) * w["valence"]
    score += valence_points
    reasons.append(f"valence closeness (+{valence_points:.2f})")

    song_tempo = float(song.get("tempo_bpm", 100.0))
    tempo_points = _tempo_similarity(target_energy, song_tempo) * w["tempo"]
    score += tempo_points
    reasons.append(f"tempo fit (+{tempo_points:.2f})")

    target_dance = float(user_prefs.get("danceability", target_energy))
    song_dance = float(song.get("danceability", 0.5))
    dance_points = _closeness_score(target_dance, song_dance) * w["danceability"]
    score += dance_points
    reasons.append(f"danceability fit (+{dance_points:.2f})")

    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))
    song_acoustic = float(song.get("acousticness", 0.5))
    if likes_acoustic:
        acoustic_points = song_acoustic * w["acousticness"]
        reasons.append(f"acoustic preference (+{acoustic_points:.2f})")
    else:
        acoustic_points = (1.0 - song_acoustic) * w["acousticness"]
        reasons.append(f"non-acoustic preference (+{acoustic_points:.2f})")
    score += acoustic_points

    return score, reasons

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    numeric_fields = {
        "id": int,
        "energy": float,
        "tempo_bpm": float,
        "valence": float,
        "danceability": float,
        "acousticness": float,
    }
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            song: Dict = {}
            for key, value in row.items():
                if key in numeric_fields and value is not None and value != "":
                    song[key] = numeric_fields[key](value)
                else:
                    song[key] = value
            songs.append(song)
    logger.info(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
    include_mood: bool = True,
    use_rag: bool = False,
    rag_retriever=None,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic with optional RAG.
    
    Args:
        user_prefs: User preference dictionary
        songs: List of song dictionaries
        k: Number of recommendations to return
        weights: Optional weight overrides
        include_mood: Whether to include mood in scoring
        use_rag: Whether to use RAG enrichment
        rag_retriever: RAG retriever instance
        
    Returns:
        List of (song_dict, score, explanation) tuples
    """
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights=weights, include_mood=include_mood)
        scored.append((song, score, "; ".join(reasons)))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    results = ranked[:k]
    
    # RAG enrichment: add contextual information
    if use_rag and rag_retriever:
        enriched_results = []
        for song, score, explanation in results:
            enriched = rag_retriever.enrich_recommendation(song, score, explanation.split("; "))
            enriched_results.append((song, score, explanation))
        results = enriched_results
    
    return results
