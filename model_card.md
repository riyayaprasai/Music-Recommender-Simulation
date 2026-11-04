# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0** — A content-based music recommender simulation.

---

## 2. Intended Use

VibeFinder is designed to simulate how streaming platforms recommend music based on song attributes. It is a classroom exploration tool, not a production system. It takes a user's taste profile (preferred genre, mood, energy level, and other preferences) and returns a ranked list of song suggestions from a small catalog with explanations for each recommendation.

**Not intended for**: real music streaming, commercial recommendations, or handling real user data. It is a learning exercise to understand how recommendation algorithms work.

---

## 3. How the Model Works

The system uses a weighted scoring approach. For every song in the catalog, it checks how well the song matches the user's preferences across seven features:

1. **Genre match** (worth the most — 2.0 points): Does the song's genre exactly match what the user prefers?
2. **Mood match** (1.0 point): Does the song's mood tag match the user's preferred mood?
3. **Energy similarity** (up to 1.5 points): How close is the song's energy level to the user's target? A perfect match gets full points; the further away, the fewer points.
4. **Valence similarity** (up to 0.5 points): How close is the song's musical positivity to the user's target?
5. **Danceability similarity** (up to 0.5 points): How close is the song's danceability to the user's target?
6. **Acousticness preference** (up to 0.5 points): If the user likes acoustic music, songs with higher acousticness score better. If not, less acoustic songs score better.
7. **Tempo similarity** (up to 0.5 points): How close is the song's BPM to the user's preferred tempo, normalized across a 40-220 BPM range?

The maximum score is 6.5 points. After scoring, the system can optionally re-rank results using different strategies (genre-first, mood-first, or energy-focused) and applies a diversity penalty to prevent the same artist from appearing too many times.

---

## 4. Data

The model uses a catalog of **18 songs** stored in `data/songs.csv` with 13 attributes each. The dataset covers **15 genres** (pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, r&b, electronic, country, classical, latin, metal, world) and **14 moods** (happy, chill, intense, relaxed, moody, focused, aggressive, romantic, euphoric, nostalgic, melancholy, playful, angry, mysterious).

**Limitations of the data**: The catalog is very small. Most genres have only 1-2 songs, which means recommendations within a genre are extremely limited. The dataset does not include lyrics, language, release year, or user listening history. All numerical attributes were assigned manually, not derived from audio analysis.

---

## 5. Strengths

- **Works well for clear-preference users**: When a user has a strong genre and mood preference (e.g., "pop + happy + high energy"), the system reliably surfaces the best matches. The Gym Hero and Sunrise City songs consistently top the list for pop-happy profiles, which matches intuition.
- **Energy similarity is effective**: The linear distance formula (`1 - abs(song - target)`) provides smooth differentiation. Songs with energy 0.82 score noticeably higher than songs at 0.35 for a user targeting 0.8.
- **Explanations are transparent**: Every recommendation includes a breakdown showing exactly which features contributed points and how many, making it easy to verify the logic.
- **Diversity penalty works**: Without it, an artist with multiple songs in the catalog could dominate the results. The penalty ensures variety.

---

## 6. Limitations and Bias

- **Genre dominance**: Genre match is worth 2.0 out of 6.5 points (31% of the max score). This means a mediocre match in the right genre often outranks a great match in the wrong genre. For example, a lofi song with mismatched energy still beats a rock song with perfect energy for a lofi-preferring user.
- **Small catalog bias**: With only 1-2 songs per genre, the system cannot provide meaningful variety within a genre. A real recommender would have thousands of options.
- **Binary categorical matching**: "Indie pop" receives zero credit for matching "pop," even though they are closely related genres. There is no concept of genre similarity or hierarchy.
- **Acousticness oversimplification**: The boolean `likes_acoustic` forces a binary choice. A user who enjoys moderate acousticness (say, 0.5) has no way to express that preference.
- **No collaborative signal**: The system has no concept of "users like you also enjoyed..." It can only match on song attributes.

---

## 7. Evaluation

I tested the system with four user profiles:

1. **High-Energy Pop Fan** (genre=pop, mood=happy, energy=0.85): Expected pop songs to dominate. [FILL FROM REAL OUTPUT]
2. **Chill Lofi Listener** (genre=lofi, mood=chill, energy=0.35): Expected lofi songs with low energy. [FILL FROM REAL OUTPUT]
3. **Intense Rock Enthusiast** (genre=rock, mood=intense, energy=0.90): Expected rock and high-energy songs. [FILL FROM REAL OUTPUT]
4. **Adversarial Profile** (genre=classical, mood=melancholy, energy=0.90): This profile has conflicting preferences — classical music is typically low-energy, but the target energy is high. [FILL FROM REAL OUTPUT]

I also tested the different ranking modes (`--mode genre`, `--mode mood`, `--mode energy`) to verify that they reorder results as expected.

**Observations**: [FILL AFTER RUNNING — note what surprised you, what felt right, what felt wrong]

---

## 8. Future Work

1. **Genre similarity scores**: Instead of exact matching, use a similarity matrix so "indie pop" gets partial credit for matching "pop." This would make recommendations feel less rigid.
2. **User listening history**: Track which songs a user has already heard and penalize repeats. This would simulate a more realistic recommendation loop.
3. **Larger, real-world dataset**: Replace the 18-song catalog with data from the Spotify API or a public dataset to test how the algorithm scales.
4. **Tunable weights via CLI**: Let users adjust the scoring weights at runtime to experiment with different balances without editing code.

---

## 9. Personal Reflection

[WRITE YOUR OWN REFLECTION HERE. Prompts to consider:
- What was your biggest learning moment during this project?
- How did using AI tools help you, and when did you need to double-check them?
- What surprised you about how simple algorithms can still "feel" like recommendations?
- What would you try next if you extended this project?]
