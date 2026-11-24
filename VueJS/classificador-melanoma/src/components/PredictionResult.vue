<template>
  <section class="prediction-result" aria-label="Resultado" aria-live="polite">
    <h2>Resultado</h2>

    <div v-if="isLoading" class="state">
      <p class="loading-message">Analisando a imagem</p>
      <div class="progress" aria-hidden="true"><span></span></div>
      <p class="detail" aria-live="off">Tempo de espera: {{ elapsedText }}</p>
      <p v-if="hint" class="detail">{{ hint }}</p>
    </div>

    <div v-else-if="error" class="state">
      <p class="error-title">Não foi possível classificar</p>
      <p class="error-message">{{ error }}</p>
    </div>

    <div v-else-if="kind" class="state" :class="kind">
      <p class="label">{{ prediction }}</p>
      <template v-if="probabilityText">
        <p class="probability-message">Probabilidade de malignidade: <strong>{{ probabilityText }}</strong></p>
        <div class="meter" aria-hidden="true">
          <div class="meter-track"><span class="meter-fill" :style="{ width: `${probability * 100}%` }"></span></div>
          <span class="meter-cut"></span>
          <div class="meter-scale"><span>0%</span><span>corte: 50%</span><span>100%</span></div>
        </div>
        <p class="detail">O resultado é Maligno quando a probabilidade chega a 50%.</p>
      </template>
    </div>

    <p v-else class="initial-message">
      {{ hasImage ? 'Clique em Classificar imagem para ver o resultado.' : 'Escolha uma imagem para começar.' }}
    </p>

    <p class="notice">
      Apoio ao diagnóstico, para uso de profissionais da saúde. Não substitui a avaliação clínica nem a biópsia.
    </p>
  </section>
</template>

<script>
import { formatProbability } from '../utils/probability.js'
import { formatElapsed, resultKind, waitingHint } from '../utils/result.js'

export default {
  name: 'PredictionResult',
  props: {
    isLoading: Boolean,
    elapsed: { type: Number, default: 0 },
    prediction: { type: String, default: null },
    probability: { type: Number, default: null },
    error: { type: String, default: null },
    hasImage: Boolean,
  },
  computed: {
    kind() {
      return resultKind(this.prediction)
    },
    probabilityText() {
      return formatProbability(this.probability)
    },
    elapsedText() {
      return formatElapsed(this.elapsed)
    },
    hint() {
      return waitingHint(this.elapsed)
    },
  },
}
</script>

<style scoped>
.prediction-result {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

h2 {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--line);
  font-size: 1.25rem;
  font-weight: 600;
}

.state,
.initial-message {
  padding: 28px 0;
}

.initial-message,
.detail {
  color: var(--muted);
}

.detail {
  margin-top: 14px;
  font-size: 0.95rem;
}

.label {
  font-size: 3.25rem;
  font-weight: 600;
  line-height: 1.1;
}

.malignant {
  --kind: var(--malignant);
}

.benign {
  --kind: var(--benign);
}

.malignant .label,
.benign .label {
  color: var(--kind);
}

.probability-message {
  margin-top: 10px;
  font-size: 1.15rem;
}

.meter {
  position: relative;
  margin-top: 26px;
}

.meter-track {
  height: 14px;
  border-radius: 7px;
  background: var(--line);
  overflow: hidden;
}

.meter-fill {
  display: block;
  height: 100%;
  min-width: 4px;
  background: var(--kind);
}

.meter-cut {
  position: absolute;
  top: -5px;
  left: calc(50% - 1px);
  width: 2px;
  height: 24px;
  background: var(--ink);
}

.meter-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: var(--muted);
  font-size: 0.9rem;
}

.meter-scale span {
  flex: 1;
}

.meter-scale span:nth-child(2) {
  text-align: center;
}

.meter-scale span:last-child {
  text-align: right;
}

.loading-message,
.error-title {
  font-size: 1.5rem;
  font-weight: 600;
}

.error-title {
  color: var(--warning);
}

.error-message {
  margin-top: 8px;
}

.progress {
  height: 6px;
  margin-top: 18px;
  border-radius: 3px;
  background: var(--line);
  overflow: hidden;
}

.progress span {
  display: block;
  width: 35%;
  height: 100%;
  border-radius: 3px;
  background: var(--blue);
  animation: slide 1.6s ease-in-out infinite alternate;
}

@keyframes slide {
  from { transform: translateX(0); }
  to { transform: translateX(186%); }
}

@media (prefers-reduced-motion: reduce) {
  .progress span {
    width: 100%;
    opacity: 0.5;
    animation: none;
  }
}

.notice {
  padding: 14px 18px;
  border-left: 4px solid var(--blue);
  background: var(--blue-tint);
  font-size: 0.95rem;
}
</style>
