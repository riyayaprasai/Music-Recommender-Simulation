# Model Card: Music Recommender Simulation

## 1. Model Name

VibeFinder 1.0

VibeFinder is a content-based music recommender. It compares each song's attributes with a listener's stated taste, adds up weighted points, and returns the best matches with the reasons. It is a scoring formula, not a trained model. It never learns from listening history.

---

## 2. Intended Use

VibeFinder suggests a short list of songs (five by default) from a 20-song catalog and explains each suggestion. A listener is described by a profile of targets: favorite genre and mood, how energetic, how fast, how acoustic, and a few more details.

I made it for classroom exploration. The goal is to see how data becomes a ranked list, and to keep every step easy to check. It assumes a few things about the listener:

They can describe their taste ahead of time with labels and numbers.
Closer to the target is better. Energy 0.82 is a good match for someone who wants 0.85, and energy 0.30 is not.
One genre and one mood at a time is enough to describe their taste.

Not intended for: real listeners, real streaming, or decisions about which artists get exposure. It has no skips, likes or playlists, so it cannot personalize by itself. The songs are simulated, so nothing it says applies to real recordings. It should not be used as evidence of how Spotify or YouTube Music work.
---

## 3. How the Model Works

What it reads. Each song is one row of data/songs.csv: genre, mood, energy, tempo, valence (how positive it sounds), danceability and acousticness. I added five more attributes: popularity (0 to 100), release decade, mood tags (words like "cozy" or "aggressive"), instrumentalness (how little singing there is) and liveness (how live it sounds).

What the listener gives it. A profile with a target for each of those. The four built-in profiles set a target for every attribute, so all twelve scored features are used. If a profile leaves one of the five extra attributes out, that attribute simply adds nothing for that listener.

How a song earns points.

A matching genre earns 2.0 points and a matching mood earns 1.0. These are all or nothing.
Energy earns up to 1.5. Valence, danceability, acousticness and tempo earn up to 0.5 each.
Popularity, release decade, mood tags, instrumentalness and liveness earn up to 0.25 each.
For number features the points depend on how close the song is to the target, not on being high or low. Sunrise City has energy 0.82 and the pop fan wants 0.85, so it keeps almost all of the 1.5 energy points (+1.46).
Mood tags earn points for the share of the wanted tags the song has.
For acousticness, a listener who likes acoustic music earns the song's acousticness value. Anyone else earns one minus that value.

The best possible score is 7.75. Every point is written down as a reason, so the explanation is the real arithmetic. The reasons add up exactly to the score, and a test checks that.

How the list is built. Scoring and ranking are separate steps. First every song gets a score. Then a ranking strategy orders them and the top five are returned. Ties keep the order of the file, so the lower id wins and the result is repeatable.

Four ranking modes. Each is its own class in src/strategy.py with the same rank method, so the program can switch between them without knowing which one it has.

Mode	How it orders songs
default	highest score first
genre	songs in the listener's genre first, then by score
mood	songs with the listener's mood first, then by score
energy	songs closest to the target energy first, then by score

These modes change the order, not the scores. That is why the Score column can look out of order in the last three modes.

Diversity penalty. When the list is built, a song loses 0.5 points (the default) for each song by the same artist that is already in the list. The penalty is applied during selection, so a pushed-down song can be replaced by a song from another artist. It shows up in the reasons as "artist repeat penalty". The original score is never hidden.

What changed from the starter project. The starter had placeholders for loading, scoring, ranking and explaining. I used the 10-song starter file as the first rows, extended it to 20 songs, scored the five extra attributes, rewrote the diversity penalty so it works while the list is built, fixed the command line so python -m src.main runs, and wrote the experiments and tests.
---

## 4. Data

Size. 20 songs and 15 columns. The starter had 10 songs and 10 columns.
Simulated. The 10 added songs and every value in the five new columns were made up for this project. None of it comes from a real service.
Genres (15). pop and lofi have 3 songs each, rock has 2, and the other 12 genres (ambient, jazz, synthwave, indie pop, hip hop, r&b, electronic, country, classical, latin, metal, world) have one each.
Moods (13). happy has 4 songs, chill and intense have 3 each, and the other 10 moods have one each.
Artists. 17 artists. Neon Echo, LoRoom and Voltline each have two songs.
Other spreads. Energy: 11 songs are 0.75 or higher, 5 are 0.40 or lower, and 4 are in between. Release decade runs from the 1990s to the 2020s. Mean popularity is 64.8.
Quality. The loader converts numbers and tag lists, and tests check that every id is unique and every value is in its valid range.

What is stored but not scored. Title is never scored. Artist only matters to the diversity penalty.

What is missing. The catalog is tiny, and most genres have a single song. There are no lyrics, no listener history and no subgenres. It is mostly mainstream Western-style genres, with only one "world" song.

---

## 5. Strengths

These come from the experiments (python -m src.experiments).

