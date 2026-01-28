/* ==============================
   Global state
============================== */

const players = {};   // streamId -> Hls instance
const cards   = {};   // streamId -> true (created)

/* ==============================
   Init dashboard (run once)
============================== */

async function initDashboard() {
  try {
    const streams = await fetch("/api/streams").then(r => r.json());
    const grid = document.getElementById("grid");

    streams.forEach(s => {
      if (cards[s.id]) return;

      const card = document.createElement("div");
      card.className = "card";
      card.id = `card-${s.id}`;

      card.innerHTML = `
        <b>${s.name}</b><br>
        Status: <span id="status-${s.id}">—</span><br>
        Errors: <span id="errors-${s.id}">0</span><br>
        Last Frame: <span id="last-${s.id}">—</span><br><br>
        Bitrate: <span id="bitrate-${s.id}">—</span> kbps<br>
        Packet Loss: <span id="loss-${s.id}">0</span><br>
        Freeze: <span id="freeze-${s.id}">NO</span><br>

        <button onclick="playStream('${s.id}')">▶ Play</button>
        <button onclick="stopStream('${s.id}')">⏹ Stop</button>

        <div id="video-${s.id}"></div>
      `;

      grid.appendChild(card);
      cards[s.id] = true;
    });

    // Start stats loop
    setInterval(updateStats, 3000);
    updateStats();

  } catch (e) {
    console.error("Dashboard init error:", e);
  }
}

/* ==============================
   Update stats only (NO DOM rebuild)
============================== */

async function updateStats() {
  try {
    const stats = await fetch("/api/status").then(r => r.json());
    const now = Date.now() / 1000;

    Object.keys(stats).forEach(id => {
      const st = stats[id];

      const healthy =
        st.last_frame && (now - st.last_frame < 5);

      const statusEl = document.getElementById(`status-${id}`);
      const errorsEl = document.getElementById(`errors-${id}`);
      const lastEl   = document.getElementById(`last-${id}`);
      document.getElementById(`bitrate-${id}`).textContent =
  st.bitrate_kbps ? Math.round(st.bitrate_kbps) : "—";

document.getElementById(`loss-${id}`).textContent =
  st.packet_loss || 0;

document.getElementById(`freeze-${id}`).textContent =
  st.frozen ? "YES" : "NO";

document.getElementById(`freeze-${id}`).className =
  st.frozen ? "bad" : "ok"


      if (!statusEl || !errorsEl || !lastEl) return;

      statusEl.textContent = healthy ? "OK" : "NO DATA";
      statusEl.className   = healthy ? "ok" : "bad";

      errorsEl.textContent = st.errors || 0;

      lastEl.textContent = st.last_frame
        ? Math.round(now - st.last_frame) + "s ago"
        : "—";
    });

  } catch (e) {
    console.error("Stats update error:", e);
  }
}

/* ==============================
   Play stream (on demand)
============================== */

function playStream(id) {
  try {
    if (players[id]) return;

    fetch(`/api/play/${id}`);

    const container = document.getElementById(`video-${id}`);
    if (!container) return;

    const video = document.createElement("video");
    video.controls = true;
    video.autoplay = false;
    video.muted = true; // avoids autoplay restrictions
    video.style.width = "100%";

    container.appendChild(video);

    if (window.Hls && Hls.isSupported()) {
      const hls = new Hls({
        lowLatencyMode: true,
        maxBufferLength: 10
      });

      hls.loadSource(`/hls/${id}.m3u8`);
      hls.attachMedia(video);

      hls.on(Hls.Events.ERROR, function (_, data) {
        if (data.fatal) {
          console.error(`HLS fatal error on ${id}:`, data);
        }
      });

      players[id] = hls;

    } else {
      video.src = `/hls/${id}.m3u8`;
    }

    video.play().catch(err => {
      if (err.name !== "AbortError") {
        console.error("Play failed:", err);
      }
    });

  } catch (e) {
    console.error("Play exception:", e);
  }
}

/* ==============================
   Stop stream cleanly
============================== */

function stopStream(id) {
  try {
    fetch(`/api/stop/${id}`);

    if (players[id]) {
      players[id].destroy();
      delete players[id];
    }

    const container = document.getElementById(`video-${id}`);
    if (!container) return;

    const video = container.querySelector("video");
    if (video) {
      video.pause();
      video.removeAttribute("src");
      video.load();
    }

    container.innerHTML = "";

  } catch (e) {
    console.error("Stop exception:", e);
  }
}

/* ==============================
   Start dashboard
============================== */

document.addEventListener("DOMContentLoaded", initDashboard);
