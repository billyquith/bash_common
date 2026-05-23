const state = {
  commands: [],
  selectedCommand: null,
  selectedSubcommand: null,
  configValues: {},
  activeJobId: null,
  pollTimer: null,
};

const el = (id) => document.getElementById(id);

function optionLabel(option) {
  return option.label || option.name.replaceAll("_", " ");
}

function fieldInput(field, namePrefix) {
  const id = `${namePrefix}-${field.name}`;
  const wrapper = document.createElement("label");
  wrapper.className = "field";
  wrapper.htmlFor = id;

  const title = document.createElement("span");
  title.textContent = field.label || field.name.replaceAll("_", " ");
  wrapper.appendChild(title);

  if (field.kind === "boolean") {
    const row = document.createElement("div");
    row.className = "check-row";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.id = id;
    input.name = field.name;
    input.dataset.kind = field.kind;
    row.appendChild(input);
    const text = document.createElement("span");
    text.textContent = optionLabel(field);
    row.appendChild(text);
    wrapper.appendChild(row);
    return wrapper;
  }

  let input;
  if (field.kind === "path-list") {
    input = document.createElement("textarea");
    input.rows = 4;
    input.placeholder = "One path per line";
  } else if (field.kind === "choice") {
    input = document.createElement("select");
    const blank = document.createElement("option");
    blank.value = "";
    blank.textContent = "Use default";
    input.appendChild(blank);
    for (const choice of field.choices || []) {
      const option = document.createElement("option");
      option.value = choice;
      option.textContent = choice;
      input.appendChild(option);
    }
  } else {
    input = document.createElement("input");
    input.type = field.kind === "integer" ? "number" : "text";
    input.spellcheck = false;
  }

  input.id = id;
  input.name = field.name;
  input.dataset.kind = field.kind || "string";
  if (field.required) input.required = true;
  if (field.config && state.configValues[field.config]) {
    input.value = state.configValues[field.config];
  }
  wrapper.appendChild(input);
  return wrapper;
}

function renderCommandList() {
  const list = el("command-list");
  list.innerHTML = "";
  for (const command of state.commands) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = command.name;
    button.className = command === state.selectedCommand ? "active" : "";
    button.addEventListener("click", () => {
      state.selectedCommand = command;
      state.selectedSubcommand = command.subcommands?.[0] || null;
      render();
    });
    list.appendChild(button);
  }
}

function renderSubcommands() {
  const select = el("subcommand-select");
  select.innerHTML = "";
  const command = state.selectedCommand;
  if (!command) return;
  for (const subcommand of command.subcommands || []) {
    const option = document.createElement("option");
    option.value = subcommand.name;
    option.textContent = subcommand.name;
    select.appendChild(option);
  }
  select.value = state.selectedSubcommand?.name || "";
}

function renderForm() {
  const command = state.selectedCommand;
  const subcommand = state.selectedSubcommand;
  const form = el("command-form");
  form.innerHTML = "";
  el("command-title").textContent = command ? command.name : "Command";
  el("command-summary").textContent = subcommand?.summary || command?.summary || "";
  if (!command || !subcommand) return;

  const fields = document.createElement("div");
  fields.className = "fields";
  for (const option of subcommand.options || []) {
    fields.appendChild(fieldInput(option, "option"));
  }
  for (const arg of subcommand.args || []) {
    fields.appendChild(fieldInput(arg, "arg"));
  }

  const run = document.createElement("button");
  run.type = "submit";
  run.className = "primary";
  run.textContent = `Run ${command.name} ${subcommand.name}`;

  form.appendChild(fields);
  form.appendChild(run);
}

function renderConfig(config) {
  const output = el("config-output");
  const parts = [];
  if (config?.files?.stdout) parts.push(config.files.stdout.trim());
  if (config?.effective?.stdout) parts.push(config.effective.stdout.trim());
  output.textContent = parts.filter(Boolean).join("\n\n") || "No config output.";
}

function render() {
  renderCommandList();
  renderSubcommands();
  renderForm();
}

