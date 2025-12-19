// ========================
// API (backend)
// ========================
const API = "http://127.0.0.1:8000";

const filesEl  = document.getElementById("files");
const speedEl  = document.getElementById("speed");
const runEl    = document.getElementById("run");
const statusEl = document.getElementById("status");

// ========================
// Digest (your fixed images)
//  - index.html に <div id="digest" class="thumb-row"></div> を用意してね
//  - frontend/assets/ に画像を置いて、ここで列挙
// ========================
const digestEl = document.getElementById("digest");

// ✅ あなたの「特定の画像」をここに並べる（assets配下）
const IMAGES = [
  "./assets/a.jpg",
  "./assets/b.jpg",
  "./assets/c.jpg",
  "./assets/d.jpg",
  "./assets/e.jpg",
  "./assets/f.jpg",
];

let digestIdx = 0;
let digestTimer = null;

function renderDigest3() {
  if (!digestEl || IMAGES.length === 0) return;

  digestEl.innerHTML = "";
  for (let k = 0; k < 3; k++) {
    const src = IMAGES[(digestIdx + k) % IMAGES.length];
    const img = document.createElement("img");
    img.className = "thumb";     // styles.css の .thumb を使う前提
    img.src = src;
    img.alt = `digest-${digestIdx + k}`;
    digestEl.appendChild(img);
  }
  digestIdx = (digestIdx + 3) % IMAGES.length;
}

function startDigest(intervalMs = 1500) {
  if (!digestEl) return;
  if (digestTimer) clearInterval(digestTimer);

  renderDigest3();
  digestTimer = setInterval(renderDigest3, intervalMs);
}

// ページ読み込み時に自動スタート
startDigest(1500);

// ========================
// Upload + Process
// ========================
runEl?.addEventListener("click", async () => {
  const files = filesEl?.files;

  if (!files || files.length === 0) {
    statusEl.textContent = "tif/tiff を複数選択してください";
    return;
  }

  statusEl.textContent = "Uploading…";

  const fd = new FormData();
  for (const f of files) fd.append("files", f);
  fd.append("speed", String(parseInt(speedEl?.value || "20", 10)));

  try {
    const res = await fetch(`${API}/api/process`, { method: "POST", body: fd });
    const data = await res.json().catch(() => ({}));

    // ここはバックエンドの返しに合わせて調整
    // data.ok を返してないなら、下の行を消す（または data.message 等に変更）
    if (!res.ok || (data.ok === false)) throw new Error(data?.error || `HTTP ${res.status}`);

    statusEl.textContent =
      `✅ Received ${data.count ?? files.length} files | speed=${data.speed ?? fd.get("speed")}`;
  } catch (e) {
    statusEl.textContent = `❌ ${e.message}`;
  }
});
