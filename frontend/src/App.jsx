import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Activity, Bot, Download, Play, Radio, Server, ShieldCheck } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import "./style.css";

const API = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const defaultCommand = "On Floor 6, Robot 1 must collect the blue box from the office. Robot 2 must collect the coffee mug from the kitchen. Robot 3 must inspect the corridor. All robots must avoid blocking each other and deliver or report to the storage room. Use the most efficient allocation based on distance, capability and battery level.";

function Panel({ title, icon, children, className = "" }) {
  return <section className={`panel ${className}`}><div className="panel-title">{icon}{title}</div>{children}</section>;
}

function CodeBox({ value }) {
  return <pre className="codebox">{typeof value === "string" ? value : JSON.stringify(value, null, 2)}</pre>;
}

function download(name, value) {
  const blob = new Blob([typeof value === "string" ? value : JSON.stringify(value, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

function App() {
  const [command, setCommand] = useState(defaultCommand);
  const [scenario, setScenario] = useState("Floor 6 default demo");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState(null);

  async function refreshStatus() {
    const res = await fetch(`${API}/api/status`);
    setStatus(await res.json());
  }

  async function runPipeline() {
    setRunning(true);
    try {
      await refreshStatus();
      const res = await fetch(`${API}/api/run-full-pipeline`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
      });
      setResult(await res.json());
    } finally {
      setRunning(false);
    }
  }

  const chartData = useMemo(() => {
    const allocation = result?.allocation?.allocation || [];
    return allocation.map((row) => ({ task: row.task_id, cost: row.cost || 0, utility: row.utility || 0 }));
  }, [result]);

  return <main>
    <header className="topbar">
      <div>
        <h1>Open LaMMA-R</h1>
        <p>Local-LLM, PDDL, Fast Downward and MILP coordination for Floor 6 LIMO demos</p>
      </div>
      <button onClick={runPipeline} disabled={running}><Play size={18}/>{running ? "Running" : "Run Pipeline"}</button>
    </header>

    <div className="grid">
      <Panel title="Mission Command" icon={<Bot size={18}/>} className="wide">
        <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
          <option>Floor 6 default demo</option>
          <option>warehouse demo</option>
          <option>custom scenario</option>
        </select>
        <textarea value={command} onChange={(e) => setCommand(e.target.value)} />
      </Panel>

      <Panel title="Local LLM Status" icon={<Server size={18}/>}>
        <button className="secondary" onClick={refreshStatus}><Radio size={16}/>Refresh</button>
        <CodeBox value={status || { status: "not checked" }} />
      </Panel>

      <Panel title="Parsed JSON" icon={<ShieldCheck size={18}/>}>
        <button className="secondary" onClick={() => download("mission.json", result?.mission || {})}><Download size={16}/>JSON</button>
        <CodeBox value={result?.mission || {}} />
      </Panel>

      <Panel title="Generated PDDL" icon={<Activity size={18}/>}>
        <button className="secondary" onClick={() => download("problem.pddl", result?.pddl || "")}><Download size={16}/>PDDL</button>
        <CodeBox value={result?.pddl || ""} />
      </Panel>

      <Panel title="Fast Downward Plan" icon={<Activity size={18}/>}>
        <button className="secondary" onClick={() => download("plan.json", result?.plan || {})}><Download size={16}/>Plan</button>
        <CodeBox value={result?.plan || {}} />
      </Panel>

      <Panel title="MILP Allocation" icon={<Bot size={18}/>}>
        <button className="secondary" onClick={() => download("allocation.json", result?.allocation || {})}><Download size={16}/>Allocation</button>
        <CodeBox value={result?.allocation || {}} />
      </Panel>

      <Panel title="Metrics Dashboard" icon={<Activity size={18}/>} className="wide">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="task" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="cost" fill="#2563eb" />
            <Bar dataKey="utility" fill="#16a34a" />
          </BarChart>
        </ResponsiveContainer>
      </Panel>

      <Panel title="Execution Log" icon={<Activity size={18}/>} className="wide">
        <CodeBox value={result?.execution?.logs || []} />
      </Panel>

      <Panel title="Demo Recording" icon={<Download size={18}/>} className="wide">
        <p className="plain">Use scripts/record_demo.sh to capture the GUI, simulator window, or full desktop. Recommended submission format: H.264 MP4, 720p, compressed below 50 MB where required.</p>
      </Panel>
    </div>
  </main>;
}

createRoot(document.getElementById("root")).render(<App />);

