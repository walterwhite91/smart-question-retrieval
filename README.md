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
-   Metadata Filtering (Semester, Subject, Section, Paper Type)

The system eliminates brute-force searching and significantly reduces
retrieval complexity.

------------------------------------------------------------------------

## 🚀 Features

-   Constant-time exact match lookup
-   Efficient candidate retrieval using inverted index
-   Token-based similarity scoring
-   Top-k result ranking
-   CLI-based academic metadata filtering
-   Modular architecture

------------------------------------------------------------------------

## 🧠 Data Structures Used

  Structure        Purpose
  ---------------- -------------------------------
  Hash Map         O(1) exact lookup
  Inverted Index   Efficient candidate selection
  Set              Fast token overlap scoring

------------------------------------------------------------------------

## 📂 Project Structure

    smart-question-retrieval/
    │
    ├── src/
    │   ├── loader.py
    │   ├── normalizer.py
    │   ├── hashmap.py
    │   ├── inverted_index.py
    │   ├── matcher.py
    │   ├── cli_select.py
    │   └── main.py
    │
    ├── dataset/
    │   └── dataset.json
    │
    ├── report/
    │   ├── report.tex
    │   ├── chapters/
    │   └── figures/
    │
    ├── LICENSE
    ├── README.md
    └── requirements.txt

------------------------------------------------------------------------

## ⚙️ Installation

``` bash
git clone https://github.com/yourusername/smart-question-retrieval.git
cd smart-question-retrieval
```

No external dependencies required (pure Python 3).

------------------------------------------------------------------------

## ▶️ Running the System

``` bash
python3 src/main.py dataset/dataset.json
```

The system will prompt for:

-   Semester
-   Subject
-   Paper Type
-   Section

Then enter a query to retrieve similar questions.

------------------------------------------------------------------------

## 🧮 Time Complexity

Build Phase: - Hash Map: O(N) - Inverted Index: O(N × T)

Query Phase: - Exact Match: O(1) - Candidate Retrieval: O(k) -
Similarity Scoring: O(C × k)

------------------------------------------------------------------------

## 📄 Project Report

The complete academic report is located in:

    /report/

Compile using:

``` bash
pdflatex report.tex
```

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
