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


# =====================================================================
# Additional tests: scoring math, ranking, strategies, diversity, profiles, CLI
# =====================================================================

import subprocess
from pathlib import Path

import pytest

from src import recommender
from src.main import PROFILES, SONGS_CSV, main as cli_main
from src.recommender import W_MAX, _split_tags

ROOT = Path(__file__).resolve().parent.parent

# A song and a profile built so every contribution is easy to work out by hand.
PERFECT_PREFS = {"genre": "pop", "mood": "happy", "energy": 0.8, "valence": 0.5,
                 "danceability": 0.5, "likes_acoustic": False, "tempo": 120.0}


def _song(**changes):
    base = {"id": 1, "title": "T", "artist": "A", "genre": "pop", "mood": "happy",
            "energy": 0.8, "tempo_bpm": 120.0, "valence": 0.5, "danceability": 0.5,
            "acousticness": 0.0, "popularity": 50, "release_decade": 2020,
            "mood_tags": ["calm", "sunny"], "instrumentalness": 0.5, "liveness": 0.5}
    base.update(changes)
    return base


@pytest.fixture(scope="module")
def catalog():
    return load_songs(str(SONGS_CSV))


# ---------- data ----------

def test_catalog_has_20_songs_with_unique_ids(catalog):
    assert len(catalog) == 20
    assert len({s["id"] for s in catalog}) == 20


def test_catalog_values_are_in_valid_ranges(catalog):
    for s in catalog:
        for name in ("energy", "valence", "danceability", "acousticness", "instrumentalness", "liveness"):
            assert 0.0 <= s[name] <= 1.0, (s["title"], name)
        assert 0 <= s["popularity"] <= 100
        assert s["release_decade"] in (1990, 2000, 2010, 2020)
        assert s["mood_tags"], s["title"]


def test_loader_converts_types_and_splits_tags(catalog):
    first = catalog[0]
    assert isinstance(first["tempo_bpm"], float)
    assert isinstance(first["popularity"], int)
    assert first["mood_tags"] == ["uplifting", "sunny", "danceable"]


def test_split_tags_handles_blank_and_case():
    assert _split_tags("") == []
    assert _split_tags(None) == []
    assert _split_tags(" Calm | COZY ") == ["calm", "cozy"]


# ---------- scoring math ----------

def test_perfect_song_scores_the_core_maximum():
    score, _ = score_song(PERFECT_PREFS, _song())
    assert score == 6.5


def test_energy_gap_removes_exactly_the_expected_points():
    score, _ = score_song(PERFECT_PREFS, _song(energy=0.6))
    assert score == pytest.approx(6.5 - 1.5 * 0.2)


def test_genre_and_mood_each_add_their_weight():
    both, _ = score_song(PERFECT_PREFS, _song())
    no_genre, _ = score_song(PERFECT_PREFS, _song(genre="rock"))
    no_mood, _ = score_song(PERFECT_PREFS, _song(mood="sad"))
    assert both - no_genre == pytest.approx(W_GENRE)
    assert both - no_mood == pytest.approx(W_MOOD)


def test_likes_acoustic_flips_the_acousticness_reward():
    acoustic_song = _song(acousticness=1.0)
    fan, _ = score_song({**PERFECT_PREFS, "likes_acoustic": True}, acoustic_song)
    other, _ = score_song({**PERFECT_PREFS, "likes_acoustic": False}, acoustic_song)
    assert fan - other == pytest.approx(0.5)


def test_tempo_similarity_is_zero_at_the_edge_of_the_range():
    near, _ = score_song(PERFECT_PREFS, _song(tempo_bpm=120.0))
    far, _ = score_song({**PERFECT_PREFS, "tempo": 40.0}, _song(tempo_bpm=220.0))
    assert near - far == pytest.approx(0.5, abs=0.01)


def test_reasons_add_up_to_the_score(catalog):
    for profile in PROFILES:
        for song in catalog:
            score, reasons = score_song(profile, song)
            total = sum(float(r.rsplit("(+", 1)[1].rstrip(")")) for r in reasons)
            assert total == pytest.approx(score, abs=0.011), (profile["key"], song["title"])


def test_score_never_exceeds_w_max(catalog):
    for profile in PROFILES:
        for song in catalog:
            assert score_song(profile, song)[0] <= W_MAX + 1e-9


# ---------- the five extra attributes really change the score ----------

