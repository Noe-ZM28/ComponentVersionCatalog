const categories = [...new Set(CATALOG.map(c => c.category))];
const $ = id => document.getElementById(id);
const escapeHtml = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const statusClass = s => ({ 'Approved': 'approved', 'In Review': 'review', 'Draft': 'draft', 'Deprecated': 'deprecated', 'Pending verification': 'pending' }[s] || 'draft');
const pill = s => `<span class="pill ${statusClass(s)}">${escapeHtml(s)}</span>`;
const approvedVersion = c => c.versions.find(v => v.status === "Approved")?.version || "Not confirmed";
const latestRecorded = c => [...c.versions].sort((a, b) => b.recordedDate.localeCompare(a.recordedDate))[0]?.version || "—";
const dateLabel = d => d ? new Date(d + "T12:00:00").toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) : "Not recorded";
function init() {
  categories.forEach(c => $('categoryFilter').insertAdjacentHTML('beforeend', `<option>${escapeHtml(c)}</option>`));
  renderStats(); renderCategories(); renderRows();
  $('searchInput').addEventListener('input', renderRows);
  $('categoryFilter').addEventListener('change', () => { renderCategories(); renderRows() });
  $('statusFilter').addEventListener('change', renderRows);
  $('resetBtn').addEventListener('click', () => { $('searchInput').value = ''; $('categoryFilter').value = ''; $('statusFilter').value = ''; renderCategories(); renderRows() });
  $('backBtn').addEventListener('click', showHome);
}
function renderStats() {
  const approved = CATALOG.filter(c => c.versions.some(v => v.status === 'Approved')).length;
  const review = CATALOG.filter(c => c.status === 'In Review').length;
  const pending = CATALOG.filter(c => c.status === 'Pending verification').length;
  $('stats').innerHTML = [
    ['Components', CATALOG.length, 'Across all tracked categories'],
    ['Approved reference', approved, 'At least one approved version recorded'],
    ['In review', review, 'Newer records awaiting approval'],
    ['Needs verification', pending, 'Current source/version not confirmed']
  ].map(x => `<div class="stat"><div class="stat-label">${x[0]}</div><div class="stat-number">${x[1]}</div><div class="stat-note">${x[2]}</div></div>`).join('');
}
function renderCategories() {
  const selected = $('categoryFilter').value;
  $('categoryCards').innerHTML = `<button class="category ${!selected ? 'active' : ''}" data-cat=""><strong>All components</strong><span>${CATALOG.length} tracked</span></button>` + categories.map(cat => `<button class="category ${selected === cat ? 'active' : ''}" data-cat="${escapeHtml(cat)}"><strong>${escapeHtml(cat)}</strong><span>${CATALOG.filter(c => c.category === cat).length} components</span></button>`).join('');
  document.querySelectorAll('[data-cat]').forEach(b => b.addEventListener('click', () => { $('categoryFilter').value = b.dataset.cat; renderCategories(); renderRows() }));
}
function renderRows() {
  const q = $('searchInput').value.toLowerCase().trim(), cat = $('categoryFilter').value, status = $('statusFilter').value;
  const list = CATALOG.filter(c => (!cat || c.category === cat) && (!status || c.status === status) && (!q || [c.id, c.name, c.category, c.carrier, c.owner, c.status, ...c.versions.map(v => v.ticket)].join(' ').toLowerCase().includes(q)));
  $('componentRows').innerHTML = list.map(c => `<tr>
 <td><a href="#" class="component-name" data-open="${escapeHtml(c.id)}">${escapeHtml(c.name)}</a><div class="subline">${escapeHtml(c.id)}${c.carrier ? ' · ' + escapeHtml(c.carrier) : ''}</div></td>
 <td>${escapeHtml(c.category)}</td><td><strong>${escapeHtml(approvedVersion(c))}</strong></td><td>${escapeHtml(latestRecorded(c))}</td><td>${pill(c.status)}</td>
 <td><button class="btn small" data-open="${escapeHtml(c.id)}">View</button></td></tr>`).join('');
  $('emptyState').hidden = list.length !== 0;
  document.querySelectorAll('[data-open]').forEach(b => b.addEventListener('click', e => { e.preventDefault(); showDetail(b.dataset.open) }));
}
function showHome() { $('home').style.display = ''; $('detailView').classList.remove('active'); window.scrollTo({ top: 0, behavior: 'smooth' }) }
function showDetail(id) {
  const c = CATALOG.find(x => x.id === id); if (!c) return;
  $('home').style.display = 'none'; $('detailView').classList.add('active');
  $('detailCategory').textContent = c.category;
  $('detailName').textContent = c.name;
  $('detailSubtitle').textContent = [c.id, c.carrier].filter(Boolean).join(' · ');
  $('detailStatus').innerHTML = pill(c.status);
  $('detailId').textContent = c.id;
  const newest = latestRecorded(c), approved = approvedVersion(c);
  $('detailGrid').innerHTML = [
    ['Latest approved version', approved],
    ['Latest recorded version', newest],
    ['Last catalog update', dateLabel(c.lastUpdated)],
    ['Owner', c.owner || 'Not assigned'],
    ['Validation', c.validation],
    ['Environment / scope', c.scope || 'Not specified']
  ].map(([a, b]) => `<div class="detail-cell"><div class="label">${escapeHtml(a)}</div><strong>${escapeHtml(b)}</strong></div>`).join('');
  $('detailDescription').textContent = c.description;
  $('detailLinks').innerHTML = `<a class="btn primary" href="${escapeHtml(c.sourceUrl || '#')}" target="_blank" rel="noopener">Open source location ↗</a> <a class="btn" href="${escapeHtml(c.ticketUrl || '#')}" target="_blank" rel="noopener">Open latest Jira ticket ↗</a>`;
  $('detailSource').textContent = c.sourceLabel;
  $('historyCount').textContent = `${c.versions.length} recorded version(s)`;
  $('historyList').innerHTML = [...c.versions].sort((a, b) => b.recordedDate.localeCompare(a.recordedDate)).map(v => `<div class="history-item">
 <div><div class="history-version">${escapeHtml(v.version)}</div><div class="history-date">${dateLabel(v.recordedDate)}</div></div>
 <div><div class="tagline">${pill(v.status)} ${v.version === approved ? '<span class="pill approved">Current approved</span>' : ''} ${v.version === newest ? '<span class="pill draft">Latest recorded</span>' : ''}</div>
 <div class="history-desc">${escapeHtml(v.change)}</div><div class="small muted">Ticket: <a class="link" href="${escapeHtml(v.ticketUrl || '#')}" target="_blank" rel="noopener">${escapeHtml(v.ticket)}</a> · Updated by ${escapeHtml(v.author)}</div>${v.notes ? `<div class="small muted">${escapeHtml(v.notes)}</div>` : ''}</div></div>`).join('');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
init();
