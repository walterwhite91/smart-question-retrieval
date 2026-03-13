const state = {
  filteredQuestions: [],
  visibleQuestions: [],
  selectedIndex: -1,
  selectedChapter: "",
  chapterSourceEntries: [],
};

const semesterEl = document.getElementById("semester");
const subjectEl = document.getElementById("subject");
const filterModeEl = document.getElementById("filterMode");
const paperTypeEl = document.getElementById("paperType");
const sectionEl = document.getElementById("section");
const chapterBlockEl = document.getElementById("chapterBlock");
const paperSectionBlockEl = document.getElementById("paperSectionBlock");
const chapterChecklistEl = document.getElementById("chapterChecklist");
const toggleAllChaptersEl = document.getElementById("toggleAllChapters");
const questionListEl = document.getElementById("questionList");
const searchInputEl = document.getElementById("searchInput");
const statusCountEl = document.getElementById("statusCount");
const statusScopeEl = document.getElementById("statusScope");
const statusChapterEl = document.getElementById("statusChapter");

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function setOptions(selectEl, values) {
  const current = selectEl.value;
  selectEl.innerHTML = "";
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = String(value);
    option.textContent = String(value);
    selectEl.appendChild(option);
  });
  if (values.includes(current)) {
    selectEl.value = current;
  }
}

function normalizeChapterEntries(chapters) {
  return (chapters || []).map((chapter) => {
    if (typeof chapter === "string") {
      return { name: chapter, count: null, label: chapter };
    }
    return {
      name: chapter.name || "",
      count: Number.isFinite(Number(chapter.count)) ? Number(chapter.count) : null,
      label: chapter.label || chapter.name || "",
    };
  });
}

function withDerivedCounts(chapters, questions) {
  const counts = new Map();
  (questions || []).forEach((question) => {
    (question.chapter || []).forEach((chapter) => {
      counts.set(chapter, (counts.get(chapter) || 0) + 1);
    });
  });
  return chapters.map((chapter) => ({
    ...chapter,
    count: chapter.count ?? counts.get(chapter.name) ?? 0,
  }));
}

function renderChecklist(chapters) {
  const selected = state.selectedChapter;
  chapterChecklistEl.innerHTML = "";
  const normalized = withDerivedCounts(normalizeChapterEntries(chapters), state.filteredQuestions);
  const totalCount = normalized.reduce((sum, chapter) => sum + (chapter.count ?? 0), 0);
  const items = [{ name: "", count: totalCount, label: "All chapters" }, ...normalized];
  items.forEach((chapter) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `check-item${selected === chapter.name ? " active" : ""}`;
    button.dataset.chapter = chapter.name;
    button.innerHTML =
      `<span class="chapter-name">${escapeHtml(chapter.label || chapter.name)}</span>` +
      `<span class="chapter-count">(${chapter.count ?? 0})</span>`;
    button.addEventListener("click", async () => {
      state.selectedChapter = chapter.name;
      renderChecklist(state.chapterSourceEntries);
      updateStatus();
      if (filterModeEl.value === "chapter") {
        await loadFilteredQuestions();
      }
    });
    chapterChecklistEl.appendChild(button);
  });
}

function getSelectedChapters() {
  return state.selectedChapter ? [state.selectedChapter] : [];
}

function getFilterPayload() {
  return {
    semester: semesterEl.value,
    subject: subjectEl.value,
    filter_mode: filterModeEl.value,
    chapters: getSelectedChapters(),
    paper_type: paperTypeEl.value,
    section: sectionEl.value,
  };
}

function updateModeVisibility() {
  const mode = filterModeEl.value;
  chapterBlockEl.classList.toggle("hidden", mode !== "chapter");
  paperSectionBlockEl.classList.toggle("hidden", mode !== "paper_section");
}

