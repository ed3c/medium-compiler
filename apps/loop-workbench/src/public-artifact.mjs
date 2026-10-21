/** Reviewed public artifact reader. Display only, never a Host or authority interface. */
const DIGEST = /^[a-f0-9]{64}$/;
const PREFIX = /^\/assets\/loop-data\/([a-f0-9]{64})\/graph\.json$/;
const MAX_BYTES = 2 * 1024 * 1024;

export function reviewedArtifactRef(snapshot, manifest, id, origin) {
  if (typeof manifest !== 'string' || typeof origin !== 'string') throw new Error('SOURCE_UNBOUND');
  const parsed = new URL(manifest, origin);
  const matched = parsed.pathname.match(PREFIX);
  if (!matched || parsed.origin !== origin || parsed.search || parsed.hash ||
      parsed.username || parsed.password) throw new Error('SOURCE_UNBOUND');
  const digest = matched[1];
  if (!snapshot || snapshot.schema_version !== 2 || snapshot.snapshot_sha256 !== digest ||
      !Array.isArray(snapshot.graph?.artifacts) ||
      !snapshot.content_urls || typeof snapshot.content_urls !== 'object' ||
      Array.isArray(snapshot.content_urls)) throw new Error('SOURCE_UNBOUND');
  const rows = snapshot.graph.artifacts.filter(a => a.id === id);
  if (rows.length !== 1) throw new Error('ARTIFACT_IDENTITY_UNKNOWN');
  const artifact = rows[0];
  if ('content' in artifact || 'content_encoding' in artifact || 'public_content' in artifact)
    throw new Error('RAW_ARTIFACT_REFUSED');
  if (artifact.status !== 'available' || !DIGEST.test(artifact.public_sha256 || '') ||
      !Number.isSafeInteger(artifact.public_bytes) ||
      artifact.public_bytes < 0 || artifact.public_bytes > MAX_BYTES)
    throw new Error('NOT_PUBLIC');
  const pathname = '/assets/loop-data/' + digest + '/artifacts/' +
    artifact.public_sha256 + '.txt';
  if (snapshot.content_urls[id] !== pathname) throw new Error('ARTIFACT_URL_UNBOUND');
  return {pathname, sha256: artifact.public_sha256, bytes: artifact.public_bytes};
}

export async function readReviewedArtifact(snapshot, manifest, id, origin,
    fetchImpl = fetch, cryptoImpl = globalThis.crypto) {
  const ref = reviewedArtifactRef(snapshot, manifest, id, origin);
  const response = await fetchImpl(new URL(ref.pathname, origin).href, {
    credentials: 'omit', redirect: 'error'
  });
  if (!response.ok || response.redirected) throw new Error('ARTIFACT_UNAVAILABLE');
  const payload = await response.arrayBuffer();
  if (payload.byteLength !== ref.bytes) throw new Error('ARTIFACT_BYTES_DRIFT');
  const sha = await cryptoImpl.subtle.digest('SHA-256', payload);
  const observed = Array.from(new Uint8Array(sha), v => v.toString(16).padStart(2, '0')).join('');
  if (observed !== ref.sha256) throw new Error('ARTIFACT_DIGEST_DRIFT');
  return new TextDecoder('utf-8', {fatal: true}).decode(payload);
}
