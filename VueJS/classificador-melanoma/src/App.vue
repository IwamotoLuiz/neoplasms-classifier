<script setup>
import ImageUploader from './components/ImageUploader.vue'
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Classificação de neoplasmas cutâneos</h1>
      <p>Uma rede neural analisa a imagem dermatoscópica e indica se a lesão parece benigna ou maligna.</p>
    </header>
    <main>
      <ImageUploader />
    </main>
    <footer class="page-footer">
      <span>Trabalho de Conclusão de Curso de Luiz Paulo Iwamoto, Sistemas de Informação, Unesp Bauru</span>
      <span class="samples">
        <a href="/amostras/amostra-1.jpg" download>amostra 1</a> ·
        <a href="/amostras/amostra-2.jpg" download>amostra 2</a>
      </span>
      <a href="https://github.com/IwamotoLuiz/neoplasms-classifier">Código no GitHub</a>
    </footer>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  max-width: 1060px;
  min-height: 100vh;
  margin: 0 auto;
  padding: 48px 32px 28px;
}

.page-header {
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 700;
  line-height: 1.15;
  text-wrap: balance;
}

.page-header h1::after {
  content: '';
  display: block;
  width: 72px;
  height: 5px;
  margin: 16px 0;
  background: var(--blue);
}

.page-header p {
  max-width: 62ch;
  color: var(--muted);
}

main {
  flex: 1;
}

.page-footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px 24px;
  margin-top: 56px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.9rem;
}

.page-footer a {
  color: var(--blue);
}

/* Discretos de propósito: imagens de apoio para a demonstração */
.page-footer .samples a {
  color: inherit;
  text-decoration: none;
}

.page-footer .samples a:hover,
.page-footer .samples a:focus-visible {
  text-decoration: underline;
}

@media (max-width: 760px) {
  .page {
    padding: 32px 20px 24px;
  }
}
</style>
