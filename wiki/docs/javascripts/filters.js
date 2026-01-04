/**
 * COST Action CA19130 Wiki - Filter & Search Utilities
 * Uses Fuse.js for fuzzy search
 */

/**
 * URL State Manager - Sync filters with URL params
 */
class URLStateManager {
  constructor() {
    this.params = new URLSearchParams(window.location.search);
  }

  get(key, defaultValue = '') {
    return this.params.get(key) || defaultValue;
  }

  set(key, value) {
    if (value) {
      this.params.set(key, value);
    } else {
      this.params.delete(key);
    }
    this.updateURL();
  }

  updateURL() {
    const newURL = `${window.location.pathname}?${this.params.toString()}`;
    history.replaceState(null, '', newURL);
  }

  getAll() {
    return Object.fromEntries(this.params.entries());
  }

  clear() {
    this.params = new URLSearchParams();
    this.updateURL();
  }
}

/**
 * Filter State Manager
 */
class FilterState {
  constructor() {
    this.filters = {};
    this.subscribers = [];
  }

  set(key, value) {
    this.filters[key] = value;
    this.notify();
  }

  get(key) {
    return this.filters[key] || '';
  }

  getAll() {
    return { ...this.filters };
  }

  clear() {
    this.filters = {};
    this.notify();
  }

  subscribe(callback) {
    this.subscribers.push(callback);
  }

  notify() {
    this.subscribers.forEach(cb => cb(this.filters));
  }

  hasActiveFilters() {
    return Object.values(this.filters).some(v => v && v.length > 0);
  }
}

/**
 * Data Manager with caching
 */
class DataManager {
  constructor() {
    this.cache = {};
  }

  async load(key, url) {
    if (this.cache[key]) {
      return this.cache[key];
    }

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      this.cache[key] = data;
      return data;
    } catch (error) {
      console.error(`Failed to load ${url}:`, error);
      return null;
    }
  }

  get(key) {
    return this.cache[key] || null;
  }
}

/**
 * Fuzzy Search with Fuse.js
 */
class FuzzySearch {
  constructor(data, options = {}) {
    if (typeof Fuse === 'undefined') {
      console.warn('Fuse.js not loaded, falling back to simple search');
      this.fuse = null;
      this.data = data;
    } else {
      this.fuse = new Fuse(data, {
        threshold: options.threshold || 0.3,
        keys: options.keys || ['title', 'name'],
        includeScore: true,
        minMatchCharLength: 2
      });
    }
  }

  search(query) {
    if (!query) return this.data || [];

    if (this.fuse) {
      return this.fuse.search(query).map(result => result.item);
    }

    // Fallback simple search
    const lowerQuery = query.toLowerCase();
    return (this.data || []).filter(item => {
      return Object.values(item).some(value =>
        String(value).toLowerCase().includes(lowerQuery)
      );
    });
  }
}

/**
 * Pagination helper
 */
class Pagination {
  constructor(options = {}) {
    this.perPage = options.perPage || 25;
    this.currentPage = 1;
    this.totalItems = 0;
    this.onPageChange = options.onPageChange || (() => {});
  }

  setTotalItems(count) {
    this.totalItems = count;
    this.currentPage = 1;
  }

  getTotalPages() {
    return Math.ceil(this.totalItems / this.perPage);
  }

  getSlice(items) {
    const start = (this.currentPage - 1) * this.perPage;
    const end = start + this.perPage;
    return items.slice(start, end);
  }

  goToPage(page) {
    const maxPage = this.getTotalPages();
    this.currentPage = Math.max(1, Math.min(page, maxPage));
    this.onPageChange(this.currentPage);
  }

  nextPage() {
    this.goToPage(this.currentPage + 1);
  }

  prevPage() {
    this.goToPage(this.currentPage - 1);
  }

  renderControls(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const totalPages = this.getTotalPages();
    if (totalPages <= 1) {
      container.innerHTML = '';
      return;
    }

    let html = '<div class="pagination">';

    // Previous button
    html += `<button onclick="pagination.prevPage()" ${this.currentPage === 1 ? 'disabled' : ''}>Prev</button>`;

    // Page numbers
    const pageNumbers = this.getPageNumbers(totalPages);
    pageNumbers.forEach(num => {
      if (num === '...') {
        html += '<span>...</span>';
      } else {
        html += `<button onclick="pagination.goToPage(${num})" class="${num === this.currentPage ? 'active' : ''}">${num}</button>`;
      }
    });

    // Next button
    html += `<button onclick="pagination.nextPage()" ${this.currentPage === totalPages ? 'disabled' : ''}>Next</button>`;

    html += '</div>';
    container.innerHTML = html;
  }

  getPageNumbers(totalPages) {
    const current = this.currentPage;
    const pages = [];

    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (current > 3) pages.push('...');
      for (let i = Math.max(2, current - 1); i <= Math.min(totalPages - 1, current + 1); i++) {
        pages.push(i);
      }
      if (current < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }

    return pages;
  }
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Show loading skeleton
 */
function showSkeleton(containerId, count = 5) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = Array(count).fill(
    '<div class="skeleton skeleton-row"></div>'
  ).join('');
}

/**
 * Hide loading skeleton
 */
function hideSkeleton(containerId) {
  const container = document.getElementById(containerId);
  if (container) container.innerHTML = '';
}

/**
 * Update filter count badge
 */
function updateFilterBadge(filterState, badgeId) {
  const badge = document.getElementById(badgeId);
  if (!badge) return;

  const count = Object.values(filterState.getAll()).filter(v => v).length;
  badge.textContent = count > 0 ? `(${count})` : '';
  badge.style.display = count > 0 ? 'inline' : 'none';
}

/**
 * Initialize filter inputs from URL
 */
function initFiltersFromURL(urlState, filterState, inputMap) {
  Object.entries(inputMap).forEach(([paramKey, inputId]) => {
    const value = urlState.get(paramKey);
    const input = document.getElementById(inputId);
    if (input && value) {
      input.value = value;
      filterState.set(paramKey, value);
    }
  });
}

/**
 * Setup filter input listeners
 */
function setupFilterListeners(filterState, urlState, inputMap, onFilter) {
  Object.entries(inputMap).forEach(([paramKey, inputId]) => {
    const input = document.getElementById(inputId);
    if (!input) return;

    const handler = debounce((value) => {
      filterState.set(paramKey, value);
      urlState.set(paramKey, value);
      onFilter();
    }, 300);

    input.addEventListener('input', (e) => handler(e.target.value));
    input.addEventListener('change', (e) => handler(e.target.value));
  });
}

// Global instances
const urlState = new URLStateManager();
const filterState = new FilterState();
const dataManager = new DataManager();
let pagination = null;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    URLStateManager,
    FilterState,
    DataManager,
    FuzzySearch,
    Pagination,
    debounce,
    showSkeleton,
    hideSkeleton
  };
}
