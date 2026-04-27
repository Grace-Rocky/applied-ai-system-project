"""
RAG (Retrieval-Augmented Generation) Module for Music Recommender.

This module implements retrieval-augmented generation to enrich recommendations
with contextual metadata about songs. It retrieves relevant song descriptions,
artist information, and thematic tags to provide more informed recommendations.
"""

from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Song metadata and descriptions for RAG
SONG_METADATA = {
    1: {
        "title": "Sunrise City",
        "description": "Uplifting electronic track with vibrant synth layers",
        "tags": ["uplifting", "electronic", "energetic", "urban"],
        "audio_features": "high-frequency synths with strong beat",
        "artist_style": "Neon Echo - known for pop-electronic fusion"
    },
    2: {
        "title": "Midnight Coding",
        "description": "Relaxing lo-fi beats perfect for focused work sessions",
        "tags": ["lo-fi", "chill", "focus-friendly", "study"],
        "audio_features": "smooth jazz-influenced loops with soft instruments",
        "artist_style": "LoRoom - specializes in ambient background music"
    },
    3: {
        "title": "Storm Runner",
        "description": "Intense rock with powerful guitars and aggressive drums",
        "tags": ["rock", "intense", "high-energy", "guitar-driven"],
        "audio_features": "distorted guitars with pounding percussion",
        "artist_style": "Voltline - rock band known for dynamic performances"
    },
    4: {
        "title": "Library Rain",
        "description": "Ambient lo-fi with rain sounds for deep relaxation",
        "tags": ["lo-fi", "ambient", "nature", "meditative"],
        "audio_features": "rain sfx with minimal piano and soft pads",
        "artist_style": "Paper Lanterns - creators of atmospheric soundscapes"
    },
    5: {
        "title": "Gym Hero",
        "description": "High-energy pop track designed to pump up workout sessions",
        "tags": ["pop", "workout", "motivational", "dance"],
        "audio_features": "pounding bass with catchy vocal hooks",
        "artist_style": "Max Pulse - fitness and motivational music specialist"
    },
    6: {
        "title": "Spacewalk Thoughts",
        "description": "Ethereal ambient composition evoking cosmic wonder",
        "tags": ["ambient", "cinematic", "spacey", "meditative"],
        "audio_features": "lush pads with reverb-heavy atmospheres",
        "artist_style": "Orbit Bloom - crafts expansive ambient worlds"
    },
    7: {
        "title": "Coffee Shop Stories",
        "description": "Warm jazz ideal for cafes and intimate gatherings",
        "tags": ["jazz", "relaxed", "warm", "social"],
        "audio_features": "upright bass and soft percussion with horn sections",
        "artist_style": "Slow Stereo - vintage-inspired jazz musicians"
    },
    8: {
        "title": "Night Drive Loop",
        "description": "Dark synthwave with moody vibes for late-night drives",
        "tags": ["synthwave", "80s-retro", "moody", "cinematic"],
        "audio_features": "vintage synths with dreamy reverb and pulsing bass",
        "artist_style": "Neon Echo - masters of retro-futuristic sound"
    },
    9: {
        "title": "Focus Flow",
        "description": "Minimal lo-fi beats optimized for concentration",
        "tags": ["lo-fi", "productivity", "minimal", "instrumental"],
        "audio_features": "sparse instrumentation with gentle beat",
        "artist_style": "LoRoom - experts in focus-enhancing compositions"
    },
    10: {
        "title": "Rooftop Lights",
        "description": "Indie pop with romantic and uplifting melodies",
        "tags": ["indie-pop", "happy", "romantic", "bittersweet"],
        "audio_features": "layered indie guitars with catchy hooks",
        "artist_style": "Indigo Parade - indie pop pioneers"
    },
    11: {
        "title": "Desert Bounce",
        "description": "Energetic afrobeat with infectious rhythms",
        "tags": ["afrobeat", "groovy", "danceable", "world-music"],
        "audio_features": "polyrhythmic drums with funky bass lines",
        "artist_style": "Mirage Unit - brings African rhythms to modern production"
    },
    12: {
        "title": "Velvet Thunder",
        "description": "Aggressive metal track with crushing distortion",
        "tags": ["metal", "aggressive", "heavy", "intense"],
        "audio_features": "distorted guitars and blast-beat drums",
        "artist_style": "Iron Chapel - extreme metal sound architects"
    },
    13: {
        "title": "Lantern Harbor",
        "description": "Warm folk acoustic with storytelling finger-picking",
        "tags": ["folk", "acoustic", "warm", "storytelling"],
        "audio_features": "fingerpicked acoustic guitar with soft vocals",
        "artist_style": "Blue Current - folk tradition meets modern production"
    },
    14: {
        "title": "Neon Alley Run",
        "description": "Fast-paced drum and bass for intense focus",
        "tags": ["drum-and-bass", "fast", "energetic", "intense"],
        "audio_features": "rapid breakbeats with dark bass lines",
        "artist_style": "City Prism - drum and bass innovators"
    },
    15: {
        "title": "Winter Letters",
        "description": "Serene classical piece for meditation and relaxation",
        "tags": ["classical", "peaceful", "instrumental", "meditative"],
        "audio_features": "orchestral arrangement with subtle dynamics",
        "artist_style": "Quiet Harbor - classical composers for modern listeners"
    },
    16: {
        "title": "Solar Parade",
        "description": "Vibrant electropop with infectious energy",
        "tags": ["electropop", "happy", "uplifting", "danceable"],
        "audio_features": "bright synths with dynamic electronic arrangement",
        "artist_style": "Luma Kid - electropop trend-setters"
    },
    17: {
        "title": "Porchlight Dreams",
        "description": "Nostalgic country with acoustic warmth",
        "tags": ["country", "nostalgic", "acoustic", "warm"],
        "audio_features": "country guitar with storytelling vocals",
        "artist_style": "Moss Thread - modern country traditionalists"
    },
    18: {
        "title": "Granite Pulse",
        "description": "Dark industrial track with mechanical textures",
        "tags": ["industrial", "dark", "experimental", "mechanical"],
        "audio_features": "harsh synths and metallic percussion",
        "artist_style": "Frame Collapse - industrial sound pioneers"
    }
}


