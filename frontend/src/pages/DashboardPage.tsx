import React, { useState } from 'react';
import { 
  Search, 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  UserCheck, 
  CopyCheck, 
  RefreshCw,
  ChevronRight,
  Check,
  X,
  GitMerge
} from 'lucide-react';
import { CaseRecord, CaseStatus } from '../types';
import { apiService } from '../services/api';

interface DashboardPageProps {
  cases: CaseRecord[];
  onRefresh: () => void;
  onSelectCase: (caseRecord: CaseRecord) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ cases, onRefresh, onSelectCase }) => {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [locationFilter, setLocationFilter] = useState<string>('');
  const [sortMode, setSortMode] = useState<'priority' | 'most_reported' | 'recent'>('priority');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const [selectedCaseForReview, setSelectedCaseForReview] = useState<CaseRecord | null>(null);
  const [reviewDecision, setReviewDecision] = useState<'approve' | 'merge_duplicate' | 'reject'>('approve');
  const [reviewerNotes, setReviewerNotes] = useState('Reviewed by Facility Supervisor');
  const [targetTeam, setTargetTeam] = useState('Plumbing & Water Infrastructure Team');
  const [reviewLoading, setReviewLoading] = useState(false);

  const filteredCases = cases.filter(c => {
    if (statusFilter !== 'all' && c.status !== statusFilter) return false;
    if (categoryFilter !== 'all' && c.extraction.issue_type !== categoryFilter) return false;
    if (priorityFilter !== 'all' && c.priority_level !== priorityFilter) return false;
    if (locationFilter && !`${c.extraction.building_block} ${c.extraction.floor_or_room || ''}`.toLowerCase().includes(locationFilter.toLowerCase())) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchText = c.raw_complaint.toLowerCase();
      const matchNum = c.case_number.toLowerCase();
      const matchSummary = c.extraction.clean_summary.toLowerCase();
      const matchLoc = c.extraction.building_block.toLowerCase();
      return matchText.includes(q) || matchNum.includes(q) || matchSummary.includes(q) || matchLoc.includes(q);
    }
    return true;
  }).sort((first, second) => {
    if (sortMode === 'most_reported') return second.corroborating_report_count - first.corroborating_report_count || second.priority_score - first.priority_score;
    if (sortMode === 'recent') return new Date(second.created_at).getTime() - new Date(first.created_at).getTime();
    return second.priority_score - first.priority_score || second.corroborating_report_count - first.corroborating_report_count;
  });

  const priorityClass = (level: string) => ({
    critical: 'bg-[var(--red-surface)] text-[var(--red-foreground)] border-[var(--red-border)]',
    high: 'bg-[var(--orange-surface)] text-[var(--orange-foreground)] border-[var(--orange-border)]',
    medium: 'bg-[var(--amber-surface)] text-[var(--amber-foreground)] border-[var(--amber-border)]',
    low: 'bg-[var(--emerald-surface)] text-[var(--emerald-foreground)] border-[var(--emerald-border)]',
  }[level] || 'bg-[var(--surface-muted)] text-[var(--foreground)] border-[var(--border)]');

  const handleDecisionSubmit = async () => {
    if (!selectedCaseForReview) return;
    setReviewLoading(true);
    try {
      await apiService.makeCaseDecision(selectedCaseForReview.id, {
        decision: reviewDecision,
        reviewer_notes: reviewerNotes,
        target_team: reviewDecision === 'approve' ? targetTeam : undefined,
        parent_case_id: reviewDecision === 'merge_duplicate' && selectedCaseForReview.duplicate_candidates?.[0]?.matched_case_id
          ? selectedCaseForReview.duplicate_candidates[0].matched_case_id
          : undefined
      });
      setSelectedCaseForReview(null);
      onRefresh();
    } catch (err) {
      console.error("Decision error:", err);
      alert("Failed to save decision.");
    } finally {
      setReviewLoading(false);
    }
  };

  const getStatusBadge = (status: CaseStatus, isHeld: boolean) => {
    if (isHeld || status === 'held_for_review') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--amber-surface)] text-[var(--amber-foreground)] border border-[var(--amber-border)]">
          <CopyCheck className="w-3 h-3 text-[var(--amber-foreground)]" />
          <span>Held for Review</span>
        </span>
      );
    }
    switch (status) {
      case 'assigned':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--blue-surface)] text-[var(--blue-foreground)] border border-[var(--blue-border)]">
            <UserCheck className="w-3 h-3 text-[var(--blue-foreground)]" />
            <span>Assigned</span>
          </span>
        );
      case 'in_progress':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--indigo-surface)] text-[var(--indigo-foreground)] border border-[var(--indigo-border)]">
            <Clock className="w-3 h-3 text-[var(--indigo-foreground)]" />
            <span>In Progress</span>
          </span>
        );
      case 'resolved':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--emerald-surface)] text-[var(--emerald-foreground)] border border-[var(--emerald-border)]">
            <CheckCircle2 className="w-3 h-3 text-[var(--emerald-foreground)]" />
            <span>Resolved</span>
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--surface-muted)] text-[var(--foreground)] border border-[var(--border)]">
            <X className="w-3 h-3 text-[var(--foreground-muted)]" />
            <span>Rejected</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-[var(--surface-muted)] text-[var(--foreground)]">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 py-6 max-w-7xl mx-auto">
      {/* Page Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[var(--foreground)]">Admin Maintenance Triage</h1>
          <p className="text-sm text-[var(--foreground-muted)]">Authoritative priority queue, image evidence, duplicate validation, and audit timeline</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={onRefresh}
            className="p-2.5 rounded-xl border border-[var(--border)] hover:bg-[var(--surface-muted)] text-[var(--foreground)] flex items-center space-x-1.5 text-xs font-medium transition-all"
            title="Refresh cases from server"
          >
            <RefreshCw className="w-4 h-4 text-[var(--foreground-muted)]" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-[var(--foreground-muted)]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search complaint, room, or ticket..."
            className="w-full pl-9 pr-4 py-2 rounded-xl border border-[var(--border)] text-xs sm:text-sm focus:border-red-600 outline-none"
          />
        </div>

        <div className="relative w-full md:w-52">
          <input
            type="text"
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            placeholder="Filter location..."
            className="w-full px-3.5 py-2 rounded-xl border border-[var(--border)] text-xs sm:text-sm focus:border-red-600 outline-none"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl border border-[var(--border)] text-xs bg-[var(--surface)] text-[var(--foreground)] outline-none"
          >
            <option value="all">All Statuses</option>
            <option value="held_for_review">Held for Review</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="rejected">Rejected</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 rounded-xl border border-[var(--border)] text-xs bg-[var(--surface)] text-[var(--foreground)] outline-none"
          >
            <option value="all">All Categories</option>
            <option value="water_leak">Water Leak</option>
            <option value="electrical">Electrical</option>
            <option value="furniture">Furniture</option>
            <option value="hvac">HVAC</option>
            <option value="internet_it">Internet & IT</option>
            <option value="cleanliness">Cleanliness</option>
            <option value="security">Security</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 rounded-xl border border-[var(--border)] text-xs bg-[var(--surface)] text-[var(--foreground)] outline-none"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={sortMode}
            onChange={(e) => setSortMode(e.target.value as typeof sortMode)}
            className="px-3 py-2 rounded-xl border border-[var(--border)] text-xs bg-[var(--surface)] text-[var(--foreground)] outline-none"
          >
            <option value="priority">Highest priority</option>
            <option value="most_reported">Most reported</option>
            <option value="recent">Most recent</option>
          </select>
        </div>
      </div>

      {/* Case List Table */}
      <div className="bg-[var(--surface)] rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-[var(--surface-muted)] border-b border-[var(--border)] text-[var(--foreground-muted)] font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th className="px-4 py-3.5">Ticket #</th>
                <th className="px-4 py-3.5">Report & Evidence</th>
                <th className="px-4 py-3.5">Extracted Details</th>
                <th className="px-4 py-3.5">Status & Routing</th>
                <th className="px-4 py-3.5">Duplicate Evidence</th>
                <th className="px-4 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {filteredCases.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-[var(--foreground-muted)]">
                    No tickets found matching the selected filters.
                  </td>
                </tr>
              ) : (
                filteredCases.map((c) => (
                  <tr key={c.id} className="hover:bg-[var(--surface-muted)]/70 transition-colors">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="font-bold text-[var(--foreground)]">{c.case_number}</div>
                      <div className="text-[11px] text-[var(--foreground-muted)]">
                        {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </td>

                    <td className="px-4 py-4 max-w-xs">
                      <div className="flex gap-2.5">
                        {c.images[0] && <img src={c.images[0].thumbnail_url} alt="Issue evidence" className="h-10 w-12 rounded-lg object-cover border border-[var(--border)] shrink-0" />}
                        <div className="min-w-0">
                          <p className="text-[var(--foreground)] font-medium line-clamp-2">{c.raw_complaint}</p>
                          <p className="text-[11px] text-[var(--foreground-muted)] mt-0.5">By {c.student_name} · {c.images.length} image{c.images.length === 1 ? '' : 's'}</p>
                        </div>
                      </div>
                    </td>

                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="font-semibold text-[var(--foreground)] capitalize">
                        {c.extraction.issue_type.replace('_', ' ')}
                      </div>
                      <div className="text-[11px] text-[var(--foreground-muted)]">
                        {c.extraction.building_block} • {c.extraction.floor_or_room || 'General'}
                      </div>
                      <div className="mt-1 flex items-center gap-1.5">
                        <span className={`inline-flex border px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${priorityClass(c.priority_level)}`}>
                          {c.priority_level} {c.priority_score}/10
                        </span>
                        <span className="text-[10px] text-[var(--foreground-muted)]">
                          {c.corroborating_report_count} report{c.corroborating_report_count === 1 ? '' : 's'}
                        </span>
                      </div>
                    </td>

                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="mb-1">{getStatusBadge(c.status, c.is_held_as_duplicate)}</div>
                      <div className="text-[11px] text-[var(--foreground-muted)] font-medium truncate max-w-[180px]">
                        {c.assigned_team || 'Pending assignment'}
                      </div>
                      {c.n8n_dispatch && (
                        <div className="text-[10px] font-mono text-[var(--foreground-muted)]">
                          n8n: {c.n8n_dispatch.workflow_branch}
                        </div>
                      )}
                    </td>

                    <td className="px-4 py-4">
                      {c.duplicate_candidates && c.duplicate_candidates.length > 0 ? (
                        <div className="space-y-1">
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-bold bg-[var(--amber-surface)] text-[var(--amber-foreground)] border border-[var(--amber-border)]">
                            <span>Score: {(c.duplicate_candidates[0].overall_hybrid_score * 100).toFixed(0)}%</span>
                          </span>
                          <p className="text-[10px] text-[var(--foreground-muted)] max-w-[160px] truncate">
                            Matches {c.duplicate_candidates[0].matched_case_title}
                          </p>
                           {c.duplicate_candidates[0].visual_similarity !== null && c.duplicate_candidates[0].visual_similarity !== undefined && (
                             <p className="text-[10px] text-[var(--foreground-muted)]">Visual: {(c.duplicate_candidates[0].visual_similarity * 100).toFixed(0)}%</p>
                           )}
                        </div>
                      ) : (
                        <span className="text-xs text-[var(--foreground-muted)] italic">Unique</span>
                      )}
                    </td>

                    <td className="px-4 py-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end space-x-2">
                        {c.status === 'held_for_review' && (
                          <button
                            onClick={() => setSelectedCaseForReview(c)}
                            className="px-2.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-semibold text-xs shadow-sm transition-all"
                          >
                            Review
                          </button>
                        )}
                        <button
                          onClick={() => onSelectCase(c)}
                          className="p-1.5 rounded-lg border border-[var(--border)] hover:bg-[var(--surface-muted)] text-[var(--foreground-muted)] transition-all"
                          title="View Audit Trail & Evidence"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Human-in-the-Loop Decision Modal */}
      {selectedCaseForReview && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[var(--surface)] rounded-2xl max-w-xl w-full border border-[var(--border)] shadow-2xl p-6 space-y-6">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[var(--amber-foreground)]">
                  Human-in-the-Loop Approval Required
                </span>
                <h3 className="text-xl font-bold text-[var(--foreground)] mt-1">
                  Review Case {selectedCaseForReview.case_number}
                </h3>
              </div>
              <button 
                onClick={() => setSelectedCaseForReview(null)}
                className="text-[var(--foreground-muted)] hover:text-[var(--foreground-muted)] p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <div className="p-3.5 rounded-xl bg-[var(--surface-muted)] border border-[var(--border)] text-xs space-y-1">
              <div className="font-semibold text-[var(--foreground)]">Complaint Text:</div>
              <p className="text-[var(--foreground)] italic">"{selectedCaseForReview.raw_complaint}"</p>
              <div className="pt-2 text-[11px] text-[var(--foreground-muted)]">
                Location: {selectedCaseForReview.extraction.building_block} ({selectedCaseForReview.extraction.specific_location_hint})
              </div>
            </div>

            {selectedCaseForReview.duplicate_candidates && selectedCaseForReview.duplicate_candidates.length > 0 && (
              <div className="p-3.5 rounded-xl bg-[var(--amber-surface)] border border-[var(--amber-border)] text-xs space-y-1.5">
                <div className="font-bold text-[var(--amber-foreground)] flex items-center space-x-1.5">
                  <AlertCircle className="w-4 h-4 text-[var(--amber-foreground)]" />
                  <span>Suspected Duplicate of Case #{selectedCaseForReview.duplicate_candidates[0].matched_case_id}</span>
                </div>
                <p className="text-[var(--foreground)]">
                  Target Title: {selectedCaseForReview.duplicate_candidates[0].matched_case_title}
                </p>
                <div className="font-mono text-[11px] text-[var(--amber-foreground)]">
                  Hybrid Score: {(selectedCaseForReview.duplicate_candidates[0].overall_hybrid_score * 100).toFixed(1)}% | 
                  Semantic: {(selectedCaseForReview.duplicate_candidates[0].semantic_similarity * 100).toFixed(1)}% | 
                  Location: {(selectedCaseForReview.duplicate_candidates[0].location_match_score * 100).toFixed(1)}%
                </div>
              </div>
            )}

            {/* Decision choices */}
            <div className="space-y-3">
              <label className="text-xs font-bold text-[var(--foreground)] uppercase tracking-wider block">
                Select Administrative Action
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setReviewDecision('approve')}
                  className={`p-3 rounded-xl border text-center transition-all ${
                    reviewDecision === 'approve'
                      ? 'border-emerald-600 bg-[var(--emerald-surface)] text-[var(--emerald-foreground)] font-bold'
                      : 'border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <Check className="w-4 h-4 mx-auto mb-1 text-emerald-600" />
                  <span className="text-xs">Approve & Dispatch</span>
                </button>

                <button
                  type="button"
                  onClick={() => setReviewDecision('merge_duplicate')}
                  className={`p-3 rounded-xl border text-center transition-all ${
                    reviewDecision === 'merge_duplicate'
                      ? 'border-amber-600 bg-[var(--amber-surface)] text-[var(--amber-foreground)] font-bold'
                      : 'border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <GitMerge className="w-4 h-4 mx-auto mb-1 text-amber-600" />
                  <span className="text-xs">Merge Duplicate</span>
                </button>

                <button
                  type="button"
                  onClick={() => setReviewDecision('reject')}
                  className={`p-3 rounded-xl border text-center transition-all ${
                    reviewDecision === 'reject'
                      ? 'border-red-600 bg-[var(--red-surface)] text-[var(--red-foreground)] font-bold'
                      : 'border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--surface-muted)]'
                  }`}
                >
                  <X className="w-4 h-4 mx-auto mb-1 text-red-600" />
                  <span className="text-xs">Reject Case</span>
                </button>
              </div>
            </div>

            {/* Target Team dropdown if approving */}
            {reviewDecision === 'approve' && (
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-[var(--foreground)]">Assign Maintenance Team</label>
                <select
                  value={targetTeam}
                  onChange={(e) => setTargetTeam(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-[var(--border)] text-xs bg-[var(--surface)] text-[var(--foreground)]"
                >
                  <option value="Plumbing & Water Infrastructure Team">Plumbing & Water Infrastructure Team</option>
                  <option value="High & Low Voltage Electrical Operations">High & Low Voltage Electrical Operations</option>
                  <option value="Carpentry & Facilities Maintenance Unit">Carpentry & Facilities Maintenance Unit</option>
                  <option value="HVAC & Thermal Systems Engineering">HVAC & Thermal Systems Engineering</option>
                  <option value="IT & Network Operations Center (NOC)">IT & Network Operations Center (NOC)</option>
                  <option value="Sanitation & Groundskeeping Services">Sanitation & Groundskeeping Services</option>
                </select>
              </div>
            )}

            {/* Reviewer Note */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[var(--foreground)]">Audit Trail Reason / Notes</label>
              <input
                type="text"
                value={reviewerNotes}
                onChange={(e) => setReviewerNotes(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-[var(--border)] text-xs text-[var(--foreground)]"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                onClick={() => setSelectedCaseForReview(null)}
                className="px-4 py-2 rounded-xl border border-[var(--border)] text-[var(--foreground)] text-xs font-semibold hover:bg-[var(--surface-muted)]"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDecisionSubmit}
                disabled={reviewLoading}
                className="px-5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-md"
              >
                {reviewLoading ? "Saving..." : "Confirm & Write Audit Log"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
