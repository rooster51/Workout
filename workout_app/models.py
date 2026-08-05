from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Difficulty = Literal["Beginner", "Intermediate", "Advanced"]
Impact = Literal["Low", "Moderate", "High"]


@dataclass(frozen=True)
class Exercise:
    id: str
    name: str
    muscles: tuple[str, ...]
    equipment: tuple[str, ...]
    pattern: str
    difficulty: Difficulty
    goals: tuple[str, ...]
    category: str
    impact: Impact
    instructions: tuple[str, ...]
    mistakes: tuple[str, ...]
    substitutions: tuple[str, ...]


@dataclass(frozen=True)
class WorkoutRequest:
    goal: str
    focus: str
    duration: int
    equipment: tuple[str, ...]
    difficulty: Difficulty
    intensity: str
    low_impact: bool = False
    disabled: tuple[str, ...] = ()
    recent: tuple[str, ...] = ()


@dataclass
class WorkoutItem:
    exercise_id: str
    name: str
    section: str
    sets: int
    reps: str
    rest_seconds: int
    instructions: tuple[str, ...]
    muscles: tuple[str, ...]
    equipment: tuple[str, ...]
    pattern: str
    completed_sets: int = 0
    completed_reps: int = 0
    weight: float = 0.0
    rating: int = 7
    notes: str = ""
    pain: bool = False


@dataclass
class Workout:
    id: str
    title: str
    created_at: str
    goal: str
    focus: str
    duration: int
    difficulty: Difficulty
    intensity: str
    equipment: tuple[str, ...]
    items: list[WorkoutItem]
    completed: bool = False
    completion_percentage: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProgramDay:
    week: int
    day: int
    label: str
    workout: Workout
    progression: str


@dataclass
class Program:
    id: str
    title: str
    weeks: int
    days_per_week: int
    created_at: str
    goal: str
    focus: str
    schedule: list[ProgramDay] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
