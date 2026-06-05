/**
 * workout.js — Webcam capture, MediaPipe analysis via backend, live UI updates
 */
document.addEventListener('DOMContentLoaded', () => {
  // ── State ───────────────────────────────────────────────────────────────────
  let isRunning = false;
  let selectedExercise = 'squat';
  let sessionStartTime = null;
  let currentReps = 0;
  let currentAccuracy = 0;
  let lastFeedback = '';
  let analyzeInterval = null;

  const video     = document.getElementById('webcam-video');
  const canvas    = document.getElementById('webcam-canvas');
  const ctx2d     = canvas ? canvas.getContext('2d') : null;
  const startBtn  = document.getElementById('start-btn');
  const stopBtn   = document.getElementById('stop-btn');
  const saveBtn   = document.getElementById('save-btn');
  const statusDot = document.getElementById('status-dot');
  const statusTxt = document.getElementById('status-text');
  const feedbackEl = document.getElementById('feedback-overlay');
  const repBig    = document.getElementById('rep-count-big');
  const repOverlay = document.getElementById('rep-overlay');
  const liveReps  = document.getElementById('live-reps');
  const liveAcc   = document.getElementById('live-accuracy');
  const liveCal   = document.getElementById('live-calories');
  const liveTime  = document.getElementById('live-time');
  const accRing   = document.getElementById('accuracy-ring');
  const accText   = document.getElementById('accuracy-ring-text');
  const placeholder = document.getElementById('webcam-placeholder');

  // Calories per rep table (must match backend config)
  const CAL_PER_REP = { squat: 0.32, pushup: 0.29, bicep_curl: 0.18 };

  // ── Exercise Selection ──────────────────────────────────────────────────────
  document.querySelectorAll('.exercise-option').forEach(opt => {
    opt.addEventListener('click', () => {
      if (isRunning) return; // don't switch mid-session
      document.querySelectorAll('.exercise-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      selectedExercise = opt.dataset.exercise;
    });
  });

  // ── Start webcam ────────────────────────────────────────────────────────────
  startBtn && startBtn.addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false
      });
      video.srcObject = stream;
      await video.play();

      canvas.width  = video.videoWidth  || 640;
      canvas.height = video.videoHeight || 480;

      // Show video/canvas, hide placeholder
      video.style.display = 'block';
      canvas.style.display = 'block';
      if (placeholder) placeholder.style.display = 'none';
      if (feedbackEl) feedbackEl.style.display = 'block';
      if (repOverlay) repOverlay.style.display = 'block';

      isRunning = true;
      sessionStartTime = Date.now();

      updateStatus(true);
      startBtn.disabled = true;
      stopBtn && (stopBtn.disabled = false);
      saveBtn && (saveBtn.disabled = false);

      // Reset counters
      currentReps = 0;
      currentAccuracy = 0;
      updateLiveUI();

      // Reset backend state
      await fetch('/workout/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exercise: selectedExercise }),
      });

      // Start analysis loop (every 150ms ≈ ~6-7 fps to backend)
      analyzeInterval = setInterval(analyzeFrame, 150);

      // Timer updater
      setInterval(() => {
        if (!isRunning) return;
        const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
        if (liveTime) liveTime.textContent = formatTime(elapsed);
      }, 1000);

    } catch (err) {
      alert('Camera access denied or unavailable. Please allow camera permissions.');
      console.error('Camera error:', err);
    }
  });

  // ── Stop webcam ─────────────────────────────────────────────────────────────
  stopBtn && stopBtn.addEventListener('click', stopSession);

  function stopSession() {
    if (!isRunning) return;
    isRunning = false;
    clearInterval(analyzeInterval);

    // Stop all tracks
    if (video.srcObject) {
      video.srcObject.getTracks().forEach(t => t.stop());
      video.srcObject = null;
    }

    video.style.display = 'none';
    canvas.style.display = 'none';
    if (placeholder) placeholder.style.display = 'flex';
    if (feedbackEl) feedbackEl.style.display = 'none';
    if (repOverlay) repOverlay.style.display = 'none';

    updateStatus(false);
    startBtn && (startBtn.disabled = false);
    stopBtn  && (stopBtn.disabled = true);
  }

  // ── Save session ─────────────────────────────────────────────────────────────
  saveBtn && saveBtn.addEventListener('click', async () => {
    if (currentReps === 0) {
      showToast('⚠️ No reps recorded yet!', 'warning');
      return;
    }

    const duration = sessionStartTime
      ? Math.floor((Date.now() - sessionStartTime) / 1000)
      : 0;

    stopSession();

    try {
      const res = await fetch('/workout/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exercise: selectedExercise,
          reps: currentReps,
          accuracy: currentAccuracy,
          duration,
        }),
      });
      const data = await res.json();
      if (data.status === 'saved') {
        showToast('✅ Session saved successfully!');
        setTimeout(() => { window.location.href = '/'; }, 1800);
      }
    } catch (e) {
      showToast('❌ Failed to save session.', 'error');
    }
  });

  // ── Frame analysis ───────────────────────────────────────────────────────────
  async function analyzeFrame() {
    if (!isRunning || !video || video.readyState < 2) return;

    // Capture frame to canvas
    ctx2d.drawImage(video, 0, 0, canvas.width, canvas.height);
    const frameData = canvas.toDataURL('image/jpeg', 0.75);

    try {
      const res = await fetch('/workout/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frame: frameData, exercise: selectedExercise }),
      });
      const data = await res.json();

      // Draw annotated frame from backend
      if (data.frame) {
        const img = new Image();
        img.onload = () => ctx2d.drawImage(img, 0, 0, canvas.width, canvas.height);
        img.src = data.frame;
      }

      // Update UI
      currentReps     = data.reps     ?? currentReps;
      currentAccuracy = data.accuracy ?? currentAccuracy;
      lastFeedback    = data.feedback ?? '';

      updateLiveUI();
      updateFeedbackBanner(data.feedback, data.stage);

    } catch (e) {
      // Silently handle network glitches during live analysis
    }
  }

  // ── UI Updaters ──────────────────────────────────────────────────────────────
  function updateLiveUI() {
    if (repBig) repBig.textContent = currentReps;
    if (liveReps) liveReps.textContent = currentReps;

    const acc = Math.round(currentAccuracy);
    if (liveAcc) liveAcc.textContent = acc + '%';

    const cal = (currentReps * (CAL_PER_REP[selectedExercise] || 0.25)).toFixed(1);
    if (liveCal) liveCal.textContent = cal;

    // Accuracy conic ring
    if (accRing) accRing.style.setProperty('--pct', acc + '%');
    if (accText) accText.textContent = acc + '%';
  }

  function updateFeedbackBanner(feedback, stage) {
    if (!feedbackEl || !feedback) return;
    feedbackEl.textContent = feedback;
    feedbackEl.className = 'feedback-overlay';

    if (!feedback) return;
    const lower = feedback.toLowerCase();
    if (lower.includes('correct') || lower.includes('✓')) {
      feedbackEl.classList.add('correct');
    } else if (lower.includes('ready') || lower.includes('stand')) {
      // neutral
    } else {
      feedbackEl.classList.add('warning');
    }
  }

  function updateStatus(live) {
    if (statusDot) statusDot.className = 'status-dot' + (live ? ' live' : '');
    if (statusTxt) statusTxt.textContent = live ? 'Live' : 'Offline';
  }

  // ── Toast notification ───────────────────────────────────────────────────────
  function showToast(msg, type = 'success') {
    let toast = document.getElementById('save-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'save-toast';
      toast.className = 'save-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    if (type === 'error')   toast.style.background = 'var(--clr-danger)';
    if (type === 'warning') toast.style.background = 'var(--clr-warning)';
    if (type === 'success') toast.style.background = 'var(--clr-success)';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2800);
  }

  function formatTime(secs) {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }
});
