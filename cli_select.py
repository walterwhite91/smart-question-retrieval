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

def choose_filter_mode() -> str:
    print("\nSelect filter mode:")
    print("1. Chapter wise")
    print("2. Paper and section wise")
    print("3. All")

    while True:
        try:
            c = int(input("Select filter mode number: "))
            if c == 1:
                return "chapter"
            if c == 2:
                return "paper_section"
            if c == 3:
                return "all"
        except ValueError:
            pass
        print("Invalid selection. Try again.")

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

def choose_chapter(dataset: List[QObj]) -> str | None:
    chapters = sorted({
        chapter
        for q in dataset
        for chapter in q.get("chapter", [])
        if isinstance(chapter, str)
    })

    if not chapters:
        return None

    print("\nAvailable chapters:")
    print("0. All chapters")
    for i, chapter in enumerate(chapters, start=1):
        print(f"{i}. {chapter}")

    while True:
        try:
            c = int(input("Select chapter number: "))
            if c == 0:
                return None
            if 1 <= c <= len(chapters):
                return chapters[c - 1]
        except ValueError:
            pass
        print("Invalid selection. Try again.")
