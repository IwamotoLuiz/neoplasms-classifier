<template>
  <div class="viewer">
    <section class="picker" aria-label="Imagem dermatoscópica">
      <label
        for="file-upload"
        class="stage"
        :class="{ 'stage--filled': imageUrl, 'stage--dragging': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
      >
        <img v-if="imageUrl" :src="imageUrl" alt="Imagem selecionada" class="image-preview" @load="onImageLoad">
        <span v-else class="stage-hint">
          <span class="corner corner--tl" aria-hidden="true"></span>
          <span class="corner corner--tr" aria-hidden="true"></span>
          <span class="corner corner--bl" aria-hidden="true"></span>
          <span class="corner corner--br" aria-hidden="true"></span>
          <svg class="lens" viewBox="0 0 48 48" width="44" height="44" aria-hidden="true">
            <circle cx="24" cy="24" r="19" fill="none" stroke="currentColor" stroke-width="1.5" />
            <circle cx="24" cy="24" r="11" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3 3" />
            <path d="M24 1v8M24 39v8M1 24h8M39 24h8" stroke="currentColor" stroke-width="1.5" />
          </svg>
          <strong>{{ isDragging ? 'Solte para abrir a imagem' : 'Abrir imagem dermatoscópica' }}</strong>
          <span>Clique para escolher ou arraste o arquivo para cá</span>
        </span>
      </label>
      <input id="file-upload" type="file" accept="image/*" @change="onFileSelected">

      <div class="infobar">
        <template v-if="imageUrl">
          <span class="file-name" :title="selectedFileName">{{ selectedFileName }}</span>
          <span v-for="detail in fileDetails" :key="detail" class="file-detail">{{ detail }}</span>
          <label for="file-upload" class="change-image">Trocar imagem</label>
        </template>
        <template v-else>
          <span>Nenhuma imagem aberta</span>
          <span class="file-detail">JPEG ou PNG</span>
        </template>
      </div>
    </section>

    <aside class="panel" aria-label="Análise">
      <PredictionResult
        :is-loading="isLoading"
        :elapsed="elapsed"
        :prediction="prediction"
        :probability="probability"
        :error="error"
        :has-image="Boolean(imageUrl)"
      />

      <div class="panel-foot">
        <button class="upload-button" :disabled="!imageUrl || isLoading" @click="uploadImage">
          Classificar imagem
        </button>
        <dl class="model">
          <div><dt>Modelo</dt><dd>EfficientNetV2-S</dd></div>
          <div><dt>Entrada</dt><dd>112 × 112 px</dd></div>
          <div><dt>Corte</dt><dd>50%</dd></div>
        </dl>
        <p class="notice">
          Apoio ao diagnóstico, para uso de profissionais da saúde. Não substitui a avaliação clínica nem a biópsia.
        </p>
      </div>
    </aside>
  </div>
</template>

<script>
import PredictionResult from './PredictionResult.vue'
import { apiUrl } from '../utils/api.js'
import { formatDimensions, formatFileSize } from '../utils/file.js'
import { httpErrorMessage, resultKind } from '../utils/result.js'

// URL da API (local: VITE_API_URL=http://127.0.0.1:8000/predict)
const API_URL = apiUrl(import.meta.env)

export default {
  name: 'ImageUploader',
  components: { PredictionResult },
  data() {
    return {
      selectedFile: null,
      selectedFileName: '',
      imageUrl: null,
      imageWidth: null,
      imageHeight: null,
      prediction: null,
      probability: null,
      error: null,
      isLoading: false,
      isDragging: false,
      elapsed: 0,
    }
  },
  computed: {
    fileDetails() {
      return [
        formatDimensions(this.imageWidth, this.imageHeight),
        formatFileSize(this.selectedFile?.size),
      ].filter(Boolean)
    },
  },
  created() {
    this.request = null
    this.timer = null
  },
  beforeUnmount() {
    this.cancelRequest()
    if (this.imageUrl) URL.revokeObjectURL(this.imageUrl)
  },
  methods: {
    onFileSelected(event) {
      const file = event.target.files[0]
      // Fechar o seletor sem escolher nada mantém a imagem atual
      if (file) this.selectFile(file)
      event.target.value = ''
    },
    onDrop(event) {
      this.isDragging = false
      const file = event.dataTransfer.files[0]
      if (file) this.selectFile(file)
    },
    onImageLoad(event) {
      this.imageWidth = event.target.naturalWidth
      this.imageHeight = event.target.naturalHeight
    },
    selectFile(file) {
      // A resposta da imagem anterior não pode aparecer ao lado da nova
      this.cancelRequest()
      this.clearResult()
      if (this.imageUrl) URL.revokeObjectURL(this.imageUrl)
      this.selectedFile = file
      this.selectedFileName = file.name
      this.imageWidth = null
      this.imageHeight = null
      this.imageUrl = URL.createObjectURL(file)
    },
    clearResult() {
      this.prediction = null
      this.probability = null
      this.error = null
    },
    cancelRequest() {
      if (this.request) this.request.abort()
      this.request = null
      this.stopTimer()
      this.isLoading = false
    },
    startTimer() {
      const startedAt = Date.now()
      this.elapsed = 0
      this.timer = setInterval(() => {
        this.elapsed = Math.floor((Date.now() - startedAt) / 1000)
      }, 1000)
    },
    stopTimer() {
      clearInterval(this.timer)
      this.timer = null
    },
    async uploadImage() {
      if (!this.selectedFile) return

      const request = new AbortController()
      this.request = request
      this.clearResult()
      this.isLoading = true
      this.startTimer()

      const formData = new FormData()
      formData.append('file', this.selectedFile)

      try {
        const response = await fetch(API_URL, { method: 'POST', body: formData, signal: request.signal })
        if (!response.ok) {
          this.error = httpErrorMessage(response.status)
          return
        }

        const data = await response.json()
        if (request.signal.aborted) return

        if (resultKind(data?.prediction) === 'error' || !data?.prediction) {
          console.error('Resposta inesperada da API:', data)
          this.error = 'A API não conseguiu analisar este arquivo. Confira se é uma imagem válida.'
          return
        }
        this.prediction = data.prediction
        this.probability = data.probability ?? null
      } catch (error) {
        if (request.signal.aborted) return
        console.error('Erro ao consultar a API:', error)
        this.error = 'Não foi possível conectar à API. Confira a internet e tente de novo.'
      } finally {
        if (this.request === request) this.cancelRequest()
      }
    },
  },
}
</script>