Different listeners get different lists. The lofi list shares no songs with any other profile. Pop and rock share only Gym Hero.
Closeness works. The average energy of each list lands near the target: 0.85 for a pop target of 0.85, 0.36 for lofi (target 0.35), 0.89 for rock (target 0.90).
Explanations are the real math. Library Rain scores 7.66 for the lofi listener, and the table shows exactly where: genre +2.00, mood +1.00, energy +1.50, and nearly full points on the rest.
The five extra attributes matter. Turning each one off changed the top-10 order for at least one profile (popularity and instrumentalness for all four, release decade and liveness for rock and the adversarial profile, mood tags for pop and rock).
The adversarial profile gives a sensible answer. A sad, high-energy classical request returns the one classical song first and then the loudest songs, and the table shows why.
Mood-first and energy-first really are different. For the pop fan, mood-first pushes Gym Hero (an intense song) from third to fifth. Energy-first puts the latin song Calle Sol first.
---

## 6. Limitations and Bias

What I observed, kept apart from what I only suspect.

Observed in the experiments

The catalog runs out. Pop and lofi have 3 songs each and rock has 2, so slots four and five always go to other genres. The pop fan gets Calle Sol (latin) and Rooftop Lights (indie pop).
Labels must match exactly. Rooftop Lights is indie pop, so it gets no genre points from a pop listener. Coffee Shop Stories is jazz tagged "relaxed", so a chill lofi listener gets no mood points for it. It still reaches fifth place for the lofi listener (4.02) on the numbers alone.
Conflicting requests are settled silently. The adversarial profile asks for melancholy music with energy 0.90. No song is both: the only melancholy song has energy 0.22. The system returns the classical song first (6.58) and then songs with scores near 3, and it never tells the listener that the request could not be met. The average energy of the list is 0.65 against a target of 0.90.
Gym Hero keeps showing up for the happy pop fan. It is a pop song, so it gets +2.00 for genre, and it is close on energy, danceability, tempo and popularity. It gets no mood points because it is "intense", not "happy". It ranks third at 6.25. Genre is not the only reason. It is the genre bonus plus being close on everything else.
Modes that sort by one feature break the score order. In energy mode the pop fan's number 1 is Calle Sol at 5.30, and Sunrise City (7.55) is third. The list is sorted by energy closeness first, so the score column no longer goes down.
Ties are decided by file order. The adversarial profile has Night Drive Loop and Storm Cellar tied at 3.12. The song listed earlier in the CSV (Night Drive Loop) ranks higher. That is repeatable but arbitrary.
Acousticness is coarse. The boolean likes_acoustic pays a song's acousticness directly, so even a very acoustic song like Library Rain (0.86) earns only +0.43 of 0.50.
The diversity penalty is gentle at five songs. Only three artists have two songs. With the default 0.5 penalty, no profile's top-5 list changed. With a penalty of 2.0, only the lofi list changed (Focus Flow dropped from third to fourth). At ten songs the penalty did more: distinct artists rose from 8 to 10 for the pop fan, 9 to 10 for the adversarial profile and 8 to 9 for rock.
The five extra attributes have a small effect. Each is worth at most 0.25 points, and switching all five off changed the order for pop, rock and the adversarial profile, but not for lofi.

Possible, but not tested

Popularity bias. Popularity only counts when a profile sets a target. I did not run a profile without one, so I have no evidence either way.
Energy bias. 11 of the 20 songs have energy of 0.75 or higher and only 4 are in the middle. A listener who likes medium energy probably has fewer close matches. I did not run a medium-energy profile.
Filter bubbles. The system only returns what matches the stated taste, and it has no way to suggest something new. I did not test this over time, since nothing in the system feeds back.
Culture and language. The catalog is small and mostly mainstream.

How the diversity penalty helps with fairness. Without it, an artist with several songs near the top could fill the list. With it, repeated artists are pushed down so other artists get a chance. In this catalog that effect is real but small, and it only covers artists. It does nothing about repeated genres, so it does not make the system "fair" overall.

## 7. Evaluation

What I did. I ran four profiles through the real recommender with python -m src.main and python -m src.experiments: a high-energy pop fan, a chill lofi listener, an intense rock enthusiast and an adversarial profile (sad classical but high energy). I also have 56 automated tests for the formulas, ranking, strategies, diversity and the command line. I checked the tests by deliberately breaking the code (removing the diversity penalty, changing the tag math, flipping the acousticness rule) and confirming that tests failed each time.

Top five for each profile (default ranking, no diversity penalty).

pop: High-Energy Pop Fan
  1. Sunrise City         Neon Echo       pop         7.55
  2. Confetti Sky         Luma Vale       pop         7.50
  3. Gym Hero             Max Pulse       pop         6.25
  4. Calle Sol            Marisol Vega    latin       5.30
  5. Rooftop Lights       Indigo Parade   indie pop   5.21
lofi: Chill Lofi Listener
  1. Library Rain         Paper Lanterns  lofi        7.66
  2. Midnight Coding      LoRoom          lofi        7.32
  3. Focus Flow           LoRoom          lofi        6.42
  4. Spacewalk Thoughts   Orbit Bloom     ambient     5.18
  5. Coffee Shop Stories  Slow Stereo     jazz        4.02
