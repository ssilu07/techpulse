/**
 * TechPulse Portal Client Script
 * Features:
 * - Instant clientside search with keyboard shortcut '/'
 * - Category filter pill selection with instant grid reflow
 * - Lightbox modal dialog for AMP Web Stories with history back support & light-dismiss
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const searchInput = document.getElementById('story-search-input');
  const categoryPills = document.querySelectorAll('.category-pill');
  const storyCards = document.querySelectorAll('.story-card');
  const countDisplay = document.getElementById('visible-count');
  const noStoriesFound = document.getElementById('no-stories-found');

  // Lightbox Modal Elements
  const storyDialog = document.getElementById('story-dialog');
  const modalIframe = document.getElementById('modal-story-iframe');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const modalExternalBtn = document.getElementById('modal-external-btn');

  let activeCategory = 'all';
  let activeSearchQuery = '';

  // 1. Instant Search & Category Filtering Engine
  function filterStories() {
    let visibleCount = 0;
    const query = activeSearchQuery.toLowerCase().trim();

    storyCards.forEach(card => {
      const title = (card.getAttribute('data-title') || '').toLowerCase();
      const summary = (card.getAttribute('data-summary') || '').toLowerCase();
      const category = card.getAttribute('data-category') || '';

      const matchesCategory = activeCategory === 'all' || category === activeCategory;
      const matchesSearch = !query || title.includes(query) || summary.includes(query);

      if (matchesCategory && matchesSearch) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (countDisplay) {
      countDisplay.textContent = visibleCount;
    }

    if (noStoriesFound) {
      noStoriesFound.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  // Search Input Event
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      activeSearchQuery = e.target.value;
      filterStories();
    });

    // Keyboard shortcut '/' to focus search
    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    });
  }

  // Category Pills Event
  categoryPills.forEach(pill => {
    pill.addEventListener('click', () => {
      categoryPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeCategory = pill.getAttribute('data-category') || 'all';
      filterStories();
    });
  });

  // 2. Interactive Lightbox Modal with History Back Support
  function openStoryModal(slug, pushHistory = true) {
    if (!storyDialog || !modalIframe) return;

    const storyUrl = `/stories/${slug}/`;
    modalIframe.src = storyUrl;

    if (modalExternalBtn) {
      modalExternalBtn.href = storyUrl;
    }

    if (typeof storyDialog.showModal === 'function') {
      storyDialog.showModal();
    } else {
      storyDialog.setAttribute('open', '');
    }

    document.body.style.overflow = 'hidden';

    if (pushHistory) {
      history.pushState({ story: slug }, '', `#story-${slug}`);
    }
  }

  function closeStoryModal(updateHistory = true) {
    if (!storyDialog) return;

    if (typeof storyDialog.close === 'function') {
      storyDialog.close();
    } else {
      storyDialog.removeAttribute('open');
    }

    if (modalIframe) {
      modalIframe.src = 'about:blank';
    }

    document.body.style.overflow = '';

    if (updateHistory && window.location.hash.startsWith('#story-')) {
      history.pushState({}, '', window.location.pathname + window.location.search);
    }
  }

  // Attach card click handlers with touch-drag detection
  let touchStartX = 0;
  let touchStartY = 0;
  let isTouchDragging = false;

  storyCards.forEach(card => {
    // Detect finger drag to distinguish deliberate tap from vertical page scrolling
    card.addEventListener('touchstart', (e) => {
      if (e.touches && e.touches.length > 0) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        isTouchDragging = false;
      }
    }, { passive: true });

    card.addEventListener('touchmove', (e) => {
      if (e.touches && e.touches.length > 0) {
        const diffX = Math.abs(e.touches[0].clientX - touchStartX);
        const diffY = Math.abs(e.touches[0].clientY - touchStartY);
        if (diffX > 8 || diffY > 8) {
          isTouchDragging = true;
        }
      }
    }, { passive: true });

    card.addEventListener('click', (e) => {
      // If user was scrolling or dragging on mobile, ignore click to prevent scroll freeze
      if (isTouchDragging) {
        isTouchDragging = false;
        return;
      }

      // Don't intercept if user specifically clicked an inner anchor
      if (e.target.closest('a')) return;

      const slug = card.getAttribute('data-slug');
      if (slug) {
        // On mobile viewports (<= 768px), direct navigate to AMP story for 100% native 120Hz gestures
        if (window.innerWidth <= 768) {
          window.location.href = `/stories/${slug}/`;
          return;
        }
        openStoryModal(slug, true);
      }
    });

    // Keyboard enter/space access
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const slug = card.getAttribute('data-slug');
        if (slug) {
          if (window.innerWidth <= 768) {
            window.location.href = `/stories/${slug}/`;
            return;
          }
          openStoryModal(slug, true);
        }
      }
    });
  });

  // Close button click
  if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', () => closeStoryModal(true));
  }

  // Light dismiss on backdrop click
  if (storyDialog) {
    storyDialog.addEventListener('click', (event) => {
      if (event.target === storyDialog) {
        closeStoryModal(true);
      }
    });

    // Escape key
    storyDialog.addEventListener('cancel', (e) => {
      e.preventDefault();
      closeStoryModal(true);
    });
  }

  // Handle browser back button (popstate)
  window.addEventListener('popstate', (e) => {
    if (e.state && e.state.story) {
      openStoryModal(e.state.story, false);
    } else {
      closeStoryModal(false);
    }
  });

  // Auto-open if URL contains hash on load
  const initialHash = window.location.hash;
  if (initialHash && initialHash.startsWith('#story-')) {
    const targetSlug = initialHash.replace('#story-', '');
    if (targetSlug) {
      openStoryModal(targetSlug, false);
    }
  }

  // 3. Robust Image Fallback & Crash Prevention Handler
  document.querySelectorAll('img.story-card-bg').forEach(img => {
    img.addEventListener('error', function() {
      const card = this.closest('.story-card');
      const cat = card ? (card.getAttribute('data-category') || 'default') : 'default';
      const fallbackUrl = `/static/images/fallbacks/${cat}.svg`;
      if (!this.src.endsWith(fallbackUrl)) {
        this.src = fallbackUrl;
      }
    });
  });
});