<style scoped>
/* Uma janela só: a imagem à esquerda e a análise à direita, como num visualizador */
.viewer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface);
  overflow: hidden;
}

.picker {
  display: flex;
  flex-direction: column;
  min-width: 0;
  border-right: 1px solid var(--line);
}

.stage {
  position: relative;
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  /* Largura fixa: sem ela, o aspect-ratio encolhe o palco quando a altura bate no limite */
  width: 100%;
  min-height: 360px;
  max-height: calc(100vh - 210px);
  aspect-ratio: 4 / 3;
  background: var(--well);
  cursor: pointer;
  overflow: hidden;
  transition: background-color 0.15s;
}

.stage:hover,
.stage--dragging {
  background: var(--blue-tint);
}

.stage--filled,
.stage--filled:hover {
  background: var(--stage);
}

.stage--dragging::after {
  content: '';
  position: absolute;
  inset: 8px;
  border: 2px solid var(--blue);
  border-radius: 4px;
  pointer-events: none;
}

/* Absoluta para centralizar mesmo quando a altura do palco é limitada pela tela */
.image-preview {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.stage-hint {
  position: absolute;
  inset: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 24px;
  color: var(--muted);
  text-align: center;
}

.stage-hint strong {
  margin-top: 14px;
  color: var(--ink);
  font-size: 1.05rem;
  font-weight: 600;
}

.stage-hint span {
  font-size: 0.925rem;
}

.lens {
  color: var(--line-strong);
  transition: color 0.15s;
}

.stage:hover .lens,
.stage--dragging .lens {
  color: var(--blue);
}

/* Cantos de enquadramento, no lugar da borda tracejada */
.corner {
  position: absolute;
  width: 22px;
  height: 22px;
  border: 0 solid var(--line-strong);
}

.corner--tl { top: 0; left: 0; border-top-width: 2px; border-left-width: 2px; }
.corner--tr { top: 0; right: 0; border-top-width: 2px; border-right-width: 2px; }
.corner--bl { bottom: 0; left: 0; border-bottom-width: 2px; border-left-width: 2px; }
.corner--br { bottom: 0; right: 0; border-bottom-width: 2px; border-right-width: 2px; }

.stage:hover .corner,
.stage--dragging .corner {
  border-color: var(--blue);
}

/* Continua acessível pelo teclado, ao contrário de display: none */
#file-upload {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.picker:has(#file-upload:focus-visible) .stage {
  outline: 2px solid var(--blue);
  outline-offset: -2px;
}

.infobar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 16px;
  min-height: 44px;
  padding: 10px 16px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.875rem;
}

.file-name {
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  color: var(--ink);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-detail {
  font-family: var(--mono);
  font-size: 0.8125rem;
}

.change-image {
  margin-left: auto;
  color: var(--blue);
  font-weight: 600;
  cursor: pointer;
}

.change-image:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.panel {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.panel-foot {
  padding: 16px 20px 20px;
  border-top: 1px solid var(--line);
}

.upload-button {
  width: 100%;
  padding: 11px 16px;
  border: 0;
  border-radius: 6px;
  background: var(--blue);
  color: var(--on-blue);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s;
}

.upload-button:hover {
  background: var(--blue-dark);
}

.upload-button:focus-visible {
  outline: 2px solid var(--blue);
  outline-offset: 2px;
}

.upload-button:disabled {
  background: var(--line);
  color: var(--muted);
  cursor: not-allowed;
}

.model {
  display: grid;
  gap: 4px;
  margin-top: 18px;
  font-size: 0.8125rem;
}

.model div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.model dt {
  color: var(--muted);
}

.model dd {
  font-family: var(--mono);
}

.notice {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.8125rem;
  line-height: 1.45;
}

@media (max-width: 860px) {
  .viewer {
    grid-template-columns: minmax(0, 1fr);
  }

  .picker {
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .stage {
    min-height: 0;
  }
}
</style>
