const $ = (id) => document.getElementById(id);
let state = { slug: "", data: null };

function tabTo(name) {
  document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === name));
  ["bible", "plot", "canon", "scenes"].forEach((t) => $(`tab-${t}`).classList.toggle("hidden", t !== name));
}

document.querySelectorAll(".tabs button").forEach((b) => b.addEventListener("click", () => tabTo(b.dataset.tab)));

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) {
    let msg = await res.text();
    try { msg = JSON.parse(msg).detail || msg; } catch { /* keep */ }
    throw new Error(msg);
  }
  return res.json();
}

async function refreshProjects(selectSlug) {
  const list = await api("/api/projects");
  const sel = $("projectSelect");
  sel.innerHTML = list.map((p) => `<option value="${p.slug}">${p.title}</option>`).join("");
  if (selectSlug) sel.value = selectSlug;
  if (sel.value) await loadProject(sel.value);
}

async function loadProject(slug) {
  state.slug = slug;
  state.data = await api(`/api/projects/${slug}`);
  renderAll();
}

function renderAll() {
  const d = state.data;
  $("metaTitle").value = d.meta.title || "";
  $("metaGenre").value = d.meta.genre || "";
  $("metaLogline").value = d.meta.logline || "";
  $("chars").innerHTML = (d.characters || []).map(charForm).join("");
  $("premise").value = d.plot.premise || "";
  $("stakes").value = d.plot.stakes || "";
  $("threads").value = (d.plot.open_threads || []).join("\n");
  $("acts").innerHTML = (d.plot.acts || []).map(actForm).join("");
  renderCanon(d.canon);
  renderScenes(d.scenes || []);
}

function charForm(c, i) {
  const v = c.voice || {};
  return `<article class="char" data-i="${i}">
    <h3>${c.name || "未命名"} <small>${c.id}</small></h3>
    <div class="grid2">
      <input data-k="id" value="${esc(c.id)}" placeholder="id" />
      <input data-k="name" value="${esc(c.name)}" placeholder="姓名" />
      <input data-k="age" value="${esc(c.age)}" placeholder="年龄" />
      <input data-k="role" value="${esc(c.role)}" placeholder="剧作功能" />
    </div>
    <textarea data-k="identity" rows="2" placeholder="身份">${esc(c.identity)}</textarea>
    <input data-k="locked_traits" value="${esc((c.locked_traits||[]).join(" / "))}" placeholder="锁定人设，用 / 分隔" />
    <input data-k="values" value="${esc((c.values||[]).join(" / "))}" placeholder="价值观" />
    <input data-k="fears" value="${esc((c.fears||[]).join(" / "))}" placeholder="恐惧" />
    <input data-k="desires" value="${esc((c.desires||[]).join(" / "))}" placeholder="欲望" />
    <input data-k="limits" value="${esc((c.limits||[]).join(" / "))}" placeholder="能力边界" />
    <input data-k="verbal" value="${esc((v.verbal_tics||[]).join(" / "))}" placeholder="口头禅" />
    <input data-k="never" value="${esc((v.never_says||[]).join(" / "))}" placeholder="绝不会说" />
    <textarea data-k="register" rows="2" placeholder="语域/说话方式">${esc(v.register||"")}</textarea>
  </article>`;
}

function actForm(a, ai) {
  const beats = (a.beats || []).map((b, bi) => `<div class="beat">
    <div class="grid2">
      <input data-act="${ai}" data-beat="${bi}" data-k="id" value="${esc(b.id)}" placeholder="节拍id" />
      <select data-act="${ai}" data-beat="${bi}" data-k="status">
        ${["pending","in_progress","done"].map((s)=>`<option ${s===b.status?"selected":""}>${s}</option>`).join("")}
      </select>
    </div>
    <input data-act="${ai}" data-beat="${bi}" data-k="title" value="${esc(b.title)}" placeholder="节拍标题" />
    <textarea data-act="${ai}" data-beat="${bi}" data-k="description" rows="2">${esc(b.description)}</textarea>
  </div>`).join("");
  return `<div class="act" data-ai="${ai}">
    <div class="grid2">
      <input data-act="${ai}" data-k="actId" value="${esc(a.id)}" />
      <input data-act="${ai}" data-k="actTitle" value="${esc(a.title)}" />
    </div>
    ${beats}
    <button type="button" class="ghost add-beat" data-ai="${ai}">加节拍</button>
  </div>`;
}

function renderCanon(canon) {
  const facts = (canon.facts || []).map((f) => `<li>${f.locked ? "锁定" : "开放"} · ${f.category} · ${f.text}</li>`).join("") || "<li>暂无</li>";
  const tl = (canon.timeline || []).map((t) => `<li>${t.when} — ${t.event}</li>`).join("") || "<li>暂无</li>";
  $("canonView").innerHTML = `<h3>事实</h3><ul>${facts}</ul><h3>时间线</h3><ul>${tl}</ul>`;
}

function renderScenes(scenes) {
  $("sceneList").innerHTML = scenes.map((s) => `<article class="scene-item">
    <strong>${s.id} ${s.title}</strong> <em>${s.status}</em>
    <p>${esc(s.summary||"")}</p>
    <pre>${esc(s.content||"")}</pre>
  </article>`).join("") || "<p class='hint'>还没有场次</p>";
}

function splitList(v) {
  return v.split(/[/，,;；\n]/).map((x) => x.trim()).filter(Boolean);
}

