/**
 * dashboard.js — Fetch stats & history, render Chart.js charts
 */
document.addEventListener('DOMContentLoaded', async () => {
  await loadStats();
  await loadHistory();
});

// ── Stats ─────────────────────────────────────────────────────────────────────

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();

    setText('stat-total-reps',     data.total_reps ?? 0);
    setText('stat-total-sessions', data.total_sessions ?? 0);
    setText('stat-calories',       (data.total_calories ?? 0).toFixed(1));
    setText('stat-accuracy',       (data.avg_accuracy ?? 0).toFixed(1) + '%');
    setText('stat-streak',         (data.streak ?? 0) + ' day' + (data.streak === 1 ? '' : 's'));

    renderWeekChart(data.week_labels || [], data.week_reps || []);
    renderBreakdownChart(data.exercise_breakdown || {});
  } catch (e) {
    console.error('Failed to load stats:', e);
  }
}

// ── History ───────────────────────────────────────────────────────────────────

async function loadHistory() {
  const tbody = document.getElementById('history-tbody');
  if (!tbody) return;

  try {
    const res = await fetch('/api/history');
    const sessions = await res.json();

    if (!sessions.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6">
            <div class="empty-state">
              <div class="empty-state-icon">🏋️</div>
              <p>No workouts yet. Start your first session!</p>
            </div>
          </td>
        </tr>`;
      return;
    }

    tbody.innerHTML = sessions.map(s => `
      <tr>
        <td>${s.created_at}</td>
        <td><span class="exercise-chip">${exerciseIcon(s.exercise_type)} ${s.exercise_label}</span></td>
        <td><strong>${s.reps}</strong></td>
        <td>
          <div class="accuracy-bar-wrap">
            <div class="accuracy-bar-track">
              <div class="accuracy-bar-fill" style="width:${s.accuracy_score}%"></div>
            </div>
            <span class="accuracy-pct">${s.accuracy_score}%</span>
          </div>
        </td>
        <td>${s.calories_burned} kcal</td>
        <td>${formatDuration(s.duration_seconds)}</td>
      </tr>
    `).join('');
  } catch (e) {
    console.error('Failed to load history:', e);
  }
}

// ── Charts ─────────────────────────────────────────────────────────────────────

function renderWeekChart(labels, reps) {
  const ctx = document.getElementById('weekChart');
  if (!ctx) return;

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const gridColor = isDark ? '#334155' : '#E2E8F0';
  const textColor = isDark ? '#94A3B8' : '#64748B';

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Reps',
        data: reps,
        backgroundColor: 'rgba(37, 99, 235, 0.18)',
        borderColor: '#2563EB',
        borderWidth: 2,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1E293B',
          titleColor: '#fff',
          bodyColor: '#94A3B8',
          callbacks: {
            label: ctx => ` ${ctx.raw} reps`
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { family: 'Inter', size: 12 } },
        },
        y: {
          beginAtZero: true,
          grid: { color: gridColor },
          ticks: { color: textColor, font: { family: 'Inter', size: 12 }, stepSize: 5 },
        }
      }
    }
  });
}

function renderBreakdownChart(breakdown) {
  const ctx = document.getElementById('breakdownChart');
  if (!ctx) return;

  const labels = Object.keys(breakdown).map(k => k.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()));
  const data = Object.values(breakdown);

  if (!data.length) { ctx.parentElement.innerHTML = '<div class="empty-state" style="height:160px"><p>No data yet</p></div>'; return; }

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: ['#2563EB', '#7C3AED', '#16A34A'],
        borderWidth: 0,
        hoverOffset: 4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: document.documentElement.getAttribute('data-theme') === 'dark' ? '#94A3B8' : '#64748B',
            font: { family: 'Inter', size: 12 },
            boxWidth: 10,
            padding: 14,
          }
        },
        tooltip: {
          backgroundColor: '#1E293B',
          titleColor: '#fff',
          bodyColor: '#94A3B8',
        }
      }
    }
  });
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function exerciseIcon(type) {
  const icons = { squat: '🏋️', pushup: '💪', bicep_curl: '🦾' };
  return icons[type] || '🏃';
}

function formatDuration(secs) {
  if (!secs) return '—';
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}
