import React, { useEffect, useState } from 'react';
import { 
  BarChart2, 
  TrendingUp, 
  CheckCircle, 
  Layers, 
  GitCompare, 
  Award,
  Zap,
  Target
} from 'lucide-react';
import { EvaluationMetrics } from '../types';
import { apiService } from '../services/api';

export const BenchmarkPage: React.FC = () => {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiService.getBenchmarkMetrics()
      .then(res => setMetrics(res))
      .catch(err => console.error("Metrics load error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !metrics) {
    return (
      <div className="py-20 text-center text-[var(--foreground-muted)]">
        Loading empirical benchmark data...
      </div>
    );
  }

  return (
    <div className="space-y-10 py-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-[var(--red-surface)] text-[var(--red-foreground)] text-xs font-semibold mb-2">
          <Award className="w-3.5 h-3.5" />
          <span>Slide 5 Implementation: Benchmarked, Not Assumed</span>
        </div>
        <h1 className="text-3xl font-extrabold text-[var(--foreground)]">Empirical Performance & Ablation Study</h1>
        <p className="text-sm text-[var(--foreground-muted)] max-w-2xl">
          Held-out fictional campus benchmark evaluation showing classification accuracy, duplicate precision/recall, and ablation across detection strategies.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-1">
          <span className="text-xs font-bold uppercase text-[var(--foreground-muted)]">Category Macro-F1</span>
          <div className="text-3xl font-black text-[var(--foreground)]">
            {(metrics.category_macro_f1 * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-[var(--foreground-muted)]">Across 8 maintenance categories</p>
        </div>

        <div className="p-5 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-1">
          <span className="text-xs font-bold uppercase text-[var(--foreground-muted)]">Duplicate Recall</span>
          <div className="text-3xl font-black text-[var(--red-foreground)]">
            {(metrics.recall_heldout * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-[var(--foreground-muted)]">Catches paraphrased duplicate tickets</p>
        </div>

        <div className="p-5 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-1">
          <span className="text-xs font-bold uppercase text-[var(--foreground-muted)]">Duplicate Precision</span>
          <div className="text-3xl font-black text-[var(--foreground)]">
            {(metrics.precision_heldout * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-[var(--foreground-muted)]">Extremely low false-positive merges</p>
        </div>

        <div className="p-5 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-1">
          <span className="text-xs font-bold uppercase text-[var(--foreground-muted)]">n8n Execution Success</span>
          <div className="text-3xl font-black text-emerald-600">
            {(metrics.n8n_workflow_success_rate * 100).toFixed(1)}%
          </div>
          <p className="text-[11px] text-[var(--foreground-muted)]">Idempotent retry resilience</p>
        </div>
      </div>

      {/* Ablation Study Table (Slide 5) */}
      <div className="bg-[var(--surface)] rounded-2xl border border-[var(--border)] shadow-sm p-6 space-y-4">
        <div className="flex items-center space-x-2">
          <GitCompare className="w-5 h-5 text-[var(--red-foreground)]" />
          <h3 className="text-lg font-bold text-[var(--foreground)]">
            Ablation Study: Keyword vs Pure Embeddings vs ResolveAI Hybrid
          </h3>
        </div>
        <p className="text-xs text-[var(--foreground-muted)]">
          Evaluated against {metrics.total_benchmark_cases} held-out student complaints with ground-truth duplicate and non-duplicate pairs.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-[var(--surface-muted)] border-b border-[var(--border)] text-[var(--foreground-muted)] font-semibold uppercase text-[11px]">
              <tr>
                <th className="px-4 py-3">Approach / Model</th>
                <th className="px-4 py-3">Duplicate Precision</th>
                <th className="px-4 py-3">Duplicate Recall</th>
                <th className="px-4 py-3">F1-Score</th>
                <th className="px-4 py-3">False Positive Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {Object.entries(metrics.ablation_comparison).map(([name, scores], idx) => {
                const isWinner = name.includes('Hybrid');
                return (
                  <tr key={idx} className={isWinner ? "bg-[var(--red-surface)]/50 font-semibold" : ""}>
                    <td className="px-4 py-3.5 flex items-center space-x-2">
                      {isWinner && <Target className="w-4 h-4 text-[var(--red-foreground)] shrink-0" />}
                      <span className={isWinner ? "text-[var(--red-foreground)] font-bold" : "text-[var(--foreground)]"}>
                        {name}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">{(scores.precision * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3.5">{(scores.recall * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3.5">
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        isWinner ? 'bg-red-700 text-white font-bold' : 'text-[var(--foreground)]'
                      }`}>
                        {(scores.f1_score * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-[var(--foreground-muted)]">
                      {(scores.false_positive_rate * 100).toFixed(1)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Category Confusion Matrix Preview */}
      <div className="bg-[var(--surface)] rounded-2xl border border-[var(--border)] shadow-sm p-6 space-y-4">
        <h3 className="text-base font-bold text-[var(--foreground)]">
          Category Extraction Confusion Matrix (Sample)
        </h3>
        <p className="text-xs text-[var(--foreground-muted)]">
          Empirical validation showing clean separation between Water Leak, Electrical, Furniture, and HVAC.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-center text-xs">
            <thead className="bg-[var(--surface-muted)] border-b border-[var(--border)] text-[var(--foreground-muted)] font-bold">
              <tr>
                <th className="px-3 py-2 text-left">Actual \ Predicted</th>
                <th className="px-3 py-2">Water Leak</th>
                <th className="px-3 py-2">Electrical</th>
                <th className="px-3 py-2">Furniture</th>
                <th className="px-3 py-2">HVAC</th>
                <th className="px-3 py-2">Cleanliness</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {Object.entries(metrics.confusion_matrix).map(([actual, preds]) => (
                <tr key={actual} className="hover:bg-[var(--surface-muted)]">
                  <td className="px-3 py-2 text-left font-semibold text-[var(--foreground)] capitalize">
                    {actual.replace('_', ' ')}
                  </td>
                  <td className="px-3 py-2 font-mono font-bold text-[var(--foreground)]">
                    {preds.water_leak || 0}
                  </td>
                  <td className="px-3 py-2 font-mono font-bold text-[var(--foreground)]">
                    {preds.electrical || 0}
                  </td>
                  <td className="px-3 py-2 font-mono font-bold text-[var(--foreground)]">
                    {preds.furniture || 0}
                  </td>
                  <td className="px-3 py-2 font-mono font-bold text-[var(--foreground)]">
                    {preds.hvac || 0}
                  </td>
                  <td className="px-3 py-2 font-mono font-bold text-[var(--foreground)]">
                    {preds.cleanliness || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
