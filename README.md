# Music Recommender Simulation

## Project Summary

This is a small music recommender where you describe a listener (favorite genre and mood, how energetic, how fast, how acoustic, and a few more details) and it scores every song in a 20-song catalog against that description. It then ranks the songs and prints the top five with the exact reasons behind each score.

It is a content-based system. It only looks at what the songs are like, not at what other people listen to, and it does not learn anything. The score comes from a plain weighted formula, so every recommendation can be traced by hand. On top of the basic version it has five extra song attributes that count in the score, four ways of ranking (a Strategy design pattern), an artist diversity penalty, and a formatted results table with the reasons.

The model card (model_card.md) has the full evaluation, limits and bias notes. ai_interactions.md documents the AI-assisted parts of the work.
---

## How The System Works

Spotify, YouTube and TikTok mix two ideas. Collaborative filtering looks at behavior: if people who play the same songs as you also play a track you have never heard, that track gets suggested. It needs a lot of users and their history (plays, skips, likes, playlists). Content-based filtering looks at the songs themselves: if you like fast, loud, happy pop, it finds other songs with those attributes. This project does the second one only. There are no users and no history here, so collaborative filtering is not possible.

It helps to keep three things apart:

Input data is the song catalog, one row per song with its attributes.
User preferences are the targets one listener asks for (a profile).
Ranking is the step that turns scores into an ordered list and picks the top few.
### Input Data

data/songs.csv has 20 songs and 15 columns. The first 10 songs came with the starter. I extended the file to 20 songs and added five new attributes. The new songs and all the values in the new columns are made up for this exercise, not taken from Spotify or any real service.

Attribute	     Type	      What it describes
genre, mood     	label	    the song's style and feeling
energy, valence, danceability, acousticness 	0 to 1	       intensity, positivity, how danceable, how acoustic
tempo_bpm    	number	  speed in beats per minute
popularity	        0 to 100	           how well known the song is (new)
release_decade	       1990 to 2020.   	the era of the song (new)
mood_tags	         list of words     	finer mood labels like "cozy" or "aggressive" (new)
instrumentalness        	0 to 1	  how little singing there is (new)
liveness            	0 to 1	   how much it sounds like a live recording (new)
id, title, artist        	text	      identification only (artist is used by the diversity penalty)
### User Preferences

A profile is a dictionary of targets. There are four built in (see src/main.py): a high-energy pop fan, a chill lofi listener, an intense rock enthusiast, and an adversarial profile that wants sad classical music but with very high energy, which the catalog cannot fully satisfy. The UserProfile class in src/recommender.py covers the original seven preferences. The five extra attributes are only scored when a profile sets a target for them, and all four built-in profiles do.

Scoring recipe

Each song earns points, and the points are added up.

Feature	Weight	How points are earned
genre	2.0	all or nothing on an exact match
mood	1.0	all or nothing on an exact match
energy	1.5	1 - abs(song - target), so closer is better
valence	0.5	same closeness formula
danceability	0.5	same closeness formula
acousticness	0.5	the song's acousticness if the listener likes acoustic, otherwise 1 - acousticness
tempo	0.5	closeness within a 40 to 220 BPM range
popularity	0.25	closeness, range 100
release decade	0.25	closeness, range 30 years
mood tags	0.25	share of the wanted tags the song has
instrumentalness	0.25	closeness
liveness	0.25	closeness

The maximum score is 7.75. For the number features, being higher or lower is not better. Only being closer is. Every contribution is rounded to two decimals, so the reasons printed next to a song add up exactly to its score (a test checks this).


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



###How Songs Are Chosen

score_song(user_prefs, song) judges one song and returns (score, reasons). recommend_songs(...) runs it on every song, hands the scored list to a ranking strategy, and returns the top k as (song, score, explanation).

Scoring and ranking are separate on purpose. A score only says how well one song fits. Ranking has to compare all songs, break ties and choose how many to show. Ties keep the order of the CSV, so the lower id wins and results are repeatable.
### Ranking Modes 

The four modes are classes in src/strategy.py that share one rank method, so main.py can swap them with --mode. They do not change scores. They only change the order.

default: highest score first.
genre: songs in the listener's genre first, then by score.
mood: songs with the listener's mood first, then by score.
energy: songs closest to the target energy first, then by score.

Because the last three sort by something other than the score, the Score column can look out of order in those modes. That is expected, and the Limitations section says why it matters.

Diversity penalty

After a song is picked, every remaining song by the same artist loses --artist-penalty points (0.5 by default) for each song of theirs already in the list. The penalty is applied while the list is being built, so a song that gets pushed down can be replaced by one from a different artist. It is shown in the reasons as "artist repeat penalty". Use --artist-penalty 0 to turn it off.

### Expected Bias
Genre is worth 2.0 of 7.75 points, the biggest single weight, so I expected the system to favor same-genre songs even when a song from another genre matches mood and energy better. The experiments below test that, and the result was more mixed than I expected.
---

## Getting Started
### Setup

Create a virtual environment (optional but recommended):
bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
Install dependencies:
bash
   pip install -r requirements.txt
Run the app from the project folder (all four profiles, default ranking):
bash
   python -m src.main
