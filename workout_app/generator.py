from __future__ import annotations

import hashlib
import random
from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from .data import BY_ID, EXERCISES
from .models import Program, ProgramDay, Workout, WorkoutItem, WorkoutRequest

FOCUS_MUSCLES = {
    "Upper body": {"Chest","Back","Shoulders","Biceps","Triceps","Forearms"}, "Lower body": {"Quads","Glutes","Hamstrings","Calves","Adductors"},
    "Arms": {"Biceps","Triceps","Forearms","Grip"}, "Chest": {"Chest"}, "Back": {"Back"}, "Shoulders": {"Shoulders"},
    "Legs": {"Quads","Glutes","Hamstrings","Calves","Adductors"}, "Core": {"Core","Obliques"}, "Cardio": {"Full body","Legs"},
}
PATTERNS = {
    "Full body": ["Squat","Hinge","Horizontal push","Horizontal pull","Core stability","Locomotion"],
    "Upper body": ["Horizontal push","Horizontal pull","Vertical push","Vertical pull","Arm isolation","Core stability"],
    "Lower body": ["Squat","Hinge","Lunge","Core stability","Locomotion"],
    "Arms": ["Arm isolation","Horizontal push","Vertical pull","Carry"],
    "Core": ["Core stability","Anti-rotation","Core flexion","Rotation"],
    "Mobility": ["Mobility"], "Recovery": ["Mobility"], "Cardio": ["Locomotion","Horizontal pull"], "Speed and agility": ["Locomotion"],
}
DIFFICULTY_RANK = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def _rng(seed: str | int | None) -> random.Random:
    if seed is None: return random.Random()
    stable = int(hashlib.sha256(str(seed).encode()).hexdigest()[:16], 16)
    return random.Random(stable)


def _equipment_matches(exercise, selected: tuple[str, ...]) -> bool:
    available = set(selected) | {"No equipment"}
    if "Full gym" in available: return True
    return bool(set(exercise.equipment) & available)


def _eligible(request: WorkoutRequest):
    candidates = [e for e in EXERCISES if e.id not in request.disabled and _equipment_matches(e, request.equipment)]
    if request.low_impact: candidates = [e for e in candidates if e.impact == "Low"]
    rank = DIFFICULTY_RANK[request.difficulty]
    candidates = [e for e in candidates if DIFFICULTY_RANK[e.difficulty] <= rank]
    if request.goal == "Mobility and recovery": candidates = [e for e in candidates if e.category in {"Mobility","Recovery","Core"}]
    elif request.goal == "Calisthenics": candidates = [e for e in candidates if e.category in {"Calisthenics","Bodyweight","Core","Mobility"}]
    return candidates


