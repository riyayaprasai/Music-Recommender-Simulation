"""Command line runner for the Music Recommender Simulation.

Usage:
    python -m src.main              # default ranking mode
    python -m src.main --mode genre # genre-first ranking mode
    python -m src.main --mode mood  # mood-first ranking mode
    python -m src.main --mode energy # energy-focused ranking mode
"""

import argparse
from tabulate import tabulate
from recommender import load_songs, score_song, recommend_songs, W_MAX
from strategy import get_strategy


PROFILES = [
    {
        "name": "High-Energy Pop Fan",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "valence": 0.80,
        "danceability": 0.80,
        "likes_acoustic": False,
        "tempo": 125.0,
    },
    {
        "name": "Chill Lofi Listener",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "valence": 0.60,
        "danceability": 0.55,
        "likes_acoustic": True,
        "tempo": 75.0,
    },
    {
        "name": "Intense Rock Enthusiast",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.90,
        "valence": 0.45,
        "danceability": 0.65,
        "likes_acoustic": False,
        "tempo": 150.0,
    },
    {
        "name": "Adversarial: Sad but High-Energy",
        "genre": "classical",
        "mood": "melancholy",
        "energy": 0.90,
        "valence": 0.30,
        "danceability": 0.25,
        "likes_acoustic": True,
        "tempo": 65.0,
    },
]


def format_profile(profile: dict) -> str:
    """Return a one-line summary of a profile's preferences."""
    parts = [
        f"genre={profile['genre']}",
        f"mood={profile['mood']}",
        f"energy={profile['energy']}",
        f"acoustic={'yes' if profile.get('likes_acoustic') else 'no'}",
        f"tempo={profile.get('tempo', 120)}bpm",
    ]
    return ", ".join(parts)


def apply_diversity_penalty(
    results: list, seen_artists: int = 2
) -> list:
    """Penalize repeated artists in the top results to reduce filter bubbles."""
    artist_count: dict = {}
    penalized = []
    for song, score, reasons in results:
        artist = song["artist"]
        count = artist_count.get(artist, 0)
        penalty = 0.0
        if count >= seen_artists:
            penalty = 0.5 * (count - seen_artists + 1)
        adjusted = round(max(0.0, score - penalty), 4)
        if penalty > 0:
            reasons_list = reasons.split("; ") if isinstance(reasons, str) else list(reasons)
            reasons_list.append(f"artist repeat penalty (-{penalty:.2f})")
            reasons = "; ".join(reasons_list)
        artist_count[artist] = count + 1
        penalized.append((song, adjusted, reasons))
    penalized.sort(key=lambda x: x[1], reverse=True)
    return penalized


def run_profile(profile: dict, songs: list, strategy_name: str, k: int = 5) -> list:
    """Score, re-rank, and apply diversity penalty for one profile."""
    scored_raw = []
    for song in songs:
        total, reasons = score_song(profile, song)
        scored_raw.append((song, total, reasons))

    strategy = get_strategy(strategy_name)
    ranked = strategy.rank(profile, scored_raw)
    top_k = ranked[:k]

    results = []
    for song, total, reasons in top_k:
        explanation = "; ".join(reasons) if isinstance(reasons, list) else reasons
        results.append((song, total, explanation))

    results = apply_diversity_penalty(results)
    return results


def print_results(profile: dict, results: list, mode: str) -> None:
    """Print a formatted table of recommendations for one profile."""
    print("=" * 80)
    print(f"  Profile: {profile['name']}")
    print(f"  Preferences: {format_profile(profile)}")
    print(f"  Ranking mode: {mode}")
    print("=" * 80)

    table_data = []
    for rank, (song, score, explanation) in enumerate(results, 1):
        table_data.append([
            rank,
            song["title"],
            song["artist"],
            f"{score:.2f}/{W_MAX:.1f}",
            explanation,
        ])

    print(tabulate(
        table_data,
        headers=["Rank", "Title", "Artist", "Score", "Reasons"],
        tablefmt="grid",
        maxcolwidths=[None, 20, 18, None, 45],
    ))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument(
        "--mode",
        choices=["default", "genre", "mood", "energy"],
        default="default",
        help="Ranking strategy to use (default: default)",
    )
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs from catalog.\n")

    for profile in PROFILES:
        results = run_profile(profile, songs, args.mode, k=5)
        print_results(profile, results, args.mode)


if __name__ == "__main__":
    main()
