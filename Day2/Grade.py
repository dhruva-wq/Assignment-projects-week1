"""Student Grade Manager
Features: add/remove students, record grades per subject, averages,
letter grades, class report, ranking, and JSON persistence.
Run: python grade_manager.py
"""
import json
import os

DATA_FILE = "students.json"


# ---------- Persistence ----------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print("Warning: could not read data file. Starting fresh.")
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------- Helpers ----------
def average(grades):
    """grades is a dict {subject: [scores]}; returns overall average or None."""
    scores = [s for subject in grades.values() for s in subject]
    return sum(scores) / len(scores) if scores else None


def letter_grade(avg):
    if avg is None:
        return "N/A"
    if avg >= 90:
        return "A"
    if avg >= 80:
        return "B"
    if avg >= 70:
        return "C"
    if avg >= 60:
        return "D"
    return "F"


def ask_score(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            score = float(raw)
            if 0 <= score <= 100:
                return score
            print("Score must be between 0 and 100.")
        except ValueError:
            print("Please enter a number.")


def pick_student(data):
    name = input("Student name: ").strip().title()
    if name not in data:
        print(f"No student named '{name}'.")
        return None
    return name


# ---------- Actions ----------
def add_student(data):
    name = input("Student name: ").strip().title()
    if not name:
        print("Name cannot be empty.")
    elif name in data:
        print("Student already exists.")
    else:
        data[name] = {}
        print(f"Added {name}.")


def remove_student(data):
    name = pick_student(data)
    if name:
        del data[name]
        print(f"Removed {name}.")


def add_grade(data):
    name = pick_student(data)
    if not name:
        return
    subject = input("Subject: ").strip().title()
    if not subject:
        print("Subject cannot be empty.")
        return
    score = ask_score("Score (0-100): ")
    data[name].setdefault(subject, []).append(score)
    print(f"Recorded {score:g} in {subject} for {name}.")


def view_student(data):
    name = pick_student(data)
    if not name:
        return
    grades = data[name]
    print(f"\n--- {name} ---")
    if not grades:
        print("No grades yet.")
        return
    for subject, scores in grades.items():
        avg = sum(scores) / len(scores)
        print(f"{subject:<15} {', '.join(f'{s:g}' for s in scores)}  (avg {avg:.1f})")
    overall = average(grades)
    print(f"Overall: {overall:.1f} ({letter_grade(overall)})")


def class_report(data):
    if not data:
        print("No students yet.")
        return
    rows = [(n, average(g)) for n, g in data.items()]
    ranked = sorted(rows, key=lambda r: (r[1] is None, -(r[1] or 0)))
    print(f"\n{'Rank':<6}{'Student':<20}{'Average':<10}{'Grade'}")
    print("-" * 42)
    for i, (name, avg) in enumerate(ranked, 1):
        avg_text = f"{avg:.1f}" if avg is not None else "-"
        print(f"{i:<6}{name:<20}{avg_text:<10}{letter_grade(avg)}")
    valid = [a for _, a in rows if a is not None]
    if valid:
        print(f"\nClass average: {sum(valid) / len(valid):.1f}")
        print(f"Highest: {max(valid):.1f} | Lowest: {min(valid):.1f}")


# ---------- Main loop ----------
MENU = """
===== Student Grade Manager =====
1. Add student
2. Add grade
3. View student
4. Class report
5. Remove student
6. Save & exit
"""


def main():
    data = load_data()
    actions = {
        "1": add_student,
        "2": add_grade,
        "3": view_student,
        "4": class_report,
        "5": remove_student,
    }
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "6":
            save_data(data)
            print("Saved. Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action(data)
            save_data(data)  # autosave after every change
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()