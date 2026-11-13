(() => {
  "use strict";

  const API_BASE = (window.CVC_API_BASE || window.location.origin).replace(/\/+$/, "");
  const $ = id => document.getElementById(id);
  const COMPONENT_TYPES = ["PC1", "Reporte", "Carrier", "API", "Batch", "Seguridad", "other"];
  const state = {
    projects: [],
    projectDetailsById: new Map(),
    selectedProjectId: "",
    selectedCategory: "",
    selectedComponentId: null,
    currentComponent: null,
    toastTimer: null
  };

  const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);

  async function api(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, options);
    const contentType = response.headers.get("content-type") || "";
    const body = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const detail = typeof body === "object" && body !== null
        ? body.detail || body.message
        : body;
      throw new Error(detail || `Error HTTP ${response.status}`);
    }

    return body;
  }

  function showToast(message, isError = false) {
    const toast = $("toast");
    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.add("visible");
    window.clearTimeout(state.toastTimer);
    state.toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 4200);
  }

  function showGlobalError(error) {
    const message = $("globalMessage");
    message.textContent = error.message || "No fue posible completar la solicitud.";
    message.hidden = false;
  }

  function showProjectUpdateSummary(summary) {
    const categories = [
      { key: "new_projects", countId: "projectsAddedCount", listId: "projectsAddedList" },
      { key: "updated_projects", countId: "projectsModifiedCount", listId: "projectsModifiedList" },
      { key: "skipped_projects", countId: "projectsIgnoredCount", listId: "projectsIgnoredList" }
    ];

    categories.forEach(({ key, countId, listId }) => {
      const projects = summary[key];
      if (!Array.isArray(projects) || !projects.every(name => typeof name === "string")) {
        throw new Error("La API devolvió un resumen de actualización inválido.");
      }

      $(countId).textContent = projects.length;
      $(listId).innerHTML = projects.length
        ? projects.map(name => `<li>${escapeHtml(name)}</li>`).join("")
        : "<li>Ninguno</li>";
    });

    $("projectUpdateDialog").showModal();
  }

  function showComponentUpdateSummary(summary) {
    const categories = [
      { key: "new_components", countId: "componentsAddedCount", listId: "componentsAddedList" },
      { key: "updated_components", countId: "componentsModifiedCount", listId: "componentsModifiedList" },
      { key: "skipped_components", countId: "componentsIgnoredCount", listId: "componentsIgnoredList" }
    ];

    categories.forEach(({ key, countId, listId }) => {
      const components = summary[key];
      if (!Array.isArray(components) || !components.every(name => typeof name === "string")) {
        throw new Error("La API devolvió un resumen de actualización de componentes inválido.");
      }

      $(countId).textContent = components.length;
      $(listId).innerHTML = components.length
        ? components.map(name => `<li>${escapeHtml(name)}</li>`).join("")
        : "<li>Ninguno</li>";
    });

    $("componentUpdateTitle").textContent = "Resultado de actualización de componentes";
    $("componentUpdateProgress").hidden = true;
    $("componentUpdateResults").hidden = false;
    $("componentUpdateError").hidden = true;
    $("componentUpdateDone").hidden = false;
    $("componentUpdateClose").disabled = false;
    $("componentUpdateDialog").hidden = false;
  }

  function showComponentUpdateProgress() {
    $("componentUpdateTitle").textContent = "Sincronizando componentes";
    $("componentUpdateStatus").textContent = "La sincronización está en curso. El resultado aparecerá aquí.";
    $("componentUpdateProgress").hidden = false;
    $("componentUpdateResults").hidden = true;
    $("componentUpdateError").hidden = true;
    $("componentUpdateDone").hidden = true;
    $("componentUpdateClose").disabled = true;
    $("componentUpdateDialog").hidden = false;
  }

  function showComponentUpdateError(error) {
    $("componentUpdateTitle").textContent = "No se pudo sincronizar componentes";
    $("componentUpdateProgress").hidden = true;
    $("componentUpdateResults").hidden = true;
    const errorMessage = $("componentUpdateError");
    errorMessage.textContent = error.message || "No fue posible completar la sincronización.";
    errorMessage.hidden = false;
    $("componentUpdateDone").hidden = false;
    $("componentUpdateClose").disabled = false;
    $("componentUpdateDialog").hidden = false;
  }

  function setConnection(connected, message = "") {
    const status = $("connectionStatus");
    status.textContent = connected ? "API conectada" : "API no disponible";
    status.classList.toggle("offline", !connected);
    status.title = message;
  }

  function currentProject() {
    return state.projectDetailsById.get(state.selectedProjectId) ||
      state.projects.find(project => String(project.id) === state.selectedProjectId) ||
      null;
  }

  function projectTickets(projectId = state.selectedProjectId) {
    return state.projectDetailsById.get(String(projectId))?.tickets || [];
  }

  function componentType(component) {
    return component.type_component || "other";
  }

  function formatDate(value) {
    if (!value) return "Sin fecha";
    const date = new Date(value);
    return Number.isNaN(date.getTime())
      ? "Sin fecha"
      : date.toLocaleDateString("es-MX", { day: "2-digit", month: "short", year: "numeric" });
  }

  function ticketLink(ticket) {
    const ticketKey = escapeHtml(ticket.ticket_key);
    try {
      const url = new URL(ticket.ticket_url, API_BASE);
      if (url.protocol === "http:" || url.protocol === "https:") {
        return `<a class="history-ticket-link" href="${escapeHtml(url.href)}" target="_blank" rel="noopener noreferrer">${ticketKey}</a>`;
      }
    } catch {
      // Show the ticket key as text if its URL is invalid.
    }
    return `<strong>${ticketKey}</strong>`;
  }

  function allChanges() {
    return projectTickets().flatMap(ticket =>
      (ticket.changes || []).map(change => ({ ...change, ticket }))
    );
  }

  async function loadCatalog() {
    $("globalMessage").hidden = true;
    $("connectionStatus").textContent = "Conectando…";
    try {
      const projects = await api("/projects");
      state.projects = projects;
      state.projectDetailsById = new Map();

      if (!projects || projects.length === 0) {
        state.selectedProjectId = "";
        setConnection(true);
        renderProjectOptions();
        renderStats();
        renderCategories();
        renderComponents();

        $("projectDescription").textContent = "";
        $("projectSelectionPrompt").textContent =
          "No hay proyectos para cargar.";

        return;
      }

      setConnection(true);
      renderProjectOptions();
      renderStats();
      renderCategories();
      renderComponents();

      if (state.selectedProjectId) {
        await loadProjectDetails(state.selectedProjectId);
      }

    } catch (error) {
      setConnection(false, error.message);
      showGlobalError(error);

      $("projectSelectionPrompt").textContent =
        `No se pudo cargar el catálogo. Comprueba que el backend esté activo (${API_BASE}) y vuelve a intentar.`;
    }
  }

  async function loadProjectDetails(projectId) {
    const project = await api(`/projects/${projectId}`);
    if (!Array.isArray(project.components) || !Array.isArray(project.tickets)) {
      throw new Error("La API devolvió un detalle de proyecto inválido.");
    }

    const id = String(projectId);
    state.projectDetailsById.set(id, project);
    if (state.selectedProjectId === id) {
      renderProjectOptions();
      renderStats();
      renderCategories();
      renderComponents();
    }
    return project;
  }


  function renderProjectOptions() {
    const select = $("projectFilter");
    const selected = state.selectedProjectId;
    select.innerHTML = '<option value="">Selecciona un proyecto</option>' +
      state.projects.map(project =>
      `<option value="${project.id}">${project.cust_num == null ? "" : `${escapeHtml(project.cust_num)} · `}${escapeHtml(project.name)}</option>`
      ).join("");
    select.value = state.projects.some(project => String(project.id) === selected) ? selected : "";
    state.selectedProjectId = select.value;
    const hasDetails = state.projectDetailsById.has(state.selectedProjectId);
    $("updateComponentsBtn").disabled = !hasDetails;
    $("createTicketBtn").disabled = !hasDetails;
    $("projectElementsView").hidden = !state.selectedProjectId;
    $("projectSelectionPrompt").hidden = Boolean(state.selectedProjectId);
    const project = currentProject();
    $("projectDescription").textContent = project
      ? `${project.cust_num == null ? "" : `CustNum: ${project.cust_num} · `}${project.description || ""}`
      : "";
  }

  function renderStats() {
    const components = currentProject()?.components || [];
    const tickets = projectTickets();
    $("projectCount").textContent = state.projects.length;
    $("componentCount").textContent = components.length;
    $("ticketCount").textContent = tickets.length;
    $("changeCount").textContent = tickets.reduce(
      (count, ticket) => count + (ticket.changes || []).length, 0
    );
  }

  function renderCategories() {
    const project = currentProject();
    const components = project?.components || [];
    const disabled = state.projectDetailsById.has(state.selectedProjectId) ? "" : " disabled";
    if (state.selectedCategory && !COMPONENT_TYPES.includes(state.selectedCategory)) {
      state.selectedCategory = "";
    }
    $("categoryCards").innerHTML = [
      `<button class="category ${state.selectedCategory === "" ? "active" : ""}" type="button" data-category=""${disabled}><strong>Todos</strong><span>${components.length}</span></button>`,
      ...COMPONENT_TYPES.map(category => {
        const count = components.filter(component => componentType(component) === category).length;
        return `<button class="category ${state.selectedCategory === category ? "active" : ""}" type="button" data-category="${escapeHtml(category)}"${disabled}><strong>${escapeHtml(category)}</strong><span>${count}</span></button>`;
      })
    ].join("");
    $("categoryCards").querySelectorAll("[data-category]").forEach(button => {
      button.addEventListener("click", () => {
        state.selectedCategory = button.dataset.category;
        renderCategories();
        renderComponents();
      });
    });
  }

  function componentChanges(componentId) {
    return allChanges()
      .filter(change => change.component_id === componentId)
      .sort((left, right) => new Date(right.created_at) - new Date(left.created_at));
  }

  function renderComponents() {
    const project = currentProject();
    const hasProject = Boolean(project);
    $("projectElementsView").hidden = !hasProject;
    $("projectSelectionPrompt").hidden = hasProject;
    if (!project) {
      $("componentRows").innerHTML = "";
      $("emptyState").hidden = true;
      $("componentSummary").textContent = "";
      return;
    }

    if (!state.projectDetailsById.has(state.selectedProjectId)) {
      $("componentRows").innerHTML = "";
      $("emptyState").hidden = true;
      $("componentSummary").textContent = "Cargando componentes y tickets…";
      return;
    }

    const search = $("componentSearch").value.trim().toLocaleLowerCase();
    const list = (project.components || []).filter(component => {
      const matchesCategory = !state.selectedCategory || componentType(component) === state.selectedCategory;
      const matchesSearch = !search ||
        `${component.name} ${component.description} ${component.cadena} ${component.ref_id || ""}`.toLocaleLowerCase().includes(search);
      return matchesCategory && matchesSearch;
    }).sort((left, right) => left.name.localeCompare(right.name, "es"));

    $("componentSummary").textContent = `${list.length} de ${(project.components || []).length} componentes`;
    $("componentRows").innerHTML = list.map(component => {
      const changes = componentChanges(component.id);
      const latest = changes[0];
      return `<tr>
        <td><button class="text-button component-name" type="button" data-open-component="${component.id}">${escapeHtml(component.name)}</button><div class="subline">${escapeHtml(component.type_component || "other")}${component.source_reference ? ` · ${escapeHtml(component.source_reference)}` : ""}</div></td>
        <td>${escapeHtml(component.ref_id || "—")}</td>
        <td><strong>${escapeHtml(component.cadena)}</strong><span class="muted"> / ${escapeHtml(component.step)}</span></td>
        <td>${escapeHtml(componentType(component))}</td>
        <td>${latest ? `<strong>#${latest.change_number}</strong><div class="subline">${ticketLink(latest.ticket)}</div>` : "—"}</td>
        <td><button class="btn small" type="button" data-open-component="${component.id}">Ver</button></td>
      </tr>`;
    }).join("");
    $("emptyState").hidden = list.length > 0;
    $("componentRows").querySelectorAll("[data-open-component]").forEach(button => {
      button.addEventListener("click", () => showComponent(Number(button.dataset.openComponent)));
    });
  }

  function renderComponentDetail(component) {
    const project = currentProject();
    const changes = componentChanges(component.id);
    state.currentComponent = component;
    $("home").style.display = "none";
    $("detailView").classList.add("active");
    $("detailCategory").textContent = `${project?.name || "Proyecto"} · ${componentType(component)}`;
    $("detailName").textContent = component.name;
    $("detailSubtitle").textContent = `${component.cadena} · Paso ${component.step}`;
    $("detailId").textContent = `ID ${component.id}`;
    $("detailGrid").innerHTML = [
      ["Proyecto", project?.name],
      ["RefID", component.ref_id || "—"],
      ["Cadena", component.cadena],
      ["Paso", component.step],
      ["Tipo de componente", component.type_component || "other"],
      ["Referencia", component.source_reference || "Sin referencia"],
      ["Cambios registrados", changes.length]
    ].map(([label, value]) => `<div class="detail-cell"><div class="label">${escapeHtml(label)}</div><strong>${escapeHtml(value ?? "—")}</strong></div>`).join("");
    $("detailDescription").textContent = component.description || "Sin descripción.";
    $("historyCount").textContent = `(${changes.length})`;
    $("historyList").innerHTML = changes.length
      ? changes.map(renderChange).join("")
      : '<div class="empty">Todavía no hay cambios registrados para este componente.</div>';
    $("detailExamples").innerHTML = renderFiles(changes);
    setDetailTab("componentDetailPane");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function showComponent(componentId) {
    const component = (currentProject()?.components || []).find(item => item.id === componentId);
    if (!component) return;
    state.selectedComponentId = componentId;
    renderComponentDetail(component);
  }

  function renderChange(change) {
    const ticket = change.ticket;
    return `<article class="history-item">
      <div><div class="history-version">#${escapeHtml(change.change_number)}</div><div class="history-date">${formatDate(change.created_at)}</div></div>
      <div class="history-content">
        <div class="history-ticket"><span class="history-ticket-label">Ticket</span>${ticketLink(ticket)}<span class="small muted">${escapeHtml(ticket.title)}</span></div>
        <h3>${escapeHtml(change.title)}</h3>
        <p class="history-desc">${escapeHtml(change.description)}</p>
        <div class="small muted">${escapeHtml(change.cadena)} · Paso ${escapeHtml(change.step)}</div>
        <button class="btn small edit-change-btn" type="button" data-edit-change="${change.id}">Editar cambio</button>
      </div>
    </article>`;
  }

  function renderFiles(changes) {
    const files = changes.flatMap(change => (change.files || []).map(item => ({ ...item, change })));
    if (!files.length) return '<p class="small muted">No hay archivos asociados a los cambios de este componente.</p>';
    return `<div class="file-list">${files.map(item => {
      const file = item.file;
      const downloadUrl = `/projects/${item.change.project_id}/changes/${item.change.id}/files/${item.file_id}/download`;
      return `<div class="file-row"><div><strong>${escapeHtml(file.original_name)}</strong><div class="small muted">${escapeHtml(item.role)} · ${escapeHtml(item.description)} · ${escapeHtml(file.type_file)}</div></div><a class="btn small" href="${API_BASE}${downloadUrl}" target="_blank" rel="noopener">Descargar</a></div>`;
    }).join("")}</div>`;
  }

  function setDetailTab(activePane) {
    document.querySelectorAll(".detail-pane").forEach(pane => pane.classList.toggle("active", pane.id === activePane));
    document.querySelectorAll("[data-detail-tab]").forEach(button => {
      const active = button.dataset.detailTab === activePane;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", String(active));
    });
  }

  function showHome() {
    $("home").style.display = "";
    $("detailView").classList.remove("active");
    state.selectedComponentId = null;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function initTheme() {
    const savedTheme = localStorage.getItem("catalog-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(savedTheme || (prefersDark ? "dark" : "light"));
    $("themeToggle").addEventListener("click", () => {
      const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      localStorage.setItem("catalog-theme", nextTheme);
      setTheme(nextTheme);
    });
  }

  function setTheme(theme) {
    document.documentElement.dataset.theme = theme;
    const isDark = theme === "dark";
    $("themeToggle").textContent = isDark ? "Modo claro" : "Modo nocturno";
    $("themeToggle").setAttribute("aria-pressed", String(isDark));
  }

  function openDialog(title, fields, submitLabel = "Guardar", eyebrow = "Catálogo", mode = "") {
    $("dialogEyebrow").textContent = eyebrow;
    $("dialogTitle").textContent = title;
    $("dialogFields").innerHTML = fields;
    $("dialogSubmit").textContent = submitLabel;
    $("entityForm").dataset.mode = mode;
    $("entityForm").dataset.changeId = "";
    $("entityDialog").showModal();
  }

  function closeDialog() {
    $("entityDialog").close();
    $("entityForm").reset();
  }

  function formField(label, name, options = {}) {
    const { value = "", required = true, type = "text", maxLength = 1000, placeholder = "" } = options;
    return `<label class="form-field">${escapeHtml(label)}<input name="${escapeHtml(name)}" type="${type}" value="${escapeHtml(value)}" ${required ? "required" : ""} maxlength="${maxLength}" placeholder="${escapeHtml(placeholder)}"></label>`;
  }

  function changeEntry(index, componentId = "") {
    const components = currentProject()?.components || [];
    return `<fieldset class="change-entry"><legend>Cambio ${index + 1}</legend>
      <label class="form-field">Componente<select name="component_id" required><option value="">Selecciona componente</option>${components.map(component => `<option value="${component.id}" ${String(component.id) === String(componentId) ? "selected" : ""}>${escapeHtml(component.name)}</option>`).join("")}</select></label>
      ${formField("Título del cambio", "change_title", { maxLength: 250 })}
      <label class="form-field">Descripción<textarea name="change_description" required maxlength="1000" rows="3"></textarea></label>
    </fieldset>`;
  }

  function addChangeEntryButton() {
    return '<button class="btn small" type="button" id="addChangeEntry">＋ Otro cambio</button>';
  }

  $("updateProjectsBtn").addEventListener("click", async () => {
    const button = $("updateProjectsBtn");
    button.disabled = true;
    try {
      const summary = await api("/projects/update", { method: "POST" });
      showProjectUpdateSummary(summary);
      await loadCatalog();
    } catch (error) {
      showToast(error.message, true);
    } finally {
      button.disabled = false;
    }
  });

  function closeProjectUpdateDialog() {
    $("projectUpdateDialog").close();
  }

  $("projectUpdateClose").addEventListener("click", closeProjectUpdateDialog);
  $("projectUpdateDone").addEventListener("click", closeProjectUpdateDialog);
  $("projectUpdateDialog").addEventListener("click", event => {
    if (event.target === $("projectUpdateDialog")) closeProjectUpdateDialog();
  });

  function closeComponentUpdateDialog() {
    $("componentUpdateDialog").hidden = true;
  }

  $("componentUpdateClose").addEventListener("click", closeComponentUpdateDialog);
  $("componentUpdateDone").addEventListener("click", closeComponentUpdateDialog);
  $("componentUpdateDialog").addEventListener("click", event => {
    if (event.target === $("componentUpdateDialog")) closeComponentUpdateDialog();
  });

  $("updateComponentsBtn").addEventListener("click", async () => {
    if (!currentProject()) return;
    const button = $("updateComponentsBtn");
    button.disabled = true;
    try {
      showComponentUpdateProgress();
      const summary = await api(`/projects/${state.selectedProjectId}/components/update`, {
        method: "POST"
      });
      showComponentUpdateSummary(summary);
      await loadCatalog();
    } catch (error) {
      showComponentUpdateError(error);
    } finally {
      button.disabled = false;
    }
  });

  $("createTicketBtn").addEventListener("click", () => {
    if (!currentProject()) return;
    openDialog("Registrar ticket y cambio", `<div class="form-grid">
      ${formField("Clave del ticket", "ticket_key", { maxLength: 100, placeholder: "PAY-123" })}
      ${formField("Título del ticket", "title", { maxLength: 250 })}
      ${formField("URL del ticket", "ticket_url", { type: "url", maxLength: 500, placeholder: "https://…" })}
      <label class="form-field full">Descripción<textarea name="description" rows="3" required maxlength="1000"></textarea></label>
      <div id="changeEntries" class="form-field full">${changeEntry(0)}</div>
      <div class="form-field full">${addChangeEntryButton()}</div>
    </div>`, "Registrar", "Catálogo", "ticket");
  });

  $("addChangeBtn").addEventListener("click", () => {
    const tickets = projectTickets();
    if (!tickets.length) {
      showToast("Crea un ticket antes de agregar cambios.", true);
      return;
    }
    openDialog("Agregar cambio a ticket", `<div class="form-grid">
      <label class="form-field full">Ticket<select name="ticket_id" required><option value="">Selecciona ticket</option>${tickets.map(ticket => `<option value="${ticket.id}">${escapeHtml(ticket.ticket_key)} · ${escapeHtml(ticket.title)}</option>`).join("")}</select></label>
      <div id="changeEntries" class="form-field full">${changeEntry(0, state.selectedComponentId)}</div>
      <div class="form-field full">${addChangeEntryButton()}</div>
    </div>`, "Agregar", "Catálogo", "add-changes");
  });

  $("dialogFields").addEventListener("click", event => {
    if (event.target.id !== "addChangeEntry") return;
    const container = $("changeEntries");
    const count = container.querySelectorAll(".change-entry").length;
    container.insertAdjacentHTML("beforeend", changeEntry(count, state.selectedComponentId));
  });

  $("dialogClose").addEventListener("click", closeDialog);
  $("dialogCancel").addEventListener("click", closeDialog);
  $("entityDialog").addEventListener("click", event => {
    if (event.target === $("entityDialog")) closeDialog();
  });

  $("entityForm").addEventListener("submit", async event => {
    event.preventDefault();
    const submit = $("dialogSubmit");
    submit.disabled = true;
    try {
      const form = new FormData(event.currentTarget);
      const entries = [...$("dialogFields").querySelectorAll(".change-entry")].map(entry => ({
        component_id: Number(entry.querySelector('[name="component_id"]').value),
        title: entry.querySelector('[name="change_title"]').value.trim(),
        description: entry.querySelector('[name="change_description"]').value.trim()
      }));
      const projectId = Number(state.selectedProjectId);
      const hasChangeEntries = entries.length > 0;
      const mode = event.currentTarget.dataset.mode;
      if (mode === "edit-change") {
        await api(`/change/${event.currentTarget.dataset.changeId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            component_id: Number(form.get("component_id")),
            title: form.get("title"),
            description: form.get("description")
          })
        });
        showToast("Cambio actualizado.");
      } else if (mode === "add-changes") {
        await api(`/tickets/${Number(form.get("ticket_id"))}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(entries)
        });
        showToast("Cambios agregados al ticket.");
      } else if (mode === "ticket" && hasChangeEntries) {
        await api(`/projects/${projectId}/tickets`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ticket_key: form.get("ticket_key"),
            title: form.get("title"),
            description: form.get("description"),
            ticket_url: form.get("ticket_url"),
            changes: entries
          })
        });
        showToast("Ticket y cambio registrados.");
      } else if (mode === "project") {
        await api("/projects", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: form.get("name"),
            description: form.get("description"),
            cust_num: form.get("cust_num") === "" ? null : Number(form.get("cust_num"))
          })
        });
        showToast("Proyecto creado.");
      } else if (mode === "component") {
        await api(`/projects/${projectId}/components`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: form.get("name"),
            description: form.get("description"),
            cadena: form.get("cadena"),
            step: Number(form.get("step")),
            ref_id: form.get("ref_id") || null,
            type_component: form.get("type_component"),
            source_reference: form.get("source_reference") || null
          })
        });
        showToast("Componente creado.");
      }
      closeDialog();
      await loadCatalog();
      if (state.selectedComponentId) await showComponent(state.selectedComponentId);
    } catch (error) {
      showToast(error.message, true);
    } finally {
      submit.disabled = false;
    }
  });

  $("historyList").addEventListener("click", event => {
    const button = event.target.closest("[data-edit-change]");
    if (!button) return;
    const change = componentChanges(state.selectedComponentId).find(item => item.id === Number(button.dataset.editChange));
    if (!change) return;
    openDialog("Editar cambio", `<div class="form-grid">
      <label class="form-field full">Componente<select name="component_id" required>${(currentProject()?.components || []).map(component => `<option value="${component.id}" ${component.id === change.component_id ? "selected" : ""}>${escapeHtml(component.name)}</option>`).join("")}</select></label>
      ${formField("Título", "title", { value: change.title, maxLength: 250 })}
      <label class="form-field full">Descripción<textarea name="description" rows="3" required maxlength="1000">${escapeHtml(change.description)}</textarea></label>
    </div>`, "Guardar", "Historial", "edit-change");
    $("entityForm").dataset.changeId = String(change.id);
  });

  $("projectFilter").addEventListener("change", async event => {
    state.selectedProjectId = event.target.value;
    state.selectedCategory = "";
    state.projectDetailsById.delete(state.selectedProjectId);
    $("projectDescription").textContent = currentProject()?.description || "";
    renderProjectOptions();
    renderStats();
    renderCategories();
    renderComponents();
    if (state.selectedProjectId) {
      try {
        await loadProjectDetails(state.selectedProjectId);
      } catch (error) {
        $("componentSummary").textContent = "No se pudieron cargar los componentes y tickets.";
        showToast(error.message, true);
      }
    }
  });
  $("componentSearch").addEventListener("input", renderComponents);
  $("backBtn").addEventListener("click", showHome);
  document.querySelectorAll("[data-detail-tab]").forEach(button =>
    button.addEventListener("click", () => setDetailTab(button.dataset.detailTab))
  );

  $("uploadFileBtn").addEventListener("click", () => $("fileInput").click());
  $("fileInput").addEventListener("change", async event => {
    const files = [...event.target.files];
    const component = state.currentComponent;
    const project = currentProject();
    if (!files.length || !component || !project) return;
    const changes = componentChanges(component.id);
    const selectedChange = changes[0];
    if (!selectedChange) {
      showToast("Registra un cambio antes de adjuntar archivos.", true);
      event.target.value = "";
      return;
    }
    const formData = new FormData();
    files.forEach(file => formData.append("files", file));
    formData.append("metadata", JSON.stringify(files.map(file => ({
      type_file: file.name.split(".").pop().slice(0, 30) || "other",
      role: "attachment",
      description: file.name
    }))));
    try {
      await api(`/projects/${project.id}/changes/${selectedChange.id}/files/uploadfiles`, {
        method: "POST",
        body: formData
      });
      showToast(`${files.length} archivo(s) adjuntado(s).`);
      await loadCatalog();
      await showComponent(component.id);
    } catch (error) {
      showToast(error.message, true);
    } finally {
      event.target.value = "";
    }
  });

  $("apiBaseLabel").textContent = `API: ${API_BASE}`;
  initTheme();
  loadCatalog();
})();
