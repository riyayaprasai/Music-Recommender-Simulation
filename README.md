# Music Recommender Simulation

## Project Summary

This project simulates a content-based music recommendation system. Given a catalog of 18 songs and a user's taste profile, it scores each song using weighted feature matching (genre, mood, energy, valence, danceability, acousticness, and tempo), ranks them, and returns the top recommendations with plain-language explanations. It supports multiple ranking strategies (genre-first, mood-first, energy-focused) via a Strategy design pattern and applies an artist diversity penalty to reduce filter bubbles.

---

## How The System Works

Production recommender systems like Spotify's combine collaborative filtering (what similar users listen to) and content-based filtering (what a song sounds like) to generate personalized suggestions. This project focuses on the content-based side only: given a user's preferences and a catalog of songs, score and rank each song by how well its attributes match what the user wants. No listening history from other users is involved.

### Input Data

The song catalog (`data/songs.csv`) contains 18 songs, each with 13 attributes: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness, popularity, instrumentalness, and liveness.

### User Preferences

A user profile specifies:

| Preference | Type | Example |
|---|---|---|
| `genre` | Categorical | "pop" |
| `mood` | Categorical | "happy" |
| `energy` | Numerical (0.0-1.0) | 0.85 |
| `valence` | Numerical (0.0-1.0) | 0.80 |
| `danceability` | Numerical (0.0-1.0) | 0.80 |
| `likes_acoustic` | Boolean | False |
| `tempo` | BPM (40-220) | 125 |

### Scoring Algorithm

Each song starts at 0 points. The system adds:

| Condition | Weight | Points |
|---|---|---|
| Song genre matches user's preferred genre | 2.0 | +2.0 (binary) |
| Song mood matches user's preferred mood | 1.0 | +1.0 (binary) |
| Energy similarity: `1 - abs(song - target)` | 1.5 | +0.0 to +1.5 |
| Valence similarity: `1 - abs(song - target)` | 0.5 | +0.0 to +0.5 |
| Danceability similarity: `1 - abs(song - target)` | 0.5 | +0.0 to +0.5 |
| Acousticness: song value if user likes acoustic, else `1 - value` | 0.5 | +0.0 to +0.5 |
| Tempo similarity: normalized distance within 40-220 BPM range | 0.5 | +0.0 to +0.5 |

**Maximum possible score: 6.5**

Songs are sorted descending by total score. An artist diversity penalty (-0.5 per repeat beyond 2 appearances) reduces filter bubbles.

### Ranking Modes

The system supports four ranking strategies via the `--mode` CLI flag:

- **default** — sort by total score only
- **genre** — genre-matching songs float to the top, then sorted by score
- **mood** — mood-matching songs float to the top, then sorted by score
- **energy** — songs closest to target energy float to the top, then sorted by score

### Expected Bias

Because genre match carries the highest weight (2.0 out of 6.5), the system is biased toward same-genre recommendations and will underrank songs from other genres even when their mood and energy are a near-perfect match. The diversity penalty partially mitigates this by preventing the same artist from dominating results.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

4. Run with a specific ranking mode:

```bash
python -m src.main --mode genre
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

[PASTE REAL TERMINAL OUTPUT HERE AFTER RUNNING: python -m src.main]

---

## Experiments You Tried

[PASTE YOUR EXPERIMENTS HERE. For example:]

- [What happened when you changed the weight on genre from 2.0 to 0.5]
- [What happened when you ran --mode genre vs --mode energy]
- [How did the adversarial profile (classical + melancholy + high energy) behave]
- [What happened when you removed the diversity penalty]

---

## Limitations and Risks

- **Small catalog**: With only 18 songs, recommendations are heavily constrained. Most genres have only 1-2 representatives, so a genre match often returns the same song regardless of other preferences.
- **Binary categorical matching**: Genre and mood are exact-match only. "Indie pop" gets zero credit for matching a "pop" preference, even though they overlap musically.
- **No collaborative signal**: The system only knows about song attributes, not what other similar users enjoy. It cannot discover songs through social patterns.
- **Acousticness is coarse**: The `likes_acoustic` boolean is too simple. A user might prefer moderate acousticness (0.5) rather than maximum or minimum.

---

## Reflection

[**Model Card**](model_card.md)

[WRITE 1-2 PARAGRAPHS HERE ABOUT WHAT YOU LEARNED:
- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this]
