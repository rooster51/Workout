import pytest

from workout_app.data import EXERCISES
from workout_app.generator import generate_program, generate_workout, replacement_for
from workout_app.models import WorkoutRequest

def request(**changes):
    data=dict(goal="Improve general fitness",focus="Full body",duration=30,equipment=("No equipment",),difficulty="Beginner",intensity="Moderate")
    data.update(changes); return WorkoutRequest(**data)

def test_catalog_has_at_least_75_complete_exercises():
    assert len(EXERCISES)>=75
    assert all(e.instructions and e.substitutions and e.mistakes for e in EXERCISES)

@pytest.mark.parametrize("changes",[
    {"goal":"Lose fat"}, {"goal":"Gain muscle","focus":"Arms","equipment":("Dumbbells",)},
    {"goal":"Calisthenics"}, {"focus":"Legs","equipment":("Dumbbells",)},
    {"duration":10}, {"duration":60,"difficulty":"Advanced"}, {"goal":"Mobility and recovery","focus":"Recovery"},
])
def test_expected_workout_scenarios(changes):
    workout=generate_workout(request(**changes),seed=42)
    assert workout.items
    assert any(i.section=="Main workout" for i in workout.items)
    assert all(i.exercise_id for i in workout.items)

def test_deterministic_with_seed():
    a=generate_workout(request(),seed="same"); b=generate_workout(request(),seed="same")
    assert [x.exercise_id for x in a.items]==[x.exercise_id for x in b.items]

def test_disabled_exercises_never_appear():
    disabled=tuple(e.id for e in EXERCISES[:20]); workout=generate_workout(request(disabled=disabled),seed=1)
    assert not ({i.exercise_id for i in workout.items}&set(disabled))

def test_recent_items_are_deprioritized():
    first=generate_workout(request(),seed=1); recent=tuple(i.exercise_id for i in first.items)
    second=generate_workout(request(recent=recent),seed=1)
    assert [i.exercise_id for i in first.items]!=[i.exercise_id for i in second.items]

def test_replacement_is_compatible():
    req=request(equipment=("Dumbbells",)); workout=generate_workout(req,seed=2); item=next(i for i in workout.items if i.section=="Main workout")
    replacement=replacement_for(item,req,3)
    assert replacement.exercise_id!=item.exercise_id and replacement.pattern==item.pattern

def test_program_has_every_week_and_day():
    program=generate_program(request(),10,3,"fixed")
    assert len(program.schedule)==30
    assert {d.week for d in program.schedule}==set(range(1,11))
    assert "Reduce volume" in next(d.progression for d in program.schedule if d.week==4)

def test_workout_item_tracks_completed_reps_separately():
    workout=generate_workout(request(),seed="reps")
    item=next(i for i in workout.items if i.section=="Main workout")
    item.completed_reps=27
    assert item.reps != "27" and item.completed_reps==27
