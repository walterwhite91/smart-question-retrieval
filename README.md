# Smart Question Retrieval - Study Hub

A fast, minimalist academic question retrieval web engine. Designed to efficiently search, rank, and study examination questions using underlying Data Structures indexing techniques, now wrapping a beautiful, modern Flask and glassmorphic UI.

---

## 📌 Overview

This project has evolved from a simple Python CLI tool into a scalable, interactive web application. The core search engine continues to leverage fundamental Data Structures:

- **Hash Maps** (Exact Match Layer)
- **Inverted Index** (Similarity Retrieval Layer)
- **Set-based Token Overlap Scoring**

The frontend provides a premium, responsive "Study Hub" interface, allowing students to filter, search, and track their study progress in an intuitive way.

---

## 🚀 Key Web Features

- **Study Modes**: Toggle each answer individually between "Exam Mode" (concise, exam-oriented) and "Guided Mode" (detailed, conceptual steps).
- **Subject & Chapter Filtering**: Drill down dynamically into specific academic requirements.
- **Smart Progress Tracking**: Mark questions as "Solved." Your progress is saved locally and instantly reflects in a beautiful floating circular progress ring that calculates progress against the entire subject.
- **Detailed Progress Dashboard**: A statistics modal showcases both overall subject progress and a specific, localized chapter-wise breakdown.
- **Premium UI**: Minimalistic dark mode with glassmorphism effects, fluid animations, and focused reading layouts.
- **Math, Tables & Code Blocks**: Out-of-the-box MathJax rendering for LaTeX equations and a custom JS/CSS parser for formatting text-based tables and code blocks.
- **Copy answers**: One-click copying of answers to the clipboard.

---

## 📂 Project Structure

```text
smart-question-retrieval/
├── webapp/                  # The new Web Application layer
│   ├── static/              # CSS Styles, JS logic, and animations
│   ├── templates/           # HTML Jinja templates (index.html)
│   └── app.py               # Main Flask server entry point
├── services/                # Backend services bridging UI and Search
│   └── search_controller.py 
├── hashmap.py               # Core O(1) exact match lookup
├── inverted_index.py        # Core candidate selection
├── matcher.py               # Core token overlap computation
├── loader.py                # Data ingestion handlers
├── normalizer.py            # Text normalization functions
├── dataset.json             # Core question index
├── expanded_dataset.jsonl   # Answer dataset and formatting
├── requirements.txt         # Python dependencies
└── README.md                # You are here!
```

---

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd smart-question-retrieval
   ```

2. **Install requirements:**
   *(Ensure you have Python 3 installed)*
   ```bash
   pip3 install -r requirements.txt
   ```

---

## ▶️ Running the Study Hub

1. **Start the Flask Backend:**
   ```bash
   python3 webapp/app.py
   ```

2. **Open the Web UI:**
   Navigate your browser to `http://127.0.0.1:5001`.

*The app runs entirely locally. Progress tracking is stored securely inside your browser's Local Storage.*

---

## 👨‍💻 Author

Mimansh Pokhrel  
Kathmandu University  
B.Sc. Computer Science

------------------------------------------------------------------------

## 📜 License

MIT License