function collectCharacters() {
  return [...document.querySelectorAll(".char")].map((el) => {
    const g = (k) => el.querySelector(`[data-k="${k}"]`)?.value || "";
    return {
      id: g("id"),
      name: g("name"),
      age: g("age"),
      role: g("role"),
      identity: g("identity"),
      locked_traits: splitList(g("locked_traits")),
      values: splitList(g("values")),
      fears: splitList(g("fears")),
      desires: splitList(g("desires")),
      limits: splitList(g("limits")),
      capabilities: [],
      relationships: {},
      current_state: {},
      voice: {
        register: g("register"),
        vocabulary: "",
        verbal_tics: splitList(g("verbal")),
        never_says: splitList(g("never")),
        sample_lines: [],
      },
    };
  });
}

function collectPlot() {
  const acts = [];
  document.querySelectorAll(".act").forEach((actEl, ai) => {
    const beats = [];
    actEl.querySelectorAll(".beat").forEach((beatEl) => {
      const val = (k) => beatEl.querySelector(`[data-k="${k}"]`)?.value || "";
      beats.push({
        id: val("id"),
        title: val("title"),
        description: val("description"),
        status: val("status"),
        planted: [],
        payoff: [],
      });
    });
    acts.push({
      id: actEl.querySelector('[data-k="actId"]').value,
      title: actEl.querySelector('[data-k="actTitle"]').value,
      beats,
    });
  });
  return {
    premise: $("premise").value,
    stakes: $("stakes").value,
    open_threads: $("threads").value.split("\n").map((x) => x.trim()).filter(Boolean),
    acts,
  };
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

$("projectSelect").addEventListener("change", (e) => loadProject(e.target.value));
$("newProjectBtn").addEventListener("click", async () => {
  const title = prompt("剧名？", "未命名剧本");
  if (!title) return;
  const p = await api("/api/projects", { method: "POST", body: { title, logline: "", genre: "都市剧" } });
  await refreshProjects(p.slug);
});
$("saveMetaBtn").addEventListener("click", async () => {
  await api(`/api/projects/${state.slug}/meta`, {
    method: "PATCH",
    body: { title: $("metaTitle").value, genre: $("metaGenre").value, logline: $("metaLogline").value },
  });
  $("status").textContent = "剧作信息已保存";
});
$("saveCharsBtn").addEventListener("click", async () => {
  await api(`/api/projects/${state.slug}/characters`, { method: "PUT", body: collectCharacters() });
  await loadProject(state.slug);
  $("status").textContent = "人设已保存";
});
$("addCharBtn").addEventListener("click", () => {
  state.data.characters.push({
    id: `c${state.data.characters.length + 1}`,
    name: "新角色",
    age: "",
    role: "",
    identity: "",
    locked_traits: [],
    values: [],
    fears: [],
    desires: [],
    limits: [],
    voice: { register: "", verbal_tics: [], never_says: [], sample_lines: [], vocabulary: "" },
    current_state: {},
    relationships: {},
    capabilities: [],
  });
  renderAll();
});
$("savePlotBtn").addEventListener("click", async () => {
  await api(`/api/projects/${state.slug}/plot`, { method: "PUT", body: collectPlot() });
  await loadProject(state.slug);
  $("status").textContent = "大纲已保存";
});
$("addActBtn").addEventListener("click", () => {
  const n = (state.data.plot.acts || []).length + 1;
  state.data.plot.acts = state.data.plot.acts || [];
  state.data.plot.acts.push({
    id: `A${n}`,
    title: `第${n}幕`,
    beats: [{ id: `A${n}B1`, title: "新节拍", description: "", status: "pending", planted: [], payoff: [] }],
  });
  renderAll();
  tabTo("plot");
});
document.body.addEventListener("click", (e) => {
  if (e.target.classList.contains("add-beat")) {
    const ai = Number(e.target.dataset.ai);
    const act = state.data.plot.acts[ai];
    const n = act.beats.length + 1;
    act.beats.push({ id: `${act.id}B${n}`, title: "新节拍", description: "", status: "pending", planted: [], payoff: [] });
    renderAll();
    tabTo("plot");
  }
});

$("generateBtn").addEventListener("click", async () => {
  $("status").textContent = "正在跑工作流：规划 → 写作 → 校验 → 改写…";
  $("result").innerHTML = "";
  $("generateBtn").disabled = true;
  try {
    const out = await api(`/api/projects/${state.slug}/generate`, {
      method: "POST",
      body: { extra_instruction: $("extra").value, auto_save: $("autoSave").checked },
    });
    const p = out.persona, c = out.continuity;
    const issues = [...(p.issues || []), ...(c.issues || [])]
      .map((i) => `<div class="issue ${i.severity}">[${i.severity}] ${i.agent}: ${esc(i.detail)}</div>`)
      .join("");
    $("result").innerHTML = `<p class="${p.passed && c.passed ? "ok" : "bad"}">人设 ${p.passed ? "通过" : "未过"}（${p.score}）· 贯通 ${c.passed ? "通过" : "未过"}（${c.score}）· 改写 ${out.rewrite_rounds} 轮</p>
      ${issues}
      <h3>${esc(out.scene.id)} ${esc(out.scene.title)}</h3>
      <div>${esc(out.scene.content)}</div>`;
    $("status").textContent = out.auto_saved ? "已写入项目" : "未保存";
    await loadProject(state.slug);
  } catch (err) {
    $("status").innerHTML = `<span class="bad">${esc(err.message)}</span>`;
  } finally {
    $("generateBtn").disabled = false;
  }
});

refreshProjects();
