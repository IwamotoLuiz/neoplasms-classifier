import test from 'node:test'
import assert from 'node:assert/strict'
import { formatDimensions, formatFileSize } from '../src/utils/file.js'

test('formats file sizes in bytes, KB and MB with a Brazilian decimal comma', () => {
  assert.equal(formatFileSize(0), '0 B')
  assert.equal(formatFileSize(850), '850 B')
  assert.equal(formatFileSize(1024), '1 KB')
  assert.equal(formatFileSize(217_000), '212 KB')
  assert.equal(formatFileSize(1_468_006), '1,4 MB')
})

test('switches to MB instead of showing 1024 KB', () => {
  assert.equal(formatFileSize(1024 * 1024 - 1), '1,0 MB')
})

test('leaves out a size it does not know', () => {
  for (const value of [null, undefined, -1, Number.NaN, Infinity, '212']) {
    assert.equal(formatFileSize(value), null)
  }
})

test('formats the pixel size of the image', () => {
  assert.equal(formatDimensions(1024, 768), '1024 × 768 px')
})

test('leaves out the pixel size before the image is decoded', () => {
  for (const [width, height] of [[0, 0], [null, null], [undefined, 768], [1024, 0], [10.5, 20]]) {
    assert.equal(formatDimensions(width, height), null)
  }
})
