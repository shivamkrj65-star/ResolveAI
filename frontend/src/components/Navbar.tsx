import React from 'react';
import { 
  ShieldCheck, 
  Layers, 
  Workflow, 
  BarChart2, 
  FilePlus, 
  FileText,
  Search,
  ArrowLeft,
  LogOut,
  RotateCcw,
  Lock,
  User,
  Sparkles
} from 'lucide-react';
import { UserSession } from '../types';

interface NavbarProps {
  currentPortal: 'selection' | 'user' | 'admin' | 'testing';
  currentTab: string;
  onSelectPortal: (portal: 'selection' | 'user' | 'admin' | 'testing') => void;
  onSelectTab: (tab: string) => void;
  pendingReviewCount: number;
  session: UserSession | null;
  onLogout: () => void;
  onResetDemo?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentPortal,
  currentTab,
  onSelectPortal,
  onSelectTab,
  pendingReviewCount,
  session,
  onLogout,
  onResetDemo,
}) => {
  return (
    <header className="app-navbar sticky top-0 z-40 bg-[var(--surface)] border-b border-[var(--border)] shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap justify-between items-center min-h-16 gap-3 py-3 lg:flex-nowrap">
          {/* Logo & Brand */}
          <button
            type="button"
            className="flex items-center space-x-3 text-left rounded-lg shrink-0"
            onClick={() => onSelectPortal('selection')}
            title="Return to Portal Selection"
          >
            <span className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-700 to-rose-600 flex items-center justify-center text-white shadow-md shadow-red-500/20">
              <ShieldCheck className="w-6 h-6" />
            </span>
            <span>
              <span className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-[var(--foreground)]">
                  RESOLVE<span className="text-[var(--primary)]">AI</span>
                </span>
              </span>
              <span className="text-[10px] text-[var(--foreground-muted)] font-medium hidden sm:block">
                {currentPortal === 'user' && 'User Portal • Public Access'}
                {currentPortal === 'admin' && 'Admin Portal • Maintenance Triage'}
                {currentPortal === 'testing' && 'Testing Portal • Workflows & Evaluation'}
                {currentPortal === 'selection' && 'Intelligent Campus Maintenance'}
              </span>
            </span>
          </button>

          {/* Portal-Specific Navigation Tabs */}
          <nav aria-label="Portal navigation" className="order-last flex w-full min-w-0 items-center gap-1 overflow-x-auto py-1 lg:order-none lg:w-auto lg:flex-1">
            {/* PORTAL SELECTION VIEW */}
            {currentPortal === 'selection' && (
              <>
                <button
                  onClick={() => onSelectPortal('user')}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-[var(--foreground)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)] transition-colors flex items-center space-x-1"
                >
                  <FilePlus className="w-3.5 h-3.5 text-red-600" />
                  <span>User Portal</span>
                </button>
                <button
                  onClick={() => onSelectPortal('admin')}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-[var(--foreground)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)] transition-colors flex items-center space-x-1"
                >
                  <Layers className="w-3.5 h-3.5 text-[var(--foreground)]" />
                  <span>Admin Portal</span>
                </button>
                <button
                  onClick={() => onSelectPortal('testing')}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-[var(--foreground)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)] transition-colors flex items-center space-x-1"
                >
                  <Workflow className="w-3.5 h-3.5 text-red-600" />
                  <span>Testing Portal</span>
                </button>
              </>
            )}

            {/* USER PORTAL TABS */}
            {currentPortal === 'user' && (
              <>
                <button
                  aria-current={currentTab === 'overview' ? 'page' : undefined}
                  onClick={() => onSelectTab('overview')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    currentTab === 'overview'
                      ? 'bg-[var(--surface-muted)] text-[var(--foreground)] font-bold'
                      : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  Overview
                </button>
                <button
                  aria-current={currentTab === 'submit' ? 'page' : undefined}
                  onClick={() => onSelectTab('submit')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'submit'
                      ? 'bg-red-700 text-white shadow-sm'
                      : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <FilePlus className="w-3.5 h-3.5" />
                  <span>Submit Issue</span>
                </button>
                <button
                  aria-current={currentTab === 'track' ? 'page' : undefined}
                  onClick={() => onSelectTab('track')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'track'
                      ? 'bg-[var(--foreground)] text-[var(--surface)] shadow-sm'
                      : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>Track Complaint</span>
                </button>
              </>
            )}

            {/* ADMIN PORTAL TABS */}
            {currentPortal === 'admin' && (
              <>
                <button
                  aria-current={currentTab === 'triage' ? 'page' : undefined}
                  onClick={() => onSelectTab('triage')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'triage'
                      ? 'bg-[var(--foreground)] text-[var(--surface)] shadow-sm'
                      : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Admin Triage</span>
                  {pendingReviewCount > 0 && (
                    <span className="ml-1 px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-amber-500 text-white">
                      {pendingReviewCount}
                    </span>
                  )}
                </button>
              </>
            )}

            {/* TESTING PORTAL TABS */}
            {currentPortal === 'testing' && (
              <>
                <button
                  aria-current={currentTab === 'workflow' ? 'page' : undefined}
                  onClick={() => onSelectTab('workflow')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'workflow'
                      ? 'bg-[var(--foreground)] text-[var(--surface)] shadow-sm'
                      : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <Workflow className="w-3.5 h-3.5 text-red-400" />
                  <span>n8n Workflow</span>
                </button>
                <button
                  aria-current={currentTab === 'benchmark' ? 'page' : undefined}
                  onClick={() => onSelectTab('benchmark')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'benchmark'
                      ? 'bg-[var(--foreground)] text-[var(--surface)] shadow-sm'
                      : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <BarChart2 className="w-3.5 h-3.5" />
                  <span>Benchmark & USP</span>
                </button>
                <button
                  aria-current={currentTab === 'notion' ? 'page' : undefined}
                  onClick={() => onSelectTab('notion')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'notion'
                      ? 'bg-[var(--foreground)] text-[var(--surface)] shadow-sm'
                      : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <FileText className="w-3.5 h-3.5 text-red-400" />
                  <span>Notion Docs</span>
                </button>
              </>
            )}
          </nav>

          {/* Right Controls: Role Badge, Back to Portal Selection & Logout */}
          <div className="flex items-center space-x-2 shrink-0">
            {currentPortal !== 'selection' && (
              <button
                onClick={() => onSelectPortal('selection')}
                className="px-2.5 py-1.5 rounded-lg border border-[var(--border)] hover:bg-[var(--surface-muted)] text-[var(--foreground)] text-xs font-semibold flex items-center space-x-1 transition-colors"
                title="Back to Portal Selection"
              >
                <ArrowLeft className="w-3.5 h-3.5 text-[var(--foreground-muted)]" />
                <span className="hidden md:inline">Portal Selection</span>
              </button>
            )}

            {/* If in testing portal and resetDemo prop provided */}
            {currentPortal === 'testing' && onResetDemo && (
              <button
                onClick={onResetDemo}
                className="px-2.5 py-1.5 rounded-lg border border-[var(--border)] hover:bg-[var(--surface-muted)] text-[var(--foreground)] text-xs font-semibold flex items-center space-x-1 transition-colors"
                title="Reset benchmark & test data"
              >
                <RotateCcw className="w-3.5 h-3.5 text-red-600" />
                <span className="hidden sm:inline">Reset Demo</span>
              </button>
            )}

            {/* Session Indicator & Logout */}
            {session ? (
              <div className="flex items-center space-x-1.5">
                <span className="px-2.5 py-1 rounded-lg bg-[var(--surface-muted)] text-[var(--foreground)] text-[11px] font-mono font-semibold border border-[var(--border)] hidden sm:inline-flex items-center space-x-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>{session.username}</span>
                  <span className="text-[var(--foreground-muted)]">({session.role})</span>
                </span>
                <button
                  onClick={onLogout}
                  className="px-2.5 py-1.5 rounded-lg bg-[var(--surface-muted)] hover:bg-red-50 hover:text-red-700 text-[var(--foreground)] text-xs font-semibold flex items-center space-x-1 transition-colors"
                  title="Logout demo session"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </div>
            ) : currentPortal !== 'user' && currentPortal !== 'selection' ? (
              <span className="px-2 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-xs font-semibold flex items-center space-x-1">
                <Lock className="w-3 h-3 text-amber-600" />
                <span>Protected</span>
              </span>
            ) : null}
          </div>
        </div>
      </div>
    </header>
  );
};