async function refreshOptions() {
  const base = await fetchJSON(`/api/options?${new URLSearchParams({
    semester: semesterEl.value || "",
  }).toString()}`);
  setOptions(semesterEl, base.semesters.map(String));
  setOptions(subjectEl, base.subjects);

  const subjectData = await fetchJSON(`/api/options?${new URLSearchParams({
    semester: semesterEl.value || "",
    subject: subjectEl.value || "",
  }).toString()}`);
  const normalizedChapters = normalizeChapterEntries(subjectData.chapters);
  state.chapterSourceEntries = normalizedChapters;
  if (!normalizedChapters.some((chapter) => chapter.name === state.selectedChapter)) {
    state.selectedChapter = "";
  }
  renderChecklist(normalizedChapters);
  setOptions(paperTypeEl, subjectData.paper_types);

  const sectionData = await fetchJSON(`/api/options?${new URLSearchParams({
    semester: semesterEl.value || "",
    subject: subjectEl.value || "",
    paper_type: paperTypeEl.value || "",
  }).toString()}`);
  setOptions(sectionEl, sectionData.sections);
  updateModeVisibility();
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function splitMathSegments(text) {
  const segments = [];
  const mathPattern = /(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\$[^$\n]+\$|\\\([\s\S]+?\\\))/g;
  let lastIndex = 0;
  let match;

  while ((match = mathPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }
    segments.push({ type: "math", value: match[0] });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    segments.push({ type: "text", value: text.slice(lastIndex) });
  }

  return segments;
}

function highlightPlainText(text, query) {
  let rendered = escapeHtml(text);
  const tokens = Array.from(new Set(
    query
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter(Boolean),
  )).sort((a, b) => b.length - a.length);

  tokens.forEach((token) => {
    const pattern = new RegExp(`\\b(${token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})\\b`, "gi");
    rendered = rendered.replace(pattern, "<mark>$1</mark>");
  });

  return rendered;
}

function highlightText(text, query) {
  return splitMathSegments(text)
    .map((segment) => {
      if (segment.type === "math") {
        return escapeHtml(segment.value);
      }
      return highlightPlainText(segment.value, query);
    })
    .join("");
}

async function typesetMath() {
  if (!window.MathJax?.typesetPromise) {
    return;
  }
  try {
    await window.MathJax.typesetPromise([questionListEl]);
  } catch (error) {
    console.error("MathJax rendering failed", error);
  }
}

function renderQuestions(questions, query = "") {
  const template = document.getElementById("questionCardTemplate");
  questionListEl.innerHTML = "";
  state.visibleQuestions = questions;
  state.selectedIndex = questions.length ? 0 : -1;

  questions.forEach((question, index) => {
    const card = template.content.firstElementChild.cloneNode(true);
    const chapters = (question.chapter || []).join(", ") || "N/A";
    card.querySelector(".question-meta").innerHTML =
      `<strong>Marks:</strong> ${question.mark ?? "N/A"} &nbsp;&nbsp;` +
      `<strong>Paper:</strong> ${question.paper_type ?? "N/A"} &nbsp;&nbsp;` +
      `<strong>Section:</strong> ${question.section ?? "N/A"}<br>` +
      `<strong>Chapter:</strong> ${escapeHtml(chapters)}`;
    card.querySelector(".question-body").innerHTML = highlightText(question.question || "", query);
    card.addEventListener("click", () => selectQuestion(index));
    if (index === state.selectedIndex) {
      card.classList.add("selected");
    }
    questionListEl.appendChild(card);
  });

  typesetMath();
}

function selectQuestion(index) {
  state.selectedIndex = index;
  Array.from(questionListEl.children).forEach((card, currentIndex) => {
    card.classList.toggle("selected", currentIndex === index);
  });
}

function currentQuestion() {
  if (state.selectedIndex < 0 || state.selectedIndex >= state.visibleQuestions.length) {
    return null;
  }
  return state.visibleQuestions[state.selectedIndex];
}

function formatQuestion(question) {
  const chapters = (question.chapter || []).join(", ") || "N/A";
  return `[Subject: ${question.subject ?? "N/A"}]\n` +
    `[Chapter: ${chapters}]\n` +
    `[Marks: ${question.mark ?? "N/A"}]\n\n` +
    `Question: ${question.question ?? ""}`;
}

function formatBulk(questions) {
  return questions.map((question, index) => `Q${index + 1}. ${question.question ?? ""}`).join("\n\n");
}

async function copyText(text) {
  await navigator.clipboard.writeText(text);
}

function downloadFile(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function updateStatus(searchCount = null) {
  const payload = getFilterPayload();
  statusCountEl.textContent = `Loaded questions: ${searchCount ?? state.visibleQuestions.length} / ${state.filteredQuestions.length}`;

  const scope = [`Semester ${payload.semester || "-"}`, payload.subject || "Subject -"];
  if (payload.filter_mode === "chapter") {
    scope.push("Chapter wise");
  } else if (payload.filter_mode === "paper_section") {
    scope.push(payload.paper_type || "Paper -");
    scope.push(payload.section ? `Section ${payload.section}` : "Section -");
  } else {
    scope.push("All");
  }
  statusScopeEl.textContent = `Scope: ${scope.join(" | ")}`;

  const chapters = payload.chapters.length ? payload.chapters.join(", ") : "All";
  statusChapterEl.textContent = `Chapters: ${chapters}`;
}

async function loadFilteredQuestions() {
  const data = await fetchJSON("/api/filter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(getFilterPayload()),
  });
  state.filteredQuestions = data.questions;
  renderChecklist(state.chapterSourceEntries);
  renderQuestions(data.questions);
  updateStatus();
}

async function runSearch() {
  const data = await fetchJSON("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...getFilterPayload(),
      query: searchInputEl.value.trim(),
    }),
  });
  renderQuestions(data.questions, searchInputEl.value.trim());
  updateStatus(data.count);
}