Options
bash
python -m src.main --profile lofi                   # pop, lofi, rock, adversarial, or all
python -m src.main --profile pop --mode genre       # default, genre, mood, or energy
python -m src.main --profile rock --k 3             # how many songs to show
python -m src.main --artist-penalty 0               # turn the diversity penalty off

### Running Tests

Run the starter tests with:

```bash
pytest
```
There are 56 tests. They cover the data loader, the scoring math (with hand-calculated values), each of the five extra attributes, ranking and ties, the four strategies, the diversity penalty and the command line.
Reproducing the experiments
bash
python -m src.experiments

This prints every result quoted below, from the real recommender, so you can check my numbers.
You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

This is the real output of python -m src.main (default ranking, artist penalty 0.5). The catalog loads with a line saying how many songs it found:

Loaded 20 songs from catalog.
High-Energy Pop Fan
================================================================================
  Profile: High-Energy Pop Fan
  Preferences: genre=pop, mood=happy, energy=0.85, acoustic=no, tempo=125.0bpm, popularity=80, release_decade=2020, instrumentalness=0.02, liveness=0.15, mood_tags=uplifting/sunny/danceable
  Ranking mode: default | artist penalty: 0.5
================================================================================
+--------+----------------+---------------+-----------+----------------------------------------------------------------+
|   Rank | Title          | Artist        | Score     | Reasons                                                        |
+========+================+===============+===========+================================================================+
|      1 | Sunrise City   | Neon Echo     | 7.55/7.75 | genre match: pop (+2.00)                                       |
|        |                |               |           | mood match: happy (+1.00)                                      |
|        |                |               |           | energy: song 0.82 vs target 0.85 (+1.46)                       |
|        |                |               |           | valence: song 0.84 vs target 0.8 (+0.48)                       |
|        |                |               |           | danceability: song 0.79 vs target 0.8 (+0.49)                  |
|        |                |               |           | low acoustic sound (acousticness 0.18) (+0.41)                 |
|        |                |               |           | tempo: song 118 vs target 125 BPM (+0.48)                      |
|        |                |               |           | popularity: song 78 vs target 80 (+0.24)                       |
|        |                |               |           | release decade: song 2020 vs target 2020 (+0.25)               |
|        |                |               |           | instrumentalness: song 0.02 vs target 0.02 (+0.25)             |
|        |                |               |           | liveness: song 0.12 vs target 0.15 (+0.24)                     |
|        |                |               |           | mood tags: 3 of 3 wanted (uplifting, sunny, danceable) (+0.25) |
+--------+----------------+---------------+-----------+----------------------------------------------------------------+
|      2 | Confetti Sky   | Luma Vale     | 7.50/7.75 | genre match: pop (+2.00)                                       |
|        |                |               |           | mood match: happy (+1.00)                                      |
|        |                |               |           | energy: song 0.87 vs target 0.85 (+1.47)                       |
|        |                |               |           | valence: song 0.9 vs target 0.8 (+0.45)                        |
|        |                |               |           | danceability: song 0.85 vs target 0.8 (+0.48)                  |
|        |                |               |           | low acoustic sound (acousticness 0.14) (+0.43)                 |
|        |                |               |           | tempo: song 126 vs target 125 BPM (+0.50)                      |
|        |                |               |           | popularity: song 80 vs target 80 (+0.25)                       |
|        |                |               |           | release decade: song 2020 vs target 2020 (+0.25)               |
|        |                |               |           | instrumentalness: song 0.02 vs target 0.02 (+0.25)             |
|        |                |               |           | liveness: song 0.14 vs target 0.15 (+0.25)                     |
|        |                |               |           | mood tags: 2 of 3 wanted (uplifting, sunny) (+0.17)            |
+--------+----------------+---------------+-----------+----------------------------------------------------------------+
|      3 | Gym Hero       | Max Pulse     | 6.25/7.75 | genre match: pop (+2.00)                                       |
|        |                |               |           | energy: song 0.93 vs target 0.85 (+1.38)                       |
|        |                |               |           | valence: song 0.77 vs target 0.8 (+0.48)                       |
|        |                |               |           | danceability: song 0.88 vs target 0.8 (+0.46)                  |
|        |                |               |           | low acoustic sound (acousticness 0.05) (+0.47)                 |
|        |                |               |           | tempo: song 132 vs target 125 BPM (+0.48)                      |
|        |                |               |           | popularity: song 88 vs target 80 (+0.23)                       |
|        |                |               |           | release decade: song 2020 vs target 2020 (+0.25)               |
|        |                |               |           | instrumentalness: song 0.01 vs target 0.02 (+0.25)             |
|        |                |               |           | liveness: song 0.15 vs target 0.15 (+0.25)                     |
|        |                |               |           | mood tags: 0 of 3 wanted (none) (+0.00)                        |
+--------+----------------+---------------+-----------+----------------------------------------------------------------+
|      4 | Calle Sol      | Marisol Vega  | 5.30/7.75 | mood match: happy (+1.00)                                      |
|        |                |               |           | energy: song 0.85 vs target 0.85 (+1.50)                       |
|        |                |               |           | valence: song 0.88 vs target 0.8 (+0.46)                       |
|        |                |               |           | danceability: song 0.9 vs target 0.8 (+0.45)                   |
|        |                |               |           | low acoustic sound (acousticness 0.3) (+0.35)                  |
|        |                |               |           | tempo: song 100 vs target 125 BPM (+0.43)                      |
|        |                |               |           | popularity: song 82 vs target 80 (+0.24)                       |
|        |                |               |           | release decade: song 2020 vs target 2020 (+0.25)               |
|        |                |               |           | instrumentalness: song 0.03 vs target 0.02 (+0.25)             |
|        |                |               |           | liveness: song 0.35 vs target 0.15 (+0.20)                     |
|        |                |               |           | mood tags: 2 of 3 wanted (sunny, danceable) (+0.17)            |
+--------+----------------+---------------+-----------+----------------------------------------------------------------+
|      5 | Rooftop Lights | Indigo Parade | 5.21/7.75 | mood match: happy (+1.00)                                      |
|        |                |               |           | energy: song 0.76 vs target 0.85 (+1.36)                       |
|        |                |               |           | valence: song 0.81 vs target 0.8 (+0.49)                       |
|        |                |               |           | danceability: song 0.82 vs target 0.8 (+0.49)                  |
|        |                |               |           | low acoustic sound (acousticness 0.35) (+0.33)                 |
|        |                |               |           | tempo: song 124 vs target 125 BPM (+0.50)                      |
|        |                |               |           | popularity: song 64 vs target 80 (+0.21)                       |
|        |                |               |           | release decade: song 2010 vs target 2020 (+0.17)               |
|        |                |               |           | instrumentalness: song 0.03 vs target 0.02 (+0.25)             |
|        |                |               |           | liveness: song 0.2 vs target 0.15 (+0.24)                      |
|        |                |               |           | mood tags: 2 of 3 wanted (uplifting, sunny) (+0.17)            |
+--------+----------------+---------------+-----------+----------------------------------------------------------------+
Chill Lofi Listener
================================================================================
  Profile: Chill Lofi Listener
  Preferences: genre=lofi, mood=chill, energy=0.35, acoustic=yes, tempo=75.0bpm, popularity=55, release_decade=2020, instrumentalness=0.9, liveness=0.08, mood_tags=calm/studious/cozy
  Ranking mode: default | artist penalty: 0.5
