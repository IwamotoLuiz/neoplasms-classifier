<template>
  <div class="workspace">
    <section class="picker" aria-label="Imagem dermatoscópica">
      <label
        for="file-upload"
        class="frame"
        :class="{ 'frame--filled': imageUrl, 'frame--dragging': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
      >
        <img v-if="imageUrl" :src="imageUrl" alt="Imagem selecionada" class="image-preview">
        <span v-else class="frame-hint">
          <strong>Escolha a imagem</strong>
          <span>ou arraste o arquivo para cá</span>
          <span class="frame-formats">Imagem dermatoscópica em JPEG ou PNG</span>
        </span>
      </label>
      <input id="file-upload" type="file" accept="image/*" @change="onFileSelected">

      <div class="picker-actions">
        <button class="upload-button" :disabled="!imageUrl || isLoading" @click="uploadImage">
          Classificar imagem
        </button>
        <label v-if="imageUrl" for="file-upload" class="change-image">Trocar imagem</label>
      </div>
      <p v-if="selectedFileName" class="file-name">{{ selectedFileName }}</p>
    </section>

    <PredictionResult
      :is-loading="isLoading"
      :elapsed="elapsed"
      :prediction="prediction"
      :probability="probability"
      :error="error"
      :has-image="Boolean(imageUrl)"
    />
  </div>
</template>

<script>
import PredictionResult from './PredictionResult.vue'
import { apiUrl } from '../utils/api.js'
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
      prediction: null,
      probability: null,
      error: null,
      isLoading: false,
      isDragging: false,
      elapsed: 0,
    }
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
    selectFile(file) {
      // A resposta da imagem anterior não pode aparecer ao lado da nova
      this.cancelRequest()
      this.clearResult()
      if (this.imageUrl) URL.revokeObjectURL(this.imageUrl)
      this.selectedFile = file
      this.selectedFileName = file.name
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
.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 40px;
  align-items: start;
}

.frame {
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 1;
  border: 2px dashed var(--line-strong);
  border-radius: 10px;
  background: var(--surface);
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.15s, background-color 0.15s;
}

.frame:hover,
.frame--dragging {
  border-color: var(--blue);
  background: var(--blue-tint);
}

.frame--filled,
.frame--filled:hover {
  border: 2px solid var(--ink);
  background: var(--ink);
}

.frame--filled.frame--dragging {
  border-color: var(--blue);
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.frame-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 24px;
  text-align: center;
  color: var(--muted);
}

.frame-hint strong {
  font-size: 1.25rem;
  color: var(--blue);
}

.frame-formats {
  margin-top: 16px;
  font-size: 0.9rem;
}

/* Continua acessível pelo teclado, ao contrário de display: none */
#file-upload {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

.picker:has(#file-upload:focus-visible) .frame {
  outline: 3px solid var(--blue);
  outline-offset: 3px;
}

.picker-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 24px;
  margin-top: 20px;
}

.upload-button {
  padding: 14px 28px;
  border: 0;
  border-radius: 8px;
  background: var(--blue);
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s;
}

.upload-button:hover {
  background: var(--blue-dark);
}

.upload-button:focus-visible {
  outline: 3px solid var(--blue);
  outline-offset: 3px;
}

.upload-button:disabled {
  background: var(--line);
  color: var(--muted);
  cursor: not-allowed;
}

.change-image {
  color: var(--blue);
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 4px;
  cursor: pointer;
}

.file-name {
  margin-top: 12px;
  color: var(--muted);
  font-size: 0.9rem;
  overflow-wrap: anywhere;
}

@media (max-width: 760px) {
  .workspace {
    grid-template-columns: minmax(0, 1fr);
    gap: 32px;
  }
}
</style>
