"""Strategy pattern for multiple ranking modes.

Each strategy re-ranks an already-scored list of songs. Scores are NOT
recalculated — strategies act as tiebreakers and re-rankers, keeping the
scoring pipeline clean and testable. The scored list entries are tuples of
(song_dict, score, reasons_list).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple


class RankingStrategy(ABC):
    """Abstract base class for ranking strategies."""

    @abstractmethod
    def rank(
        self,
        user_prefs: Dict,
        scored: List[Tuple[Dict, float, List[str]]],
    ) -> List[Tuple[Dict, float, List[str]]]:
        """Re-rank the scored list based on this strategy's priority."""
        ...


class DefaultStrategy(RankingStrategy):
    """Ranks by total score only (no re-ranking adjustment)."""

    def rank(self, user_prefs, scored):
        return sorted(scored, key=lambda x: x[1], reverse=True)


class GenreFirstStrategy(RankingStrategy):
    """Prioritizes genre-matching songs, then sorts by score within each group."""

    def rank(self, user_prefs, scored):
        target_genre = user_prefs.get("genre", "")

        def sort_key(item):
            song, score, _ = item
            genre_match = 1 if song["genre"] == target_genre else 0
            return (genre_match, score)

        return sorted(scored, key=sort_key, reverse=True)


class MoodFirstStrategy(RankingStrategy):
    """Prioritizes mood-matching songs, then sorts by score within each group."""

    def rank(self, user_prefs, scored):
        target_mood = user_prefs.get("mood", "")

        def sort_key(item):
            song, score, _ = item
            mood_match = 1 if song["mood"] == target_mood else 0
            return (mood_match, score)

        return sorted(scored, key=sort_key, reverse=True)


class EnergyFocusedStrategy(RankingStrategy):
    """Prioritizes songs closest to the user's target energy, then by score."""

    def rank(self, user_prefs, scored):
        target_energy = user_prefs.get("energy", 0.5)

        def sort_key(item):
            song, score, _ = item
            energy_closeness = 1.0 - abs(song["energy"] - target_energy)
            return (energy_closeness, score)

        return sorted(scored, key=sort_key, reverse=True)


STRATEGIES = {
    "default": DefaultStrategy,
    "genre": GenreFirstStrategy,
    "mood": MoodFirstStrategy,
    "energy": EnergyFocusedStrategy,
}


def get_strategy(name: str) -> RankingStrategy:
    """Factory function that returns a RankingStrategy by name."""
    cls = STRATEGIES.get(name.lower())
    if cls is None:
        valid = ", ".join(STRATEGIES.keys())
        raise ValueError(f"Unknown strategy '{name}'. Valid options: {valid}")
    return cls()