================================================================================
+--------+---------------------+----------------+-----------+-----------------------------------------------------------------+
|   Rank | Title               | Artist         | Score     | Reasons                                                         |
+========+=====================+================+===========+=================================================================+
|      1 | Library Rain        | Paper Lanterns | 7.66/7.75 | genre match: lofi (+2.00)                                       |
|        |                     |                |           | mood match: chill (+1.00)                                       |
|        |                     |                |           | energy: song 0.35 vs target 0.35 (+1.50)                        |
|        |                     |                |           | valence: song 0.6 vs target 0.6 (+0.50)                         |
|        |                     |                |           | danceability: song 0.58 vs target 0.55 (+0.49)                  |
|        |                     |                |           | acoustic sound (acousticness 0.86) (+0.43)                      |
|        |                     |                |           | tempo: song 72 vs target 75 BPM (+0.49)                         |
|        |                     |                |           | popularity: song 55 vs target 55 (+0.25)                        |
|        |                     |                |           | release decade: song 2020 vs target 2020 (+0.25)                |
|        |                     |                |           | instrumentalness: song 0.9 vs target 0.9 (+0.25)                |
|        |                     |                |           | liveness: song 0.08 vs target 0.08 (+0.25)                      |
|        |                     |                |           | mood tags: 3 of 3 wanted (calm, studious, cozy) (+0.25)         |
+--------+---------------------+----------------+-----------+-----------------------------------------------------------------+
|      2 | Midnight Coding     | LoRoom         | 7.32/7.75 | genre match: lofi (+2.00)                                       |
|        |                     |                |           | mood match: chill (+1.00)                                       |
|        |                     |                |           | energy: song 0.42 vs target 0.35 (+1.40)                        |
|        |                     |                |           | valence: song 0.56 vs target 0.6 (+0.48)                        |
|        |                     |                |           | danceability: song 0.62 vs target 0.55 (+0.47)                  |
|        |                     |                |           | acoustic sound (acousticness 0.71) (+0.35)                      |
|        |                     |                |           | tempo: song 78 vs target 75 BPM (+0.49)                         |
|        |                     |                |           | popularity: song 62 vs target 55 (+0.23)                        |
|        |                     |                |           | release decade: song 2020 vs target 2020 (+0.25)                |
|        |                     |                |           | instrumentalness: song 0.85 vs target 0.9 (+0.24)               |
|        |                     |                |           | liveness: song 0.1 vs target 0.08 (+0.24)                       |
|        |                     |                |           | mood tags: 2 of 3 wanted (calm, studious) (+0.17)               |
+--------+---------------------+----------------+-----------+-----------------------------------------------------------------+
|      3 | Focus Flow          | LoRoom         | 5.92/7.75 | genre match: lofi (+2.00)                                       |
|        |                     |                |           | energy: song 0.4 vs target 0.35 (+1.42)                         |
|        |                     |                |           | valence: song 0.59 vs target 0.6 (+0.49)                        |
|        |                     |                |           | danceability: song 0.6 vs target 0.55 (+0.48)                   |
|        |                     |                |           | acoustic sound (acousticness 0.78) (+0.39)                      |
|        |                     |                |           | tempo: song 80 vs target 75 BPM (+0.49)                         |
|        |                     |                |           | popularity: song 58 vs target 55 (+0.24)                        |
|        |                     |                |           | release decade: song 2020 vs target 2020 (+0.25)                |
|        |                     |                |           | instrumentalness: song 0.88 vs target 0.9 (+0.24)               |
|        |                     |                |           | liveness: song 0.09 vs target 0.08 (+0.25)                      |
|        |                     |                |           | mood tags: 2 of 3 wanted (calm, studious) (+0.17)               |
|        |                     |                |           | artist repeat penalty: LoRoom already has 1 song(s) in the list |
|        |                     |                |           | (-0.50)                                                         |
+--------+---------------------+----------------+-----------+-----------------------------------------------------------------+
|      4 | Spacewalk Thoughts  | Orbit Bloom    | 5.18/7.75 | mood match: chill (+1.00)                                       |
|        |                     |                |           | energy: song 0.28 vs target 0.35 (+1.40)                        |
|        |                     |                |           | valence: song 0.65 vs target 0.6 (+0.47)                        |
|        |                     |                |           | danceability: song 0.41 vs target 0.55 (+0.43)                  |
|        |                     |                |           | acoustic sound (acousticness 0.92) (+0.46)                      |
|        |                     |                |           | tempo: song 60 vs target 75 BPM (+0.46)                         |
|        |                     |                |           | popularity: song 45 vs target 55 (+0.23)                        |
|        |                     |                |           | release decade: song 2010 vs target 2020 (+0.17)                |
|        |                     |                |           | instrumentalness: song 0.95 vs target 0.9 (+0.24)               |
|        |                     |                |           | liveness: song 0.06 vs target 0.08 (+0.24)                      |
|        |                     |                |           | mood tags: 1 of 3 wanted (calm) (+0.08)                         |
+--------+---------------------+----------------+-----------+-----------------------------------------------------------------+
|      5 | Coffee Shop Stories | Slow Stereo    | 4.02/7.75 | energy: song 0.37 vs target 0.35 (+1.47)                        |
|        |                     |                |           | valence: song 0.71 vs target 0.6 (+0.45)                        |
|        |                     |                |           | danceability: song 0.54 vs target 0.55 (+0.49)                  |
|        |                     |                |           | acoustic sound (acousticness 0.89) (+0.45)                      |
|        |                     |                |           | tempo: song 90 vs target 75 BPM (+0.46)                         |
|        |                     |                |           | popularity: song 52 vs target 55 (+0.24)                        |
|        |                     |                |           | release decade: song 2000 vs target 2020 (+0.08)                |
|        |                     |                |           | instrumentalness: song 0.4 vs target 0.9 (+0.12)                |
|        |                     |                |           | liveness: song 0.35 vs target 0.08 (+0.18)                      |
|        |                     |                |           | mood tags: 1 of 3 wanted (cozy) (+0.08)                         |
+--------+---------------------+----------------+-----------+-----------------------------------------------------------------+
Intense Rock Enthusiast
================================================================================
  Profile: Intense Rock Enthusiast
  Preferences: genre=rock, mood=intense, energy=0.9, acoustic=no, tempo=150.0bpm, popularity=65, release_decade=2010, instrumentalness=0.05, liveness=0.3, mood_tags=aggressive/driving/powerful
  Ranking mode: default | artist penalty: 0.5
