import React from 'react';
import { 
  ArrowRight, 
  Sparkles, 
  GitBranch, 
  Cpu, 
  ShieldCheck, 
  CheckCircle, 
  Users, 
  TrendingUp, 
  AlertCircle,
  CopyCheck,
  RefreshCw
} from 'lucide-react';

interface LandingPageProps {
  onStartDemo: (demoType: 'unique' | 'paraphrased') => void;
  onNavigateToTab: (tab: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStartDemo, onNavigateToTab }) => {
  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="theme-inverse relative overflow-hidden rounded-3xl bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white p-8 md:p-14 border border-slate-800 shadow-2xl">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-red-600/15 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 rounded-full bg-rose-600/10 blur-3xl pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-red-950/80 border border-red-700/60 text-red-300 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-red-400" />
            <span>Built for n8n Primary Track • HackShift_404</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
            Turns Unstructured Complaints into <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-rose-300">Auditable Assignments</span>
          </h1>

          <p className="text-lg md:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Free-form student complaints cause severe duplication, unclear categories, and slow triage. ResolveAI extracts structured JSON with Gemma, runs hybrid duplicate detection, and orchestrates team dispatch via n8n.
          </p>

          {/* Quick Interactive Demo Trigger Cards */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => onStartDemo('unique')}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-red-600 hover:bg-red-700 font-semibold text-white shadow-lg shadow-red-700/30 flex items-center justify-center space-x-2 transition-all transform hover:-translate-y-0.5"
            >
              <span>Test Case 1: Unique Complaint</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onStartDemo('paraphrased')}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 font-semibold text-slate-200 border border-slate-700 flex items-center justify-center space-x-2 transition-all"
            >
              <span>Test Case 2: Paraphrased Duplicate</span>
              <CopyCheck className="w-4 h-4 text-amber-400" />
            </button>
          </div>

          {/* Scope statement from PPT */}
          <div className="pt-2">
            <p className="text-xs text-[var(--foreground-muted)] italic">
              Users: Students • Maintenance Staff • Facility Admins | Scope: Campus simulation with fictional benchmark data
            </p>
          </div>
        </div>
      </section>

      {/* Problem vs Solution (Slide 2) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="p-8 rounded-2xl bg-[var(--surface)] border border-[var(--red-border)] shadow-sm relative overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-[var(--red-surface)] text-[var(--red-foreground)] flex items-center justify-center mb-5">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-[var(--foreground)] mb-2">The Problem</h3>
            <p className="text-[var(--foreground-muted)] leading-relaxed">
              Campus students submit free-form text with messy descriptions (e.g. "water dripping", "pipe leaking near stairs"). These create duplicate work orders, misassigned departments, and inconsistent triage. Maintenance fixes get slow and untracked.
            </p>
            <ul className="mt-4 space-y-2 text-sm text-[var(--foreground-muted)]">
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                <span>Duplicate work orders sent to same physical site</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                <span>Lack of structured category & location extraction</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                <span>No audit trail or automated workflow orchestration</span>
              </li>
            </ul>
          </div>

          <div className="p-8 rounded-2xl bg-[var(--surface)] border border-[var(--emerald-border)] shadow-sm relative overflow-hidden">
            <div className="w-12 h-12 rounded-xl bg-[var(--emerald-surface)] text-[var(--emerald-foreground)] flex items-center justify-center mb-5">
              <CheckCircle className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-[var(--foreground)] mb-2">Our Solution</h3>
            <p className="text-[var(--foreground-muted)] leading-relaxed">
              ResolveAI turns unstructured maintenance complaints into structured, schema-validated JSON, evaluates duplicate candidates using a hybrid formula, and routes verified tickets via n8n automated workflows.
            </p>
            <ul className="mt-4 space-y-2 text-sm text-[var(--foreground-muted)]">
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                <span>Gemma structured extraction for issue type, location & urgency</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                <span>Hybrid check flags duplicates with empirical evidence score</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                <span>n8n routes by category; holds ambiguous cases for human review</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* 4-Step Pipeline (Slide 2 & 3) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl font-bold text-[var(--foreground)]">How It Works</h2>
          <p className="text-[var(--foreground-muted)] mt-2">End-to-end intelligent maintenance lifecycle</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm hover:border-[var(--red-border)] transition-all">
            <div className="w-10 h-10 rounded-lg bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold flex items-center justify-center mb-4">
              1
            </div>
            <h4 className="text-lg font-bold text-[var(--foreground)] mb-1">Submit</h4>
            <p className="text-sm text-[var(--foreground-muted)]">
              Student files a natural text complaint via the portal without needing complex dropdowns.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm hover:border-[var(--red-border)] transition-all">
            <div className="w-10 h-10 rounded-lg bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold flex items-center justify-center mb-4">
              2
            </div>
            <h4 className="text-lg font-bold text-[var(--foreground)] mb-1">Understand</h4>
            <p className="text-sm text-[var(--foreground-muted)]">
              Gemma model extracts schema-validated JSON: category, building block, floor/room, and urgency score.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm hover:border-[var(--red-border)] transition-all">
            <div className="w-10 h-10 rounded-lg bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold flex items-center justify-center mb-4">
              3
            </div>
            <h4 className="text-lg font-bold text-[var(--foreground)] mb-1">Compare</h4>
            <p className="text-sm text-[var(--foreground-muted)]">
              Hybrid check flags duplicate candidates combining embeddings, physical proximity, and time window rules.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm hover:border-[var(--red-border)] transition-all">
            <div className="w-10 h-10 rounded-lg bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold flex items-center justify-center mb-4">
              4
            </div>
            <h4 className="text-lg font-bold text-[var(--foreground)] mb-1">Route</h4>
            <p className="text-sm text-[var(--foreground-muted)]">
              n8n workflow assigns tickets directly or branches to the human approval queue if flagged as duplicate.
            </p>
          </div>
        </div>
      </section>

      {/* Unique Selling Propositions (Slide 5) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="theme-inverse p-8 md:p-12 rounded-3xl bg-slate-900 text-white border border-slate-800">
          <div className="max-w-3xl mb-8">
            <span className="text-red-400 font-semibold text-xs tracking-wider uppercase">Why ResolveAI Wins</span>
            <h2 className="text-3xl font-bold mt-2">Core Technical USPs & Safeguards</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-red-300 flex items-center space-x-2">
                <CopyCheck className="w-5 h-5 text-red-400" />
                <span>Hybrid Duplicates</span>
              </h4>
              <p className="text-sm text-slate-300">
                Embeddings plus location and time rules. Shows a concrete match score, never silently merges.
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-red-300 flex items-center space-x-2">
                <GitBranch className="w-5 h-5 text-red-400" />
                <span>n8n at the Core</span>
              </h4>
              <p className="text-sm text-slate-300">
                Branching, routing, idempotency keys, and execution history that a plain script cannot provide.
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-red-300 flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-red-400" />
                <span>Benchmarked Rigor</span>
              </h4>
              <p className="text-sm text-slate-300">
                Keyword vs embeddings vs hybrid tested on held-out fictional dataset with 0.927 F1-score.
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="text-lg font-semibold text-red-300 flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-red-400" />
                <span>Human-in-the-Loop</span>
              </h4>
              <p className="text-sm text-slate-300">
                Every action is logged in an immutable audit trail. Ambiguous or duplicate tickets wait for human decision.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Team & Track Footer (Slide 1) */}
      <footer className="border-t border-[var(--border)] pt-8 pb-12 max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-[var(--foreground-muted)]">
          <div>
            <p className="font-semibold text-[var(--foreground)]">ResolveAI • HackShift_404</p>
            <p>Anshul Gupta (Team Leader) • Aditya Gupta • Shivam Jhingan</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="px-3 py-1 rounded-full bg-[var(--surface-muted)] font-medium text-[var(--foreground)] border border-[var(--border)]">
              Track: n8n (Primary Sponsored Track)
            </span>
            <span className="text-xs text-[var(--foreground-muted)]">Reforged '26 • BPIT</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
