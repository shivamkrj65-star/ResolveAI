import { EvidenceImage } from '../components/EvidenceImage';
import React, { useRef, useState } from 'react';
import { 
  Send, 
  Sparkles, 
  MapPin, 
  User, 
  Mail, 
  AlertTriangle, 
  CheckCircle, 
  CopyCheck, 
  Loader2,
  ImagePlus,
  Trash2,
  UploadCloud,
  Users
} from 'lucide-react';
import { ComplaintCreate, CaseRecord } from '../types';
import { apiService } from '../services/api';

interface SubmitPageProps {
  onCaseCreated: (createdCase: CaseRecord) => void;
  initialText?: string;
  onTrackTicket?: (ticketId: string) => void;
}

interface SelectedImage {
  file: File;
  previewUrl: string;
}

export const SubmitPage: React.FC<SubmitPageProps> = ({ onCaseCreated, initialText = '', onTrackTicket }) => {
  const [complaintText, setComplaintText] = useState(initialText);
  const [studentName, setStudentName] = useState('Ananya Sen');
  const [studentEmail, setStudentEmail] = useState('ananya.s@example.com');
  const [reportedBlock, setReportedBlock] = useState('Block B');
  const [reportedFloor, setReportedFloor] = useState('2nd Floor');
  const [affectedPeople, setAffectedPeople] = useState('');
  const [selectedImages, setSelectedImages] = useState<SelectedImage[]>([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const imageInputRef = useRef<HTMLInputElement>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSubmittedCase, setLastSubmittedCase] = useState<CaseRecord | null>(null);

  const addImages = (fileList: FileList | File[]) => {
    const files = Array.from(fileList);
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp'];
    const invalid = files.find((file) => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      return !allowedExtensions.includes(extension || '') || file.size > 8 * 1024 * 1024;
    });
    if (invalid) {
      setError(`${invalid.name} is not supported. Use a JPG, PNG, or WEBP image up to 8 MB.`);
      return;
    }
    if (selectedImages.length + files.length > 4) {
      setError('You can attach up to four images to one report.');
      return;
    }
    setError(null);
    setSelectedImages((current) => [
      ...current,
      ...files.map((file) => ({ file, previewUrl: URL.createObjectURL(file) })),
    ]);
  };

  const removeImage = (index: number) => {
    setSelectedImages((current) => {
      URL.revokeObjectURL(current[index].previewUrl);
      return current.filter((_, currentIndex) => currentIndex !== index);
    });
    if (imageInputRef.current) imageInputRef.current.value = '';
  };

  const sampleComplaints = [
    {
      title: "Test Case 1: Unique Complaint",
      text: "Water across B-block stairway, puddles forming near the second landing and people are slipping.",
      block: "Block B",
      floor: "2nd Floor"
    },
    {
      title: "Test Case 2: Paraphrased Duplicate Candidate",
      text: "Leaking pipe near the stairs in block B causing water to pool on the walking path.",
      block: "Block B",
      floor: "2nd Floor"
    },
    {
      title: "Urgent Electrical Fire Hazard",
      text: "Sparking switchboard and burning wire smell in Library 3rd floor reading hall near table 14.",
      block: "Central Library",
      floor: "3rd Floor"
    },
    {
      title: "Broken Furniture Report",
      text: "Room 204 in Block A has 3 broken chairs with jagged iron frames sticking out.",
      block: "Block A",
      floor: "Room 204"
    }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaintText.trim() || complaintText.length < 5) {
      setError("Please describe the issue in at least 5 characters.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload: ComplaintCreate = {
        raw_text: complaintText,
        student_name: studentName,
        student_email: studentEmail,
        reported_block: reportedBlock,
        reported_floor: reportedFloor,
        affected_people: affectedPeople ? Number(affectedPeople) : undefined,
      };

      const result = await apiService.submitComplaint(
        payload,
        selectedImages.map((image) => image.file),
        setUploadProgress,
      );
      setLastSubmittedCase(result);
      onCaseCreated(result);
      selectedImages.forEach((image) => URL.revokeObjectURL(image.previewUrl));
      setSelectedImages([]);
      setUploadProgress(0);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to process complaint. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sample: typeof sampleComplaints[0]) => {
    setComplaintText(sample.text);
    setReportedBlock(sample.block);
    setReportedFloor(sample.floor);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    addImages(event.dataTransfer.files);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-10 py-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-[var(--red-surface)] text-[var(--red-foreground)] text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>User Reporting Portal</span>
        </div>
        <h1 className="text-3xl font-extrabold text-[var(--foreground)]">Report a Maintenance Issue</h1>
        <p className="text-[var(--foreground-muted)] max-w-xl mx-auto text-sm">
          Describe the problem in plain English. Gemma parses location & urgency, and our hybrid duplicate engine checks against existing reports before automated dispatch.
        </p>
      </div>

      {/* Preset quick test buttons (Mirrors PPT test cases) */}
      <div className="p-4 rounded-2xl bg-[var(--surface)] border border-[var(--border)] shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-[var(--foreground-muted)]">
            Quick Load Benchmark Scenarios
          </span>
          <span className="text-xs text-[var(--red-foreground)] font-medium">Click to populate form</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {sampleComplaints.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadSample(sample)}
              className="text-left p-3 rounded-xl border border-[var(--border)] hover:border-red-400 hover:bg-[var(--red-surface)]/50 transition-all text-xs space-y-1"
            >
              <div className="font-semibold text-[var(--foreground)]">{sample.title}</div>
              <div className="text-[var(--foreground-muted)] truncate">"{sample.text}"</div>
            </button>
          ))}
        </div>
      </div>

      {/* Complaint Form */}
      <div className="bg-[var(--surface)] rounded-2xl border border-[var(--border)] shadow-sm p-6 sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Free-form text */}
          <div className="space-y-2">
            <label htmlFor="complaint-description" className="block text-sm font-semibold text-[var(--foreground)]">
              Complaint Description <span className="text-red-600">*</span>
            </label>
            <textarea
              id="complaint-description"
              rows={4}
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
              placeholder="e.g. Water across B-block stairway, puddle forming near second landing..."
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] focus:border-red-600 focus:ring-2 focus:ring-red-600/20 outline-none text-[var(--foreground)] text-sm transition-all"
              required
            />
            <p className="text-xs text-[var(--foreground-muted)]">
              Include any sensory details, exact floor, room numbers, or hazards.
            </p>
          </div>

          {/* Reporter metadata */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label htmlFor="reporter-name" className="text-xs font-semibold text-[var(--foreground)] flex items-center space-x-1.5">
                <User className="w-3.5 h-3.5 text-[var(--foreground-muted)]" />
                <span>Reporter Name</span>
              </label>
              <input
                type="text"
                id="reporter-name"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-[var(--border)] text-sm focus:border-red-600 outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="reporter-email" className="text-xs font-semibold text-[var(--foreground)] flex items-center space-x-1.5">
                <Mail className="w-3.5 h-3.5 text-[var(--foreground-muted)]" />
                <span>Reporter Email</span>
              </label>
              <input
                type="email"
                id="reporter-email"
                value={studentEmail}
                onChange={(e) => setStudentEmail(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-[var(--border)] text-sm focus:border-red-600 outline-none"
              />
            </div>
          </div>

          {/* Location cues */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label htmlFor="building-hint" className="text-xs font-semibold text-[var(--foreground)] flex items-center space-x-1.5">
                <MapPin className="w-3.5 h-3.5 text-[var(--foreground-muted)]" />
                <span>Building Block Hint</span>
              </label>
              <select
                id="building-hint"
                value={reportedBlock}
                onChange={(e) => setReportedBlock(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-[var(--border)] text-sm focus:border-red-600 outline-none bg-[var(--surface)]"
              >
                <option value="Block A">Block A</option>
                <option value="Block B">Block B</option>
                <option value="Block C">Block C</option>
                <option value="Block D">Block D</option>
                <option value="Central Library">Central Library</option>
                <option value="Hostel 1">Hostel 1</option>
                <option value="Hostel 2">Hostel 2</option>
                <option value="Cafeteria">Cafeteria</option>
                <option value="Main Facility">Main Facility</option>
              </select>
            </div>

           {/* Image evidence */}
           <div className="space-y-2">
             <div className="flex flex-wrap items-center justify-between gap-3">
               <label htmlFor="photo-evidence" className="text-sm font-semibold text-[var(--foreground)] flex items-center gap-2">
                 <ImagePlus className="w-4 h-4 text-[var(--red-foreground)]" />
                 Photo evidence <span className="font-normal text-[var(--foreground-muted)] text-xs">(optional)</span>
               </label>
               <span className="text-[11px] text-[var(--foreground-muted)]">JPG, PNG, WEBP · up to 8 MB each</span>
             </div>
             <input
               id="photo-evidence"
               ref={imageInputRef}
               type="file"
               accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
               multiple
               className="hidden"
               onChange={(event) => event.target.files && addImages(event.target.files)}
             />
             <div
               role="button"
               tabIndex={0}
               onClick={() => imageInputRef.current?.click()}
               onKeyDown={(event) => {
                 if (event.key === 'Enter' || event.key === ' ') {
                   event.preventDefault();
                   imageInputRef.current?.click();
                 }
               }}
               onDragOver={(event) => event.preventDefault()}
               onDrop={handleDrop}
               className="cursor-pointer rounded-xl border-2 border-dashed border-[var(--border)] hover:border-red-400 bg-[var(--surface-muted)] hover:bg-[var(--red-surface)]/40 px-5 py-6 text-center transition-colors"
             >
               <UploadCloud className="w-6 h-6 text-[var(--foreground-muted)] mx-auto mb-2" />
               <p className="text-sm font-semibold text-[var(--foreground)]">Drag photos here or choose files</p>
               <p className="text-xs text-[var(--foreground-muted)] mt-1">OpenCV checks image integrity and quality before secure storage.</p>
             </div>
             {selectedImages.length > 0 && (
               <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
                 {selectedImages.map((image, index) => (
                   <div key={`${image.file.name}-${index}`} className="relative overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface)]">
                     <img src={image.previewUrl} alt={`Selected evidence ${index + 1}`} className="h-24 w-full object-cover" />
                     <div className="p-2 pr-8 text-[10px] text-[var(--foreground-muted)] truncate" title={image.file.name}>{image.file.name}</div>
                     <button
                       type="button"
                       onClick={(event) => { event.stopPropagation(); removeImage(index); }}
                       className="absolute right-1.5 top-1.5 rounded-full bg-slate-900/80 p-1 text-white hover:bg-red-700"
                       aria-label={`Remove ${image.file.name}`}
                     >
                       <Trash2 className="w-3 h-3" />
                     </button>
                   </div>
                 ))}
               </div>
             )}
           </div>

           <div className="space-y-1.5 max-w-xs">
             <label htmlFor="affected-people" className="text-xs font-semibold text-[var(--foreground)] flex flex-wrap items-center gap-1.5">
               <Users className="w-3.5 h-3.5 text-[var(--foreground-muted)]" /> Estimated people affected <span className="font-normal text-[var(--foreground-muted)]">(optional)</span>
             </label>
             <input
               type="number"
               id="affected-people"
               min="0"
               value={affectedPeople}
               onChange={(event) => setAffectedPeople(event.target.value)}
               placeholder="e.g. 50"
               className="w-full px-3.5 py-2 rounded-lg border border-[var(--border)] text-sm focus:border-red-600 outline-none"
             />
           </div>

            <div className="space-y-1.5">
              <label htmlFor="floor-hint" className="text-xs font-semibold text-[var(--foreground)]">Floor / Room Hint</label>
              <input
                type="text"
                id="floor-hint"
                value={reportedFloor}
                onChange={(e) => setReportedFloor(e.target.value)}
                placeholder="e.g. 2nd Floor, Stairway"
                className="w-full px-3.5 py-2 rounded-lg border border-[var(--border)] text-sm focus:border-red-600 outline-none"
              />
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-[var(--red-surface)] border border-[var(--red-border)] text-[var(--red-foreground)] text-sm flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-xl bg-red-700 hover:bg-red-800 text-white font-semibold text-sm shadow-md shadow-red-700/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{selectedImages.length ? `Uploading evidence ${uploadProgress}% & analysing issue...` : 'Running Gemma Extraction & Hybrid Duplicate Engine...'}</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Process & Route Complaint</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Live Result Feedback Card after submission */}
      {lastSubmittedCase && (
        <div className="bg-[var(--surface)] rounded-2xl border-2 border-[var(--red-border)] shadow-lg p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[var(--border)] pb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-[var(--emerald-surface)] text-[var(--emerald-foreground)] flex items-center justify-center font-bold">
                ✓
              </div>
              <div>
                <h3 className="font-bold text-[var(--foreground)]">Case Created: {lastSubmittedCase.case_number}</h3>
                <p className="text-xs text-[var(--foreground-muted)]">Processed through Gemma NLP & n8n Router</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {lastSubmittedCase.is_held_as_duplicate ? (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-[var(--amber-surface)] text-[var(--amber-foreground)] border border-[var(--amber-border)] flex items-center space-x-1">
                  <CopyCheck className="w-3.5 h-3.5 text-[var(--amber-foreground)]" />
                  <span>Held for Human Review (Suspected Duplicate)</span>
                </span>
              ) : (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-[var(--emerald-surface)] text-[var(--emerald-foreground)] border border-[var(--emerald-border)] flex items-center space-x-1">
                  <CheckCircle className="w-3.5 h-3.5 text-[var(--emerald-foreground)]" />
                  <span>Assigned: {lastSubmittedCase.assigned_team}</span>
                </span>
              )}
              {onTrackTicket && (
                <button
                  type="button"
                  onClick={() => onTrackTicket(lastSubmittedCase.case_number)}
                  className="px-3 py-1 rounded-full text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white transition-all shadow-sm flex items-center space-x-1"
                >
                  <span>Track Ticket</span>
                  <span>→</span>
                </button>
              )}
            </div>
          </div>

          {/* Extraction summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-3 rounded-xl bg-[var(--surface-muted)] border border-[var(--border)]">
              <div className="text-[var(--foreground-muted)] font-medium">Classified Category</div>
              <div className="text-sm font-bold text-[var(--foreground)] capitalize mt-0.5">
                {lastSubmittedCase.extraction.issue_type.replace('_', ' ')}
              </div>
              <div className="text-[11px] text-[var(--foreground-muted)] mt-1">
                Confidence: {(lastSubmittedCase.extraction.confidence * 100).toFixed(0)}%
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[var(--surface-muted)] border border-[var(--border)]">
              <div className="text-[var(--foreground-muted)] font-medium">Location Extracted</div>
              <div className="text-sm font-bold text-[var(--foreground)] mt-0.5">
                {lastSubmittedCase.extraction.building_block}
              </div>
              <div className="text-[11px] text-[var(--foreground-muted)] mt-1">
                {lastSubmittedCase.extraction.floor_or_room || lastSubmittedCase.extraction.specific_location_hint}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[var(--surface-muted)] border border-[var(--border)]">
              <div className="text-[var(--foreground-muted)] font-medium">Priority & Urgency</div>
              <div className="text-sm font-bold text-[var(--foreground)] uppercase mt-0.5">
                {lastSubmittedCase.priority_level} ({lastSubmittedCase.priority_score}/10)
              </div>
              <div className="text-[11px] text-[var(--foreground-muted)] mt-1">
                {lastSubmittedCase.corroborating_report_count} corroborating report{lastSubmittedCase.corroborating_report_count === 1 ? '' : 's'} · n8n: {lastSubmittedCase.n8n_dispatch?.workflow_branch}
              </div>
            </div>
          </div>

          {/* Duplicate candidates view if any */}
          {lastSubmittedCase.duplicate_candidates && lastSubmittedCase.duplicate_candidates.length > 0 && (
            <div className="p-4 rounded-xl bg-[var(--amber-surface)]/70 border border-[var(--amber-border)] space-y-2">
              <div className="text-xs font-bold text-[var(--amber-foreground)] flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-[var(--amber-foreground)]" />
                <span>Duplicate Candidate Matches Detected (Never Auto-Merged):</span>
              </div>
              {lastSubmittedCase.duplicate_candidates.map((cand, i) => (
                <div key={i} className="text-xs bg-[var(--surface)] p-3 rounded-lg border border-[var(--amber-border)] flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <span className="font-semibold text-[var(--foreground)]">Matches Case #{cand.matched_case_id}:</span> {cand.matched_case_title}
                    <p className="text-[11px] text-[var(--foreground-muted)] mt-0.5">{cand.reason}</p>
                    {cand.visual_similarity !== null && cand.visual_similarity !== undefined && (
                      <p className="text-[11px] text-[var(--foreground-muted)]">Visual similarity: {(cand.visual_similarity * 100).toFixed(0)}%</p>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    <span className="px-2 py-0.5 rounded font-mono font-bold bg-[var(--amber-surface)] text-[var(--amber-foreground)] text-xs">
                      Hybrid Score: {(cand.overall_hybrid_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
          {lastSubmittedCase.images.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-bold text-[var(--foreground)]">OpenCV-Validated Evidence (Cloudinary Stored)</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {lastSubmittedCase.images.map((image) => (
                  <div key={image.id} className="rounded-xl overflow-hidden border border-[var(--border)] bg-[var(--surface)]">
                    <a href={image.secure_url} target="_blank" rel="noreferrer" className="block relative group">
                      <EvidenceImage image={image} alt={image.original_filename} className="h-28 w-full object-cover group-hover:opacity-90 transition-opacity" />
                      <div className="absolute top-1.5 right-1.5 bg-slate-900/80 text-[10px] text-white px-1.5 py-0.5 rounded font-mono">
                        {image.width}×{image.height}
                      </div>
                    </a>
                    <div className="p-2.5 space-y-1">
                      <div className="text-[11px] font-semibold text-[var(--foreground)] truncate" title={image.original_filename}>
                        {image.original_filename}
                      </div>
                      {image.visual_analysis && (
                        <div className="text-[10px] text-[var(--foreground-muted)] font-mono">
                          Sharpness: {image.visual_analysis.sharpness} · Brightness: {image.visual_analysis.brightness}
                        </div>
                      )}
                      {image.quality_warning ? (
                        <div className="text-[10px] text-[var(--amber-foreground)] bg-[var(--amber-surface)] px-1.5 py-0.5 rounded border border-[var(--amber-border)]">
                          {image.quality_warning}
                        </div>
                      ) : (
                        <div className="text-[10px] text-[var(--emerald-foreground)] bg-[var(--emerald-surface)] px-1.5 py-0.5 rounded border border-[var(--emerald-border)]">
                          ✓ OpenCV Integrity Verified
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
