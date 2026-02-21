let stream;
let webcamMode = null;
let capturedEmbedding = null;
let blinkDetected = false;

const api = async (url, method = 'GET', body) => {
  const token = localStorage.getItem('token');
  const csrf = localStorage.getItem('csrf');
  const res = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(csrf ? { 'X-CSRF-Token': csrf } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

async function initCsrf() {
  const data = await api('/api/auth/csrf', 'POST');
  localStorage.setItem('csrf', data.csrf_token);
}
initCsrf().catch(console.error);

async function openWebcam(mode) {
  webcamMode = mode;
  document.getElementById('webcamModal').classList.remove('hidden');
  document.getElementById('webcamModal').classList.add('flex');
  stream = await navigator.mediaDevices.getUserMedia({ video: true });
  document.getElementById('webcamVideo').srcObject = stream;
}

function closeWebcam() {
  document.getElementById('webcamModal').classList.add('hidden');
  document.getElementById('webcamModal').classList.remove('flex');
  if (stream) stream.getTracks().forEach(t => t.stop());
}

function captureFrame() {
  // Stub embedding extraction in browser; replace with real WASM/worker extraction in prod.
  capturedEmbedding = Array.from({ length: 128 }, () => Math.random());
  blinkDetected = true;
  const el = document.getElementById('blinkStatus');
  if (el) el.textContent = 'Blink status: detected';
  closeWebcam();
}

const regForm = document.getElementById('registerForm');
if (regForm) regForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(regForm);
  await api('/api/auth/register', 'POST', {
    name: fd.get('name'),
    email: fd.get('email'),
    password: fd.get('password'),
    face_embedding: capturedEmbedding,
  });
  alert('Registration successful');
});

const loginForm = document.getElementById('loginForm');
if (loginForm) loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(loginForm);
  await api('/api/auth/login', 'POST', {
    email: fd.get('email'),
    password: fd.get('password'),
    face_embedding: capturedEmbedding,
    blink_detected: blinkDetected,
  });
  location.href = '/otp';
});

const otpForm = document.getElementById('otpForm');
if (otpForm) otpForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(otpForm);
  const data = await api('/api/auth/verify-otp', 'POST', { email: fd.get('email'), otp: fd.get('otp') });
  localStorage.setItem('token', data.access_token);
  location.href = '/vote';
});

async function loadCandidates() {
  const list = document.getElementById('candidateList');
  if (!list) return;
  const candidates = await api('/api/voting/candidates');
  list.innerHTML = candidates.map(c => `<button class="glass p-4 rounded-xl text-left" onclick="castVote(${c.id})"><p class="font-bold">${c.name}</p><p class="text-sm">${c.party_symbol}</p></button>`).join('');
}
window.castVote = async (candidateId) => {
  const rec = await api('/api/voting/cast', 'POST', { candidate_id: candidateId });
  localStorage.setItem('receipt_hash', rec.receipt_hash);
  location.href = '/receipt';
};
loadCandidates().catch(console.error);

const receiptHash = document.getElementById('receiptHash');
if (receiptHash) receiptHash.textContent = localStorage.getItem('receipt_hash') || 'No receipt available';

const candidateForm = document.getElementById('candidateForm');
if (candidateForm) candidateForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(candidateForm);
  await api('/api/admin/candidates', 'POST', { name: fd.get('name'), party_symbol: fd.get('party_symbol') });
  alert('Candidate added');
});

const electionForm = document.getElementById('electionForm');
if (electionForm) electionForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(electionForm);
  await api('/api/admin/election-window', 'PUT', {
    start_time: new Date(fd.get('start_time')).toISOString(),
    end_time: new Date(fd.get('end_time')).toISOString(),
    is_active: fd.get('is_active') === 'on',
  });
  alert('Election window updated');
});

async function loadAdminData() {
  const logsEl = document.getElementById('auditLogs');
  if (!logsEl) return;
  const [stats, logs] = await Promise.all([api('/api/admin/stats'), api('/api/admin/audit-logs')]);
  logsEl.textContent = JSON.stringify(logs, null, 2);
  const ctx = document.getElementById('statsChart');
  if (ctx && window.Chart) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: stats.candidate_stats.map(s => s.name),
        datasets: [{ label: 'Votes', data: stats.candidate_stats.map(s => s.votes), backgroundColor: '#3b82f6' }],
      },
    });
  }
}
loadAdminData().catch(() => {});

const toggle = document.getElementById('themeToggle');
if (toggle) toggle.addEventListener('click', () => document.documentElement.classList.toggle('dark'));
