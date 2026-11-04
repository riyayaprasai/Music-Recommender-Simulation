"""Core recommendation engine for the Music Recommender Simulation."""

import csv
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

def _split_tags(raw):
    """Convert pipe-, comma-, or semicolon-separated tags into lowercase lists."""
    if not raw:
        return []

    if isinstance(raw, str):
        raw = raw.replace(",", "|").replace(";", "|").split("|")

    return [
        str(tag).strip().lower()
        for tag in raw
        if str(tag).strip()
    ]

# --- Weight constants (used by score_song and documented in the README) ---
W_GENRE = 2.0
W_MOOD = 1.0
W_ENERGY = 1.5
W_VALENCE = 0.5
W_DANCE = 0.5
W_ACOUSTIC = 0.5
W_TEMPO = 0.5
# Five extra attributes. They only count when the user profile sets a target for them.
W_POPULARITY = 0.25
W_DECADE = 0.25
W_TAGS = 0.25
W_INSTRUMENTAL = 0.25
W_LIVENESS = 0.25
W_MAX = (W_GENRE + W_MOOD + W_ENERGY + W_VALENCE + W_DANCE + W_ACOUSTIC + W_TEMPO
         + W_POPULARITY + W_DECADE + W_TAGS + W_INSTRUMENTAL + W_LIVENESS)

TEMPO_MIN = 40.0
TEMPO_MAX = 220.0
POPULARITY_RANGE = 100.0
DECADE_RANGE = 30.0


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
    release_decade: int = 0
    mood_tags: Optional[List[str]] = None


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


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile object into the dictionary that score_song expects."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "valence": user.target_valence,
        "danceability": user.target_danceability,
        "likes_acoustic": user.likes_acoustic,
        "tempo": user.target_tempo,
    }


class Recommender:
    """OOP wrapper around the scoring logic. Required by tests/test_recommender.py"""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Scores one Song object by reusing score_song, so there is only one scoring formula."""
        return score_song(_profile_to_prefs(user), song.__dict__)[0]

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k songs sorted by score, highest first."""
        scored = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return scored[:max(k, 0)]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a plain-language breakdown of how a song earned its score."""
        total, reasons = score_song(_profile_to_prefs(user), song.__dict__)
        return f"Score {total:.2f}/{W_MAX:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from the CSV catalog."""
    songs = []

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(line for line in f if line.strip())

        if reader.fieldnames:
            reader.fieldnames = [
                name.strip().lstrip("\ufeff") for name in reader.fieldnames
            ]

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
                "popularity": int(row.get("popularity") or 0),
                "release_decade": int(row.get("release_decade") or 0),
                "mood_tags": _split_tags(row.get("mood_tags")),
                "instrumentalness": float(row.get("instrumentalness") or 0.0),
                "liveness": float(row.get("liveness") or 0.0),
            })

    return songs

