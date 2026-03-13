# Smart Question Retrieval System

A Data Structures--based academic question retrieval engine designed to
efficiently search and rank similar examination questions using indexing
techniques.

------------------------------------------------------------------------

## 📌 Overview

This project implements a scalable question retrieval system using
fundamental Data Structures concepts including:

-   Hash Maps (Exact Match Layer)
-   Inverted Index (Similarity Retrieval Layer)
-   Set-based Token Overlap Scoring
-   Metadata Filtering (Semester, Subject, Chapter, Section, Paper Type)

The system eliminates brute-force searching and significantly reduces
retrieval complexity.

------------------------------------------------------------------------

## 🚀 Features

-   Constant-time exact match lookup
-   Efficient candidate retrieval using inverted index
-   Token-based similarity scoring
-   Top-k result ranking
-   CLI-based academic metadata filtering
-   Chapter-aware filtering and search
-   `all` command to print all questions in the active filtered scope
-   Modular architecture

------------------------------------------------------------------------

## 🧠 Data Structures Used

| Structure      | Purpose                        |
| -------------- | ------------------------------ |
| Hash Map       | O(1) exact match lookup        |
| Inverted Index | Efficient candidate selection  |
| Set            | Fast token overlap computation |

------------------------------------------------------------------------

## 📂 Project Structure

    smart-question-retrieval/
    ├── loader.py
    ├── normalizer.py
    ├── hashmap.py
    ├── inverted_index.py
    ├── matcher.py
    ├── cli_select.py
    ├── main.py
    ├── dataset.json
    ├── Syllabus/
    ├── LICENSE
    └── README.md

------------------------------------------------------------------------

## ⚙️ Installation

``` bash
git clone <repository-url>
cd smart-question-retrieval
```

No external dependencies required (pure Python 3).

------------------------------------------------------------------------

## ▶️ Running the System

``` bash
python3 main.py dataset.json
```

The system will prompt for:

-   Semester
-   Subject
-   Filter Mode

Depending on the selected filter mode:

-   Chapter wise -> Chapter
-   Paper and section wise -> Paper Type, then Section
-   All -> no additional filter

At the final prompt:

-   Enter a question to retrieve similar questions
-   Enter `all` to print all questions within the current filtered scope
-   Enter `exit` or `quit` to stop the program

------------------------------------------------------------------------

## 🧮 Time Complexity

Build Phase: - Hash Map: O(N) - Inverted Index: O(N × T)

Query Phase: - Exact Match: O(1) - Candidate Retrieval: O(k) -
Similarity Scoring: O(C × k)

------------------------------------------------------------------------

## 🎯 Applications

-   Academic question bank search
-   Exam preparation systems
-   Educational retrieval platforms
-   Preprocessing layer for AI-based systems

------------------------------------------------------------------------

## 👨‍💻 Author

Mimansh Pokhrel\
Kathmandu University\
B.Sc. Computer Science

------------------------------------------------------------------------

## 📜 License

MIT License
