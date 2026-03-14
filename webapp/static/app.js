/**
 * Smart Question Retrieval - app.js
 */

class StudyApp {
  constructor() {
    this.state = {
      semester: null,
      subject: '',
      filter_mode: 'all',
      chapters: [],
      paper_type: '',
      section: '',
      query: '',
      studyMode: 'exam', // 'exam' or 'guided'
      questions: []
    };

    this.init();
  }

  async init() {
    this.cacheElements();
    this.bindEvents();
    await this.loadInitialOptions();
    this.restoreState();
  }

  cacheElements() {
    // Buttons
    this.searchBtn = document.getElementById('searchButton');
    this.openDatasetBtn = document.getElementById('openDatasetFolder');

    // Inputs
    this.semSelect = document.getElementById('semester');
    this.subSelect = document.getElementById('subject');
    this.modeSelect = document.getElementById('filterMode');
    this.searchInput = document.getElementById('searchInput');
    this.paperSelect = document.getElementById('paperType');
    this.sectionSelect = document.getElementById('section');

    // Containers
    this.chapterBlock = document.getElementById('chapterBlock');
    this.chapterChecklist = document.getElementById('chapterChecklist');
    this.paperSectionBlock = document.getElementById('paperSectionBlock');
    this.questionList = document.getElementById('questionList');

    // Status
    this.statusCount = document.getElementById('statusCount');
    this.statusScope = document.getElementById('statusScope');

    // Templates
    this.cardTemplate = document.getElementById('questionCardTemplate');
  }

