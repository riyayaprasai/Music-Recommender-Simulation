"""Reproducible experiments for the Music Recommender Simulation.

Run from the project folder with:  python -m src.experiments

Every number printed here comes from the real recommender, using the same profiles and
catalog as `python -m src.main`. Nothing is typed in by hand. The weight experiments work by
temporarily changing the W_* constants in src/recommender.py, which score_song reads each
time it runs, and then putting them back.
"""

import itertools
import statistics
from collections import Counter
from contextlib import contextmanager

from src import recommender
from src.main import PROFILES, SONGS_CSV
from src.recommender import load_songs, recommend_songs

SONGS = load_songs(str(SONGS_CSV))
MODES = ["default", "genre", "mood", "energy"]
EXTRA_WEIGHTS = ["W_POPULARITY", "W_DECADE", "W_TAGS", "W_INSTRUMENTAL", "W_LIVENESS"]
BAR = "=" * 90


@contextmanager
def weights(**overrides):
    """Temporarily sets recommender weight constants, then restores them."""
    saved = {name: getattr(recommender, name) for name in overrides}
    for name, value in overrides.items():
        setattr(recommender, name, value)
    try:
        yield
    finally:
        for name, value in saved.items():
            setattr(recommender, name, value)


def top(profile, mode="default", penalty=0.0, k=5):
    """Returns the recommended songs (dicts) for a profile."""
    return [s for s, _, _ in recommend_songs(profile, SONGS, k=k, strategy=mode, artist_penalty=penalty)]


def titles(songs):
    """Titles in order."""
    return [s["title"] for s in songs]


def show(label, profile, mode="default", penalty=0.0):
    """Prints one ranked list with scores."""
    print(f"  {label}")
    for i, (s, score, _) in enumerate(recommend_songs(profile, SONGS, k=5, strategy=mode, artist_penalty=penalty), 1):
        print(f"    {i}. {s['title']:<20} {s['artist']:<15} {s['genre']:<10} {score:5.2f}")


def main():
    print(BAR + "\nEXPERIMENT 1: four profiles, default ranking, no diversity penalty")
    base = {}
    for p in PROFILES:
        base[p["key"]] = top(p)
        show(f"{p['key']}: {p['name']}", p)

    print("\n" + BAR + "\nEXPERIMENT 2: profile pairs (top 5 overlap)")
    for a, b in itertools.combinations(PROFILES, 2):
        shared = [s["title"] for s in base[a["key"]] if s in base[b["key"]]]
        print(f"  {a['key']} vs {b['key']}: shared={len(shared)} {shared}")

    print("\n" + BAR + "\nEXPERIMENT 3: ranking modes (compared with default)")
    for p in PROFILES:
        print(f"  --- {p['key']}")
        for mode in MODES:
            got = top(p, mode)
            print(f"    {mode:<8} top1_same={got[0] == base[p['key']][0]} overlap={len([s for s in got if s in base[p['key']]])}/5 "
                  f"same_order={got == base[p['key']]}")
            print("        " + " > ".join(titles(got)))

    print("\n" + BAR + "\nEXPERIMENT 4: weight shift (genre 2.0 -> 1.0, energy 1.5 -> 3.0)")
    with weights(W_GENRE=1.0, W_ENERGY=3.0):
        for p in PROFILES:
            got = top(p)
            print(f"  {p['key']}: same_order={got == base[p['key']]}")
            print(f"      default: {titles(base[p['key']])}\n      shifted: {titles(got)}")

    print("\n" + BAR + "\nEXPERIMENT 5a: feature removal, mood weight set to 0")
    with weights(W_MOOD=0.0):
        for p in PROFILES:
            got = top(p)
            print(f"  {p['key']}: same_order={got == base[p['key']]}\n      default: {titles(base[p['key']])}\n      no mood: {titles(got)}")
    print("\nEXPERIMENT 5b: all five extra attributes set to 0")
    with weights(**{name: 0.0 for name in EXTRA_WEIGHTS}):
        for p in PROFILES:
            got = top(p)
            print(f"  {p['key']}: same_order={got == base[p['key']]}\n      default: {titles(base[p['key']])}\n      no extras: {titles(got)}")
    print("\nEXPERIMENT 5c: each extra attribute alone set to 0 (did the top-10 order change?)")
    ref10 = {p["key"]: top(p, k=10) for p in PROFILES}
    for name in EXTRA_WEIGHTS:
        with weights(**{name: 0.0}):
            changed = [p["key"] for p in PROFILES if top(p, k=10) != ref10[p["key"]]]
        print(f"  {name:<16} changed for: {changed or 'no profile'}")

    print("\n" + BAR + "\nEXPERIMENT 6: diversity (artist penalty), top 5 and top 10")
    for p in PROFILES:
        for k in (5, 10):
            for penalty in (0.0, 0.5, 1.0, 2.0):
                rows = recommend_songs(p, SONGS, k=k, strategy="default", artist_penalty=penalty)
                artists = Counter(s["artist"] for s, _, _ in rows)
                total = round(sum(score for _, score, _ in rows), 2)
                hit = [f"{s['title']} ({score:.2f})" for s, score, why in rows if "artist repeat penalty" in why]
                print(f"  {p['key']:<12} k={k:<2} penalty={penalty:<4} distinct_artists={len(artists)}/{k} "
                      f"score_total={total:<6} penalized={hit or 'none'}")
        for penalty in (0.0, 2.0):
            print(f"      k=5 penalty={penalty}: {titles(top(p, penalty=penalty))}")

    print("\n" + BAR + "\nCHECKS")
    print("genres:", dict(Counter(s["genre"] for s in SONGS)))
    print("moods :", dict(Counter(s["mood"] for s in SONGS)))
    print("artists with 2+ songs:", {a: n for a, n in Counter(s["artist"] for s in SONGS).items() if n > 1})
    energies = [s["energy"] for s in SONGS]
    print(f"energy: >=0.75: {sum(e >= 0.75 for e in energies)}, <=0.40: {sum(e <= 0.40 for e in energies)}, between: {sum(0.40 < e < 0.75 for e in energies)}")
    print(f"mean popularity: {statistics.mean(s['popularity'] for s in SONGS):.1f}")
    for p in PROFILES:
        got = base[p["key"]]
        print(f"  {p['key']:<12} genre matches in top5={sum(s['genre'] == p['genre'] for s in got)} "
              f"(catalog has {sum(s['genre'] == p['genre'] for s in SONGS)}); mean energy={statistics.mean(s['energy'] for s in got):.2f} (target {p['energy']})")
    print("max possible score:", round(recommender.W_MAX, 2))


if __name__ == "__main__":
    main()