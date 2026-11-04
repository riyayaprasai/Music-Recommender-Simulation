"""Core recommendation engine for the Music Recommender Simulation."""

import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# --- Weight constants (used by score_song and documented in README) ---
W_GENRE = 2.0
W_MOOD = 1.0
W_ENERGY = 1.5
W_VALENCE = 0.5
W_DANCE = 0.5
W_ACOUSTIC = 0.5
W_TEMPO = 0.5
W_MAX = W_GENRE + W_MOOD + W_ENERGY + W_VALENCE + W_DANCE + W_ACOUSTIC + W_TEMPO


@dataclass
class Song:
    """Represents a song and its attributes. Required by tests/test_recommender.py"""
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
    popularity: int = 0
    instrumentalness: float = 0.0
    liveness: float = 0.0


@dataclass
class UserProfile:
    """Represents a user's taste preferences. Required by tests/test_recommender.py"""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_danceability: float = 0.5
    target_valence: float = 0.5
    target_tempo: float = 120.0


TEMPO_MIN = 40.0
TEMPO_MAX = 220.0


class Recommender:
    """OOP implementation of the recommendation logic. Required by tests/test_recommender.py"""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Score a single Song object against a UserProfile."""
        score = 0.0
        if song.genre == user.favorite_genre:
            score += W_GENRE
        if song.mood == user.favorite_mood:
            score += W_MOOD
        score += W_ENERGY * (1.0 - abs(song.energy - user.target_energy))
        score += W_VALENCE * (1.0 - abs(song.valence - user.target_valence))
        score += W_DANCE * (1.0 - abs(song.danceability - user.target_danceability))
        if user.likes_acoustic:
            score += W_ACOUSTIC * song.acousticness
        else:
            score += W_ACOUSTIC * (1.0 - song.acousticness)
        tempo_range = TEMPO_MAX - TEMPO_MIN
        tempo_sim = 1.0 - abs(song.tempo_bpm - user.target_tempo) / tempo_range
        score += W_TEMPO * max(0.0, tempo_sim)
        return round(score, 4)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return top-k songs sorted by score descending."""
        scored = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song scored as it did."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre match (+{W_GENRE:.1f})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match (+{W_MOOD:.1f})")
        e_sim = 1.0 - abs(song.energy - user.target_energy)
        reasons.append(f"energy similarity (+{W_ENERGY * e_sim:.2f})")
        v_sim = 1.0 - abs(song.valence - user.target_valence)
        reasons.append(f"valence similarity (+{W_VALENCE * v_sim:.2f})")
        d_sim = 1.0 - abs(song.danceability - user.target_danceability)
        reasons.append(f"danceability similarity (+{W_DANCE * d_sim:.2f})")
        if user.likes_acoustic:
            reasons.append(f"acousticness preference (+{W_ACOUSTIC * song.acousticness:.2f})")
        else:
            reasons.append(f"low acousticness preference (+{W_ACOUSTIC * (1.0 - song.acousticness):.2f})")
        tempo_range = TEMPO_MAX - TEMPO_MIN
        t_sim = max(0.0, 1.0 - abs(song.tempo_bpm - user.target_tempo) / tempo_range)
        reasons.append(f"tempo similarity (+{W_TEMPO * t_sim:.2f})")
        total = self._score(user, song)
        return f"Score {total:.2f}/{W_MAX:.1f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file. Required by src/main.py"""
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row.get("popularity", 0)),
                "instrumentalness": float(row.get("instrumentalness", 0.0)),
                "liveness": float(row.get("liveness", 0.0)),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song against user preferences. Returns (score, reasons)."""
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += W_GENRE
        reasons.append(f"genre match (+{W_GENRE:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += W_MOOD
        reasons.append(f"mood match (+{W_MOOD:.1f})")

    energy_sim = 1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))
    score += W_ENERGY * energy_sim
    reasons.append(f"energy similarity (+{W_ENERGY * energy_sim:.2f})")

    valence_sim = 1.0 - abs(song["valence"] - user_prefs.get("valence", 0.5))
    score += W_VALENCE * valence_sim
    reasons.append(f"valence similarity (+{W_VALENCE * valence_sim:.2f})")

    dance_sim = 1.0 - abs(song["danceability"] - user_prefs.get("danceability", 0.5))
    score += W_DANCE * dance_sim
    reasons.append(f"danceability similarity (+{W_DANCE * dance_sim:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        acoustic_score = song["acousticness"]
    else:
        acoustic_score = 1.0 - song["acousticness"]
    score += W_ACOUSTIC * acoustic_score
    reasons.append(f"acousticness preference (+{W_ACOUSTIC * acoustic_score:.2f})")

    target_tempo = user_prefs.get("tempo", 120.0)
    tempo_range = TEMPO_MAX - TEMPO_MIN
    tempo_sim = max(0.0, 1.0 - abs(song["tempo_bpm"] - target_tempo) / tempo_range)
    score += W_TEMPO * tempo_sim
    reasons.append(f"tempo similarity (+{W_TEMPO * tempo_sim:.2f})")

    return (round(score, 4), reasons)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Functional implementation of the recommendation logic. Required by src/main.py"""
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    scored = []
    for song in songs:
        total, reasons = score_song(user_prefs, song)
        scored.append((song, total, reasons))
    scored.sort(key=lambda x: x[1], reverse=True)
    result = []
    for song, total, reasons in scored[:k]:
        explanation = "; ".join(reasons)
        result.append((song, total, explanation))
    return result
