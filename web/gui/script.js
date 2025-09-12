import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// Scene setup


// your Three.js code here

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111111);

// make Z the up axis (G-code usually uses Z up)
scene.up.set(0, 0, 1);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
// ensure camera uses Z up too
camera.up.set(0, 0, 1);
camera.position.set(0, -150, 150);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
const container = document.getElementById("visualizer-content");
container.appendChild(renderer.domElement);
renderer.setSize(container.clientWidth, container.clientHeight);


// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Disable rotation and force pan/zoom only (2D top-down view)
controls.enableRotate = false;
controls.enablePan = true;
controls.enableZoom = true;
controls.screenSpacePanning = true; // pan in screen-space (works well for 2D)
controls.minPolarAngle = 0;
controls.maxPolarAngle = 0; // lock tilt to straight down
// remap mouse so left=pan, middle=zoom, right=pan
controls.mouseButtons = {
  LEFT: THREE.MOUSE.PAN,
  MIDDLE: THREE.MOUSE.DOLLY,
  RIGHT: THREE.MOUSE.PAN
};
controls.touches = {
  ONE: THREE.TOUCH.PAN,
  TWO: THREE.TOUCH.DOLLY_PAN
};

// Lighting
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(100, -100, 200).normalize();
scene.add(dirLight);

// Materials
const materialCut = new THREE.LineBasicMaterial({ color: 0x00ff00 }); // green
const materialRapid = new THREE.LineDashedMaterial({ color: 0xff0000, dashSize: 2, gapSize: 1 }); // red dashed

// Parse G-code text
function parseGcode(gcodeText) {
  const lines = gcodeText.split("\n");
  const moves = [];
  let x = 0, y = 0, z = 0;

  lines.forEach(line => {
    line = line.split(";")[0].trim(); // strip comments
    if (line.startsWith("G0") || line.startsWith("G1")) {
      const matchX = line.match(/X([-0-9.]+)/i);
      const matchY = line.match(/Y([-0-9.]+)/i);
      const matchZ = line.match(/Z([-0-9.]+)/i);
      const newX = matchX ? parseFloat(matchX[1]) : x;
      const newY = matchY ? parseFloat(matchY[1]) : y;
      const newZ = matchZ ? parseFloat(matchZ[1]) : z;
      moves.push({
        from: { x, y, z },
        to: { x: newX, y: newY, z: newZ },
        type: line.startsWith("G0") ? "rapid" : "cut"
      });
      x = newX; y = newY; z = newZ;
    }
  });
  return moves;
}

// create a group to hold the G-code lines so we can center/fit them
let gcodeGroup = null;

// Render moves
function renderGcode(moves) {
  // remove previous group if present
  if (gcodeGroup) {
    scene.remove(gcodeGroup);
    gcodeGroup.traverse(obj => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
  }

  gcodeGroup = new THREE.Group();
  moves.forEach(move => {
    // flatten to Z=0 so everything is on a 2D plane
    const geometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(move.from.x, move.from.y, 0),
      new THREE.Vector3(move.to.x, move.to.y, 0)
    ]);
    const mat = move.type === "cut" ? materialCut : materialRapid;
    const line = new THREE.Line(geometry, mat);
    if (move.type === "rapid") {
      geometry.computeBoundingSphere();
      line.computeLineDistances();
    }
    gcodeGroup.add(line);
  });

  scene.add(gcodeGroup);

  // center and frame the group in view
  frameGcodeToView(gcodeGroup);
}

// centers the object at origin and positions the camera to fit it
function frameGcodeToView(object) {
  const box = new THREE.Box3().setFromObject(object);
  if (box.isEmpty()) return;

  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());

  // move object so its center is at the origin (XY center)
  // keep any Z offset at zero because we flattened geometry
  object.position.sub(center);

  // set controls target to origin (where the object is now centered)
  controls.target.set(0, 0, 0);
  controls.update();

  // compute a distance to fit the object in view
  const maxDim = Math.max(size.x, size.y);
  const fov = camera.fov * (Math.PI / 180);
  const distance = Math.abs(maxDim / (2 * Math.tan(fov / 2))) * 1.2;

  // position the camera directly above the object (top-down)
  camera.position.set(0, 0, distance);
  camera.lookAt(0, 0, 0);
  controls.update();
}

// File input handler
document.getElementById("fileInput").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (evt) => {
    const gcodeText = evt.target.result;
    const moves = parseGcode(gcodeText);
    renderGcode(moves);
  };
  reader.readAsText(file);
});

// Animate
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

// Resize
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
