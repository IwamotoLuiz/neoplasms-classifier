import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const app = readFileSync(new URL('../src/App.vue', import.meta.url), 'utf8')
const links = [...app.matchAll(/<a\s[^>]*href="(\/amostras\/[^"]+)"[^>]*>/g)]

test('offers two sample images as downloads', () => {
  assert.deepEqual(links.map((link) => link[1]), ['/amostras/amostra-1.jpg', '/amostras/amostra-2.jpg'])
  for (const [tag] of links) assert.match(tag, /\sdownload[\s>=]/)
})

test('every sample is a JPEG that does not give away its class', () => {
  assert.ok(links.length)
  for (const [, href] of links) {
    const bytes = readFileSync(new URL(`../public${href}`, import.meta.url))
    assert.equal(bytes.subarray(0, 3).toString('hex'), 'ffd8ff')
    assert.doesNotMatch(href + bytes.toString('latin1'), /malig|benig|melanom|nevus/i)
  }
})
