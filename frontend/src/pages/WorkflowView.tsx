import React, { useState } from 'react';
import { 
  GitBranch, 
  Workflow, 
  Zap, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Terminal, 
  ShieldCheck, 
  Copy, 
  ExternalLink,
  Cpu,
  Layers,
  ArrowRight
} from 'lucide-react';
import { CaseRecord } from '../types';

interface WorkflowViewProps {
  cases: CaseRecord[];
}

export const WorkflowView: React.FC<WorkflowViewProps> = ({ cases }) => {
  const [activeTab, setActiveTab] = useState<'diagram' | 'executions' | 'webhook'>('diagram');

  // Filter cases that went through n8n
  const executedCases = cases.filter(c => c.n8n_dispatch);

  return (
    <div className="space-y-8 py-6 max-w-7xl mx-auto">
      {/* Title */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-[var(--red-surface)] text-[var(--red-foreground)] text-xs font-semibold mb-2">
            <Workflow className="w-3.5 h-3.5" />
            <span>n8n Core Orchestration Engine</span>
          </div>
          <h1 className="text-3xl font-extrabold text-[var(--foreground)]">Automation & Workflow Architecture</h1>
          <p className="text-sm text-[var(--foreground-muted)]">
            End-to-End Implementation: Webhook Ingestion, Idempotency Checks, Conditional Branching, & Execution History
          </p>
        </div>

        {/* Tab selection */}
        <div className="flex bg-[var(--surface-muted)]/70 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('diagram')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'diagram' ? 'bg-[var(--surface)] text-[var(--foreground)] shadow-sm' : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)]'
            }`}
          >
            Workflow Graph
          </button>
          <button
            onClick={() => setActiveTab('executions')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'executions' ? 'bg-[var(--surface)] text-[var(--foreground)] shadow-sm' : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)]'
            }`}
          >
            Live Execution Runs ({executedCases.length})
          </button>
          <button
            onClick={() => setActiveTab('webhook')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'webhook' ? 'bg-[var(--surface)] text-[var(--foreground)] shadow-sm' : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)]'
            }`}
          >
            Webhook Payload
          </button>
        </div>
      </div>

      {activeTab === 'diagram' && (
        <div className="space-y-6">
          {/* Interactive visual workflow diagram  */}
          <div className="theme-inverse bg-slate-950 rounded-3xl p-8 border border-slate-800 text-white shadow-2xl relative overflow-hidden">
            <div className="text-center max-w-2xl mx-auto mb-10">
              <span className="text-xs font-mono text-red-400 tracking-wider uppercase">n8n Execution Topology</span>
              <h3 className="text-2xl font-bold mt-1">Autonomous Dispatch & Guardrails</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative items-center">
              {/* Node 1 */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-700 text-center space-y-2">
                <div className="w-10 h-10 rounded-xl bg-red-600/20 text-red-400 border border-red-500/30 flex items-center justify-center mx-auto">
                  <Zap className="w-5 h-5" />
                </div>
                <div className="font-bold text-sm">Webhook Trigger</div>
                <p className="text-[11px] text-[var(--foreground-muted)]">
                  FastAPI emits POST /case-events with unique Idempotency Key
                </p>
                <div className="pt-1">
                  <span className="px-2 py-0.5 rounded text-[10px] bg-red-950 text-red-300 font-mono">
                    POST /case-events
                  </span>
                </div>
              </div>

              {/* Node 2 */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-700 text-center space-y-2">
                <div className="w-10 h-10 rounded-xl bg-amber-600/20 text-amber-400 border border-amber-500/30 flex items-center justify-center mx-auto">
                  <GitBranch className="w-5 h-5" />
                </div>
                <div className="font-bold text-sm">IF Check: Duplicate?</div>
                <p className="text-[11px] text-[var(--foreground-muted)]">
                  Evaluates hybrid score & confidence threshold (&ge; 0.58)
                </p>
                <div className="pt-1 flex justify-center space-x-2 text-[10px] font-mono">
                  <span className="text-amber-400">Yes &rarr; Hold</span>
                  <span className="text-emerald-400">No &rarr; Assign</span>
                </div>
              </div>

              {/* Node 3 - Two Branches */}
              <div className="space-y-4">
                {/* Branch YES */}
                <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-700/50 text-left space-y-1">
                  <div className="flex items-center space-x-1.5 text-amber-300 text-xs font-bold">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Branch A: Hold for Review</span>
                  </div>
                  <p className="text-[11px] text-slate-300">
                    Case held for human triage. Evidence recorded. Never auto-merged.
                  </p>
                </div>

                {/* Branch NO */}
                <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-700/50 text-left space-y-1">
                  <div className="flex items-center space-x-1.5 text-emerald-300 text-xs font-bold">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Branch B: Category Route</span>
                  </div>
                  <p className="text-[11px] text-slate-300">
                    Direct assignment to Plumbing, Electrical, HVAC or Carpentry.
                  </p>
                </div>
              </div>

              {/* Node 4 */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-700 text-center space-y-2">
                <div className="w-10 h-10 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center mx-auto">
                  <Terminal className="w-5 h-5" />
                </div>
                <div className="font-bold text-sm">Audit & Execution Log</div>
                <p className="text-[11px] text-[var(--foreground-muted)]">
                  Writes immutable status update and execution ID to case history.
                </p>
                <div className="pt-1">
                  <span className="px-2 py-0.5 rounded text-[10px] bg-blue-950 text-blue-300 font-mono">
                    status: 200 OK
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Core Guarantees from PPT Slide 3 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-2">
              <div className="flex items-center space-x-2 font-bold text-[var(--foreground)]">
                <ShieldCheck className="w-5 h-5 text-red-600" />
                <span>Idempotency Safeguard</span>
              </div>
              <p className="text-xs text-[var(--foreground-muted)]">
                Every webhook event carries an idempotency key (idemp_&#123;case_id&#125;). Prevents repeated network dispatches or duplicate team notifications during retries.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-2">
              <div className="flex items-center space-x-2 font-bold text-[var(--foreground)]">
                <GitBranch className="w-5 h-5 text-red-600" />
                <span>Zero Silent Auto-Merges</span>
              </div>
              <p className="text-xs text-[var(--foreground-muted)]">
                Suspected duplicates are surfaced with mathematical cosine and location evidence. A human facility manager must confirm or reject the merge.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-2">
              <div className="flex items-center space-x-2 font-bold text-[var(--foreground)]">
                <Clock className="w-5 h-5 text-red-600" />
                <span>Auditable Execution History</span>
              </div>
              <p className="text-xs text-[var(--foreground-muted)]">
                Every state transition generates a timestamped log entry with the n8n execution ID and target department for administrative accountability.
              </p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'executions' && (
        <div className="bg-[var(--surface)] rounded-2xl border border-[var(--border)] shadow-sm p-6 space-y-4">
          <h3 className="text-base font-bold text-[var(--foreground)]">Live n8n Execution History Table</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[var(--surface-muted)] border-b border-[var(--border)] text-[var(--foreground-muted)] font-semibold uppercase text-[10px]">
                <tr>
                  <th className="px-3.5 py-3">Execution ID</th>
                  <th className="px-3.5 py-3">Case ID</th>
                  <th className="px-3.5 py-3">Workflow Branch</th>
                  <th className="px-3.5 py-3">Assigned Department</th>
                  <th className="px-3.5 py-3">Idempotency Key</th>
                  <th className="px-3.5 py-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)]">
                {executedCases.map((c) => (
                  <tr key={c.id} className="hover:bg-[var(--surface-muted)]/70">
                    <td className="px-3.5 py-3 font-mono font-semibold text-[var(--red-foreground)]">
                      {c.n8n_dispatch?.n8n_execution_id}
                    </td>
                    <td className="px-3.5 py-3 font-bold text-[var(--foreground)]">
                      {c.case_number}
                    </td>
                    <td className="px-3.5 py-3">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                        c.n8n_dispatch?.workflow_branch === 'duplicate_hold'
                          ? 'bg-[var(--amber-surface)] text-[var(--amber-foreground)]'
                          : 'bg-[var(--emerald-surface)] text-[var(--emerald-foreground)]'
                      }`}>
                        {c.n8n_dispatch?.workflow_branch}
                      </span>
                    </td>
                    <td className="px-3.5 py-3 text-[var(--foreground)]">
                      {c.assigned_team}
                    </td>
                    <td className="px-3.5 py-3 font-mono text-[11px] text-[var(--foreground-muted)]">
                      {c.n8n_dispatch?.idempotency_key}
                    </td>
                    <td className="px-3.5 py-3 text-[var(--foreground-muted)] whitespace-nowrap">
                      {new Date(c.n8n_dispatch?.timestamp || '').toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'webhook' && (
        <div className="theme-inverse bg-slate-900 rounded-2xl p-6 border border-slate-800 text-white font-mono text-xs space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-slate-800">
            <span className="text-[var(--foreground-muted)]">Sample FastAPI &rarr; n8n Webhook Payload Schema</span>
            <span className="text-emerald-400 font-semibold">Content-Type: application/json</span>
          </div>
          <pre className="overflow-x-auto text-slate-300 leading-relaxed">
{`{
  "event_id": "evt_4b8f09a12c",
  "idempotency_key": "idemp_case_b_leak_001_water_leak",
  "case_id": "case_b_leak_001",
  "case_number": "RES-2026-101",
  "issue_type": "water_leak",
  "building_block": "Block B",
  "workflow_branch": "direct_assignment",
  "assigned_team": "Plumbing & Water Infrastructure Team",
  "is_held_as_duplicate": false,
  "confidence": 0.96,
  "detected_urgency": "high"
}`}
          </pre>
        </div>
      )}
    </div>
  );
};
