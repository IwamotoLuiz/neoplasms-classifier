import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { otherTheme, themeLabel } from '../src/utils/theme.js'

const read = (path) => readFileSync(new URL(path, import.meta.url), 'utf8')
const css = read('../src/assets/main.css')

function tokens(selector) {
  const block = css.split(`${selector} {`)[1].split('}')[0]
  return Object.fromEntries([...block.matchAll(/--([\w-]+):\s*(#[0-9a-f]{6})/g)].map((m) => [m[1], m[2]]))
}

function luminance(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function contrast(a, b) {
  const [high, low] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (high + 0.05) / (low + 0.05)
}

const themes = { light: tokens(':root'), dark: tokens(":root[data-theme='dark']") }

test('both themes define the same colors', () => {
  assert.deepEqual(Object.keys(themes.dark).sort(), Object.keys(themes.light).sort())
})

test('the dark theme is actually dark', () => {
  for (const name of ['bg', 'surface', 'stage', 'blue-tint']) {
    assert.ok(luminance(themes.dark[name]) < 0.05, `${name} ${themes.dark[name]}`)
  }
})

const pairs = [
  ['ink', 'bg'], ['ink', 'blue-tint'], ['muted', 'bg'], ['muted', 'surface'], ['muted', 'blue-tint'],
  ['blue', 'bg'], ['blue', 'surface'], ['blue', 'blue-tint'], ['on-blue', 'blue'], ['on-blue', 'blue-dark'],
  ['malignant', 'bg'], ['benign', 'bg'], ['warning', 'bg'],
]

for (const [theme, color] of Object.entries(themes)) {
  for (const [text, background] of pairs) {
    test(`${theme}: ${text} is readable on ${background}`, () => {
      const ratio = contrast(color[text], color[background])
      assert.ok(ratio >= 4.5, `${ratio.toFixed(2)}:1`)
    })
  }
}

test('components use only the theme colors', () => {
  const folder = new URL('../src/components/', import.meta.url)
  const files = readdirSync(folder).filter((name) => name.endsWith('.vue')).map((name) => `../src/components/${name}`)
  for (const file of ['../src/App.vue', ...files]) {
    assert.doesNotMatch(read(file), /#[0-9a-f]{3,8}\s*;|rgba?\(/i, file)
  }
})

test('switches between the two themes and names the next one', () => {
  assert.equal(otherTheme('light'), 'dark')
  assert.equal(otherTheme('dark'), 'light')
  assert.equal(otherTheme(undefined), 'dark')
  assert.equal(themeLabel('light'), 'Modo escuro')
  assert.equal(themeLabel('dark'), 'Modo claro')
})

test('the theme is set before the page is painted', () => {
  const html = read('../index.html')
  assert.match(html.split('</head>')[0], /dataset\.theme/)
})
