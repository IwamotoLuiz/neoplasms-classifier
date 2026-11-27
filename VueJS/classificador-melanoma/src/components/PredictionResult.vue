<template>
  <section class="prediction-result" aria-label="Resultado" aria-live="polite">
    <h2>Resultado</h2>

    <div v-if="isLoading" class="state">
      <p class="state-title">Analisando a imagem</p>
      <div class="progress" aria-hidden="true"><span></span></div>
      <p class="detail" aria-live="off">Tempo de espera <span class="mono">{{ elapsedText }}</span></p>
      <p v-if="hint" class="detail">{{ hint }}</p>
    </div>

    <div v-else-if="error" class="state">
      <p class="state-title error-title">Não foi possível classificar</p>
      <p class="detail">{{ error }}</p>
    </div>

    <div v-else-if="kind" class="state" :class="kind">
      <p class="label">{{ prediction }}</p>
      <template v-if="probabilityText">
        <p class="probability">
          <span class="value">{{ probabilityText }}</span>
          <span class="caption">probabilidade de malignidade</span>
        </p>
        <div class="meter" aria-hidden="true">
          <div class="meter-track"><span class="meter-fill" :style="{ width: `${probability * 100}%` }"></span></div>
          <span class="meter-cut"></span>
          <div class="meter-scale"><span>0</span><span>corte 50%</span><span>100</span></div>
        </div>
      </template>
    </div>

    <p v-else class="detail idle">
      {{ hasImage ? 'Clique em Classificar imagem para analisar.' : 'Abra uma imagem para começar.' }}
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
  flex: 1;
  padding: 16px 20px 24px;
}

h2 {
  color: var(--muted);
  font-size: 0.875rem;
  font-weight: 600;
}

.state,
.idle {
  margin-top: 20px;
}

.detail {
  margin-top: 10px;
  color: var(--muted);
  font-size: 0.925rem;
}

.mono {
  font-family: var(--mono);
  color: var(--ink);
}

.malignant {
  --kind: var(--malignant);
}

.benign {
  --kind: var(--benign);
}

.label {
  color: var(--kind, var(--ink));
  font-size: 2.5rem;
  font-weight: 600;
  line-height: 1.1;
}

.probability {
  display: flex;
  flex-direction: column;
  margin-top: 18px;
}

.value {
  font-size: 1.6rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
}

.caption {
  color: var(--muted);
  font-size: 0.875rem;
}

.meter {
  position: relative;
  margin-top: 16px;
}

.meter-track {
  height: 8px;
  border-radius: 2px;
  background: var(--line);
  overflow: hidden;
}

.meter-fill {
  display: block;
  height: 100%;
  min-width: 3px;
  background: var(--kind);
}

.meter-cut {
  position: absolute;
  top: -4px;
  left: calc(50% - 1px);
  width: 2px;
  height: 16px;
  background: var(--ink);
}

.meter-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  color: var(--muted);
  font-family: var(--mono);
  font-size: 0.75rem;
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

.state-title {
  font-size: 1.15rem;
  font-weight: 600;
}

.error-title {
  color: var(--warning);
}

.progress {
  height: 4px;
  margin-top: 14px;
  border-radius: 2px;
  background: var(--line);
  overflow: hidden;
}

.progress span {
  display: block;
  width: 35%;
  height: 100%;
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
</style>
