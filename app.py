from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from workout_app.data import BY_ID, EQUIPMENT, EXERCISES, FOCUSES, GOALS
from workout_app.generator import generate_program, generate_workout, replacement_for
from workout_app.models import WorkoutRequest
from workout_app.storage import load_history, load_programs, load_settings, save_history, save_programs, save_settings

st.set_page_config(page_title="Forge Fitness", page_icon="⚡", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""<style>
.block-container{max-width:760px;padding-top:1rem;padding-bottom:6rem}.stButton>button{min-height:3rem;border-radius:14px;font-weight:700}
[data-testid="stMetric"]{background:var(--secondary-background-color);border-radius:16px;padding:12px}
.workout-card{border:1px solid color-mix(in srgb,currentColor 18%,transparent);border-radius:18px;padding:16px;margin:8px 0}
.eyebrow{font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;opacity:.65}.muted{opacity:.7}
@media(max-width:600px){.block-container{padding-left:1rem;padding-right:1rem}h1{font-size:2rem!important}}
</style>""", unsafe_allow_html=True)

settings = load_settings()
history = load_history()
programs = load_programs()
for key, value in {"workout":None,"active_index":0,"page":"Home"}.items():
    st.session_state.setdefault(key, value)

def request_form(prefix: str):
    goal = st.selectbox("Goal", GOALS, index=GOALS.index("Improve general fitness"), key=f"{prefix}goal")
    focus = st.selectbox("Focus", FOCUSES, key=f"{prefix}focus")
    duration = st.select_slider("Minutes", [10,15,20,30,45,60], value=settings["duration"], key=f"{prefix}duration")
    equipment = st.multiselect("Equipment available", EQUIPMENT, default=settings["equipment"], key=f"{prefix}equipment")
    c1,c2 = st.columns(2)
    difficulty = c1.selectbox("Difficulty", ["Beginner","Intermediate","Advanced"], index=["Beginner","Intermediate","Advanced"].index(settings["difficulty"]), key=f"{prefix}difficulty")
    intensity = c2.selectbox("Intensity", ["Easy","Moderate","Hard"], index=1, key=f"{prefix}intensity")
    return WorkoutRequest(goal,focus,duration,tuple(equipment or ["No equipment"]),difficulty,intensity,settings["low_impact"],tuple(settings["disabled"]))

def render_workout(workout, interactive=True):
    st.subheader(workout.title)
    st.caption(f"{workout.duration} min · {workout.difficulty} · {workout.intensity} · {', '.join(workout.equipment)}")
    for section in ("Warm-up","Main workout","Finisher","Cooldown"):
        items = [item for item in workout.items if item.section == section]
        if not items: continue
        st.markdown(f"### {section}")
        for idx,item in enumerate(workout.items):
            if item.section != section: continue
            with st.expander(f"{item.name}  ·  {item.sets} × {item.reps}", expanded=section=="Main workout"):
                st.caption(f"Rest {item.rest_seconds}s · {', '.join(item.muscles)} · {', '.join(item.equipment)}")
                for step in item.instructions: st.write(f"• {step}")
                if interactive and section == "Main workout":
                    if st.button("Replace exercise", key=f"replace-{workout.id}-{idx}", use_container_width=True):
                        try:
                            req = WorkoutRequest(workout.goal,workout.focus,workout.duration,workout.equipment,workout.difficulty,workout.intensity,settings["low_impact"],tuple(settings["disabled"]))
                            workout.items[idx] = replacement_for(item,req,f"{workout.id}-{idx}")
                            st.rerun()
                        except ValueError as error: st.warning(str(error))

def finish_workout(workout):
    workout.completed = True; workout.completion_percentage = 100
    record = workout.to_dict()
    record["completed_at"] = datetime.now().isoformat()
    record["total_volume"] = sum(i.sets * max(i.weight,0) for i in workout.items)
    history.append(record); save_history(history)
    st.session_state.workout = None; st.session_state.page = "Home"
    st.success("Workout saved. Nice work.")

pages = ["Home","Build workout","Build program","Active workout","History","Progress","Exercises","Settings"]
page = st.sidebar.radio("Navigate", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
st.session_state.page = page

if page == "Home":
    st.markdown('<div class="eyebrow">TRAIN WITH INTENT</div>',unsafe_allow_html=True); st.title("Forge Fitness")
    today = date.today(); week_start = today - timedelta(days=today.weekday())
    this_week = sum(datetime.fromisoformat(x.get("completed_at",x["created_at"])).date() >= week_start for x in history)
    c1,c2,c3 = st.columns(3); c1.metric("This week",this_week); c2.metric("Total",len(history)); c3.metric("Programs",len(programs))
    if st.button("⚡ Build today's workout",type="primary",use_container_width=True): st.session_state.page="Build workout"; st.rerun()
    if st.button("📆 Create an X-week program",use_container_width=True): st.session_state.page="Build program"; st.rerun()
    if history:
        last=history[-1]; st.subheader("Last workout"); st.write(f"**{last['title']}** · {last['duration']} minutes · {last.get('completion_percentage',100)}% complete")
    else: st.info("Your completed workouts and progress will appear here.")

elif page == "Build workout":
    st.title("Build a workout"); req=request_form("daily-")
    if st.button("Generate workout",type="primary",use_container_width=True):
        try: st.session_state.workout=generate_workout(req,datetime.now().isoformat()); st.success("Workout ready.")
        except ValueError as error: st.error(str(error))
    if st.session_state.workout:
        render_workout(st.session_state.workout)
        if st.button("Start workout",type="primary",use_container_width=True): st.session_state.active_index=0; st.session_state.page="Active workout"; st.rerun()

elif page == "Build program":
    st.title("Build an X-week plan"); st.write("Every plan includes progressive build weeks and a lighter recovery week every fourth week.")
    c1,c2=st.columns(2); weeks=c1.number_input("Weeks",2,24,10); days=c2.number_input("Days per week",2,6,3)
    req=request_form("program-")
    if st.button("Create my program",type="primary",use_container_width=True):
        try:
            program=generate_program(req,int(weeks),int(days),f"{date.today()}-{len(programs)}")
            programs.append(program.to_dict()); save_programs(programs); st.session_state.selected_program=len(programs)-1; st.success("Program created and saved.")
        except ValueError as error: st.error(str(error))
    if programs:
        selected=st.selectbox("Saved programs",range(len(programs)),format_func=lambda i: programs[i]["title"],index=st.session_state.get("selected_program",len(programs)-1))
        program=programs[selected]; week=st.selectbox("View week",range(1,program["weeks"]+1))
        for day in [d for d in program["schedule"] if d["week"]==week]:
            with st.expander(day["label"],expanded=day["day"]==1):
                st.caption(day["progression"])
                for item in day["workout"]["items"]: st.write(f"**{item['section']}** · {item['name']} — {item['sets']} × {item['reps']}")

elif page == "Active workout":
    workout=st.session_state.workout
    if not workout: st.info("Build a workout first.")
    else:
        mains=[i for i in workout.items if i.section=="Main workout"]; idx=min(st.session_state.active_index,len(mains)-1); item=mains[idx]
        st.progress((idx+1)/len(mains),text=f"Exercise {idx+1} of {len(mains)}"); st.title(item.name); st.markdown(f"## {item.sets} sets × {item.reps}"); st.caption(f"Rest {item.rest_seconds} seconds")
        for step in item.instructions: st.write(f"• {step}")
        item.completed_sets=st.number_input("Sets completed",0,item.sets,item.completed_sets,key=f"sets-{idx}")
        item.weight=st.number_input("Weight used (optional)",0.0,1000.0,item.weight,step=2.5,key=f"weight-{idx}")
        item.rating=st.slider("Effort (1–10)",1,10,item.rating,key=f"rating-{idx}"); item.notes=st.text_input("Notes",item.notes,key=f"notes-{idx}"); item.pain=st.checkbox("Pain or discomfort",item.pain,key=f"pain-{idx}")
        c1,c2=st.columns(2)
        if c1.button("← Previous",disabled=idx==0,use_container_width=True): st.session_state.active_index-=1; st.rerun()
        if c2.button("Next →",disabled=idx==len(mains)-1,use_container_width=True): st.session_state.active_index+=1; st.rerun()
        if st.button("Finish and save",type="primary",use_container_width=True): finish_workout(workout)

elif page == "History":
    st.title("Workout history")
    if not history: st.info("Complete a workout to start your history.")
    for record in reversed(history):
        with st.expander(f"{record['title']} · {record.get('completed_at',record['created_at'])[:10]}"):
            st.write(f"{record['duration']} minutes · {record['completion_percentage']}% complete")
            for item in record["items"]: st.write(f"{item['name']} — {item['sets']} × {item['reps']}")

elif page == "Progress":
    st.title("Progress")
    if not history: st.info("Charts appear after your first completed workout.")
    else:
        frame=pd.DataFrame([{"date":pd.to_datetime(x.get("completed_at",x["created_at"])),"minutes":x["duration"],"volume":x.get("total_volume",0)} for x in history]).set_index("date")
        c1,c2=st.columns(2); c1.metric("Total minutes",int(frame.minutes.sum())); c2.metric("Training volume",f"{frame.volume.sum():,.0f}")
        st.subheader("Workout minutes"); st.bar_chart(frame["minutes"])
        muscle_counts={}
        for workout in history:
            for item in workout["items"]:
                if item["section"]=="Main workout":
                    for muscle in item["muscles"]: muscle_counts[muscle]=muscle_counts.get(muscle,0)+1
        st.subheader("Most-trained muscles"); st.bar_chart(pd.Series(muscle_counts).sort_values(ascending=False).head(8))

elif page == "Exercises":
    st.title("Exercise library"); search=st.text_input("Search"); muscle=st.selectbox("Muscle",["All"]+sorted({m for e in EXERCISES for m in e.muscles}))
    shown=[e for e in EXERCISES if search.lower() in e.name.lower() and (muscle=="All" or muscle in e.muscles)]
    st.caption(f"{len(shown)} exercises")
    for exercise in shown:
        with st.expander(exercise.name):
            st.caption(f"{exercise.difficulty} · {exercise.pattern} · {', '.join(exercise.equipment)}")
            for step in exercise.instructions: st.write(f"• {step}")
            st.write(f"**Common mistake:** {exercise.mistakes[0]}"); st.write(f"**Substitution:** {exercise.substitutions[0]}")

elif page == "Settings":
    st.title("Settings")
    equipment=st.multiselect("Default equipment",EQUIPMENT,default=settings["equipment"]); duration=st.select_slider("Default minutes",[10,15,20,30,45,60],value=settings["duration"])
    difficulty=st.selectbox("Default difficulty",["Beginner","Intermediate","Advanced"],index=["Beginner","Intermediate","Advanced"].index(settings["difficulty"])); low_impact=st.toggle("Low-impact mode",settings["low_impact"])
    disabled_names=st.multiselect("Exercises to exclude",[e.name for e in EXERCISES],default=[BY_ID[i].name for i in settings["disabled"] if i in BY_ID])
    if st.button("Save settings",type="primary",use_container_width=True):
        settings.update(equipment=equipment or ["No equipment"],duration=duration,difficulty=difficulty,low_impact=low_impact,disabled=[e.id for e in EXERCISES if e.name in disabled_names]); save_settings(settings); st.success("Settings saved.")