================================================================================
+--------+------------------+---------------+-----------+-------------------------------------------------------------------+
|   Rank | Title            | Artist        | Score     | Reasons                                                           |
+========+==================+===============+===========+===================================================================+
|      1 | Storm Runner     | Voltline      | 7.63/7.75 | genre match: rock (+2.00)                                         |
|        |                  |               |           | mood match: intense (+1.00)                                       |
|        |                  |               |           | energy: song 0.91 vs target 0.9 (+1.48)                           |
|        |                  |               |           | valence: song 0.48 vs target 0.45 (+0.48)                         |
|        |                  |               |           | danceability: song 0.66 vs target 0.65 (+0.49)                    |
|        |                  |               |           | low acoustic sound (acousticness 0.1) (+0.45)                     |
|        |                  |               |           | tempo: song 152 vs target 150 BPM (+0.49)                         |
|        |                  |               |           | popularity: song 70 vs target 65 (+0.24)                          |
|        |                  |               |           | release decade: song 2010 vs target 2010 (+0.25)                  |
|        |                  |               |           | instrumentalness: song 0.05 vs target 0.05 (+0.25)                |
|        |                  |               |           | liveness: song 0.3 vs target 0.3 (+0.25)                          |
|        |                  |               |           | mood tags: 3 of 3 wanted (aggressive, driving, powerful) (+0.25)  |
+--------+------------------+---------------+-----------+-------------------------------------------------------------------+
|      2 | Storm Cellar     | Voltline      | 7.00/7.75 | genre match: rock (+2.00)                                         |
|        |                  |               |           | mood match: intense (+1.00)                                       |
|        |                  |               |           | energy: song 0.88 vs target 0.9 (+1.47)                           |
|        |                  |               |           | valence: song 0.42 vs target 0.45 (+0.48)                         |
|        |                  |               |           | danceability: song 0.58 vs target 0.65 (+0.46)                    |
|        |                  |               |           | low acoustic sound (acousticness 0.08) (+0.46)                    |
|        |                  |               |           | tempo: song 148 vs target 150 BPM (+0.49)                         |
|        |                  |               |           | popularity: song 61 vs target 65 (+0.24)                          |
|        |                  |               |           | release decade: song 2010 vs target 2010 (+0.25)                  |
|        |                  |               |           | instrumentalness: song 0.1 vs target 0.05 (+0.24)                 |
|        |                  |               |           | liveness: song 0.28 vs target 0.3 (+0.24)                         |
|        |                  |               |           | mood tags: 2 of 3 wanted (aggressive, driving) (+0.17)            |
|        |                  |               |           | artist repeat penalty: Voltline already has 1 song(s) in the list |
|        |                  |               |           | (-0.50)                                                           |
+--------+------------------+---------------+-----------+-------------------------------------------------------------------+
|      3 | Gym Hero         | Max Pulse     | 5.00/7.75 | mood match: intense (+1.00)                                       |
|        |                  |               |           | energy: song 0.93 vs target 0.9 (+1.46)                           |
|        |                  |               |           | valence: song 0.77 vs target 0.45 (+0.34)                         |
|        |                  |               |           | danceability: song 0.88 vs target 0.65 (+0.39)                    |
|        |                  |               |           | low acoustic sound (acousticness 0.05) (+0.47)                    |
|        |                  |               |           | tempo: song 132 vs target 150 BPM (+0.45)                         |
|        |                  |               |           | popularity: song 88 vs target 65 (+0.19)                          |
|        |                  |               |           | release decade: song 2020 vs target 2010 (+0.17)                  |
|        |                  |               |           | instrumentalness: song 0.01 vs target 0.05 (+0.24)                |
|        |                  |               |           | liveness: song 0.15 vs target 0.3 (+0.21)                         |
|        |                  |               |           | mood tags: 1 of 3 wanted (powerful) (+0.08)                       |
+--------+------------------+---------------+-----------+-------------------------------------------------------------------+
|      4 | Iron Reign       | Black Granite | 4.15/7.75 | energy: song 0.97 vs target 0.9 (+1.40)                           |
|        |                  |               |           | valence: song 0.3 vs target 0.45 (+0.42)                          |
|        |                  |               |           | danceability: song 0.45 vs target 0.65 (+0.40)                    |
|        |                  |               |           | low acoustic sound (acousticness 0.03) (+0.48)                    |
|        |                  |               |           | tempo: song 168 vs target 150 BPM (+0.45)                         |
|        |                  |               |           | popularity: song 50 vs target 65 (+0.21)                          |
|        |                  |               |           | release decade: song 2000 vs target 2010 (+0.17)                  |
|        |                  |               |           | instrumentalness: song 0.1 vs target 0.05 (+0.24)                 |
|        |                  |               |           | liveness: song 0.45 vs target 0.3 (+0.21)                         |
|        |                  |               |           | mood tags: 2 of 3 wanted (aggressive, powerful) (+0.17)           |
+--------+------------------+---------------+-----------+-------------------------------------------------------------------+
|      5 | Night Drive Loop | Neon Echo     | 3.86/7.75 | energy: song 0.75 vs target 0.9 (+1.27)                           |
|        |                  |               |           | valence: song 0.49 vs target 0.45 (+0.48)                         |
|        |                  |               |           | danceability: song 0.73 vs target 0.65 (+0.46)                    |
|        |                  |               |           | low acoustic sound (acousticness 0.22) (+0.39)                    |
|        |                  |               |           | tempo: song 110 vs target 150 BPM (+0.39)                         |
|        |                  |               |           | popularity: song 66 vs target 65 (+0.25)                          |
|        |                  |               |           | release decade: song 2010 vs target 2010 (+0.25)                  |
|        |                  |               |           | instrumentalness: song 0.7 vs target 0.05 (+0.09)                 |
|        |                  |               |           | liveness: song 0.09 vs target 0.3 (+0.20)                         |
|        |                  |               |           | mood tags: 1 of 3 wanted (driving) (+0.08)                        |
+--------+------------------+---------------+-----------+-------------------------------------------------------------------+
Adversarial: Sad but High-Energy
================================================================================
  Profile: Adversarial: Sad but High-Energy
  Preferences: genre=classical, mood=melancholy, energy=0.9, acoustic=yes, tempo=65.0bpm, popularity=45, release_decade=1990, instrumentalness=0.95, liveness=0.2, mood_tags=melancholic/lonely
  Ranking mode: default | artist penalty: 0.5
