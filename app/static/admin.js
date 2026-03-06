const output = document.getElementById("output");
const baseUrlInput = document.getElementById("baseUrl");
const apiKeyInput = document.getElementById("apiKey");

const tenantSelectUrl = document.getElementById("tenantSelectUrl");
const tenantSelectFile = document.getElementById("tenantSelectFile");
const tenantSelectQuery = document.getElementById("tenantSelectQuery");

baseUrlInput.value = window.location.origin;

function log(data) {
  output.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

function apiBase() {
  return (baseUrlInput.value || "").replace(/\/+$/, "") || window.location.origin;
}

function authHeaders() {
  const key = apiKeyInput.value.trim();
  return key ? { "x-api-key": key } : {};
}

async function request(path, options = {}) {
  const res = await fetch(`${apiBase()}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...authHeaders(),
    },
  });
  const text = await res.text();
  let data = text;
  try { data = JSON.parse(text); } catch {}
  if (!res.ok) throw new Error(typeof data === "string" ? data : JSON.stringify(data));
  return data;
}

function setTenantOptions(tenants) {
  const options = tenants.map((t) => `<option value="${t.tenant_id}">${t.tenant_id}${t.name ? ` (${t.name})` : ""}</option>`).join("");
  tenantSelectUrl.innerHTML = options;
  tenantSelectFile.innerHTML = options;
  tenantSelectQuery.innerHTML = options;
}

async function refreshTenants() {
  const data = await request("/tenants");
  const tenants = data.tenants || [];
  setTenantOptions(tenants);
  log(data);
}

document.getElementById("refreshTenants").addEventListener("click", async () => {
  try { await refreshTenants(); } catch (e) { log(e.message); }
});

document.getElementById("createTenant").addEventListener("click", async () => {
  try {
    const tenant_id = document.getElementById("tenantId").value.trim();
    const name = document.getElementById("tenantName").value.trim();
    const data = await request("/tenants", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_id, name }),
    });
    log(data);
    await refreshTenants();
  } catch (e) { log(e.message); }
});

document.getElementById("ingestUrl").addEventListener("click", async () => {
  try {
    const tenant_id = tenantSelectUrl.value;
    const url = document.getElementById("urlInput").value.trim();
    const crawl = document.getElementById("crawlEnabled").value === "true";
    const max_depth = Number(document.getElementById("maxDepth").value || "1");
    const max_pages = Number(document.getElementById("maxPages").value || "20");
    const data = await request("/ingest/url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_id, url, crawl, max_depth, max_pages, same_domain_only: true }),
    });
    log(data);
  } catch (e) { log(e.message); }
});

document.getElementById("ingestFile").addEventListener("click", async () => {
  try {
    const tenant_id = tenantSelectFile.value;
    const file = document.getElementById("fileInput").files[0];
    if (!file) throw new Error("Please select a file");
    const form = new FormData();
    form.append("tenant_id", tenant_id);
    form.append("file", file);
    const data = await request("/ingest/file", {
      method: "POST",
      body: form,
    });
    log(data);
  } catch (e) { log(e.message); }
});

document.getElementById("queryBtn").addEventListener("click", async () => {
  try {
    const tenant_id = tenantSelectQuery.value;
    const query = document.getElementById("queryInput").value.trim();
    const top_k = Number(document.getElementById("topK").value || "5");
    const data = await request("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_id, query, top_k }),
    });
    log(data);
  } catch (e) { log(e.message); }
});

refreshTenants().catch((e) => log(e.message));
