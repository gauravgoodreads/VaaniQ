({ b64, isHuman }) => {
  const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  const url = URL.createObjectURL(new Blob([bytes], { type: "audio/wav" }));
  const audio = new Audio(url);
  audio.autoplay = true;
  audio.volume = 1;
  const ac = new AudioContext();
  const src = ac.createMediaElementSource(audio);
  const analyser = ac.createAnalyser();
  analyser.fftSize = 2048;
  analyser.smoothingTimeConstant = 0.72;
  src.connect(analyser);
  analyser.connect(ac.destination);

  const wave = document.getElementById("wave");
  const spec = document.getElementById("spec");
  const wctx = wave.getContext("2d");
  const sctx = spec.getContext("2d");
  const td = new Uint8Array(analyser.fftSize);
  const fd = new Uint8Array(analyser.frequencyBinCount);
  sctx.fillStyle = "#020807";
  sctx.fillRect(0, 0, spec.width, spec.height);
  let x = 0;

  function draw() {
    requestAnimationFrame(draw);
    analyser.getByteTimeDomainData(td);
    analyser.getByteFrequencyData(fd);
    wctx.fillStyle = "#020807";
    wctx.fillRect(0, 0, wave.width, wave.height);
    wctx.strokeStyle = isHuman ? "#7dffd4" : "#ff8a80";
    wctx.lineWidth = 2;
    wctx.beginPath();
    const step = wave.width / td.length;
    for (let i = 0; i < td.length; i += 1) {
      const y = (td[i] / 255) * wave.height;
      if (i === 0) wctx.moveTo(0, y);
      else wctx.lineTo(i * step, y);
    }
    wctx.stroke();
    const colW = 3;
    for (let i = 0; i < spec.height; i += 1) {
      const v = fd[Math.floor((i / spec.height) * fd.length)] / 255;
      sctx.fillStyle = isHuman
        ? "rgb(10," + Math.round(30 + v * 200) + "," + Math.round(80 + v * 90) + ")"
        : "rgb(" + Math.round(80 + v * 160) + "," + Math.round(20 + v * 40) + ",40)";
      sctx.fillRect(x, spec.height - i - 1, colW, 1);
    }
    x = (x + colW) % spec.width;
    if (x < colW) {
      sctx.fillStyle = "#020807";
      sctx.fillRect(0, 0, spec.width, spec.height);
    }
  }

  return audio.play().then(function () {
    if (ac.state === "suspended") {
      return ac.resume().then(function () { draw(); return true; });
    }
    draw();
    return true;
  }).catch(function () { return false; });
}
