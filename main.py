import json
import sys
from loader import load_dataset
from matcher import QuestionSearcher
from cli_select import (
    choose_semester,
    choose_subject,
    choose_paper_type,
    choose_section
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

    paper_type = choose_paper_type(dataset)
    dataset = [q for q in dataset if q.get("paper_type") == paper_type]

    section = choose_section(dataset)
    dataset = [q for q in dataset if q.get("section") == section]

    print(
        f"\nLoaded {len(dataset)} questions "
        f"(Sem {semester}, {subject}, {paper_type}, Section {section})\n"
    )

    searcher = QuestionSearcher(dataset)

    print("Type a question to search similar ones (or 'exit'):\n")

    while True:
        q = input("Q> ").strip()
        if q.lower() in {"exit", "quit"}:
            break

        res = searcher.find_similar_questions(q)
        print("\n" + json.dumps(res, indent=2, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
