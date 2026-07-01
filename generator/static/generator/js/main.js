/* ── Hamburger nav toggle ── */
document.addEventListener('DOMContentLoaded', () => {
  var toggle = document.getElementById('nav-toggle');
  var links  = document.getElementById('nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function() {
      links.classList.toggle('open');
    });
    document.addEventListener('click', function(e) {
      if (!toggle.contains(e.target) && !links.contains(e.target)) {
        links.classList.remove('open');
      }
    });
  }
});

/* ── File input labels ── */
document.addEventListener('DOMContentLoaded', () => {

  // Show chosen filename next to upload zone
  document.querySelectorAll('.upload-zone input[type=file]').forEach(input => {
    input.addEventListener('change', () => {
      const lbl = input.closest('.upload-zone').querySelector('.file-chosen');
      if (lbl) {
        lbl.textContent = input.files.length
          ? '📎 ' + Array.from(input.files).map(f => f.name).join(', ')
          : '';
      }
    });
  });

  // Drag & drop highlight
  document.querySelectorAll('.upload-zone').forEach(zone => {
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('drag-over');
      const input = zone.querySelector('input[type=file]');
      if (input && e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        input.dispatchEvent(new Event('change'));
      }
    });
  });

  // Design card radio toggle
  document.querySelectorAll('.design-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.design-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      const radio = card.querySelector('input[type=radio]');
      if (radio) radio.checked = true;
    });
  });

  // Spinner on form submit
  const spinnerForms = document.querySelectorAll('form[data-spinner]');
  const spinnerOverlay = document.getElementById('spinner-overlay');
  spinnerForms.forEach(form => {
    form.addEventListener('submit', () => {
      if (spinnerOverlay) spinnerOverlay.classList.add('show');
    });
  });
});

/* ── Edit row modal ── */
let currentRowIdx = null;

function openEditModal(idx) {
  currentRowIdx = idx;
  const overlay = document.getElementById('edit-modal');
  if (!overlay) return;

  fetch(`/api/row-data/${idx}/`)
    .then(r => r.json())
    .then(data => {
      const grid = document.getElementById('modal-fields');
      grid.innerHTML = '';
      Object.entries(data.row).forEach(([col, val]) => {
        const div = document.createElement('div');
        div.className = 'form-group';
        div.innerHTML = `
          <label class="form-label">${col}</label>
          <input class="form-control" data-col="${col}" value="${escHtml(val)}" />
        `;
        grid.appendChild(div);
      });
      overlay.classList.add('open');
    });
}

function closeEditModal() {
  document.getElementById('edit-modal').classList.remove('open');
  currentRowIdx = null;
}

function saveEditModal() {
  const inputs = document.querySelectorAll('#modal-fields input[data-col]');
  const values = {};
  inputs.forEach(inp => { values[inp.dataset.col] = inp.value; });

  fetch('/save-row/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ idx: currentRowIdx, values }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.ok) {
      closeEditModal();
      location.reload();
    } else {
      alert('Save failed: ' + (data.error || 'unknown'));
    }
  });
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function getCookie(name) {
  const v = document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith(name + '='));
  return v ? decodeURIComponent(v.split('=')[1]) : '';
}

// Close modal on overlay click
document.addEventListener('click', e => {
  const overlay = document.getElementById('edit-modal');
  if (overlay && e.target === overlay) closeEditModal();
});
