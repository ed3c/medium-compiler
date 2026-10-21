import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const root = dirname(fileURLToPath(import.meta.url))
test('canonical Noodle vendor closes every pinned native source with exact Git blobs', () => {
  const lock = JSON.parse(readFileSync(join(root, '../vendor/noodle/UPSTREAM.json'), 'utf8'))
  assert.match(lock.commit, /^[0-9a-f]{40}$/)
  assert.equal(lock.repository, 'ed3c/noodle')
  for (const item of lock.files) {
    assert.match(item.path, /^[a-z0-9./-]+$/i)
    assert.ok(!item.path.includes('..'))
    const bytes = readFileSync(join(root, '../vendor/noodle', item.path))
    const prefix = Buffer.from('blob ' + bytes.length + '\0')
    const blob = createHash('sha1').update(prefix).update(bytes).digest('hex')
    assert.equal(blob, item.git_blob, item.path)
  }
  assert.ok(lock.files.length >= 12)
})
