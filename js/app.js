const categories = [...new Set(CATALOG.map(c => c.category))];
const projects = [...new Set(CATALOG.map(c => c.project))];
const $ = id => document.getElementById(id);
const escapeHtml = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const statusClass = s => ({ 'Approved': 'approved', 'In Review': 'review', 'Draft': 'draft', 'Deprecated': 'deprecated', 'Pending verification': 'pending' }[s] || 'draft');
const pill = s => `<span class="pill ${statusClass(s)}">${escapeHtml(s)}</span>`;
const approvedVersion = c => c.versions.find(v => v.status === "Approved")?.version || "Not confirmed";
const latestRecorded = c => [...c.versions].sort((a, b) => b.recordedDate.localeCompare(a.recordedDate))[0]?.version || "—";
const dateLabel = d => d ? new Date(d + "T12:00:00").toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) : "Not recorded";
function init() {
  projects.forEach(project => $('projectFilter').insertAdjacentHTML('beforeend', `<option>${escapeHtml(project)}</option>`));
  categories.forEach(c => $('categoryFilter').insertAdjacentHTML('beforeend', `<option>${escapeHtml(c)}</option>`));
  renderStats(); renderProjects(); renderCategories(); renderRows();
  $('searchInput').addEventListener('input', renderRows);
  $('projectFilter').addEventListener('change', () => { renderProjects(); renderRows() });
  $('categoryFilter').addEventListener('change', () => { renderCategories(); renderRows() });
  $('statusFilter').addEventListener('change', renderRows);
  $('resetBtn').addEventListener('click', () => { $('searchInput').value = ''; $('projectFilter').value = ''; $('categoryFilter').value = ''; $('statusFilter').value = ''; renderProjects(); renderCategories(); renderRows() });
  $('backBtn').addEventListener('click', showHome);
}
function renderStats() {
  const approved = CATALOG.filter(c => c.versions.some(v => v.status === 'Approved')).length;
  const review = CATALOG.filter(c => c.status === 'In Review').length;
  const pending = CATALOG.filter(c => c.status === 'Pending verification').length;
  $('stats').innerHTML = [
    ['Elementos', CATALOG.length, 'En PC1, reportes y carriers'],
    ['Aprobados', approved, 'Con al menos una versión aprobada'],
    ['En revisión', review, 'Registros pendientes de aprobación'],
    ['Por verificar', pending, 'Fuente o versión pendiente de confirmar']
  ].map(x => `<div class="stat"><div class="stat-label">${x[0]}</div><div class="stat-number">${x[1]}</div><div class="stat-note">${x[2]}</div></div>`).join('');
}
function renderProjects() {
  const selected = $('projectFilter').value;
  $('projectCards').innerHTML = `<button class="category ${!selected ? 'active' : ''}" data-project=""><strong>Todos los proyectos</strong><span>${CATALOG.length} elementos</span></button>` + projects.map(project => `<button class="category ${selected === project ? 'active' : ''}" data-project="${escapeHtml(project)}"><strong>${escapeHtml(project)}</strong><span>${CATALOG.filter(c => c.project === project).length} elementos</span></button>`).join('');
  document.querySelectorAll('[data-project]').forEach(b => b.addEventListener('click', () => { $('projectFilter').value = b.dataset.project; renderProjects(); renderRows() }));
}
function renderCategories() {
  const selected = $('categoryFilter').value;
  $('categoryCards').innerHTML = `<button class="category ${!selected ? 'active' : ''}" data-cat=""><strong>Todos los grupos</strong><span>${CATALOG.length} elementos</span></button>` + categories.map(cat => `<button class="category ${selected === cat ? 'active' : ''}" data-cat="${escapeHtml(cat)}"><strong>${escapeHtml(cat)}</strong><span>${CATALOG.filter(c => c.category === cat).length} elementos</span></button>`).join('');
  document.querySelectorAll('[data-cat]').forEach(b => b.addEventListener('click', () => { $('categoryFilter').value = b.dataset.cat; renderCategories(); renderRows() }));
}
function renderRows() {
  const q = $('searchInput').value.toLowerCase().trim(), project = $('projectFilter').value, cat = $('categoryFilter').value, status = $('statusFilter').value;
  const categoryOrder = ["PC1", "Reportes", "Carrier"];
  const list = CATALOG.filter(c => {
    const reportFiles = (c.reportFiles || []).flatMap(file => [file.label, file.name]);
    const exampleFiles = (c.exampleFiles || []).map(file => file.name);
    const searchable = [c.id, c.name, c.project, c.category, c.reportFormat, c.reportFolder, c.carrier, c.owner, c.status, c.packageFile, ...reportFiles, ...exampleFiles, ...c.versions.map(v => v.ticket), ...(c.example ? [c.example.name, c.example.format, c.example.content, c.layout] : []), ...(c.variants || []).flatMap(v => [v.name, v.fileName])];
    return (!project || c.project === project) && (!cat || c.category === cat) && (!status || c.status === status) && (!q || searchable.join(' ').toLowerCase().includes(q));
  })
    .sort((a, b) => projects.indexOf(a.project) - projects.indexOf(b.project) || categoryOrder.indexOf(a.category) - categoryOrder.indexOf(b.category) || a.name.localeCompare(b.name));
  let lastGroup = "";
  $('componentRows').innerHTML = list.map(c => {
    const group = `${c.project} · ${c.category}`;
    const heading = group === lastGroup ? "" : `<tr class="group-row"><th colspan="7">${escapeHtml(group)}</th></tr>`;
    lastGroup = group;
    const subline = [c.id, c.reportFormat, c.category === "Carrier" ? `Design ${c.scope.split(" ").pop()}` : ""].filter(Boolean).join(" · ");
    return `${heading}<tr>
 <td><a href="#" class="component-name" data-open="${escapeHtml(c.id)}">${escapeHtml(c.name)}</a><div class="subline">${escapeHtml(subline)}</div></td>
 <td>${escapeHtml(c.project)}</td><td>${escapeHtml(c.category)}</td><td><strong>${escapeHtml(approvedVersion(c))}</strong></td><td>${escapeHtml(latestRecorded(c))}</td><td>${pill(c.status)}</td>
 <td><button class="btn small" data-open="${escapeHtml(c.id)}">Ver</button></td></tr>`;
  }).join('');
  $('emptyState').hidden = list.length !== 0;
  document.querySelectorAll('[data-open]').forEach(b => b.addEventListener('click', e => { e.preventDefault(); showDetail(b.dataset.open) }));
}
function renderExamples(c) {
  if (c.variants?.length) {
    return `<div class="package-file"><strong>RichPDFPackage</strong><a class="link package-download" href="${escapeHtml(encodeURI(c.packageFile))}" target="_blank" rel="noopener">${escapeHtml(c.packageFile.split("/").pop())} ↗</a></div>
      <div class="report-file-group"><h3>Example</h3><code>${escapeHtml(c.sourceLabel)}Example/</code>
      <div class="variant-grid">${c.variants.map(v => `<article class="example-card">
      <div class="example-heading"><strong>${escapeHtml(v.name)}</strong><span class="small muted">PDF</span></div>
      <a class="link" href="${escapeHtml(encodeURI(v.file))}" target="_blank" rel="noopener">${escapeHtml(v.fileName)} ↗</a>
    </article>`).join('')}</div></div>`;
  }
  if (c.reportFiles) {
    const renderFiles = files => `<ul class="report-file-list">${files.map(file => `<li>
      <span>${escapeHtml(file.label)}</span>
      ${file.sizeBytes === 0
        ? `<span class="report-file-name">${escapeHtml(file.name)}</span><span class="missing-file">Archivo vacío (0 bytes)</span>`
        : `<a class="link report-file-name" href="${escapeHtml(encodeURI(file.path))}" target="_blank" rel="noopener">${escapeHtml(file.name)} ↗</a><span class="small muted">${file.sizeBytes.toLocaleString("es-MX")} bytes</span>`}
    </li>`).join('')}</ul>`;
    return `<div class="report-folder"><strong>Carpeta del reporte</strong><code>${escapeHtml(c.reportFolder)}/</code></div>
      <div class="report-file-group"><h3>Archivos del reporte</h3>${renderFiles(c.reportFiles)}</div>
      <div class="report-file-group"><h3>Example</h3><code>${escapeHtml(c.reportFolder)}/Example/</code>${renderFiles(c.exampleFiles)}</div>
      ${c.reportFiles.some(file => file.path.endsWith(".sql")) ? "" : `<p class="small muted">No se encontró un archivo .sql separado en esta carpeta.</p>`}`;
  }
  const artifacts = c.rptFile ? `<div class="report-artifacts"><strong>Archivo Crystal Reports (.rpt):</strong> ${escapeHtml(c.rptFile)} <span class="missing-file">Pendiente de agregar</span><br><strong>SP:</strong> ${escapeHtml(c.storedProcedure)} <span class="missing-file">Pendiente de agregar</span></div>` : "";
  return `${artifacts}<article class="example-card">
    ${c.layout ? `<div class="report-layout"><strong>Layout</strong><p>${escapeHtml(c.layout)}</p></div>` : ""}
    <div class="example-heading"><strong>${escapeHtml(c.example.name)}</strong><span class="small muted">${escapeHtml(c.example.format)}</span></div>
    <pre class="sample">${escapeHtml(c.example.content)}</pre>
  </article>`;
}
function showHome() { $('home').style.display = ''; $('detailView').classList.remove('active'); window.scrollTo({ top: 0, behavior: 'smooth' }) }
function showDetail(id) {
  const c = CATALOG.find(x => x.id === id); if (!c) return;
  $('home').style.display = 'none'; $('detailView').classList.add('active');
  $('detailCategory').textContent = `${c.project} · ${c.category}${c.reportFormat ? ` · ${c.reportFormat}` : ""}`;
  $('detailName').textContent = c.name;
  $('detailSubtitle').textContent = [c.id, c.carrier].filter(Boolean).join(' · ');
  $('detailStatus').innerHTML = pill(c.status);
  $('detailId').textContent = c.id;
  const newest = latestRecorded(c), approved = approvedVersion(c);
  $('detailGrid').innerHTML = [
    ['Proyecto', c.project],
    ...(c.reportFolder ? [['Carpeta del reporte', c.reportFolder]] : []),
    ...(c.packageFile ? [['Archivo PKG3', c.packageFile.split("/").pop()]] : []),
    ...(c.reportFormat ? [['Formato', c.reportFormat]] : []),
    ['Última versión aprobada', approved],
    ['Última versión registrada', newest],
    ['Última actualización', dateLabel(c.lastUpdated)],
    ['Responsable', c.owner || 'Sin asignar'],
    ['Validación', c.validation],
    ['Alcance', c.scope || 'No especificado']
  ].map(([a, b]) => `<div class="detail-cell"><div class="label">${escapeHtml(a)}</div><strong>${escapeHtml(b)}</strong></div>`).join('');
  $('detailDescription').textContent = c.description;
  $('detailExamples').innerHTML = renderExamples(c);
  $('detailLinks').innerHTML = c.ticketUrl ? `<a class="btn" href="${escapeHtml(c.ticketUrl)}" target="_blank" rel="noopener">Abrir ticket ↗</a>` : "";
  $('detailSource').textContent = c.sourceLabel;
  $('historyCount').textContent = `${c.versions.length} versión(es)`;
  $('historyList').innerHTML = [...c.versions].sort((a, b) => b.recordedDate.localeCompare(a.recordedDate)).map(v => `<div class="history-item">
 <div><div class="history-version">${escapeHtml(v.version)}</div><div class="history-date">${dateLabel(v.recordedDate)}</div></div>
 <div><div class="tagline">${pill(v.status)} ${v.version === approved ? '<span class="pill approved">Aprobada actual</span>' : ''} ${v.version === newest ? '<span class="pill draft">Última registrada</span>' : ''}</div>
 <div class="history-desc">${escapeHtml(v.change)}</div><div class="small muted">Ticket: <a class="link" href="${escapeHtml(v.ticketUrl || '#')}" target="_blank" rel="noopener">${escapeHtml(v.ticket)}</a> · Actualizado por ${escapeHtml(v.author)}</div>${v.notes ? `<div class="small muted">${escapeHtml(v.notes)}</div>` : ''}</div></div>`).join('');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
init();
