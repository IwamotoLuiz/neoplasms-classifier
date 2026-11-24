import test from 'node:test'
import assert from 'node:assert/strict'
import { formatProbability } from '../src/utils/probability.js'

test('formats with one decimal place and a comma', () => {
  assert.equal(formatProbability(0.9731), '97,3%')
  assert.equal(formatProbability(0.5), '50,0%')
})

test('never shows 100% or 0% for a rounded value', () => {
  assert.equal(formatProbability(0.99996), 'mais de 99,9%')
  assert.equal(formatProbability(0.00004), 'menos de 0,1%')
  assert.equal(formatProbability(1), 'mais de 99,9%')
  assert.equal(formatProbability(0), 'menos de 0,1%')
})

test('returns null when the API sends no valid probability', () => {
  for (const value of [undefined, null, '0.9', NaN, Infinity, -0.1, 1.1]) {
    assert.equal(formatProbability(value), null)
  }
})
