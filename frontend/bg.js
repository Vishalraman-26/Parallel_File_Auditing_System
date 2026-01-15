const canvas = document.getElementById("bg");
const ctx = canvas.getContext("2d");

let w, h, dpr;

function resize() {
  dpr = window.devicePixelRatio || 1;
  w = window.innerWidth;
  h = window.innerHeight;

  canvas.width = w * dpr;
  canvas.height = h * dpr;
  canvas.style.width = w + "px";
  canvas.style.height = h + "px";

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

window.addEventListener("resize", resize);
resize();

const stars = Array.from({ length: 160 }, () => ({
  x: Math.random() * w,
  y: Math.random() * h,
  r: Math.random() * 1.5 + 0.5,
  v: Math.random() * 0.3 + 0.1
}));

function loop() {
  ctx.clearRect(0, 0, w, h);

  for (const s of stars) {
    s.y += s.v;
    if (s.y > h) {
      s.y = 0;
      s.x = Math.random() * w;
    }

    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(120,140,255,0.6)";
    ctx.fill();
  }

  requestAnimationFrame(loop);
}

loop();