@pytest.mark.parametrize("pref,close,far", [
    ("popularity", {"popularity": 80}, {"popularity": 20}),
    ("release_decade", {"release_decade": 2020}, {"release_decade": 1990}),
    ("instrumentalness", {"instrumentalness": 0.9}, {"instrumentalness": 0.1}),
    ("liveness", {"liveness": 0.9}, {"liveness": 0.1}),
])
def test_each_numeric_extra_attribute_changes_the_score(pref, close, far):
    prefs = {**PERFECT_PREFS, pref: list(close.values())[0]}
    good, _ = score_song(prefs, _song(**close))
    bad, _ = score_song(prefs, _song(**far))
    assert good > bad


def test_mood_tags_score_by_share_of_wanted_tags():
    prefs = {**PERFECT_PREFS, "mood_tags": ["calm", "sunny", "cozy", "warm"]}
    score, reasons = score_song(prefs, _song(mood_tags=["calm", "sunny"]))
    base, _ = score_song(PERFECT_PREFS, _song())
    assert score - base == pytest.approx(W_TAGS_VALUE * 2 / 4, abs=0.011)
    assert any("2 of 4 wanted" in r for r in reasons)


W_TAGS_VALUE = recommender.W_TAGS


def test_extras_are_skipped_when_the_profile_does_not_ask_for_them():
    score, reasons = score_song(PERFECT_PREFS, _song())
    assert not any(word in r for r in reasons for word in ("popularity", "decade", "tags", "liveness", "instrumentalness"))


def test_extras_are_skipped_when_a_song_has_no_data_for_them():
    prefs = {**PERFECT_PREFS, "release_decade": 2020, "mood_tags": ["calm"]}
    bare = {k: v for k, v in _song().items() if k not in ("release_decade", "mood_tags")}
    _, reasons = score_song(prefs, bare)
    assert not any("decade" in r or "tags" in r for r in reasons)


# ---------- ranking ----------

def test_ranking_is_sorted_and_returns_k(catalog):
    results = recommend_songs(PROFILES[0], catalog, k=7)
    scores = [s for _, s, _ in results]
    assert len(results) == 7 and scores == sorted(scores, reverse=True)


def test_k_larger_than_catalog_returns_everything(catalog):
    assert len(recommend_songs(PROFILES[0], catalog, k=100)) == 20


@pytest.mark.parametrize("k", [0, -3])
def test_nonpositive_k_returns_nothing(catalog, k):
    assert recommend_songs(PROFILES[0], catalog, k=k) == []


def test_empty_catalog_returns_nothing():
    assert recommend_songs(PROFILES[0], [], k=5) == []


def test_ties_keep_catalog_order():
    songs = [_song(id=2, title="Second"), _song(id=1, title="First")]
    results = recommend_songs(PERFECT_PREFS, songs, k=2)
    assert [s["title"] for s, _, _ in results] == ["Second", "First"]  # same score, input order kept


def test_recommend_songs_does_not_change_the_input_list(catalog):
    before = [s["title"] for s in catalog]
    recommend_songs(PROFILES[1], catalog, k=5, strategy="mood", artist_penalty=1.0)
    assert [s["title"] for s in catalog] == before


def test_explanations_name_real_scoring_terms(catalog):
    for _, _, explanation in recommend_songs(PROFILES[0], catalog, k=3):
        assert "genre match" in explanation or "energy" in explanation
        assert "(+" in explanation


# ---------- strategies ----------

def test_unknown_strategy_name_raises():
    with pytest.raises(ValueError):
        get_strategy("nonsense")


@pytest.mark.parametrize("mode", ["default", "genre", "mood", "energy"])
def test_every_strategy_returns_all_songs_exactly_once(catalog, mode):
    results = recommend_songs(PROFILES[2], catalog, k=20, strategy=mode)
    assert sorted(s["id"] for s, _, _ in results) == list(range(1, 21))


def test_genre_first_puts_every_genre_match_ahead_of_other_genres(catalog):
    results = recommend_songs(PROFILES[0], catalog, k=20, strategy="genre")
    genres = [s["genre"] == "pop" for s, _, _ in results]
    assert genres == sorted(genres, reverse=True)


def test_mood_first_puts_every_mood_match_ahead_of_other_moods(catalog):
    results = recommend_songs(PROFILES[1], catalog, k=20, strategy="mood")
    moods = [s["mood"] == "chill" for s, _, _ in results]
    assert moods == sorted(moods, reverse=True)


def test_energy_focused_orders_by_energy_closeness(catalog):
    target = PROFILES[0]["energy"]
    results = recommend_songs(PROFILES[0], catalog, k=20, strategy="energy")
    gaps = [round(abs(s["energy"] - target), 6) for s, _, _ in results]
    assert gaps == sorted(gaps)


