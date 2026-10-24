// Packs the generator's viewer payload into one self-contained HTML file.
// Usage (from source/viewer-build): node build.mjs ../../build/viewer_payload ../../viewer/apollo_signet_viewer.html
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';
import { MeshoptEncoder } from 'meshoptimizer';

const here = path.dirname(fileURLToPath(import.meta.url));
const [payloadDir, outFile] = process.argv.slice(2);
if (!payloadDir || !outFile) throw new Error('usage: node build.mjs <viewer_payload dir> <out.html>');
await MeshoptEncoder.ready;

const read = (name, T) => { const b = fs.readFileSync(path.join(payloadDir, name)); return new T(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength)); };
const b64 = (u8) => Buffer.from(u8.buffer, u8.byteOffset, u8.byteLength).toString('base64');

// positions: 16-bit quantised with one scale for all axes; normals: 16-bit octahedral
function packMesh(pos, idx, nrm) {
  const n = pos.length / 3;
  const [remap, unique] = MeshoptEncoder.reorderMesh(idx, true, true);   // remaps idx in place
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < n; i++) for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], pos[3 * i + k]); hi[k] = Math.max(hi[k], pos[3 * i + k]); }
  const scale = Math.max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]) / 65535;
  const q = new Uint16Array(unique * 4), N = nrm ? new Float32Array(unique * 4) : null;
  for (let i = 0; i < n; i++) {
    const j = remap[i];
    if (j === 0xffffffff) continue;
    for (let k = 0; k < 3; k++) {
      q[4 * j + k] = Math.round((pos[3 * i + k] - lo[k]) / scale);
      if (N) N[4 * j + k] = nrm[3 * i + k];
    }
  }
  const out = {
    vcount: unique, icount: idx.length, scale, offset: lo,
    pos: b64(MeshoptEncoder.encodeVertexBuffer(new Uint8Array(q.buffer), unique, 8)),
    idx: b64(MeshoptEncoder.encodeIndexBuffer(new Uint8Array(idx.buffer), idx.length, 4)),
  };
  if (N) out.nrm = b64(MeshoptEncoder.encodeVertexBuffer(MeshoptEncoder.encodeFilterOct(N, unique, 8, 16), unique, 8));
  return out;
}

const meta = JSON.parse(fs.readFileSync(path.join(payloadDir, 'meta.json'), 'utf8'));
const data = {
  meta,
  body: packMesh(read('body_pos.f32', Float32Array), read('body_idx.u32', Uint32Array), read('body_nrm.f32', Float32Array)),
  stone: packMesh(read('stone_pos.f32', Float32Array), read('stone_idx.u32', Uint32Array), null),
};

const bundle = await build({
  entryPoints: [path.join(here, 'src/main.js')], bundle: true, minify: true, format: 'iife',
  target: 'es2020', write: false, legalComments: 'none',
});
const js = bundle.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');
const html = fs.readFileSync(path.join(here, 'template.html'), 'utf8')
  .replace('__SIZE__', String(meta.us_size))
  .replace('__DATA__', () => JSON.stringify(data))
  .replace('__BUNDLE__', () => js);
fs.writeFileSync(outFile, html);
console.log(`${outFile}: ${(html.length / 1e6).toFixed(2)} MB (body ${data.body.icount / 3} tris, stone ${data.stone.icount / 3} tris)`);
