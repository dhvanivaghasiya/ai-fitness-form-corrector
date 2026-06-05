/**
 * auth.js — Login & Signup form enhancements
 */
document.addEventListener('DOMContentLoaded', () => {

  // ── Password visibility toggle ────────────────────────────
  document.querySelectorAll('.input-eye-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      if (!input) return;
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.textContent = isHidden ? '🙈' : '👁️';
    });
  });

  // ── Password strength meter (signup page only) ────────────
  const pwInput = document.getElementById('password');
  const segments = document.querySelectorAll('.strength-segment');
  const strengthLabel = document.querySelector('.strength-label');

  if (pwInput && segments.length) {
    pwInput.addEventListener('input', () => {
      const val = pwInput.value;
      const score = getStrength(val);
      updateStrengthUI(score, segments, strengthLabel);
    });
  }

  // ── Auto-dismiss flash alerts ─────────────────────────────
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    });
  }, 4000);
});

function getStrength(password) {
  let score = 0;
  if (password.length >= 6)  score++;
  if (password.length >= 10) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  return Math.min(score, 3); // 0,1,2,3
}

function updateStrengthUI(score, segments, label) {
  const labels = ['', 'Weak', 'Fair', 'Strong'];
  const classes = ['', 'weak', 'medium', 'strong'];
  segments.forEach((seg, i) => {
    seg.className = 'strength-segment';
    if (i < score) seg.classList.add(classes[score]);
  });
  if (label) {
    label.textContent = score > 0 ? labels[score] + ' password' : '';
    label.style.color = score === 3 ? 'var(--clr-success)'
                      : score === 2 ? 'var(--clr-warning)'
                      : 'var(--clr-danger)';
  }
}
