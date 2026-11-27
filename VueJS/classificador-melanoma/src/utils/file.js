// Byte count for the info bar under the image: "850 B", "212 KB", "1,4 MB".
// Returns null when the size is unknown, so the bar just leaves it out.
export function formatFileSize(bytes) {
  if (typeof bytes !== 'number' || !Number.isFinite(bytes) || bytes < 0) return null
  if (bytes < 1024) return `${bytes} B`
  const kilobytes = Math.round(bytes / 1024)
  if (kilobytes < 1024) return `${kilobytes} KB`
  return `${(bytes / 1024 / 1024).toFixed(1).replace('.', ',')} MB`
}

// Pixel size of the opened image, or null before the browser has decoded it.
export function formatDimensions(width, height) {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width <= 0 || height <= 0) return null
  return `${width} × ${height} px`
}
