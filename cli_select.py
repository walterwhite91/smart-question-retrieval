from typing import List, Dict, Any

QObj = Dict[str, Any]

def _choose_from_set(values, label):
    values = sorted(values)
    print(f"\nAvailable {label}:")
    for i, v in enumerate(values, start=1):
        print(f"{i}. {v}")

    while True:
        try:
            c = int(input(f"Select {label} number: "))
            if 1 <= c <= len(values):
                return values[c - 1]
        except ValueError:
            pass
        print("Invalid selection. Try again.")

def choose_semester(dataset: List[QObj]) -> int:
    return _choose_from_set(
        {q["semester"] for q in dataset if "semester" in q},
        "semesters"
    )

def choose_subject(dataset: List[QObj]) -> str:
    return _choose_from_set(
        {q["subject"] for q in dataset if "subject" in q},
        "subjects"
    )

def choose_paper_type(dataset: List[QObj]) -> str:
    return _choose_from_set(
        {q["paper_type"] for q in dataset if "paper_type" in q},
        "paper types"
    )

def choose_section(dataset: List[QObj]) -> str:
    return _choose_from_set(
        {q["section"] for q in dataset if "section" in q},
        "sections"
    )
