"""Simple expense tracker."""


class Tracker:
    def __init__(self):
        self._spending: dict[str, list[float]] = {}

    def add(self, category: str, amount: float) -> None:
        if category not in self._spending:
            self._spending[category] = []
        self._spending[category].append(amount)

    def total(self, category: str) -> float:
        return sum(self._spending.get(category, []))

    def categories(self) -> list[str]:
        return list(self._spending.keys())

    def report(self) -> dict[str, float]:
        return {cat: self.total(cat) for cat in self.categories()}