  bindEvents() {
    this.semSelect.addEventListener('change', () => this.handleFilterChange('semester'));
    this.subSelect.addEventListener('change', () => this.handleFilterChange('subject'));
    this.modeSelect.addEventListener('change', () => this.handleFilterChange('mode'));
    this.paperSelect.addEventListener('change', () => this.handleFilterChange('paper'));
    this.sectionSelect.addEventListener('change', () => this.handleFilterChange('section'));

    this.searchBtn.addEventListener('click', () => this.performSearch());
    this.searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.performSearch();
    });

    this.openDatasetBtn.addEventListener('click', () => this.openDataset());
  }

  async loadInitialOptions() {
    try {
      const resp = await fetch('/api/options');
      const data = await resp.json();
      this.populateSelect(this.semSelect, data.semesters, 'Select Semester');
      this.populateSelect(this.subSelect, data.subjects, 'Select Subject');
    } catch (err) {
      console.error('Failed to load options', err);
    }
  }

  populateSelect(el, items, placeholder) {
    el.innerHTML = `<option value="">${placeholder}</option>`;
    items.forEach(item => {
      const val = typeof item === 'object' ? (item.id || item.name) : item;
      const label = typeof item === 'object' ? item.name : item;
      el.innerHTML += `<option value="${val}">${label}</option>`;
    });
  }

  async handleFilterChange(trigger) {
    this.state.semester = this.semSelect.value;
    this.state.subject = this.subSelect.value;
    this.state.filter_mode = this.modeSelect.value;
    this.state.paper_type = this.paperSelect.value;
    this.state.section = this.sectionSelect.value;

    if (trigger === 'semester' || trigger === 'subject' || trigger === 'mode') {
      await this.refreshDependentOptions(trigger);
    }

    this.updateVisibility();
    this.autoLoad();
  }

  async refreshDependentOptions(trigger) {
    const params = new URLSearchParams({
      semester: this.state.semester || '',
      subject: this.state.subject || '',
      paper_type: this.state.paper_type || ''
    });

    const resp = await fetch(`/api/options?${params}`);
    const data = await resp.json();

    if (this.state.filter_mode === 'chapter') {
      this.renderChapterChecklist(data.chapters);
    }

    if (trigger === 'semester' || trigger === 'subject') {
      this.populateSelect(this.paperSelect, data.paper_types, 'Paper Type');
      this.populateSelect(this.sectionSelect, data.sections, 'Section');
    }

    if (this.state.semester && !this.subSelect.value) {
      this.populateSelect(this.subSelect, data.subjects, 'Select Subject');
    }
  }

  renderChapterChecklist(chapters) {
    this.chapterChecklist.innerHTML = '';
    chapters.forEach(ch => {
      const label = document.createElement('label');
      label.className = 'check-item';
      const checked = this.state.chapters.includes(ch.name) ? 'checked' : '';
      label.innerHTML = `
        <input type="checkbox" value="${ch.name}" ${checked}>
        <span>${ch.name} (${ch.count})</span>
      `;
      label.querySelector('input').addEventListener('change', (e) => {
        if (e.target.checked) this.state.chapters.push(ch.name);
        else this.state.chapters = this.state.chapters.filter(c => c !== ch.name);
        this.autoLoad();
      });
      this.chapterChecklist.appendChild(label);
    });
  }

  updateVisibility() {
    this.chapterBlock.style.display = this.state.filter_mode === 'chapter' ? 'block' : 'none';
    this.paperSectionBlock.style.display = this.state.filter_mode === 'paper_section' ? 'grid' : 'none';
  }

  async autoLoad() {
    if (this.state.semester && this.state.subject) {
      await this.fetchQuestions('/api/filter');
    }
  }

  async performSearch() {
    this.state.query = this.searchInput.value.strip();
    await this.fetchQuestions('/api/search');
  }

  async fetchQuestions(endpoint) {
    const payload = {
      ...this.state,
      query: this.searchInput.value
    };

    try {
      const resp = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      this.state.questions = data.questions;
      this.renderQuestions();
      this.statusCount.textContent = `${data.count} Questions found`;
      this.statusScope.textContent = `Scope: ${this.state.subject || 'All'}`;
    } catch (err) {
      console.error('Fetch failed', err);
    }
  }

  renderQuestions() {
    this.questionList.innerHTML = '';
    if (this.state.questions.length === 0) {
      this.questionList.innerHTML = '<div class="empty-state">No questions found matching your criteria</div>';
      return;
    }

    this.state.questions.forEach((q, idx) => {
      const card = this.cardTemplate.content.cloneNode(true);
      const container = card.querySelector('.question-card');
      let cardStudyMode = 'exam'; // Default to exam mode for each card

      container.querySelector('.subject-tag').textContent = q.subject;
      container.querySelector('.marks-tag').textContent = `${q.mark || q.marks || 0} Marks`;
      container.querySelector('.question-body').textContent = q.question;

      // Copy logic
      container.querySelector('.copy-btn').addEventListener('click', () => {
        navigator.clipboard.writeText(q.question);
        const btn = container.querySelector('.copy-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Copied!';
        setTimeout(() => btn.innerHTML = originalText, 2000);
      });

      // Answer logic
      const ansWrapper = container.querySelector('.answer-wrapper');
      if (q.answer_data) {
        ansWrapper.style.display = 'block';
        const showBtn = container.querySelector('.show-answer-btn');
        const content = container.querySelector('.answer-content');
        const textDisplay = container.querySelector('.answer-text');
        const followUp = container.querySelector('.follow-up-text');
        const followUpSection = container.querySelector('.follow-up-section');
        const examBtn = container.querySelector('.mode-btn.exam');
        const guidedBtn = container.querySelector('.mode-btn.guided');

        const updateAnswerDisplay = () => {
          this.updateAnswerContent(q, textDisplay, followUp, followUpSection, cardStudyMode);
          examBtn.classList.toggle('active', cardStudyMode === 'exam');
          guidedBtn.classList.toggle('active', cardStudyMode === 'guided');
          if (window.MathJax) {
            window.MathJax.typesetPromise([container]);
          }
        };

        examBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          cardStudyMode = 'exam';
          updateAnswerDisplay();
        });

        guidedBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          cardStudyMode = 'guided';
          updateAnswerDisplay();
        });

        showBtn.addEventListener('click', () => {
          const isShowing = content.classList.toggle('show');
          showBtn.classList.toggle('expanded', isShowing);
          showBtn.innerHTML = isShowing ?
            `Hide Answer <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transform: rotate(180deg)"><polyline points="6 9 12 15 18 9"></polyline></svg>` :
            `Show Answer <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>`;

          if (isShowing) {
            updateAnswerDisplay();
          }
        });
      }

      this.questionList.appendChild(card);
    });

    if (window.MathJax) {
      window.MathJax.typesetPromise();
    }
  }

  updateAnswerContent(q, textEl, followUpEl, followUpSection, mode) {
    const data = q.answer_data;
    const rawContent = mode === 'exam' ?
      (data.exam_mode || 'No exam-mode answer available.') :
      (data.guided_mode || 'No guided-mode explanation available.');

    textEl.innerHTML = this.formatContent(rawContent);
    followUpEl.textContent = mode === 'exam' ? (data.exam_f_question || '') : (data.guided_f_question || '');
    followUpSection.style.display = followUpEl.textContent ? 'block' : 'none';
  }

  formatContent(text) {
    if (!text) return '';

    const lines = text.split('\n');
    let inTable = false;
    let tableHtml = '';
    let result = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.includes('|') && line.split('|').length > 1) {
        const cols = line.split('|').map(c => c.trim());
        if (!inTable) {
          inTable = true;
          tableHtml = '<table><thead><tr>';
          cols.forEach(c => tableHtml += `<th>${c}</th>`);
          tableHtml += '</tr></thead><tbody>';
        } else {
          tableHtml += '<tr>';
          cols.forEach(c => tableHtml += `<td>${c}</td>`);
          tableHtml += '</tr>';
        }
      } else {
        if (inTable) {
          tableHtml += '</tbody></table>';
          result.push(tableHtml);
          inTable = false;
        }
        if (line) result.push(line);
      }
    }
    if (inTable) {
      tableHtml += '</tbody></table>';
      result.push(tableHtml);
    }

    return result.join('<br>');
  }

  async openDataset() {
    await fetch('/api/open-dataset-folder', { method: 'POST' });
  }

  restoreState() {
    // Optional: restore from localStorage
  }
}

// polyfill
String.prototype.strip = function () { return this.trim(); };

document.addEventListener('DOMContentLoaded', () => {
  window.app = new StudyApp();
});