async function init() {
  if (toggleAllChaptersEl) {
    toggleAllChaptersEl.style.display = "none";
  }
  await refreshOptions();
  await loadFilteredQuestions();

  semesterEl.addEventListener("change", refreshOptions);
  subjectEl.addEventListener("change", refreshOptions);
  paperTypeEl.addEventListener("change", refreshOptions);
  filterModeEl.addEventListener("change", updateModeVisibility);

  document.getElementById("loadQuestions").addEventListener("click", loadFilteredQuestions);
  document.getElementById("searchButton").addEventListener("click", runSearch);
  document.getElementById("showAllButton").addEventListener("click", () => {
    renderQuestions(state.filteredQuestions);
    updateStatus();
  });

  searchInputEl.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      runSearch();
    }
  });

  document.getElementById("copySelected").addEventListener("click", async () => {
    const question = currentQuestion();
    if (!question) {
      alert("No question selected.");
      return;
    }
    await copyText(formatQuestion(question));
  });

  document.getElementById("copyAll").addEventListener("click", async () => {
    if (!state.filteredQuestions.length) {
      alert("No filtered questions available.");
      return;
    }
    await copyText(formatBulk(state.filteredQuestions));
  });

  document.getElementById("exportTxt").addEventListener("click", () => {
    if (!state.filteredQuestions.length) {
      alert("No filtered questions available.");
      return;
    }
    const content = state.filteredQuestions.map((question, index) => {
      const chapters = (question.chapter || []).join(", ") || "N/A";
      return `Q${index + 1}\n` +
        `Subject: ${question.subject ?? "N/A"}\n` +
        `Chapter: ${chapters}\n` +
        `Marks: ${question.mark ?? "N/A"}\n` +
        `Paper Type: ${question.paper_type ?? "N/A"}\n` +
        `Section: ${question.section ?? "N/A"}\n\n` +
        `${question.question ?? ""}`;
    }).join("\n\n------------------------------------------------------------------------\n\n");
    downloadFile("filtered_questions.txt", content, "text/plain;charset=utf-8");
  });

  document.getElementById("exportJson").addEventListener("click", () => {
    if (!state.filteredQuestions.length) {
      alert("No filtered questions available.");
      return;
    }
    downloadFile(
      "filtered_questions.json",
      `${JSON.stringify(state.filteredQuestions, null, 2)}\n`,
      "application/json;charset=utf-8",
    );
  });

  document.getElementById("openDatasetFolder").addEventListener("click", async () => {
    const data = await fetchJSON("/api/open-dataset-folder", { method: "POST" });
    if (!data.ok) {
      alert(data.message || "Could not open folder.");
    }
  });

  document.addEventListener("keydown", async (event) => {
    if (event.ctrlKey && event.key.toLowerCase() === "f") {
      event.preventDefault();
      searchInputEl.focus();
    }
    if (event.ctrlKey && event.key.toLowerCase() === "c") {
      event.preventDefault();
      const question = currentQuestion();
      if (question) {
        await copyText(formatQuestion(question));
      }
    }
    if (event.ctrlKey && event.key.toLowerCase() === "e") {
      event.preventDefault();
      if (state.filteredQuestions.length) {
        downloadFile(
          "filtered_questions.txt",
          state.filteredQuestions.map((question, index) => `Q${index + 1}. ${question.question ?? ""}`).join("\n\n"),
          "text/plain;charset=utf-8",
        );
      }
    }
  });
}

init().catch((error) => {
  console.error(error);
  alert("Failed to initialize the web app.");
});
