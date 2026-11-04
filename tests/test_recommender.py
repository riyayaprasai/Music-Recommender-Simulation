import os
import sys

from src.recommender import (
    Song, UserProfile, Recommender,
    load_songs, score_song, recommend_songs,
    W_GENRE, W_MOOD,
)
from src.strategy import get_strategy, GenreFirstStrategy, MoodFirstStrategy, EnergyFocusedStrategy


# ---------- helpers ----------

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def _sample_songs() -> list:
    return [
        {
            "id": 1, "title": "Pop Hit", "artist": "A1",
            "genre": "pop", "mood": "happy", "energy": 0.8,
            "tempo_bpm": 120, "valence": 0.9, "danceability": 0.8,
            "acousticness": 0.2, "popularity": 80,
            "instrumentalness": 0.05, "liveness": 0.1,
        },
        {
            "id": 2, "title": "Lofi Chill", "artist": "A2",
            "genre": "lofi", "mood": "chill", "energy": 0.3,
            "tempo_bpm": 75, "valence": 0.5, "danceability": 0.4,
            "acousticness": 0.85, "popularity": 40,
            "instrumentalness": 0.9, "liveness": 0.05,
        },
        {
            "id": 3, "title": "Rock Anthem", "artist": "A3",
            "genre": "rock", "mood": "intense", "energy": 0.95,
            "tempo_bpm": 155, "valence": 0.4, "danceability": 0.6,
            "acousticness": 0.1, "popularity": 70,
            "instrumentalness": 0.15, "liveness": 0.35,
        },
    ]


_POP_USER = {"genre": "pop", "mood": "happy", "energy": 0.8}


# ---------- starter tests (kept passing) ----------

def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------- new tests ----------

def test_load_songs_returns_list_of_dicts():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
    songs = load_songs(csv_path)
    assert isinstance(songs, list)
    assert len(songs) >= 15
    assert isinstance(songs[0], dict)
    assert "title" in songs[0]
    assert "energy" in songs[0]
    assert isinstance(songs[0]["energy"], float)


def test_score_song_returns_float_and_reasons():
    song = _sample_songs()[0]
    score, reasons = score_song(_POP_USER, song)
    assert isinstance(score, float)
    assert isinstance(reasons, list)
    assert len(reasons) > 0
    assert all(isinstance(r, str) for r in reasons)


def test_score_song_genre_match_scores_higher():
    songs = _sample_songs()
    pop_song = songs[0]
    lofi_song = songs[1]
    pop_score, _ = score_song(_POP_USER, pop_song)
    lofi_score, _ = score_song(_POP_USER, lofi_song)
    assert pop_score > lofi_score, "Pop song should score higher for a pop-preferring user"


def test_recommend_songs_sorted_descending():
    songs = _sample_songs()
    results = recommend_songs(_POP_USER, songs, k=3)
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)


def test_recommend_songs_returns_k():
    songs = _sample_songs()
    results = recommend_songs(_POP_USER, songs, k=2)
    assert len(results) == 2


def test_strategy_factory_returns_correct_type():
    assert isinstance(get_strategy("genre"), GenreFirstStrategy)
    assert isinstance(get_strategy("mood"), MoodFirstStrategy)
    assert isinstance(get_strategy("energy"), EnergyFocusedStrategy)
