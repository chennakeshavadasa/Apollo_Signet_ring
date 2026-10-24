import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const D = window.RING_DATA;

function b64(s) {
  const bin = atob(s), u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return u;
}

// meshopt-coded mesh -> BufferGeometry (positions 16-bit quantised, normals 16-bit octahedral)
function geometry(m) {
  const q = new Uint16Array(m.vcount * 4);
  MeshoptDecoder.decodeVertexBuffer(new Uint8Array(q.buffer), m.vcount, 8, b64(m.pos));
  const P = new Float32Array(m.vcount * 3);
  for (let i = 0; i < m.vcount; i++) for (let k = 0; k < 3; k++) P[3 * i + k] = q[4 * i + k] * m.scale + m.offset[k];
  const I = new Uint32Array(m.icount);
  MeshoptDecoder.decodeIndexBuffer(new Uint8Array(I.buffer), m.icount, 4, b64(m.idx));
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(P, 3));
  g.setIndex(new THREE.BufferAttribute(I, 1));
  if (m.nrm) {
    const o = new Int16Array(m.vcount * 4);
    MeshoptDecoder.decodeVertexBuffer(new Uint8Array(o.buffer), m.vcount, 8, b64(m.nrm), 'OCTAHEDRAL');
    const N = new Float32Array(m.vcount * 3);
    for (let i = 0; i < m.vcount; i++) {
      const x = o[4 * i], y = o[4 * i + 1], z = o[4 * i + 2], l = Math.hypot(x, y, z) || 1;
      N[3 * i] = x / l; N[3 * i + 1] = y / l; N[3 * i + 2] = z / l;
    }
    g.setAttribute('normal', new THREE.BufferAttribute(N, 3));
  } else {
    g.computeVertexNormals();
  }
  return g;
}

// dark jeweller's studio: a few soft boxes, so the gold shows contrast instead of a grey room
function studio() {
  const s = new THREE.Scene();
  s.background = new THREE.Color().setRGB(0.16, 0.125, 0.11);
  const soft = (w, h, k, x, y, z, tint = [1, 0.95, 0.88]) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(...tint).multiplyScalar(k), side: THREE.DoubleSide }));
    m.position.set(x, y, z);
    m.lookAt(0, 0, 0);
    s.add(m);
  };
  soft(5, 3, 8, -4, 8, 3);                      // key, high left
  soft(1.6, 7, 5, 8, 2, 1);                     // strip, right
  soft(1.6, 7, 4, -8, 1, -3);                   // strip, back left
  soft(12, 3, 2.2, 0, -2, 9, [1, 0.85, 0.7]);   // low warm front fill
  soft(12, 3, 1.6, 0, 1, -9, [1, 0.88, 0.76]);  // back fill
  soft(16, 16, 0.7, 0, -9, 0, [0.9, 0.72, 0.58]); // warm floor bounce
  return s;
}

// darken the stone seat: the 0.1 mm fitting gap should read as a shadow, not as bright gold
function occludeSeat(g, m) {
  const P = g.attributes.position.array, C = new Float32Array(P.length);
  for (let i = 0; i < P.length; i += 3) {
    const e = Math.hypot(P[i] / m.Px, P[i + 1] / m.Py), z = P[i + 2];
    const inSeat = e < 1.03 && z < m.z_col - 0.02 && z > m.z_seat - 0.5;
    const k = inSeat ? 0.15 + 0.85 * Math.min(1, Math.max(0, (z - (m.z_col - 0.25)) / 0.25)) ** 2 : 1;
    C[i] = C[i + 1] = C[i + 2] = k;
  }
  g.setAttribute('color', new THREE.BufferAttribute(C, 3));
}