================================================================================
+--------+------------------+---------------+-----------+--------------------------------------------------------+
|   Rank | Title            | Artist        | Score     | Reasons                                                |
+========+==================+===============+===========+========================================================+
|      1 | Adagio for Rain  | Elena Voss    | 6.58/7.75 | genre match: classical (+2.00)                         |
|        |                  |               |           | mood match: melancholy (+1.00)                         |
|        |                  |               |           | energy: song 0.22 vs target 0.9 (+0.48)                |
|        |                  |               |           | valence: song 0.2 vs target 0.3 (+0.45)                |
|        |                  |               |           | danceability: song 0.18 vs target 0.25 (+0.46)         |
|        |                  |               |           | acoustic sound (acousticness 0.97) (+0.48)             |
|        |                  |               |           | tempo: song 58 vs target 65 BPM (+0.48)                |
|        |                  |               |           | popularity: song 48 vs target 45 (+0.24)               |
|        |                  |               |           | release decade: song 1990 vs target 1990 (+0.25)       |
|        |                  |               |           | instrumentalness: song 0.98 vs target 0.95 (+0.24)     |
|        |                  |               |           | liveness: song 0.2 vs target 0.2 (+0.25)               |
|        |                  |               |           | mood tags: 2 of 2 wanted (melancholic, lonely) (+0.25) |
+--------+------------------+---------------+-----------+--------------------------------------------------------+
|      2 | Desert Caravan   | Nomad Station | 3.38/7.75 | energy: song 0.45 vs target 0.9 (+0.83)                |
|        |                  |               |           | valence: song 0.4 vs target 0.3 (+0.45)                |
|        |                  |               |           | danceability: song 0.5 vs target 0.25 (+0.38)          |
|        |                  |               |           | acoustic sound (acousticness 0.8) (+0.40)              |
|        |                  |               |           | tempo: song 92 vs target 65 BPM (+0.42)                |
|        |                  |               |           | popularity: song 38 vs target 45 (+0.23)               |
|        |                  |               |           | release decade: song 1990 vs target 1990 (+0.25)       |
|        |                  |               |           | instrumentalness: song 0.65 vs target 0.95 (+0.18)     |
|        |                  |               |           | liveness: song 0.15 vs target 0.2 (+0.24)              |
|        |                  |               |           | mood tags: 0 of 2 wanted (none) (+0.00)                |
+--------+------------------+---------------+-----------+--------------------------------------------------------+
|      3 | Iron Reign       | Black Granite | 3.16/7.75 | energy: song 0.97 vs target 0.9 (+1.40)                |
|        |                  |               |           | valence: song 0.3 vs target 0.3 (+0.50)                |
|        |                  |               |           | danceability: song 0.45 vs target 0.25 (+0.40)         |
|        |                  |               |           | acoustic sound (acousticness 0.03) (+0.01)             |
|        |                  |               |           | tempo: song 168 vs target 65 BPM (+0.21)               |
|        |                  |               |           | popularity: song 50 vs target 45 (+0.24)               |
|        |                  |               |           | release decade: song 2000 vs target 1990 (+0.17)       |
|        |                  |               |           | instrumentalness: song 0.1 vs target 0.95 (+0.04)      |
|        |                  |               |           | liveness: song 0.45 vs target 0.2 (+0.19)              |
|        |                  |               |           | mood tags: 0 of 2 wanted (none) (+0.00)                |
+--------+------------------+---------------+-----------+--------------------------------------------------------+
|      4 | Night Drive Loop | Neon Echo     | 3.12/7.75 | energy: song 0.75 vs target 0.9 (+1.27)                |
|        |                  |               |           | valence: song 0.49 vs target 0.3 (+0.41)               |
|        |                  |               |           | danceability: song 0.73 vs target 0.25 (+0.26)         |
|        |                  |               |           | acoustic sound (acousticness 0.22) (+0.11)             |
|        |                  |               |           | tempo: song 110 vs target 65 BPM (+0.38)               |
|        |                  |               |           | popularity: song 66 vs target 45 (+0.20)               |
|        |                  |               |           | release decade: song 2010 vs target 1990 (+0.08)       |
|        |                  |               |           | instrumentalness: song 0.7 vs target 0.95 (+0.19)      |
|        |                  |               |           | liveness: song 0.09 vs target 0.2 (+0.22)              |
|        |                  |               |           | mood tags: 0 of 2 wanted (none) (+0.00)                |
+--------+------------------+---------------+-----------+--------------------------------------------------------+
|      5 | Storm Cellar     | Voltline      | 3.12/7.75 | energy: song 0.88 vs target 0.9 (+1.47)                |
|        |                  |               |           | valence: song 0.42 vs target 0.3 (+0.44)               |
|        |                  |               |           | danceability: song 0.58 vs target 0.25 (+0.34)         |
|        |                  |               |           | acoustic sound (acousticness 0.08) (+0.04)             |
|        |                  |               |           | tempo: song 148 vs target 65 BPM (+0.27)               |
|        |                  |               |           | popularity: song 61 vs target 45 (+0.21)               |
|        |                  |               |           | release decade: song 2010 vs target 1990 (+0.08)       |
|        |                  |               |           | instrumentalness: song 0.1 vs target 0.95 (+0.04)      |
|        |                  |               |           | liveness: song 0.28 vs target 0.2 (+0.23)              |
|        |                  |               |           | mood tags: 0 of 2 wanted (none) (+0.00)                |
+--------+------------------+---------------+-----------+--------------------------------------------------------+
Why these songs? (plain-language explanations)
Sunrise City, number 1 for the pop fan (7.55 of 7.75). It matches both the genre (pop, +2.00) and the mood (happy, +1.00). Its energy is 0.82 against a target of 0.85, so it keeps nearly all of the 1.5 energy points (+1.46). It is also close on valence, danceability and tempo, and it has all three of the tags the profile asked for (uplifting, sunny, danceable). The small losses are mostly the acoustic points (+0.41 of 0.50) and a few hundredths elsewhere.
Gym Hero, number 3 for the pop fan (6.25). This is the song that keeps showing up for people who only asked for happy pop. It is a pop song, so it gets the full genre bonus (+2.00). Its mood is "intense", not "happy", so it gets no mood points and none of the tags. It still ranks third because its energy (0.93), danceability, tempo and popularity are all close to what the fan asked for. A song that is close on almost every number, plus the genre, beats songs that only match the mood.
Library Rain, number 1 for the lofi listener (7.66). Genre and mood both match. Its energy, valence, popularity, release decade, instrumentalness and liveness are almost exactly on target, and it has all three wanted tags (calm, studious, cozy). The one place it loses much is the acoustic points, because the formula pays the song's acousticness directly, so 0.86 earns +0.43 and not the full 0.50.
Adagio for Rain, number 1 for the adversarial listener (6.58). It matches the genre (classical) and mood (melancholy) and both tags, which is worth 3.25 points on its own. Its energy is 0.22 against a target of 0.90, so it only gets +0.48 of 1.5 for energy. It wins anyway because no other song matches the genre or the mood. The conflict in the profile (sad and high energy) gets settled by the labels, not by the energy.
One other ranking mode

