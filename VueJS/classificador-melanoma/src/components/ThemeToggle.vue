<template>
  <button type="button" class="theme-toggle" :aria-label="label" :title="label" @click="toggle">
    <svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true">
      <g v-if="theme === 'dark'" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <circle cx="12" cy="12" r="4.5" />
        <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
      </g>
      <path v-else fill="currentColor" d="M20.6 14.2A8.8 8.8 0 0 1 9.8 3.4a.8.8 0 0 0-1.1-.9 9.9 9.9 0 1 0 12.8 12.8.8.8 0 0 0-.9-1.1z" />
    </svg>
  </button>
</template>

<script>
import { otherTheme, themeLabel } from '../utils/theme.js'

export default {
  name: 'ThemeToggle',
  data() {
    // O index.html já definiu o tema antes da primeira pintura
    return { theme: document.documentElement.dataset.theme }
  },
  computed: {
    label() {
      return themeLabel(this.theme)
    },
  },
  methods: {
    toggle() {
      this.theme = otherTheme(this.theme)
      document.documentElement.dataset.theme = this.theme
      try {
        localStorage.setItem('theme', this.theme)
      } catch {
        // Sem armazenamento, a escolha vale só até recarregar
      }
    },
  },
}
</script>

<style scoped>
.theme-toggle {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  padding: 0;
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
}

.theme-toggle:hover {
  border-color: var(--blue);
  color: var(--blue);
}

.theme-toggle:focus-visible {
  outline: 2px solid var(--blue);
  outline-offset: 2px;
}
</style>