def _prescription(request: WorkoutRequest, section: str, week: int = 1) -> tuple[int, str, int]:
    if section in {"Warm-up","Cooldown"}: return 1, "30–45 sec", 10
    sets = 2 if request.duration <= 20 else 3 if request.duration <= 45 else 4
    if week > 1 and week % 4 != 0: sets += min(1, (week - 1) // 3)
    if week % 4 == 0 and week > 1: sets = max(2, sets - 1)
    if request.goal == "Build strength": return sets, "4–6 reps", 120
    if request.goal == "Gain muscle": return sets, "8–12 reps", 75
    if request.goal in {"Lose fat","Improve endurance"}: return sets, "35 sec", 30
    if request.goal == "Mobility and recovery": return 1 if request.duration <= 20 else 2, "40 sec/side", 15
    return sets, "8–12 reps", 60


def generate_workout(request: WorkoutRequest, seed: str | int | None = None, *, week: int = 1) -> Workout:
    rng = _rng(seed)
    candidates = _eligible(request)
    if not candidates: raise ValueError("No exercises match those settings. Add equipment, raise difficulty, or turn off low-impact mode.")
    recent = set(request.recent)
    candidates.sort(key=lambda e: (e.id in recent, rng.random()))
    mobility = [e for e in candidates if e.pattern == "Mobility"] or [e for e in EXERCISES if e.pattern == "Mobility"]
    main_pool = [e for e in candidates if e.pattern != "Mobility"]
    if request.focus in FOCUS_MUSCLES:
        focused = [e for e in main_pool if set(e.muscles) & FOCUS_MUSCLES[request.focus]]
        if focused: main_pool = focused
    count = 3 if request.duration <= 15 else 4 if request.duration <= 30 else 5 if request.duration <= 45 else 6
    if request.goal == "Mobility and recovery": main_pool = mobility; count = max(3, count)
    wanted = PATTERNS.get(request.focus, PATTERNS["Full body"])
    chosen, used_names = [], set()
    for pattern in wanted:
        match = next((e for e in main_pool if e.pattern == pattern and e.name not in used_names), None)
        if match and len(chosen) < count: chosen.append(match); used_names.add(match.name)
    for exercise in main_pool:
        if len(chosen) >= count: break
        if exercise.name not in used_names: chosen.append(exercise); used_names.add(exercise.name)
    if not chosen: raise ValueError("No main exercises match those settings.")
    warm_count, cool_count = (1, 1) if request.duration <= 20 else (2, 2)
    warm = rng.sample(mobility, min(warm_count, len(mobility)))
    cool_options = [e for e in mobility if e.id not in {x.id for x in warm}] or mobility
    cool = rng.sample(cool_options, min(cool_count, len(cool_options)))
    items = []
    for section, exercises in (("Warm-up",warm),("Main workout",chosen),("Cooldown",cool)):
        sets, reps, rest = _prescription(request, section, week)
        items.extend(WorkoutItem(e.id,e.name,section,sets,reps,rest,e.instructions,e.muscles,e.equipment,e.pattern) for e in exercises)
    now = datetime.now(timezone.utc).isoformat()
    return Workout(str(uuid4()),f"{request.focus} • {request.goal}",now,request.goal,request.focus,request.duration,request.difficulty,request.intensity,request.equipment,items)


def replacement_for(item: WorkoutItem, request: WorkoutRequest, seed: str | int | None = None):
    options = [e for e in _eligible(request) if e.id != item.exercise_id and e.pattern == item.pattern and set(e.muscles) & set(item.muscles)]
    if not options: raise ValueError("No compatible replacement is available.")
    exercise = _rng(seed).choice(options)
    return replace(item, exercise_id=exercise.id, name=exercise.name, instructions=exercise.instructions, muscles=exercise.muscles, equipment=exercise.equipment)


def generate_program(request: WorkoutRequest, weeks: int, days_per_week: int, seed: str = "program") -> Program:
    if not 2 <= weeks <= 24: raise ValueError("Program length must be between 2 and 24 weeks.")
    if not 2 <= days_per_week <= 6: raise ValueError("Choose 2 to 6 training days per week.")
    created = datetime.now(timezone.utc).isoformat()
    program = Program(str(uuid4()),f"{weeks}-Week {request.focus} {request.goal} Program",weeks,days_per_week,created,request.goal,request.focus)
    recent: list[str] = []
    for week in range(1, weeks + 1):
        phase = "Foundation" if week <= max(2,weeks//4) else "Build" if week < weeks else "Consolidate"
        if week % 4 == 0: phase = "Recovery / technique"
        for day in range(1, days_per_week + 1):
            day_request = replace(request, recent=tuple(recent[-12:]))
            workout = generate_workout(day_request, f"{seed}-{week}-{day}", week=week)
            recent.extend(i.exercise_id for i in workout.items if i.section == "Main workout")
            progression = "Reduce volume ~25%; move crisply." if week % 4 == 0 else "Add 1–2 reps or a small load increase when all sets feel ≤7/10."
            program.schedule.append(ProgramDay(week,day,f"Week {week} · Day {day} · {phase}",workout,progression))
    return program


def workout_from_dict(data: dict) -> Workout:
    return Workout(items=[WorkoutItem(**item) for item in data.pop("items")], **data)

