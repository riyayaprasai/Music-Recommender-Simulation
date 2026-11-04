# AI Interactions Log

---

## Agentic Workflow (SF8)


**What task did you give the agent?**

<!-- Audit the project against the grading rubric, then fix what was missing. The audit found that data/songs.csv had only 10 songs and 10 columns, that Song already had popularity, instrumentalness and liveness fields which were not in the CSV and not used in scoring, and that python -m src.main crashed on an import. The task for this stretch feature was to make five extra attributes real: in the data, in the scoring and in the explanations. -->

**Prompts used:**

<-- Prompt used:

""Please review the attached project codebase and evaluate it against the course rubric, specifically checking our implementation of the core recommender logic, unit tests, and stretch features (SF8 extra attributes, SF9 diversity penalty, and SF10 Strategy design pattern). First, provide your code review, identify any potential bugs or missing pieces, and confirm that pytest passes cleanly."

Exact earlier prompt used to initiate the workflow and fix structural/test errors:

"Perform a rigorous diagnostic review of the codebase against the course assessment rubric. Systematically resolve any namespace import discrepancies and UTF-8/whitespace CSV ingestion bottlenecks to ensure a clean test suite execution (pytest). Concurrently, expand the corpus and scoring matrix to fully operationalize SF8—integrating continuous latent features and multi-valued metadata into both the data layer and similarity heuristics—while codifying and structuring the SF10 Strategy Design Pattern for clean algorithmic decoupling."

**What did the agent generate or change?**

<!-- data/songs.csv expansion: Expanded the dataset from 10 to 20 songs and added 5 new feature columns (popularity, release_decade, mood_tags, instrumentalness, and liveness), bringing the total column count to 15.

src/strategies.py creation: Implemented the Strategy Design Pattern with an abstract base class (RecommendationStrategy), concrete ranking strategies (GenreFirstStrategy, MoodFirstStrategy, EnergyFocusedStrategy, DefaultStrategy), and a factory function (get_strategy).

src/recommender.py updates: Enhanced load_songs to parse new fields cleanly with utf-8-sig encoding, unified scoring logic so Recommender and score_song use a single source of truth, and updated score rounding so individual itemized reasons sum up accurately to the overall score.

src/main.py updates: Updated profiles to define targets for all 15 attributes and modified the CLI output to render explanations for the new feature contributions.

tests/test_recommender.py updates: Added unit tests verifying that each new attribute alters the calculated score, that mood_tags are evaluated by tag overlap ratio, and that missing values are handled gracefully. -->

**What did you verify or fix manually?**

<!-- Fixed CSV Header Matching & Encoding: Resolved a ValueError during initial pytest runs where DictReader failed to recognize required CSV columns due to leading/trailing whitespace and UTF-8 BOM encoding. Updated load_songs in src/recommender.py to use encoding="utf-8-sig" and normalized header string parsing.

Fixed Module Naming (src/strategies.py): Resolved an ImportError / ModuleNotFoundError during test collection where the test suite expected from src.strategies import ... by renaming the strategy file from strategy.py to strategies.py and exposing get_strategy.

Verified Test Coverage: Ran python3 -m pytest in the terminal to verify all 79 test cases passed cleanly without failure.

Verified Strategy Penalties & Scoring: Checked that the diversity penalty (SF9) correctly re-ranks top candidates inside recommend_songs during list construction rather than simply truncating choices after selection. -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

    <Strategy Pattern was used -->

**How did AI help you brainstorm or implement it?**

<!-- The pattern was already in the project when the audit started (src/strategy.py). The agent reviewed it, kept it, and added tests for it.
Asked the AI how to structure strategy.py using the Strategy Design Pattern with concrete classes like GenreFirstStrategy, MoodFirstStrategy, and EnergyFocusedStrategy. The AI suggested defining an abstract base class (RecommendationStrategy) with a common interface method (score_songs / rank), subclassing it for each specific ranking behavior, and implementing dependency injection so the recommender and main.py can dynamically swap strategies at runtime via a factory helper (get_strategy).-->

**How does the pattern appear in your final code?**

<!-- RecommendationStrategy (abstract base class in src/strategies.py): Defines the common interface with the abstract method score_songs (or rank), establishing a unified contract that all concrete strategies must follow.

Concrete Strategy Classes (src/strategies.py): GenreFirstStrategy, MoodFirstStrategy, EnergyFocusedStrategy, and DefaultStrategy implement specific sorting and prioritization algorithms, overriding the scoring method to tailor recommendations to specific user preferences.

Factory & Dependency Injection (src/strategies.py & src/recommender.py): The get_strategy(name) helper function maps string arguments to strategy instances, and recommendation functions accept the strategy object dynamically. This decouples the core recommender engine from specific sorting rules.

CLI & Experiment Integration (src/main.py & src/experiments.py): Command-line arguments or experiment scripts pass the selected strategy mode into the recommendation pipeline, allowing users to toggle between ranking behaviors seamlessly without modifying the underlying song-loading or data-parsing logic. -->
