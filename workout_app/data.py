from __future__ import annotations

from .models import Exercise

ALL_GOALS = ("Lose fat", "Gain muscle", "Improve general fitness", "Build strength", "Improve endurance", "Calisthenics", "Mobility and recovery")
GOALS = list(ALL_GOALS)
FOCUSES = ["Full body", "Upper body", "Lower body", "Arms", "Chest", "Back", "Shoulders", "Legs", "Core", "Cardio", "Speed and agility", "Mobility", "Recovery"]
EQUIPMENT = ["No equipment", "Dumbbells", "Resistance bands", "Bench", "Pull-up bar", "Kettlebell", "Barbell", "Cable machine", "Cardio machine", "Full gym"]

# name, muscles, equipment, pattern, category, impact
_SPECS = [
    ("Air Squat",("Quads","Glutes"),("No equipment",),"Squat","Bodyweight","Moderate"),
    ("Tempo Squat",("Quads","Glutes"),("No equipment",),"Squat","Calisthenics","Moderate"),
    ("Jump Squat",("Quads","Glutes"),("No equipment",),"Squat","Calisthenics","High"),
    ("Goblet Squat",("Quads","Glutes"),("Dumbbells","Kettlebell"),"Squat","Resistance","Moderate"),
    ("Front Squat",("Quads","Core"),("Barbell","Full gym"),"Squat","Resistance","Moderate"),
    ("Back Squat",("Quads","Glutes"),("Barbell","Full gym"),"Squat","Resistance","Moderate"),
    ("Box Squat",("Quads","Glutes"),("Bench","Barbell"),"Squat","Resistance","Low"),
    ("Wall Sit",("Quads","Glutes"),("No equipment",),"Core stability","Bodyweight","Low"),
    ("Glute Bridge",("Glutes","Hamstrings"),("No equipment",),"Hinge","Bodyweight","Low"),
    ("Hip Thrust",("Glutes","Hamstrings"),("Bench","Barbell"),"Hinge","Resistance","Low"),
    ("Dumbbell Romanian Deadlift",("Hamstrings","Glutes"),("Dumbbells",),"Hinge","Resistance","Moderate"),
    ("Kettlebell Deadlift",("Hamstrings","Glutes"),("Kettlebell",),"Hinge","Resistance","Moderate"),
    ("Barbell Deadlift",("Hamstrings","Back"),("Barbell","Full gym"),"Hinge","Resistance","Moderate"),
    ("Kettlebell Swing",("Glutes","Hamstrings"),("Kettlebell",),"Hinge","Conditioning","High"),
    ("Good Morning",("Hamstrings","Back"),("Barbell","Resistance bands"),"Hinge","Resistance","Low"),
    ("Reverse Lunge",("Quads","Glutes"),("No equipment","Dumbbells"),"Lunge","Bodyweight","Moderate"),
    ("Forward Lunge",("Quads","Glutes"),("No equipment","Dumbbells"),"Lunge","Bodyweight","Moderate"),
    ("Lateral Lunge",("Adductors","Glutes"),("No equipment","Dumbbells"),"Lunge","Mobility","Moderate"),
    ("Bulgarian Split Squat",("Quads","Glutes"),("Bench","Dumbbells"),"Lunge","Resistance","Moderate"),
    ("Step Up",("Quads","Glutes"),("Bench","Dumbbells"),"Lunge","Resistance","Moderate"),
    ("Single Leg Romanian Deadlift",("Hamstrings","Glutes"),("No equipment","Dumbbells"),"Hinge","Resistance","Low"),
    ("Standing Calf Raise",("Calves",),("No equipment","Dumbbells"),"Locomotion","Resistance","Low"),
    ("Push Up",("Chest","Triceps"),("No equipment",),"Horizontal push","Calisthenics","Moderate"),
    ("Incline Push Up",("Chest","Triceps"),("Bench",),"Horizontal push","Calisthenics","Low"),
    ("Knee Push Up",("Chest","Triceps"),("No equipment",),"Horizontal push","Calisthenics","Low"),
    ("Diamond Push Up",("Triceps","Chest"),("No equipment",),"Horizontal push","Calisthenics","Moderate"),
    ("Decline Push Up",("Chest","Shoulders"),("Bench",),"Horizontal push","Calisthenics","Moderate"),
    ("Dumbbell Bench Press",("Chest","Triceps"),("Dumbbells","Bench"),"Horizontal push","Resistance","Moderate"),
    ("Barbell Bench Press",("Chest","Triceps"),("Barbell","Bench","Full gym"),"Horizontal push","Resistance","Moderate"),
    ("Dumbbell Floor Press",("Chest","Triceps"),("Dumbbells",),"Horizontal push","Resistance","Low"),
    ("Band Chest Press",("Chest","Triceps"),("Resistance bands",),"Horizontal push","Resistance","Low"),
    ("Pike Push Up",("Shoulders","Triceps"),("No equipment",),"Vertical push","Calisthenics","Moderate"),
    ("Dumbbell Shoulder Press",("Shoulders","Triceps"),("Dumbbells",),"Vertical push","Resistance","Moderate"),
    ("Kettlebell Press",("Shoulders","Triceps"),("Kettlebell",),"Vertical push","Resistance","Moderate"),
    ("Barbell Overhead Press",("Shoulders","Triceps"),("Barbell","Full gym"),"Vertical push","Resistance","Moderate"),
    ("Dumbbell Lateral Raise",("Shoulders",),("Dumbbells",),"Vertical push","Resistance","Low"),
    ("Band Pull Apart",("Back","Shoulders"),("Resistance bands",),"Horizontal pull","Resistance","Low"),
    ("Dumbbell Row",("Back","Biceps"),("Dumbbells",),"Horizontal pull","Resistance","Low"),
    ("Barbell Row",("Back","Biceps"),("Barbell","Full gym"),"Horizontal pull","Resistance","Moderate"),
    ("Inverted Row",("Back","Biceps"),("Pull-up bar","Full gym"),"Horizontal pull","Calisthenics","Moderate"),
    ("Cable Row",("Back","Biceps"),("Cable machine","Full gym"),"Horizontal pull","Resistance","Low"),
    ("Pull Up",("Back","Biceps"),("Pull-up bar",),"Vertical pull","Calisthenics","Moderate"),
    ("Chin Up",("Biceps","Back"),("Pull-up bar",),"Vertical pull","Calisthenics","Moderate"),
    ("Band Lat Pulldown",("Back","Biceps"),("Resistance bands",),"Vertical pull","Resistance","Low"),
    ("Lat Pulldown",("Back","Biceps"),("Cable machine","Full gym"),"Vertical pull","Resistance","Low"),
    ("Dumbbell Curl",("Biceps",),("Dumbbells",),"Arm isolation","Resistance","Low"),
    ("Hammer Curl",("Biceps","Forearms"),("Dumbbells",),"Arm isolation","Resistance","Low"),
    ("Band Curl",("Biceps",),("Resistance bands",),"Arm isolation","Resistance","Low"),
    ("Triceps Dip",("Triceps","Chest"),("Bench","No equipment"),"Horizontal push","Calisthenics","Moderate"),
    ("Overhead Triceps Extension",("Triceps",),("Dumbbells","Resistance bands"),"Arm isolation","Resistance","Low"),
    ("Cable Triceps Pressdown",("Triceps",),("Cable machine","Full gym"),"Arm isolation","Resistance","Low"),
    ("Wrist Curl",("Forearms",),("Dumbbells","Barbell"),"Arm isolation","Resistance","Low"),
    ("Farmer Carry",("Grip","Core"),("Dumbbells","Kettlebell"),"Carry","Conditioning","Low"),
    ("Suitcase Carry",("Core","Grip"),("Dumbbells","Kettlebell"),"Anti-rotation","Conditioning","Low"),
    ("Front Plank",("Core",),("No equipment",),"Core stability","Core","Low"),
    ("Side Plank",("Core","Obliques"),("No equipment",),"Anti-rotation","Core","Low"),
    ("Dead Bug",("Core",),("No equipment",),"Core stability","Core","Low"),
    ("Bird Dog",("Core","Back"),("No equipment",),"Core stability","Core","Low"),
    ("Hollow Hold",("Core",),("No equipment",),"Core stability","Calisthenics","Low"),
    ("Crunch",("Core",),("No equipment",),"Core flexion","Core","Low"),
    ("Reverse Crunch",("Core",),("No equipment",),"Core flexion","Core","Low"),
    ("Bicycle Crunch",("Core","Obliques"),("No equipment",),"Rotation","Core","Moderate"),
    ("Russian Twist",("Obliques","Core"),("No equipment","Dumbbells"),"Rotation","Core","Low"),
    ("Pallof Press",("Core","Obliques"),("Resistance bands","Cable machine"),"Anti-rotation","Core","Low"),
    ("Mountain Climber",("Core","Shoulders"),("No equipment",),"Locomotion","Conditioning","High"),
    ("Burpee",("Full body",),("No equipment",),"Locomotion","Conditioning","High"),
    ("Jumping Jack",("Full body",),("No equipment",),"Locomotion","Cardio","High"),
    ("High Knees",("Full body",),("No equipment",),"Locomotion","Cardio","High"),
    ("Fast Feet",("Calves","Quads"),("No equipment",),"Locomotion","Agility","High"),
    ("Skater Step",("Glutes","Quads"),("No equipment",),"Locomotion","Agility","Moderate"),
    ("Treadmill Walk",("Legs",),("Cardio machine","Full gym"),"Locomotion","Cardio","Low"),
    ("Stationary Bike",("Legs",),("Cardio machine","Full gym"),"Locomotion","Cardio","Low"),
    ("Rowing Machine",("Full body","Back"),("Cardio machine","Full gym"),"Horizontal pull","Cardio","Moderate"),
    ("Cat Cow",("Back",),("No equipment",),"Mobility","Mobility","Low"),
    ("World's Greatest Stretch",("Hips","Back"),("No equipment",),"Mobility","Mobility","Low"),
    ("Hip Flexor Stretch",("Hips",),("No equipment",),"Mobility","Mobility","Low"),
    ("Thoracic Rotation",("Back","Shoulders"),("No equipment",),"Mobility","Mobility","Low"),
    ("Child's Pose",("Back","Shoulders"),("No equipment",),"Mobility","Recovery","Low"),
    ("Downward Dog",("Hamstrings","Shoulders"),("No equipment",),"Mobility","Mobility","Low"),
    ("90/90 Hip Switch",("Hips",),("No equipment",),"Mobility","Mobility","Low"),
    ("Ankle Rock",("Calves","Ankles"),("No equipment",),"Mobility","Mobility","Low"),
    ("Shoulder Wall Slide",("Shoulders","Back"),("No equipment",),"Mobility","Mobility","Low"),
    ("Box Breathing",("Core",),("No equipment",),"Mobility","Recovery","Low"),
]

assert len(_SPECS) >= 75

def _difficulty(name: str, impact: str) -> str:
    if name in {"Barbell Deadlift","Back Squat","Pull Up","Chin Up","Decline Push Up","Barbell Overhead Press"}: return "Advanced"
    if impact == "High" or name in {"Bulgarian Split Squat","Barbell Bench Press","Barbell Row"}: return "Intermediate"
    return "Beginner"

EXERCISES = [Exercise(
    id=f"ex-{i:03}", name=name, muscles=muscles, equipment=equipment, pattern=pattern,
    difficulty=_difficulty(name, impact), goals=ALL_GOALS if category not in {"Mobility","Recovery"} else ("Improve general fitness","Mobility and recovery"),
    category=category, impact=impact,
    instructions=(f"Set up in a stable position for the {name.lower()}.", "Move with control through a comfortable range.", "Brace, breathe, and stop if you feel sharp pain."),
    mistakes=("Rushing the movement or losing a neutral, controlled position.",),
    substitutions=("Use a lighter or supported variation of the same movement pattern.",)
) for i, (name,muscles,equipment,pattern,category,impact) in enumerate(_SPECS, 1)]

BY_ID = {exercise.id: exercise for exercise in EXERCISES}
