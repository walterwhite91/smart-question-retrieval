import json
import sys
from loader import load_dataset
from matcher import QuestionSearcher
from cli_select import (
    choose_semester,
    choose_subject,
    choose_filter_mode,
    choose_paper_type,
    choose_section,
    choose_chapter,
)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <dataset.json|dataset.jsonl>")
        sys.exit(1)

    dataset = load_dataset(sys.argv[1])

    semester = choose_semester(dataset)
    dataset = [q for q in dataset if q.get("semester") == semester]

    subject = choose_subject(dataset)
    dataset = [q for q in dataset if q.get("subject") == subject]

    filter_mode = choose_filter_mode()
    paper_type = None
    section = None
    chapter = None

    if filter_mode == "chapter":
        chapter = choose_chapter(dataset)
        if chapter is not None:
            dataset = [
                q for q in dataset
                if chapter in q.get("chapter", [])
            ]
    elif filter_mode == "paper_section":
        paper_type = choose_paper_type(dataset)
        dataset = [q for q in dataset if q.get("paper_type") == paper_type]

        section = choose_section(dataset)
        dataset = [q for q in dataset if q.get("section") == section]

    filter_desc = [f"Sem {semester}", subject]
    if filter_mode == "chapter":
        filter_desc.append(chapter if chapter else "All chapters")
    elif filter_mode == "paper_section":
        filter_desc.append(paper_type)
        filter_desc.append(f"Section {section}")
    else:
        filter_desc.append("All")

    print(
        f"\nLoaded {len(dataset)} questions "
        f"({', '.join(filter_desc)})\n"
    )

    searcher = QuestionSearcher(dataset)

    print("Type a question to search similar ones, 'all' to list all filtered questions, or 'exit':\n")

    while True:
        q = input("Q> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        if q.lower() == "all":
            print("\n" + json.dumps(dataset, indent=2, ensure_ascii=False) + "\n")
            continue

        res = searcher.find_similar_questions(q)
        print("\n" + json.dumps(res, indent=2, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
