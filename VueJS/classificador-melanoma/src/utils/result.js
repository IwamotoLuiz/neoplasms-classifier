// A normal answer takes up to 20 s; past that, the server is probably waking up.
const HINT_AFTER_SECONDS = 25

// Only the exact labels count, so an error text is never shown as a diagnosis.
export function resultKind(prediction) {
  if (prediction === null || prediction === undefined) return null
  const label = prediction.trim().toLowerCase()
  if (label === 'maligno') return 'malignant'
  if (label === 'benigno') return 'benign'
  return 'error'
}

export function httpErrorMessage(status) {
  if ([502, 503, 504].includes(status)) {
    return 'O servidor ainda está iniciando. Espere um pouco e tente de novo.'
  }
  return `A API respondeu com o erro ${status}. Tente de novo.`
}

export function formatElapsed(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
}

export function waitingHint(seconds) {
  if (seconds < HINT_AFTER_SECONDS) return null
  return 'O servidor estava em repouso e pode levar cerca de 10 minutos para iniciar. Mantenha esta página aberta.'
}
