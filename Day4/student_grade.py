"""Student Grade Manager - Streamlit (Week 1, Day 4)

Run with:  streamlit run grade_app.py
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Student Grade Manager", page_icon="🎓", layout="wide")

# ---------------------------------------------------------------------------
# Grading logic  (REPLACE with your Day 2 get_grade() if your scale differs)
# ---------------------------------------------------------------------------
SCALE = [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (0, "F")]
PASS_MARK = 60
GRADE_ORDER = ["A", "B", "C", "D", "F"]


def get_grade(mark):
    for cutoff, grade in SCALE:
        if mark >= cutoff:
            return grade
    return "F"


# ---------------------------------------------------------------------------
# Session state: Streamlit reruns this whole script on every interaction, so a
# plain `students = []` would be reset to empty each time. session_state keeps
# the list alive between reruns.
# ---------------------------------------------------------------------------
if "students" not in st.session_state:
    st.session_state.students = []
if "last_import" not in st.session_state:
    st.session_state.last_import = None

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .hero {
        padding: 1.4rem 1.8rem; border-radius: 16px; margin-bottom: 1.2rem;
        background: linear-gradient(120deg, #8b1a1a 0%, #c62828 55%, #e57373 100%);
        color: white;
    }
    .hero h1 { margin: 0; font-size: 2rem; color: white; }
    .hero p  { margin: .3rem 0 0 0; opacity: .9; }
    [data-testid="stMetric"] {
        background: rgba(198, 40, 40, 0.07);
        border: 1px solid rgba(198, 40, 40, 0.25);
        border-radius: 14px; padding: .8rem 1rem;
    }
    .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
        border-radius: 10px; font-weight: 600; transition: transform .08s ease;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px);
    }
    </style>
    <div class="hero">
        <h1>🎓 Student Grade Manager</h1>
        <p>Add students, track marks, and see class performance at a glance.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def name_exists(name):
    return any(s["name"].lower() == name.lower() for s in st.session_state.students)


def add_student(name, mark):
    """Validate and add. Returns (ok, message)."""
    name = name.strip()
    if not name:
        return False, "Please enter a name."
    if not 0 <= mark <= 100:
        return False, "Mark must be between 0 and 100."
    if name_exists(name):
        return False, f"'{name}' is already in the list. Use Edit to change their mark."
    st.session_state.students.append({"name": name, "mark": mark})
    return True, f"Added {name} ({mark} → {get_grade(mark)})"


def build_df():
    df = pd.DataFrame(st.session_state.students, columns=["name", "mark"])
    if df.empty:
        return df
    df["grade"] = df["mark"].apply(get_grade)
    df["rank"] = df["mark"].rank(method="min", ascending=False).astype(int)
    return df


# ---------------------------------------------------------------------------
# Sidebar: tools
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Tools")

    st.subheader("Grading scale")
    st.table(
        pd.DataFrame(
            {
                "Grade": [g for _, g in SCALE],
                "Marks": ["90 - 100", "80 - 89", "70 - 79", "60 - 69", "0 - 59"],
            }
        ).set_index("Grade")
    )

    st.subheader("Import CSV")
    uploaded = st.file_uploader("Columns: name, mark", type="csv", label_visibility="collapsed")
    if uploaded is not None:
        file_key = f"{uploaded.name}-{uploaded.size}"
        if st.session_state.last_import != file_key:  # import once, not on every rerun
            st.session_state.last_import = file_key
            try:
                raw = pd.read_csv(uploaded)
                raw.columns = [c.strip().lower() for c in raw.columns]
                added = skipped = 0
                for _, row in raw.iterrows():
                    ok, _msg = add_student(str(row["name"]), float(row["mark"]))
                    added += ok
                    skipped += not ok
                st.toast(f"Imported {added} student(s), skipped {skipped}.", icon="📥")
            except Exception:
                st.error("Could not read that file. It needs 'name' and 'mark' columns.")

    st.subheader("Quick actions")
    if st.button("✨ Load sample data", width="stretch"):
        for n, m in [("Priya", 92), ("Arun", 78), ("Divya", 83), ("Karthik", 59), ("Meena", 67)]:
            if not name_exists(n):
                add_student(n, m)
        st.toast("Sample students loaded", icon="✨")

    confirm = st.checkbox("Confirm before clearing")
    if st.button("🗑️ Clear all students", width="stretch", disabled=not confirm):
        st.session_state.students = []
        st.toast("All students cleared", icon="🗑️")

# ---------------------------------------------------------------------------
# Add-student form (a form means typing doesn't trigger a rerun until Add)
# ---------------------------------------------------------------------------
with st.form("add", clear_on_submit=True):
    c1, c2, c3 = st.columns([3, 2, 1], vertical_alignment="bottom")
    name = c1.text_input("Name", placeholder="e.g. Divya")
    mark = c2.number_input("Mark (0 - 100)", min_value=0, max_value=100, value=75, step=1)
    submitted = c3.form_submit_button("➕ Add", width="stretch", type="primary")
    if submitted:
        ok, msg = add_student(name, mark)
        if ok:
            st.toast(msg, icon="✅")
        else:
            st.warning(msg)

df = build_df()

# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------
if df.empty:
    st.info("No students yet. Add one above, or click **Load sample data** in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# Class metrics
# ---------------------------------------------------------------------------
top = df.loc[df["mark"].idxmax()]
low = df.loc[df["mark"].idxmin()]
pass_rate = (df["mark"] >= PASS_MARK).mean() * 100

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Students", len(df))
m2.metric("Class average", f"{df['mark'].mean():.1f}")
m3.metric("Highest", f"{top['mark']:g}", delta=top["name"], delta_color="off")
m4.metric("Lowest", f"{low['mark']:g}", delta=low["name"], delta_color="off")
m5.metric("Pass rate", f"{pass_rate:.0f}%")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_table, tab_manage, tab_stats = st.tabs(["📋 Results", "✏️ Edit / Remove", "📊 Analytics"])

with tab_table:
    f1, f2, f3 = st.columns([3, 2, 2])
    search = f1.text_input("🔍 Search", placeholder="Search by name", label_visibility="collapsed")
    grades = f2.multiselect("Grade", GRADE_ORDER, placeholder="Filter by grade", label_visibility="collapsed")
    sort_by = f3.selectbox(
        "Sort",
        ["Newest first", "Highest mark", "Lowest mark", "Name A-Z"],
        label_visibility="collapsed",
    )

    view = df.copy()
    if search:
        view = view[view["name"].str.contains(search, case=False, na=False)]
    if grades:
        view = view[view["grade"].isin(grades)]
    if sort_by == "Highest mark":
        view = view.sort_values("mark", ascending=False)
    elif sort_by == "Lowest mark":
        view = view.sort_values("mark")
    elif sort_by == "Name A-Z":
        view = view.sort_values("name", key=lambda s: s.str.lower())
    else:
        view = view.iloc[::-1]

    st.dataframe(
        view[["rank", "name", "mark", "grade"]],
        hide_index=True,
        width="stretch",
        column_config={
            "rank": st.column_config.NumberColumn("Rank", width="small"),
            "name": st.column_config.TextColumn("Name"),
            "mark": st.column_config.ProgressColumn("Mark", min_value=0, max_value=100, format="%g"),
            "grade": st.column_config.TextColumn("Grade", width="small"),
        },
    )
    st.caption(f"Showing {len(view)} of {len(df)} students")

    st.download_button(
        "⬇️ Download CSV",
        df[["name", "mark", "grade"]].to_csv(index=False),
        file_name="grades.csv",
        mime="text/csv",
    )

with tab_manage:
    names = df["name"].tolist()
    left, right = st.columns(2)

    with left:
        st.subheader("Edit a mark")
        with st.form("edit"):
            who = st.selectbox("Student", names)
            current = int(df.loc[df["name"] == who, "mark"].iloc[0])
            new_mark = st.number_input("New mark", 0, 100, current, step=1, key=f"edit_{who}")
            if st.form_submit_button("💾 Update", type="primary"):
                for s in st.session_state.students:
                    if s["name"] == who:
                        s["mark"] = new_mark
                st.toast(f"Updated {who} to {new_mark} ({get_grade(new_mark)})", icon="💾")
                st.rerun()

    with right:
        st.subheader("Remove students")
        with st.form("remove"):
            to_remove = st.multiselect("Select students", names)
            if st.form_submit_button("🗑️ Remove selected") and to_remove:
                st.session_state.students = [
                    s for s in st.session_state.students if s["name"] not in to_remove
                ]
                st.toast(f"Removed {len(to_remove)} student(s)", icon="🗑️")
                st.rerun()

with tab_stats:
    a, b = st.columns(2)

    with a:
        st.subheader("Grade distribution")
        counts = df["grade"].value_counts().reindex(GRADE_ORDER, fill_value=0)
        st.bar_chart(counts, color="#c62828")

    with b:
        st.subheader("🏆 Top performers")
        for i, row in enumerate(df.sort_values("mark", ascending=False).head(3).itertuples(), 1):
            medal = ["🥇", "🥈", "🥉"][i - 1]
            st.markdown(f"{medal} **{row.name}**: {row.mark:g} (Grade {row.grade})")

        st.subheader("Summary")
        st.write(
            f"- Median mark: **{df['mark'].median():g}**\n"
            f"- Standard deviation: **{df['mark'].std(ddof=0):.1f}**\n"
            f"- Students below pass mark ({PASS_MARK}): **{int((df['mark'] < PASS_MARK).sum())}**"
        )