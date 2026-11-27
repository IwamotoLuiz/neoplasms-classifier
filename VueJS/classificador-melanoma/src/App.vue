<script setup>
import ImageUploader from './components/ImageUploader.vue'
import ThemeToggle from './components/ThemeToggle.vue'
</script>

<template>
  <div class="app">
    <header class="topbar">
      <div class="brand">
        <svg class="brand-mark" viewBox="0 0 32 32" width="22" height="22" aria-hidden="true">
          <circle cx="16" cy="16" r="12" fill="none" stroke="currentColor" stroke-width="2.5" />
          <circle cx="16" cy="16" r="4.5" fill="currentColor" />
        </svg>
        <h1>Classificador de neoplasmas cutâneos</h1>
      </div>
      <div class="topbar-side">
        <span class="course">TCC · Sistemas de Informação · Unesp Bauru</span>
        <ThemeToggle />
      </div>
    </header>

    <main class="content">
      <ImageUploader />
    </main>

    <footer class="statusbar">
      <span>Luiz Paulo Iwamoto</span>
      <span class="samples">
        <a href="/amostras/amostra-1.jpg" download>amostra 1</a>
        <a href="/amostras/amostra-2.jpg" download>amostra 2</a>
        <a href="/amostras/amostra-3.jpg" download>amostra 3</a>
      </span>
      <a class="repo" href="https://github.com/IwamotoLuiz/neoplasms-classifier">Código no GitHub</a>
    </footer>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px 24px;
  padding: 12px 24px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.brand-mark {
  flex-shrink: 0;
  color: var(--blue);
}

.brand h1 {
  font-size: 1.05rem;
  font-weight: 600;
  line-height: 1.3;
}

.topbar-side {
  display: flex;
  align-items: center;
  gap: 16px;
}

.course {
  color: var(--muted);
  font-size: 0.875rem;
}

.content {
  flex: 1;
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: 24px;
}

.statusbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 24px;
  padding: 10px 24px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.8125rem;
}

/* Discretos de propósito: imagens de apoio para a demonstração */
.samples {
  display: flex;
  gap: 12px;
}

.samples a {
  color: inherit;
  text-decoration: none;
}

.samples a:hover,
.samples a:focus-visible {
  text-decoration: underline;
}

.repo {
  margin-left: auto;
  color: var(--blue);
}

@media (max-width: 760px) {
  .topbar {
    padding: 12px 16px;
  }

  .course {
    display: none;
  }

  .content {
    padding: 16px;
  }

  .statusbar {
    padding: 10px 16px;
  }
}
</style>