rock: Intense Rock Enthusiast
  1. Storm Runner         Voltline        rock        7.63
  2. Storm Cellar         Voltline        rock        7.50
  3. Gym Hero             Max Pulse       pop         5.00
  4. Iron Reign           Black Granite   metal       4.15
  5. Night Drive Loop     Neon Echo       synthwave   3.86
adversarial: Adversarial: Sad but High-Energy
  1. Adagio for Rain      Elena Voss      classical   6.58
  2. Desert Caravan       Nomad Station   world       3.38
  3. Iron Reign           Black Granite   metal       3.16
  4. Night Drive Loop     Neon Echo       synthwave   3.12
  5. Storm Cellar         Voltline        rock        3.12

The first three slots for pop, lofi and rock are the songs I would pick myself: right genre, right mood, right energy.

Comparing each pair of profiles.

Pop vs lofi: nothing in common. One wants loud, fast, happy songs and the other wants quiet, slow, acoustic ones, so they use opposite ends of the catalog.
Pop vs rock: only Gym Hero is shared. Both want high energy, but pop asks for happy and rock asks for intense, and Gym Hero is the pop song with an intense mood.
Pop vs adversarial: nothing shared. The adversarial profile wants low valence, low danceability and acoustic sound.
Lofi vs rock: nothing shared. They are far apart on energy, tempo and acousticness.
Lofi vs adversarial: nothing shared. Both ask for acoustic sound, but the adversarial profile wants energy 0.90, which no lofi song has.
Rock vs adversarial: Storm Cellar, Iron Reign and Night Drive Loop appear in both. After the classical song and Desert Caravan, the adversarial list fills up with loud songs because of the energy 0.90 request. That is the contradiction showing up.

Ranking modes compared with default. Genre-first gave the same order as default for all four profiles, because the genre-matching songs were already on top. Mood-first changed the order for the pop fan and the lofi listener only. Energy-first changed the most: for the rock and pop profiles 3 of the 5 songs stayed, and for the adversarial profile only 1 did (its number 1 became Storm Runner, a rock song).

Weight shift (genre 2.0 to 1.0, energy 1.5 to 3.0). The lofi list did not change. Pop swapped Gym Hero and Calle Sol, rock swapped Night Drive Loop for Confetti Sky in fifth place, and the adversarial list changed in several places. I treat this as different, not more accurate, because there is no answer key.

Feature removal. With mood weight at 0, lofi swapped Midnight Coding and Focus Flow (Midnight Coding lost its mood point), and rock swapped Gym Hero and Iron Reign. Pop and adversarial did not change. With all five extra attributes off, the pop top two swapped, rock's fifth song became Neon Pulse, and the adversarial list changed.

Diversity (artist penalty). See section 6 for the numbers. In short: little change at five songs, some change at ten.

What surprised me. I expected the genre weight to dominate everything. In practice the genre-matching songs also sit close to the targets on most other features, so the weight shift (half the genre weight, double the energy weight) left the lofi list unchanged. The most surprising result was the energy-first mode, which sent a rock song to the top of the adversarial list and a latin song to the top of the pop list, because it ignores genre and mood while sorting.
---

## 8. Future Work
Let similar labels earn partial credit. Indie pop should get some genre credit for a pop listener, and "melancholy" should get some credit for "sad". A small hand-made similarity table would fix the exact-match problem.
Make the ranking modes use the score. Instead of sorting by one feature first, change the weights per mode (genre-first gets a bigger genre weight, for example). The score column would then always go down, and results would be easier to compare.
Warn when a request cannot be met. If no song satisfies the main wishes, like sad and high energy, say so and show which preference was given up.
Add genre diversity and a bigger, more balanced catalog. More songs per genre and more mid-energy songs would make the experiments more meaningful.
---

## 9. Personal Reflection
My biggest learning moment during this project was realizing that even a simple recommendation algorithm can produce results that seem intelligent, but that does not necessarily mean the recommendations are always accurate or meaningful. I learned how much small changes in weights and ranking strategies can affect the results. I was also surprised that some recommendations stayed the same even after adjusting the weights. Using AI tools helped me develop the code, understand errors, and create tests more efficiently. However, I learned that I cannot simply trust everything AI generates. I had to run the code, test different scenarios, intentionally break parts of the system, and compare the results to make sure the logic was correct.

What I found most interesting was how a relatively simple system could feel like it understood someone's music taste just by comparing features such as genre, mood, energy, and tempo. At the same time, the unusual results, like an energy-first strategy recommending rock music to a classical listener, showed me the limitations of relying too heavily on individual features. If I were to continue this project, I would try adding user feedback so the system could learn from songs people actually enjoy or skip. I would also explore more advanced machine learning techniques to make recommendations more personalized. Overall, this project gave me a better understanding of how recommendation systems work and taught me that building a useful AI system requires testing, critical thinking, and continuous improvement.