async function main() {
  await MeshoptDecoder.ready;

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = 1.0;
  document.body.prepend(renderer.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(studio(), 0.02).texture;

  const key = new THREE.DirectionalLight(0xfff1dc, 1.6);   // raking light across the portrait
  key.position.set(-30, 45, 28);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xffe2c4, 0.5);
  fill.position.set(30, 12, 22);
  scene.add(fill);

  const camera = new THREE.PerspectiveCamera(30, window.innerWidth / window.innerHeight, 1, 1000);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 16;
  controls.maxDistance = 180;
  controls.autoRotateSpeed = 2.0;

  const gold = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color().setRGB(1.0, 0.72, 0.30), metalness: 1.0, roughness: 0.24, vertexColors: true,
  });
  const carnelian = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color().setRGB(0.36, 0.028, 0.01), metalness: 0.0, roughness: 0.38,
    clearcoat: 0.6, clearcoatRoughness: 0.18,
  });

  // generator axes: z up through the bezel, y along the finger -> three.js: y up
  const ring = new THREE.Group();
  ring.rotation.x = -Math.PI / 2;
  const bodyGeo = geometry(D.body);
  occludeSeat(bodyGeo, D.meta);
  const body = new THREE.Mesh(bodyGeo, gold);
  const stone = new THREE.Mesh(geometry(D.stone), carnelian);
  ring.add(body, stone);
  scene.add(ring);

  const zc = D.meta.z_col;
  const views = {
    three: { t: [0, 3, 0], d: 74, el: 30, az: 38 },
    face: { t: [0, zc - 0.5, 0], d: 54, el: 89.9, az: 0 },
    portrait: { t: [0, zc + 0.4, 0], d: 31, el: 50, az: -32 },
    profile: { t: [0, 1, 0], d: 72, el: 3, az: 0 },
    side: { t: [0, 1, 0], d: 72, el: 3, az: 90 },
  };
  const sph = new THREE.Spherical();
  function pose(v) {
    const fit = Math.max(1, 1.3 / camera.aspect);
    const el = THREE.MathUtils.degToRad(v.el), az = THREE.MathUtils.degToRad(v.az);
    return { t: new THREE.Vector3(...v.t), s: new THREE.Spherical(v.d * fit, Math.PI / 2 - el, az) };
  }
  let anim = null;
  function setView(name, instant = false) {
    const { t, s } = pose(views[name]);
    if (instant) {
      controls.target.copy(t);
      camera.position.setFromSpherical(s).add(t);
      controls.update();
      anim = null;
      return;
    }
    const s0 = sph.setFromVector3(camera.position.clone().sub(controls.target)).clone();
    let dt = s.theta - s0.theta;
    dt = Math.atan2(Math.sin(dt), Math.cos(dt));                // shortest way round
    anim = { t0: controls.target.clone(), t1: t, s0, s1: new THREE.Spherical(s.radius, s.phi, s0.theta + dt), start: performance.now(), dur: 950 };
  }
  controls.addEventListener('start', () => { anim = null; });

  let lift = 0, liftTarget = 0;
  const bar = document.getElementById('bar');
  bar.querySelectorAll('[data-view]').forEach((b) => b.addEventListener('click', () => setView(b.dataset.view)));
  const turn = document.getElementById('turn');
  turn.addEventListener('click', () => { controls.autoRotate = !controls.autoRotate; turn.classList.toggle('on', controls.autoRotate); });
  const liftBtn = document.getElementById('lift');
  liftBtn.addEventListener('click', () => { liftTarget = liftTarget ? 0 : 6; liftBtn.classList.toggle('on', !!liftTarget); });

  function resize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }
  window.addEventListener('resize', resize);

  const params = new URLSearchParams(location.search);
  setView(views[params.get('view')] ? params.get('view') : 'three', true);
  if (params.has('lift')) { liftTarget = lift = 6; liftBtn.classList.add('on'); }

  const ease = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
  renderer.setAnimationLoop(() => {
    if (anim) {
      const k = Math.min(1, (performance.now() - anim.start) / anim.dur), e = ease(k);
      controls.target.lerpVectors(anim.t0, anim.t1, e);
      sph.set(THREE.MathUtils.lerp(anim.s0.radius, anim.s1.radius, e), THREE.MathUtils.lerp(anim.s0.phi, anim.s1.phi, e),
        THREE.MathUtils.lerp(anim.s0.theta, anim.s1.theta, e));
      camera.position.setFromSpherical(sph).add(controls.target);
      if (k >= 1) anim = null;
    }
    lift += (liftTarget - lift) * 0.12;
    stone.position.z = lift;
    controls.update();
    renderer.render(scene, camera);
  });

  document.getElementById('loading').remove();
  window.viewer = {
    setView, renderer, scene, camera, controls, stone,
    // still frame for screenshots (software GL is too slow for the animation loop)
    still(name, liftMm = 0) {
      renderer.setAnimationLoop(null);
      setView(name, true);
      stone.position.z = liftMm;
      renderer.render(scene, camera);
    },
  };
  window.__ready = true;
}

main();