def test_strategy_can_be_passed_as_an_object(catalog):
    by_name = recommend_songs(PROFILES[0], catalog, k=5, strategy="mood")
    by_object = recommend_songs(PROFILES[0], catalog, k=5, strategy=get_strategy("mood"))
    assert [s["id"] for s, _, _ in by_name] == [s["id"] for s, _, _ in by_object]


# ---------- diversity ----------

def _two_artist_catalog():
    return [_song(id=1, title="A-one", artist="Same"), _song(id=2, title="A-two", artist="Same", energy=0.78),
            _song(id=3, title="B-one", artist="Other", energy=0.7)]


def test_penalty_off_leaves_the_ranking_alone():
    results = recommend_songs(PERFECT_PREFS, _two_artist_catalog(), k=3)
    assert [s["title"] for s, _, _ in results] == ["A-one", "A-two", "B-one"]


def test_penalty_moves_a_repeat_artist_below_a_different_artist():
    results = recommend_songs(PERFECT_PREFS, _two_artist_catalog(), k=3, artist_penalty=1.0)
    assert [s["title"] for s, _, _ in results] == ["A-one", "B-one", "A-two"]


def test_penalty_is_explained_in_the_reasons_and_matches_the_score():
    plain = dict((s["title"], sc) for s, sc, _ in recommend_songs(PERFECT_PREFS, _two_artist_catalog(), k=3))
    results = recommend_songs(PERFECT_PREFS, _two_artist_catalog(), k=3, artist_penalty=1.0)
    row = [r for r in results if r[0]["title"] == "A-two"][0]
    assert "artist repeat penalty" in row[2] and "(-1.00)" in row[2]
    assert row[1] == pytest.approx(plain["A-two"] - 1.0)


def test_penalty_grows_with_each_earlier_song_by_the_same_artist():
    songs = [_song(id=i, title=f"S{i}", artist="Same", energy=0.8 - 0.01 * i) for i in range(1, 4)]
    results = recommend_songs(PERFECT_PREFS, songs, k=3, artist_penalty=0.5)
    third = results[2]
    assert "(-1.00)" in third[2]  # two earlier songs by the same artist, 2 x 0.5


def test_artist_names_are_compared_ignoring_case_and_spaces():
    songs = [_song(id=1, artist="Neon Echo"), _song(id=2, artist=" neon echo ", energy=0.79)]
    results = recommend_songs(PERFECT_PREFS, songs, k=2, artist_penalty=1.0)
    assert "artist repeat penalty" in results[1][2]


def test_penalty_works_on_the_real_catalog(catalog):
    lofi = PROFILES[1]
    plain = [s["title"] for s, _, _ in recommend_songs(lofi, catalog, k=5)]
    penalized = [s["title"] for s, _, _ in recommend_songs(lofi, catalog, k=5, artist_penalty=2.0)]
    assert plain != penalized and plain.index("Focus Flow") < penalized.index("Focus Flow")


# ---------- profiles and output ----------

def test_four_distinct_profiles_with_all_scored_features():
    assert len(PROFILES) == 4 and len({p["key"] for p in PROFILES}) == 4
    for p in PROFILES:
        for name in ("genre", "mood", "energy", "valence", "danceability", "tempo", "popularity",
                     "release_decade", "instrumentalness", "liveness", "mood_tags"):
            assert name in p


def test_profiles_get_their_own_top_song(catalog):
    top = {p["key"]: recommend_songs(p, catalog, k=1)[0][0]["genre"] for p in PROFILES}
    assert top == {"pop": "pop", "lofi": "lofi", "rock": "rock", "adversarial": "classical"}


def test_adversarial_profile_cannot_get_a_sad_song_with_high_energy(catalog):
    sad_and_loud = [s for s in catalog if s["mood"] == "melancholy" and s["energy"] >= 0.75]
    assert sad_and_loud == []


def test_cli_prints_a_table_with_reasons(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["main", "--profile", "lofi", "--k", "3"])
    cli_main()
    out = capsys.readouterr().out
    assert "Loaded 20 songs" in out and "Library Rain" in out and "Reasons" in out and "genre match: lofi" in out


def test_cli_penalty_flag_changes_the_header(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["main", "--profile", "rock", "--artist-penalty", "0"])
    cli_main()
    assert "artist penalty: 0.0" in capsys.readouterr().out


def test_module_entry_point_runs_from_the_project_folder():
    done = subprocess.run(["python", "-m", "src.main", "--profile", "pop", "--k", "3"],
                          cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert "Sunrise City" in done.stdout


def test_experiments_script_runs():
    done = subprocess.run(["python", "-m", "src.experiments"], cwd=ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert "EXPERIMENT 6" in done.stdout