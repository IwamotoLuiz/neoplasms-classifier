import test from 'node:test'
import assert from 'node:assert/strict'
import { resultKind, httpErrorMessage, formatElapsed, waitingHint } from '../src/utils/result.js'

test('recognizes the two labels returned by the API', () => {
  assert.equal(resultKind('Maligno'), 'malignant')
  assert.equal(resultKind('Benigno'), 'benign')
  assert.equal(resultKind(' maligno '), 'malignant')
})

test('never treats an error text as a label', () => {
  for (const text of ['Erro interno no servidor', 'Erro: 500 - melanoma', 'Não benigno', '']) {
    assert.equal(resultKind(text), 'error')
  }
})

test('has no kind before there is a prediction', () => {
  assert.equal(resultKind(null), null)
  assert.equal(resultKind(undefined), null)
})

test('explains that the server is still starting on gateway errors', () => {
  for (const status of [502, 503, 504]) {
    assert.match(httpErrorMessage(status), /ainda está iniciando/)
  }
})

test('shows the status code on other HTTP errors', () => {
  assert.equal(httpErrorMessage(500), 'A API respondeu com o erro 500. Tente de novo.')
})

test('formats the elapsed time as minutes and seconds', () => {
  assert.equal(formatElapsed(0), '0:00')
  assert.equal(formatElapsed(9), '0:09')
  assert.equal(formatElapsed(75), '1:15')
  assert.equal(formatElapsed(600), '10:00')
})

test('only explains the delay after a normal answer would have arrived', () => {
  assert.equal(waitingHint(0), null)
  assert.equal(waitingHint(24), null)
  assert.match(waitingHint(25), /pode levar cerca de 10 minutos/)
})