class RAGRetriever:
    """
    Retrieval-Augmented Generation system for the music recommender.
    
    Retrieves contextual metadata about songs to enhance recommendations
    with explainability and thematic matching.
    """
    
    def __init__(self, metadata: Dict[int, Dict] = None):
        """Initialize the RAG retriever with song metadata."""
        self.metadata = metadata or SONG_METADATA
        logger.info(f"RAG Retriever initialized with {len(self.metadata)} songs")
    
    def retrieve_song_context(self, song_id: int) -> Optional[Dict]:
        """
        Retrieve rich contextual information about a specific song.
        
        Args:
            song_id: The ID of the song
            
        Returns:
            Dictionary with metadata or None if not found
        """
        return self.metadata.get(song_id)
    
    def retrieve_by_tags(self, target_tags: List[str], limit: int = 5) -> List[Tuple[int, Dict, int]]:
        """
        Retrieve songs matching target tags using tag-based retrieval.
        
        Args:
            target_tags: List of tags to search for
            limit: Maximum number of results
            
        Returns:
            List of (song_id, metadata, match_count) tuples
        """
        matches = []
        target_tags_lower = [tag.lower() for tag in target_tags]
        
        for song_id, metadata in self.metadata.items():
            song_tags = [tag.lower() for tag in metadata.get("tags", [])]
            match_count = sum(1 for tag in target_tags_lower if tag in song_tags)
            if match_count > 0:
                matches.append((song_id, metadata, match_count))
        
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches[:limit]
    
    def retrieve_by_mood(self, user_mood: str, limit: int = 5) -> List[Tuple[int, Dict]]:
        """
        Retrieve songs matching a user's current mood.
        
        Args:
            user_mood: The mood to search for
            limit: Maximum number of results
            
        Returns:
            List of (song_id, metadata) tuples
        """
        mood_keywords = {
            "happy": ["happy", "joyful", "uplifting"],
            "chill": ["chill", "relaxing", "meditative"],
            "focus": ["focus", "productivity", "instrumental"],
            "intense": ["intense", "aggressive", "high-energy"],
            "romantic": ["romantic", "warm", "bittersweet"],
            "dark": ["dark", "moody", "aggressive"]
        }
        
        search_keywords = mood_keywords.get(user_mood.lower(), [user_mood.lower()])
        matches = []
        
        for song_id, metadata in self.metadata.items():
            description = metadata.get("description", "").lower()
            tags = [tag.lower() for tag in metadata.get("tags", [])]
            audio_features = metadata.get("audio_features", "").lower()
            
            match_score = 0
            for keyword in search_keywords:
                if keyword in description:
                    match_score += 2
                if keyword in tags:
                    match_score += 2
                if keyword in audio_features:
                    match_score += 1
            
            if match_score > 0:
                matches.append((song_id, metadata, match_score))
        
        matches.sort(key=lambda x: x[2], reverse=True)
        return [(song_id, metadata) for song_id, metadata, _ in matches[:limit]]
    
    def enrich_recommendation(self, song: Dict, score: float, reasons: List[str]) -> Dict:
        """
        Enrich a recommendation with RAG context.
        
        Args:
            song: The song dictionary
            score: The recommendation score
            reasons: List of reason strings
            
        Returns:
            Enriched recommendation dictionary
        """
        song_id = int(song.get("id", 0))
        metadata = self.retrieve_song_context(song_id)
        
        enriched = {
            "song": song,
            "score": score,
            "reasons": reasons,
            "confidence": min(1.0, score / 10.0),  # Normalize confidence
        }
        
        if metadata:
            enriched["metadata"] = metadata
            enriched["description"] = metadata.get("description", "")
            enriched["tags"] = metadata.get("tags", [])
            enriched["artist_style"] = metadata.get("artist_style", "")
        
        return enriched
    
    def get_retrieval_context_for_user(self, user_prefs: Dict) -> Dict:
        """
        Retrieve contextual information relevant to a user's preferences.
        
        Args:
            user_prefs: User preference dictionary
            
        Returns:
            Dictionary with retrieved contextual information
        """
        genre = user_prefs.get("genre", "").lower()
        mood = user_prefs.get("mood", "").lower()
        
        # Retrieve songs by tags that match mood
        mood_matches = self.retrieve_by_mood(mood, limit=3)
        
        context = {
            "mood_based_suggestions": mood_matches,
            "genre_search": genre,
            "mood_search": mood,
            "contextual_hints": []
        }
        
        # Add contextual hints
        if mood in ["chill", "relaxed", "calm"]:
            context["contextual_hints"].append("Prefer songs with softer audio features")
        elif mood in ["intense", "aggressive", "powerful"]:
            context["contextual_hints"].append("Prefer songs with driving rhythms and high energy")
        
        return context