def _closeness(target: float, value: float, span: float = 1.0) -> float:
    """Returns 1.0 when value equals target, falling to 0.0 as the gap reaches span."""
    return max(0.0, 1.0 - abs(target - value) / span)


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against user preferences and returns (score, reasons)."""
    parts: List[Tuple[float, str]] = []

    if song["genre"] == user_prefs.get("genre"):
        parts.append((W_GENRE, f"genre match: {song['genre']}"))
    if song["mood"] == user_prefs.get("mood"):
        parts.append((W_MOOD, f"mood match: {song['mood']}"))

    target = user_prefs.get("energy", 0.5)
    parts.append((W_ENERGY * _closeness(target, song["energy"]),
                  f"energy: song {song['energy']} vs target {target}"))
    target = user_prefs.get("valence", 0.5)
    parts.append((W_VALENCE * _closeness(target, song["valence"]),
                  f"valence: song {song['valence']} vs target {target}"))
    target = user_prefs.get("danceability", 0.5)
    parts.append((W_DANCE * _closeness(target, song["danceability"]),
                  f"danceability: song {song['danceability']} vs target {target}"))

    if user_prefs.get("likes_acoustic", False):
        parts.append((W_ACOUSTIC * song["acousticness"],
                      f"acoustic sound (acousticness {song['acousticness']})"))
    else:
        parts.append((W_ACOUSTIC * (1.0 - song["acousticness"]),
                      f"low acoustic sound (acousticness {song['acousticness']})"))

    target = user_prefs.get("tempo", 120.0)
    parts.append((W_TEMPO * _closeness(target, song["tempo_bpm"], TEMPO_MAX - TEMPO_MIN),
                  f"tempo: song {song['tempo_bpm']:g} vs target {target:g} BPM"))

    # Extra attributes: only scored when the profile asks for them and the song has the data.
    if "popularity" in user_prefs and song.get("popularity") is not None:
        parts.append((W_POPULARITY * _closeness(user_prefs["popularity"], song["popularity"], POPULARITY_RANGE),
                      f"popularity: song {song['popularity']} vs target {user_prefs['popularity']}"))
    if "release_decade" in user_prefs and song.get("release_decade"):
        parts.append((W_DECADE * _closeness(user_prefs["release_decade"], song["release_decade"], DECADE_RANGE),
                      f"release decade: song {song['release_decade']} vs target {user_prefs['release_decade']}"))
    if "instrumentalness" in user_prefs and song.get("instrumentalness") is not None:
        parts.append((W_INSTRUMENTAL * _closeness(user_prefs["instrumentalness"], song["instrumentalness"]),
                      f"instrumentalness: song {song['instrumentalness']} vs target {user_prefs['instrumentalness']}"))
    if "liveness" in user_prefs and song.get("liveness") is not None:
        parts.append((W_LIVENESS * _closeness(user_prefs["liveness"], song["liveness"]),
                      f"liveness: song {song['liveness']} vs target {user_prefs['liveness']}"))
    wanted = _split_tags(user_prefs.get("mood_tags"))
    have = _split_tags(song.get("mood_tags"))
    if wanted and have:
        shared = [t for t in wanted if t in have]
        parts.append((W_TAGS * len(shared) / len(wanted),
                      f"mood tags: {len(shared)} of {len(wanted)} wanted ({', '.join(shared) or 'none'})"))

    # Round each contribution first so the printed reasons add up exactly to the score.
    rounded = [(round(points, 2), text) for points, text in parts]
    score = round(sum(p for p, _ in rounded), 2)
    reasons = [f"{text} (+{points:.2f})" for points, text in rounded]
    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    strategy=None, artist_penalty: float = 0.0) -> List[Tuple[Dict, float, str]]:
    """Scores every song, ranks them with a strategy, and returns the top k as (song, score, explanation)."""
    # Imported here so strategy.py stays free of any dependency on this module.
    from src.strategy import get_strategy

    if k <= 0 or not songs:
        return []
    if strategy is None:
        strategy = get_strategy("default")
    elif isinstance(strategy, str):
        strategy = get_strategy(strategy)

    base = []
    for song in songs:
        total, reasons = score_song(user_prefs, song)
        base.append((song, total, reasons))

    chosen: List[Tuple[Dict, float, str]] = []
    picked_per_artist: Dict[str, int] = {}
    remaining = base
    while remaining and len(chosen) < k:
        # Re-apply the artist penalty on every round, so it is based on who is already in the list.
        adjusted = []
        for song, total, reasons in remaining:
            seen = picked_per_artist.get(song["artist"].strip().lower(), 0)
            if artist_penalty > 0 and seen:
                cut = round(artist_penalty * seen, 2)
                total = round(total - cut, 2)
                reasons = reasons + [f"artist repeat penalty: {song['artist']} already has {seen} song(s) in the list (-{cut:.2f})"]
            adjusted.append((song, total, reasons))
        song, total, reasons = strategy.rank(user_prefs, adjusted)[0]
        chosen.append((song, total, "; ".join(reasons)))
        key = song["artist"].strip().lower()
        picked_per_artist[key] = picked_per_artist.get(key, 0) + 1
        remaining = [item for item in remaining if item[0]["id"] != song["id"]]
    return chosen