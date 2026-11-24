import test from 'node:test'
import assert from 'node:assert/strict'
import { apiUrl } from '../src/utils/api.js'

const RENDER = 'https://neoplasms-classifier.onrender.com/predict'

test('uses the published API when the build sets nothing', () => {
  assert.equal(apiUrl({}), RENDER)
  assert.equal(apiUrl(undefined), RENDER)
  assert.equal(apiUrl({ VITE_API_URL: '' }), RENDER)
})

test('uses the address given to the build', () => {
  assert.equal(apiUrl({ VITE_API_URL: '/predict' }), '/predict')
})