python -m src.main --profile pop --mode energy --k 3 ranks by closeness to the target energy first:

Loaded 20 songs from catalog.

================================================================================
  Profile: High-Energy Pop Fan
  Preferences: genre=pop, mood=happy, energy=0.85, acoustic=no, tempo=125.0bpm, popularity=80, release_decade=2020, instrumentalness=0.02, liveness=0.15, mood_tags=uplifting/sunny/danceable
  Ranking mode: energy | artist penalty: 0.5
================================================================================
+--------+--------------+--------------+-----------+----------------------------------------------------------------+
|   Rank | Title        | Artist       | Score     | Reasons                                                        |
+========+==============+==============+===========+================================================================+
|      1 | Calle Sol    | Marisol Vega | 5.30/7.75 | mood match: happy (+1.00)                                      |
|        |              |              |           | energy: song 0.85 vs target 0.85 (+1.50)                       |
|        |              |              |           | valence: song 0.88 vs target 0.8 (+0.46)                       |
|        |              |              |           | danceability: song 0.9 vs target 0.8 (+0.45)                   |
|        |              |              |           | low acoustic sound (acousticness 0.3) (+0.35)                  |
|        |              |              |           | tempo: song 100 vs target 125 BPM (+0.43)                      |
|        |              |              |           | popularity: song 82 vs target 80 (+0.24)                       |
|        |              |              |           | release decade: song 2020 vs target 2020 (+0.25)               |
|        |              |              |           | instrumentalness: song 0.03 vs target 0.02 (+0.25)             |
|        |              |              |           | liveness: song 0.35 vs target 0.15 (+0.20)                     |
|        |              |              |           | mood tags: 2 of 3 wanted (sunny, danceable) (+0.17)            |
+--------+--------------+--------------+-----------+----------------------------------------------------------------+
|      2 | Confetti Sky | Luma Vale    | 7.50/7.75 | genre match: pop (+2.00)                                       |
|        |              |              |           | mood match: happy (+1.00)                                      |
|        |              |              |           | energy: song 0.87 vs target 0.85 (+1.47)                       |
|        |              |              |           | valence: song 0.9 vs target 0.8 (+0.45)                        |
|        |              |              |           | danceability: song 0.85 vs target 0.8 (+0.48)                  |
|        |              |              |           | low acoustic sound (acousticness 0.14) (+0.43)                 |
|        |              |              |           | tempo: song 126 vs target 125 BPM (+0.50)                      |
|        |              |              |           | popularity: song 80 vs target 80 (+0.25)                       |
|        |              |              |           | release decade: song 2020 vs target 2020 (+0.25)               |
|        |              |              |           | instrumentalness: song 0.02 vs target 0.02 (+0.25)             |
|        |              |              |           | liveness: song 0.14 vs target 0.15 (+0.25)                     |
|        |              |              |           | mood tags: 2 of 3 wanted (uplifting, sunny) (+0.17)            |
+--------+--------------+--------------+-----------+----------------------------------------------------------------+
|      3 | Sunrise City | Neon Echo    | 7.55/7.75 | genre match: pop (+2.00)                                       |
|        |              |              |           | mood match: happy (+1.00)                                      |
|        |              |              |           | energy: song 0.82 vs target 0.85 (+1.46)                       |
|        |              |              |           | valence: song 0.84 vs target 0.8 (+0.48)                       |
|        |              |              |           | danceability: song 0.79 vs target 0.8 (+0.49)                  |
|        |              |              |           | low acoustic sound (acousticness 0.18) (+0.41)                 |
|        |              |              |           | tempo: song 118 vs target 125 BPM (+0.48)                      |
|        |              |              |           | popularity: song 78 vs target 80 (+0.24)                       |
|        |              |              |           | release decade: song 2020 vs target 2020 (+0.25)               |
|        |              |              |           | instrumentalness: song 0.02 vs target 0.02 (+0.25)             |
|        |              |              |           | liveness: song 0.12 vs target 0.15 (+0.24)                     |
|        |              |              |           | mood tags: 3 of 3 wanted (uplifting, sunny, danceable) (+0.25) |
+--------+--------------+--------------+-----------+----------------------------------------------------------------+

