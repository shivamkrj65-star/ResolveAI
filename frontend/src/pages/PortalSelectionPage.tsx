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
  Layers,
  Workflow,
  BarChart2,
  Lock,
  FilePlus,
  KeyRound,
  Eye,
  FileText
} from 'lucide-react';

interface PortalSelectionPageProps {
  onSelectPortal: (portal: 'user' | 'admin' | 'testing') => void;
  onStartDemo: (demoType: 'unique' | 'paraphrased') => void;
  userRole?: string | null;
}

export const PortalSelectionPage: React.FC<PortalSelectionPageProps> = ({
  onSelectPortal,
  onStartDemo,
  userRole
}) => {
  return (
    <div className="space-y-16 py-6 max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="theme-inverse relative overflow-hidden rounded-3xl bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white p-8 md:p-14 border border-slate-800 shadow-2xl">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-red-600/15 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 rounded-full bg-rose-600/10 blur-3xl pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-red-950/80 border border-red-700/60 text-red-300 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-red-400" />
            <span>Built for n8n Primary Track</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
            Resolve<span className="text-red-500">AI</span> Role-Based Portals
          </h1>

          <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            Intelligent campus maintenance resolution with Gemma NLP, OpenCV image analysis, Cloudinary evidence delivery, n8n automated routing, and Notion workspace synchronization.
          </p>

          <p className="text-xs text-[var(--foreground-muted)] italic">
            Select a specialized portal below to explore the student experience, facility admin triage, or testing & evaluation engine.
          </p>
        </div>
      </section>

      {/* Three Portals Selection Cards */}
      <section className="space-y-4">
        <div className="text-center space-y-1">
          <span className="text-xs font-bold uppercase tracking-wider text-[var(--red-foreground)]">Three-Portals Architecture</span>
          <h2 className="text-2xl md:text-3xl font-extrabold text-[var(--foreground)]">Choose Your Operational Portal</h2>
          <p className="text-xs text-[var(--foreground-muted)]">Tailored views for campus reporters, facility supervisors, and QA evaluators</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          {/* USER PORTAL */}
          <div className="rounded-3xl bg-[var(--surface)] border-2 border-[var(--border)] hover:border-red-400 shadow-lg hover:shadow-xl p-7 flex flex-col justify-between transition-all transform hover:-translate-y-1 group relative overflow-hidden">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-[var(--emerald-surface)] text-[var(--emerald-foreground)] border border-[var(--emerald-border)]">
                  Public Access · No Login
                </span>
                <span className="text-xs font-semibold text-[var(--foreground-muted)]">Students & Staff</span>
              </div>

              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-red-600 to-rose-500 text-white flex items-center justify-center shadow-md shadow-red-500/20 group-hover:scale-105 transition-transform">
                <FilePlus className="w-6 h-6" />
              </div>

              <div>
                <h3 className="text-xl font-black text-[var(--foreground)] group-hover:text-[var(--red-foreground)] transition-colors">
                  User Portal
                </h3>
                <p className="text-xs text-[var(--foreground-muted)] mt-1.5 leading-relaxed">
                  Submit maintenance issues with OpenCV visual validation, Cloudinary photo uploads, and track your complaints live.
                </p>
              </div>

              <ul className="space-y-2 text-xs text-[var(--foreground-muted)] pt-2 border-t border-[var(--border)]">
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-600" />
                  <span>Free-form issue submission without rigid dropdowns</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-600" />
                  <span>OpenCV blur & integrity checks on uploaded images</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-600" />
                  <span>Cloudinary evidence delivery & live ticket tracking</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-600" />
                  <span>Gemma NLP category & location extraction</span>
                </li>
              </ul>
            </div>

            <div className="pt-6">
              <button
                onClick={() => onSelectPortal('user')}
                className="w-full py-3 px-4 rounded-xl bg-red-700 hover:bg-red-800 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-md shadow-red-700/20 transition-all"
              >
                <span>Enter User Portal</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* ADMIN PORTAL */}
          <div className="rounded-3xl bg-[var(--surface)] border-2 border-[var(--border)] hover:border-slate-800 shadow-lg hover:shadow-xl p-7 flex flex-col justify-between transition-all transform hover:-translate-y-1 group relative overflow-hidden">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-slate-900 text-white flex items-center space-x-1">
                  <Lock className="w-3 h-3 text-red-400" />
                  <span>Protected · Admin Role</span>
                </span>
                <span className="text-xs font-semibold text-[var(--foreground-muted)]">Facility Supervisors</span>
              </div>

              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-slate-900 to-slate-800 text-white flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
                <Layers className="w-6 h-6 text-red-400" />
              </div>

              <div>
                <h3 className="text-xl font-black text-[var(--foreground)] group-hover:text-[var(--red-foreground)] transition-colors">
                  Admin Portal
                </h3>
                <p className="text-xs text-[var(--foreground-muted)] mt-1.5 leading-relaxed">
                  Authoritative triage queue, duplicate review & merge, priority overrides, and immutable audit timeline.
                </p>
              </div>

              <ul className="space-y-2 text-xs text-[var(--foreground-muted)] pt-2 border-t border-[var(--border)]">
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span>Live ticket queue with search, category & location filters</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span>Hybrid duplicate evaluation with match scores</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span>Human-in-the-loop review for duplicate merging</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span>Priority calibration & department reassignments</span>
                </li>
              </ul>

              <div className="p-2.5 rounded-xl bg-[var(--surface-muted)] border border-[var(--border)] text-[11px] font-mono text-[var(--foreground-muted)] space-y-0.5">
                <span className="text-[10px] uppercase font-bold text-[var(--foreground-muted)] block font-sans">Demo Credentials:</span>
                <div>User: <span className="font-bold text-[var(--foreground)]">admin_resolve</span></div>
                <div>Pass: <span className="font-bold text-[var(--foreground)]">MapleFox47</span></div>
              </div>
            </div>

            <div className="pt-6">
              <button
                onClick={() => onSelectPortal('admin')}
                className="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-md transition-all"
              >
                <span>{userRole === 'admin' ? 'Open Admin Triage' : 'Login to Admin Portal'}</span>
                <ArrowRight className="w-4 h-4 text-red-400" />
              </button>
            </div>
          </div>

          {/* TESTING PORTAL */}
          <div className="rounded-3xl bg-[var(--surface)] border-2 border-[var(--border)] hover:border-slate-800 shadow-lg hover:shadow-xl p-7 flex flex-col justify-between transition-all transform hover:-translate-y-1 group relative overflow-hidden">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-slate-900 text-white flex items-center space-x-1">
                  <Lock className="w-3 h-3 text-red-400" />
                  <span>Protected · Tester Role</span>
                </span>
                <span className="text-xs font-semibold text-[var(--foreground-muted)]">QA & Hackathon Evaluators</span>
              </div>

              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-slate-900 to-slate-800 text-white flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
                <Workflow className="w-6 h-6 text-red-400" />
              </div>

              <div>
                <h3 className="text-xl font-black text-[var(--foreground)] group-hover:text-[var(--red-foreground)] transition-colors">
                  Testing Portal
                </h3>
                <p className="text-xs text-[var(--foreground-muted)] mt-1.5 leading-relaxed">
                  n8n workflow graphs, webhook payloads, live execution runs, benchmark ablation studies, and Notion sync.
                </p>
              </div>

              <ul className="space-y-2 text-xs text-[var(--foreground-muted)] pt-2 border-t border-[var(--border)]">
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span>n8n workflow graphs & webhook idempotency logs</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span>Held-out benchmark metrics (92.7% Macro-F1)</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span>Ablation studies (Hybrid vs Keywords vs Embeddings)</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span>Notion API synchronization of docs & test results</span>
                </li>
              </ul>

              <div className="p-2.5 rounded-xl bg-[var(--surface-muted)] border border-[var(--border)] text-[11px] font-mono text-[var(--foreground-muted)] space-y-0.5">
                <span className="text-[10px] uppercase font-bold text-[var(--foreground-muted)] block font-sans">Demo Credentials:</span>
                <div>User: <span className="font-bold text-[var(--foreground)]">tester_resolve</span></div>
                <div>Pass: <span className="font-bold text-[var(--foreground)]">OrbitPanda82</span></div>
              </div>
            </div>

            <div className="pt-6">
              <button
                onClick={() => onSelectPortal('testing')}
                className="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-md transition-all"
              >
                <span>{userRole === 'tester' ? 'Open Testing Portal' : 'Login to Testing Portal'}</span>
                <ArrowRight className="w-4 h-4 text-red-400" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Interactive Demo Trigger Cards */}
      <section className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-[var(--foreground-muted)]">
              Interactive Hackathon Demo Scenarios
            </span>
            <p className="text-xs text-[var(--foreground-muted)]">Populate and run Slide 4 test cases in the User Portal with 1 click</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onStartDemo('unique')}
              className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 font-semibold text-white text-xs shadow-md shadow-red-700/20 flex items-center space-x-1.5 transition-all"
            >
              <span>Test Case 1: Unique Issue</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onStartDemo('paraphrased')}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 font-semibold text-slate-200 border border-slate-700 text-xs flex items-center space-x-1.5 transition-all"
            >
              <span>Test Case 2: Paraphrased Duplicate</span>
              <CopyCheck className="w-3.5 h-3.5 text-amber-400" />
            </button>
          </div>
        </div>
      </section>

      {/* Problem vs Solution */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="p-8 rounded-2xl bg-[var(--surface)] border border-[var(--red-border)] shadow-sm relative overflow-hidden">
          <div className="w-12 h-12 rounded-xl bg-[var(--red-surface)] text-[var(--red-foreground)] flex items-center justify-center mb-5">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-[var(--foreground)] mb-2">The Problem</h3>
          <p className="text-[var(--foreground-muted)] leading-relaxed text-sm">
            Campus students submit free-form text with messy descriptions (e.g. "water dripping", "pipe leaking near stairs"). These create duplicate work orders, misassigned departments, and inconsistent triage. Maintenance fixes get slow and untracked.
          </p>
          <ul className="mt-4 space-y-2 text-xs text-[var(--foreground-muted)]">
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
          <p className="text-[var(--foreground-muted)] leading-relaxed text-sm">
            ResolveAI turns unstructured maintenance complaints into structured, schema-validated JSON, evaluates duplicate candidates using a hybrid formula, and routes verified tickets via n8n automated workflows.
          </p>
          <ul className="mt-4 space-y-2 text-xs text-[var(--foreground-muted)]">
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
      </section>

      {/* 4-Step Pipeline */}
      <section className="text-center space-y-8">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold text-[var(--foreground)]">How It Works</h2>
          <p className="text-[var(--foreground-muted)] mt-1 text-sm">End-to-end intelligent maintenance lifecycle</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-left">
          <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm hover:border-[var(--red-border)] transition-all">
            <div className="w-10 h-10 rounded-lg bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold flex items-center justify-center mb-4">
              1
            </div>
            <h4 className="text-base font-bold text-[var(--foreground)] mb-1">Submit</h4>
            <p className="text-xs text-[var(--foreground-muted)]">
              Student files a natural text complaint with optional OpenCV-validated image evidence.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm hover:border-[var(--red-border)] transition-all">
            <div className="w-10 h-10 rounded-lg bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold flex items-center justify-center mb-4">
              2
            </div>
            <h4 className="text-base font-bold text-[var(--foreground)] mb-1">Understand</h4>
            <p className="text-xs text-[var(--foreground-muted)]">
              Gemma model extracts schema-validated JSON: category, building block, floor/room, and urgency score.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm hover:border-[var(--red-border)] transition-all">
            <div className="w-10 h-10 rounded-lg bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold flex items-center justify-center mb-4">
              3
            </div>
            <h4 className="text-base font-bold text-[var(--foreground)] mb-1">Compare</h4>
            <p className="text-xs text-[var(--foreground-muted)]">
              Hybrid check flags duplicate candidates combining embeddings, physical proximity, and OpenCV dHash.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm hover:border-[var(--red-border)] transition-all">
            <div className="w-10 h-10 rounded-lg bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold flex items-center justify-center mb-4">
              4
            </div>
            <h4 className="text-base font-bold text-[var(--foreground)] mb-1">Route & Sync</h4>
            <p className="text-xs text-[var(--foreground-muted)]">
              n8n workflow assigns tickets directly or holds for approval, while Notion synchronizes testing logs.
            </p>
          </div>
        </div>
      </section>

      {/* Unique Technical USPs */}
      <section className="theme-inverse p-8 md:p-12 rounded-3xl bg-slate-900 text-white border border-slate-800">
        <div className="max-w-3xl mb-8">
          <span className="text-red-400 font-semibold text-xs tracking-wider uppercase">Technical Edge</span>
          <h2 className="text-3xl font-bold mt-2">Core USPs & Operational Safeguards</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="space-y-2">
            <h4 className="text-base font-semibold text-red-300 flex items-center space-x-2">
              <CopyCheck className="w-4 h-4 text-red-400" />
              <span>Hybrid Duplicates</span>
            </h4>
            <p className="text-xs text-slate-300">
              NLP embeddings, OpenCV perceptual dHash, physical location, and time window rules. Never silently auto-merges.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="text-base font-semibold text-red-300 flex items-center space-x-2">
              <Workflow className="w-4 h-4 text-red-400" />
              <span>n8n at the Core</span>
            </h4>
            <p className="text-xs text-slate-300">
              Branching, routing, idempotency keys, and execution history that a plain script cannot provide.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="text-base font-semibold text-red-300 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-red-400" />
              <span>Benchmarked Rigor</span>
            </h4>
            <p className="text-xs text-slate-300">
              Keyword vs embeddings vs hybrid tested on held-out fictional dataset with 0.927 F1-score.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="text-base font-semibold text-red-300 flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-red-400" />
              <span>Human-in-the-Loop</span>
            </h4>
            <p className="text-xs text-slate-300">
              Every action logged in an immutable audit trail. Ambiguous or duplicate tickets wait for human decision.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--border)] pt-8 pb-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-[var(--foreground-muted)]">
          <div>
            <p className="font-semibold text-[var(--foreground)]">ResolveAI • HackShift_404</p>
            <p className="text-xs">Anshul Gupta (Team Leader) • Aditya Gupta • Shivam Jhingan</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="px-3 py-1 rounded-full bg-[var(--surface-muted)] font-medium text-[var(--foreground)] border border-[var(--border)] text-xs">
              Track: n8n (Primary Sponsored Track)
            </span>
            <span className="text-xs text-[var(--foreground-muted)]">BPIT</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