async function loadState() {
  const cwd = encodeURIComponent(el("cwd").value || "");
  const response = await fetch(`/api/state?cwd=${cwd}`);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Unable to load state.");
  state.commands = data.commands || [];
  state.configValues = data.config?.values || {};
  el("cwd").value = data.cwd;
  renderConfig(data.config);
  if (!state.selectedCommand && state.commands.length) {
    state.selectedCommand = state.commands[0];
    state.selectedSubcommand = state.selectedCommand.subcommands?.[0] || null;
  }
  render();
}

function formValues(prefix) {
  const values = {};
  for (const input of el("command-form").querySelectorAll(`[id^="${prefix}-"]`)) {
    if (input.type === "checkbox") {
      values[input.name] = input.checked;
    } else {
      values[input.name] = input.value;
    }
  }
  return values;
}

function showJob(job) {
  const elapsed = Number(job.elapsed || 0).toFixed(2);
  const code = job.returncode === null || job.returncode === undefined ? "-" : job.returncode;
  el("job-meta").textContent = `${job.argv.join(" ")} | ${job.status} | exit ${code} | ${elapsed}s`;
  el("stdout").textContent = job.stdout || "";
  el("stderr").textContent = job.stderr || "";
  el("cancel-job").hidden = job.status !== "running" && job.status !== "cancelling";

  const artifacts = el("artifacts");
  artifacts.innerHTML = "";
  for (const artifact of job.artifacts || []) {
    const item = document.createElement("div");
    item.className = "artifact";
    const link = document.createElement("a");
    link.href = artifact.url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = artifact.name;
    item.appendChild(link);
    if (artifact.mime?.startsWith("image/")) {
      const image = document.createElement("img");
      image.src = artifact.url;
      image.alt = artifact.name;
      item.appendChild(image);
    }
    artifacts.appendChild(item);
  }
}

function stopPolling() {
  if (state.pollTimer) {
    clearTimeout(state.pollTimer);
    state.pollTimer = null;
  }
}

async function pollJob(jobId) {
  const response = await fetch(`/api/jobs/${jobId}`);
  const data = await response.json();
  if (!response.ok) {
    el("job-meta").textContent = "Error";
    el("stderr").textContent = data.error || "Unable to load job.";
    stopPolling();
    return;
  }
  showJob(data.job);
  if (data.job.status === "running" || data.job.status === "cancelling") {
    state.pollTimer = setTimeout(() => pollJob(jobId), 750);
  } else {
    state.activeJobId = null;
    stopPolling();
  }
}

async function runStructured(event) {
  event.preventDefault();
  const command = state.selectedCommand;
  const subcommand = state.selectedSubcommand;
  if (!command || !subcommand) return;
  await runRequest({
    mode: "structured",
    cwd: el("cwd").value,
    command: command.name,
    subcommand: subcommand.name,
    options: formValues("option"),
    args: formValues("arg"),
  });
}

async function runRaw(event) {
  event.preventDefault();
  await runRequest({
    mode: "raw",
    cwd: el("cwd").value,
    command_line: el("raw-command").value,
  });
}

async function runRequest(payload) {
  stopPolling();
  el("job-meta").textContent = "Starting...";
  el("stdout").textContent = "";
  el("stderr").textContent = "";
  el("artifacts").innerHTML = "";
  const response = await fetch("/api/run", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    el("job-meta").textContent = "Error";
    el("stderr").textContent = data.error || "Command failed before execution.";
    el("cancel-job").hidden = true;
    return;
  }
  state.activeJobId = data.job.id;
  showJob(data.job);
  await pollJob(data.job.id);
}

async function cancelActiveJob() {
  if (!state.activeJobId) return;
  const response = await fetch(`/api/jobs/${state.activeJobId}/cancel`, {method: "POST"});
  const data = await response.json();
  if (response.ok) {
    showJob(data.job);
  }
}

el("subcommand-select").addEventListener("change", (event) => {
  const command = state.selectedCommand;
  state.selectedSubcommand = (command.subcommands || []).find(
    (item) => item.name === event.target.value
  );
  render();
});

el("command-form").addEventListener("submit", runStructured);
el("raw-form").addEventListener("submit", runRaw);
el("cancel-job").addEventListener("click", cancelActiveJob);
el("cwd-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadState();
});

loadState().catch((error) => {
  el("stderr").textContent = error.message;
});
