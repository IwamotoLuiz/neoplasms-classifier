// Formats a 0 to 1 probability as a Brazilian percentage.
// Returns null when the API did not send a valid probability.
export function formatProbability(value) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 1) {
    return null
  }
  const percent = value * 100
  if (percent > 99.9) return 'mais de 99,9%'
  if (percent < 0.1) return 'menos de 0,1%'
  return `${percent.toFixed(1).replace('.', ',')}%`
}