Calle Sol, a latin song with the right mood and an energy of exactly 0.85, goes to number 1 even though its total score (5.30) is lower than Sunrise City's (7.55).

---

## Experiments You Tried

All of these come from python -m src.experiments. The model card has the details.

Four profiles (default ranking).

Pop fan: Sunrise City, Confetti Sky, Gym Hero, Calle Sol, Rooftop Lights.
Lofi listener: Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts, Coffee Shop Stories.
Rock enthusiast: Storm Runner, Storm Cellar, Gym Hero, Iron Reign, Night Drive Loop.
Adversarial (sad but high-energy): Adagio for Rain, Desert Caravan, Iron Reign, Night Drive Loop, Storm Cellar.

How the profiles differ.

Pop vs lofi: no songs in common. One wants loud, fast and happy, the other wants quiet, slow and acoustic, so they sit at opposite ends of the catalog.
Pop vs rock: only Gym Hero is shared. Both want high energy, but the pop fan wants happy and the rock fan wants intense. Gym Hero is pop and intense, so it fits both.
Pop vs adversarial: nothing shared. The adversarial profile wants low valence and acoustic sound.
Lofi vs rock: nothing shared, the biggest gap in energy and tempo.
Lofi vs adversarial: nothing shared. Both like acoustic music, but the adversarial profile asks for energy 0.90, which no lofi song has.
Rock vs adversarial: three shared songs (Storm Cellar, Iron Reign, Night Drive Loop). After the classical song and Desert Caravan, the adversarial list is filled by loud songs because the profile asks for energy 0.90. That is the contradiction showing up in the results.

