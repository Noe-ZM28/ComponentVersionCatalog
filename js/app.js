const categories = [...new Set(CATALOG.map(c => c.category))];
const projects = [...new Set(CATALOG.map(c => c.project))];
const $ = id => document.getElementById(id);
let selectedCategory = "PC1";
const escapeHtml = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const statusClass = s => ({ 'Approved': 'approved', 'In Review': 'review', 'Draft': 'draft', 'Deprecated': 'deprecated', 'Pending verification': 'pending' }[s] || 'draft');
const pill = s => `<span class="pill ${statusClass(s)}">${escapeHtml(s)}</span>`;
const approvedVersion = c => c.versions.find(v => v.status === "Approved")?.version || "Not confirmed";
const latestRecorded = c => [...c.versions].sort((a, b) => b.recordedDate.localeCompare(a.recordedDate))[0]?.version || "—";
const dateLabel = d => d ? new Date(d + "T12:00:00").toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) : "Not recorded";
function init() {
  projects.forEach(project => $('projectFilter').insertAdjacentHTML('beforeend', `<option>${escapeHtml(project)}</option>`));
  renderCategories(); renderRows();
  $('projectFilter').addEventListener('change', () => { renderCategories(); renderRows() });
  $('backBtn').addEventListener('click', showHome);
  document.querySelectorAll('[data-detail-tab]').forEach(button => button.addEventListener('click', () => setDetailTab(button.dataset.detailTab)));
  ['historyList', 'detailExamples'].forEach(containerId => $(containerId).addEventListener('toggle', event => {
    const openedFile = event.target;
    if (!openedFile.matches?.('.history-file-item') || !openedFile.open) return;

    $(containerId).querySelectorAll('.history-file-item[open]').forEach(file => {
      if (file !== openedFile) file.open = false;
    });
  }, true));
}
function setDetailTab(activePane) {
  document.querySelectorAll('.detail-pane').forEach(pane => pane.classList.toggle('active', pane.id === activePane));
  document.querySelectorAll('[data-detail-tab]').forEach(button => {
    const isActive = button.dataset.detailTab === activePane;
    button.classList.toggle('active', isActive);
    button.setAttribute('aria-selected', String(isActive));
  });
}
function renderComparedLines(content, comparison, changeClass) {
  const lines = content.split(/\r?\n/);
  const comparisonLines = comparison.split(/\r?\n/);
  return lines.map((line, index) => `<span class="diff-line ${line === comparisonLines[index] ? '' : changeClass}">${escapeHtml(line) || ' '}</span>`).join('');
}
function renderFileList(files, fullPreview = false) {
  if (!files?.length) return `<p class="small muted">No hay archivos de ejemplo asociados a esta versión.</p>`;
  const previewClass = fullPreview ? " detail-file-preview" : "";
  return `<section class="history-files${fullPreview ? " detail-files" : ""}" aria-label="Archivos de ejemplo">
    <div class="history-file-list">${files.map(file => {
    const extension = file.name.split(".").pop().toLowerCase();
    const isEmpty = file.sizeBytes === 0;
    const previewUnavailable = ["rpt", "pkg3", "pgk3"].includes(extension);
    const fileLink = file.path && !previewUnavailable ? `<div class="history-file-actions"><a class="btn small" href="${escapeHtml(encodeURI(file.path))}" target="_blank" rel="noopener">Abrir archivo en una nueva pestaña</a></div>` : "";
    const preview = previewUnavailable
      ? `<div class="small muted">La previsualización de archivos .${escapeHtml(extension)} no está disponible.</div>`
      : isEmpty
      ? `<div class="missing-file">No hay contenido para previsualizar.</div>`
      : extension === "pdf" && file.path
        ? `<iframe class="${fullPreview ? "detail-file-pdf" : ""}" src="${escapeHtml(encodeURI(file.path))}" title="Previsualización de ${escapeHtml(file.name)}" loading="lazy"></iframe>`
        : file.preview
        ? `<pre class="sample history-file-sample${previewClass}">${escapeHtml(file.preview)}${file.previewTruncated ? "\n\n… Vista parcial. Abre el archivo para consultar el contenido completo." : ""}</pre>`
          : `<div class="small muted">No hay una vista previa disponible para este archivo.</div>`;
    return `<details class="history-file-item">
          <summary><span>${escapeHtml(file.label || file.name)}</span><span class="small muted">${escapeHtml(extension.toUpperCase())}</span></summary>
          <div class="history-file-content">
          ${fileLink}
          ${preview}
          </div>
        </details>`;
  }).join("")}</div>
  </section>`;
}
function renderHistoryFiles(files) {
  return renderFileList(files);
}
function renderCategories() {
  const selected = selectedCategory;
  const hasProject = Boolean($('projectFilter').value);
  $('categoryPrompt').hidden = hasProject;
  $('categoryCards').innerHTML = categories.map(cat => `<button class="category ${selected === cat ? 'active' : ''}" data-cat="${escapeHtml(cat)}" ${hasProject ? "" : "disabled"}><strong>${escapeHtml(cat)}</strong></button>`).join('');
  document.querySelectorAll('[data-cat]').forEach(b => b.addEventListener('click', () => { selectedCategory = selectedCategory === b.dataset.cat ? '' : b.dataset.cat; renderCategories(); renderRows() }));
}
function renderRows() {
  const project = $('projectFilter').value, cat = selectedCategory;
  const hasProject = Boolean(project);
  $('projectElementsView').hidden = !hasProject;
  $('projectSelectionPrompt').hidden = hasProject;
  const categoryOrder = ["PC1", "Reporte", "Carrier"];
  const list = CATALOG.filter(c => {
    return hasProject && c.project === project && (!cat || c.category === cat);
  })
    .sort((a, b) => projects.indexOf(a.project) - projects.indexOf(b.project) || categoryOrder.indexOf(a.category) - categoryOrder.indexOf(b.category) || a.name.localeCompare(b.name));
  let lastGroup = "";
  $('componentRows').innerHTML = list.map(c => {
    const group = `${c.project} · ${c.category}`;
    const heading = group === lastGroup ? "" : `<tr class="group-row"><th colspan="5">${escapeHtml(group)}</th></tr>`;
    lastGroup = group;
    const subline = [c.id, c.reportFormat, c.category === "Carrier" ? `Design ${c.scope.split(" ").pop()}` : ""].filter(Boolean).join(" · ");
    return `${heading}<tr>
 <td><a href="#" class="component-name" data-open="${escapeHtml(c.id)}">${escapeHtml(c.name)}</a><div class="subline">${escapeHtml(subline)}</div></td>
 <td>${escapeHtml(c.project)}</td><td>${escapeHtml(c.category)}</td><td><strong>${escapeHtml(latestRecorded(c))}</strong></td>
 <td><button class="btn small" data-open="${escapeHtml(c.id)}">Ver</button></td></tr>`;
  }).join('');
  $('emptyState').hidden = list.length !== 0;
  document.querySelectorAll('[data-open]').forEach(b => b.addEventListener('click', e => { e.preventDefault(); showDetail(b.dataset.open) }));
}
function renderExamples(c) {
  if (c.variants?.length) {
    const files = [
      { label: "RichPDFPackage", name: c.packageFile.split("/").pop(), path: c.packageFile },
      ...c.variants.map(variant => ({ label: variant.name, name: variant.fileName, path: variant.file }))
    ];
    return renderFileList(files, true);
  }
  if (c.reportFiles) {
    return renderFileList([...c.reportFiles, ...c.exampleFiles], true);
  }
  const artifacts = c.rptFile ? `<div class="report-artifacts"><strong>Archivo Crystal Reports (.rpt):</strong> ${escapeHtml(c.rptFile)} <span class="missing-file">Pendiente de agregar</span><br><strong>SP:</strong> ${escapeHtml(c.storedProcedure)} <span class="missing-file">Pendiente de agregar</span></div>` : "";
  const files = [{ label: c.example.format, name: c.example.name, preview: c.example.content }];
  return `${artifacts}${c.layout ? `<div class="report-layout"><strong>Layout</strong><p>${escapeHtml(c.layout)}</p></div>` : ""}${renderFileList(files, true)}`;
}
function renderFilePreview(file) {
  const extension = file.name.split(".").pop().toLowerCase();
  if (["rpt", "pkg3", "pgk3"].includes(extension)) return "";

  if (extension === "pdf") {
    const path = escapeHtml(encodeURI(file.path));
    return `<details class="file-preview">
      <summary>Previsualizar PDF</summary>
      <iframe src="${path}" title="Vista previa de ${escapeHtml(file.name)}" loading="lazy"></iframe>
    </details>`;
  }

  if (!file.preview) return "";
  return `<details class="file-preview">
    <summary>Previsualizar archivo</summary>
    <pre class="sample">${escapeHtml(file.preview)}${file.previewTruncated ? "\n\n… Vista parcial. Abre el archivo para ver el contenido completo." : ""}</pre>
  </details>`;
}
function showHome() { $('home').style.display = ''; $('detailView').classList.remove('active'); window.scrollTo({ top: 0, behavior: 'smooth' }) }
function showDetail(id) {
  const c = CATALOG.find(x => x.id === id); if (!c) return;
  setDetailTab('componentDetailPane');
  $('home').style.display = 'none'; $('detailView').classList.add('active');
  $('detailCategory').textContent = `${c.project} · ${c.category}${c.reportFormat ? ` · ${c.reportFormat}` : ""}`;
  $('detailName').textContent = c.name;
  $('detailSubtitle').textContent = [c.id, c.carrier].filter(Boolean).join(' · ');
  $('detailId').textContent = c.id;
  const newest = latestRecorded(c), approved = approvedVersion(c);
  $('detailGrid').innerHTML = [
    ['Proyecto', c.project],
    ...(c.packageFile ? [['Archivo PKG3', c.packageFile.split("/").pop()]] : []),
    ...(c.reportFormat ? [['Formato', c.reportFormat]] : []),
    ['Última versión registrada', newest],
    ['Última actualización', dateLabel(c.lastUpdated)],
  ].map(([a, b]) => `<div class="detail-cell"><div class="label">${escapeHtml(a)}</div><strong>${escapeHtml(b)}</strong></div>`).join('');
  $('detailDescription').textContent = c.description;
  $('detailExamples').innerHTML = renderExamples(c);
  $('detailLinks').innerHTML = c.ticketUrl ? `<a class="btn" href="${escapeHtml(c.ticketUrl)}" target="_blank" rel="noopener">Abrir ticket ↗</a>` : "";
  $('historyCount').textContent = `(${c.versions.length})`;
  $('historyList').innerHTML = [...c.versions].sort((a, b) => b.recordedDate.localeCompare(a.recordedDate)).map(v => `<article class="history-item">
 <div><div class="history-version">${escapeHtml(v.version)}</div><div class="history-date">${dateLabel(v.recordedDate)}</div></div>
 <div class="history-content">
 <div class="history-ticket"><span class="history-ticket-label">Ticket: </span><a class="history-ticket-link" href="${escapeHtml(v.ticketUrl || '#')}" target="_blank" rel="noopener">${escapeHtml(v.ticketType)} - ${escapeHtml(v.ticketName)}</a></div>
 <div class="history-desc"><strong>Cambio:</strong> ${escapeHtml(v.change)}</div>
 <article class="history-snapshot">
   <div class="example-heading"><strong>${escapeHtml(c.name)} · Ejemplo de versión ${escapeHtml(v.version)}</strong><span class="small muted">${escapeHtml(c.category)}</span></div>
   ${v.previewAfter ? `<div class="change-preview">
     ${v.previewBefore ? `<div class="change-side before"><div class="change-label">Antes</div><pre class="sample">${renderComparedLines(v.previewBefore, v.previewAfter, 'removed')}</pre></div>` : ''}
     <div class="change-side after"><div class="change-label">${v.previewBefore ? 'Después' : 'Muestra de esta versión'}</div><pre class="sample">${v.previewBefore ? renderComparedLines(v.previewAfter, v.previewBefore, 'added') : escapeHtml(v.previewAfter)}</pre></div>
   </div><div class="demo-label">Previsualización de cambio simulada</div>` : ''}
   ${renderHistoryFiles(v.historyFiles)}
 </article>
 <div class="small muted"></div>${v.notes ? `<div class="small muted">${escapeHtml(v.notes)}</div>` : ''}</div></article>`).join('');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
init();