Ranking modes. Genre-first gave the same order as default for all four profiles. Mood-first changed the order for the pop fan (Gym Hero fell from third to fifth) and the lofi listener (Spacewalk Thoughts moved above Focus Flow). Energy-focused changed the most: for the adversarial profile only 1 of the 5 songs stayed the same, and its number 1 became Storm Runner, a rock song.

Weight shift (genre 2.0 to 1.0, energy 1.5 to 3.0). The lofi list did not change. Pop swapped Gym Hero and Calle Sol, rock replaced Night Drive Loop with Confetti Sky at number 5, and the adversarial list changed in several places. I would call that different and not more accurate. There is no answer key to check it against.

Feature removal. With the mood weight at 0, the lofi order swapped (Midnight Coding and Focus Flow) and the rock order swapped (Gym Hero and Iron Reign). Pop and adversarial did not change. With all five new attributes switched off, the pop top two swapped, rock's fifth song changed, and the adversarial list changed, so these attributes do affect the results. Switching each one off alone changed the top-10 order for at least one profile.

Diversity. At five songs the penalty rarely changes the list, because only three artists have two songs (Neon Echo, LoRoom, Voltline). The one case I found is the lofi profile with a penalty of 2.0, where Focus Flow (LoRoom's second song) drops from third to fourth. At ten songs a penalty of 0.5 raised the number of different artists from 8 to 10 for the pop fan, 9 to 10 for the adversarial profile and 8 to 9 for rock, at a small cost in score.
---

## Limitations and Risks

Small catalog. Twenty songs, and 12 of the 15 genres have a single song. A listener who asks for pop gets all three pop songs in the top five, and the remaining slots go to whatever is closest.
Exact label matching. An indie pop song gets no genre credit for a pop listener, and "melancholy" does not match "sad". There is no idea of similar genres or moods.
Ranking modes that ignore the score. Genre-first, mood-first and energy-first sort by one feature before the score, so a song with a much lower score can rank above a better one (Calle Sol above Sunrise City for the pop fan in energy mode). The Score column then looks out of order.
Acousticness is coarse. likes_acoustic is yes or no. A listener who likes medium acousticness cannot say so, and an acoustic song can never earn the full 0.5.
The diversity penalty is gentle. It only handles repeated artists, not repeated genres, and at five songs it usually changes nothing.
No collaborative signal. The system cannot recommend something because similar listeners enjoyed it.
Simulated data. All song values are made up, so nothing here says anything about real music.
---

## Reflection
The full reflection is in model_card.md, section 9.