"use client";

import React, { useState, useEffect } from "react";
import { ReviewResult } from "../types/api";
import { recordDecision } from "../lib/api";
import { 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  HelpCircle, 
  FileText, 
  BookOpen, 
  MessageSquare,
  Sparkles,
  X,
  ExternalLink
} from "lucide-react";

interface ResultCardProps {
  result: ReviewResult;
  onDecisionUpdated: (updated: ReviewResult) => void;
  onGoToHistory?: () => void;
}

export function ResultCard({ result, onDecisionUpdated, onGoToHistory }: ResultCardProps) {
  const [reviewerNote, setReviewerNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<{
    visible: boolean;
    status: string;
  }>({ visible: false, status: "" });

  // Auto-dismiss toast popup after 5 seconds
  useEffect(() => {
    if (toast.visible) {
      const timer = setTimeout(() => {
        setToast({ visible: false, status: "" });
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [toast.visible]);

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "Low Risk":
        return {
          bg: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
        };
      case "Medium Risk":
        return {
          bg: "bg-amber-500/10 border-amber-500/30 text-amber-400",
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />,
        };
      case "High Risk":
        return {
          bg: "bg-rose-500/10 border-rose-500/30 text-rose-400 gradient-glow-red",
          icon: <XCircle className="w-5 h-5 text-rose-400" />,
        };
      default:
        return {
          bg: "bg-slate-500/10 border-slate-500/30 text-slate-400",
          icon: <HelpCircle className="w-5 h-5 text-slate-400" />,
        };
    }
  };

  const badge = getRiskBadge(result.risk_level);

  const handleDecision = async (status: "approved" | "rejected" | "marked_for_review") => {
    setSubmitting(true);
    const updated = await recordDecision(result.review_id, {
      status,
      reviewer_note: reviewerNote,
    });
    setSubmitting(false);
    if (updated) {
      onDecisionUpdated(updated);
      const statusLabel =
        status === "approved" ? "Approved" : status === "rejected" ? "Rejected" : "Marked for Review";
      setToast({ visible: true, status: statusLabel });
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-2xl relative overflow-hidden space-y-6">
      {/* Auto-dismissing Toast Popup */}
      {toast.visible && (
        <div className="fixed bottom-6 right-6 z-50 glass-panel border border-blue-500/40 bg-slate-900/95 p-4 rounded-2xl shadow-2xl flex items-center justify-between gap-4 max-w-md animate-in slide-in-from-bottom duration-300">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-100 flex items-center gap-2">
                Decision Recorded: <span className="text-blue-400">{toast.status}</span>
              </p>
              {onGoToHistory && (
                <button
                  onClick={() => {
                    setToast({ visible: false, status: "" });
                    onGoToHistory();
                  }}
                  className="text-xs text-blue-400 hover:text-blue-300 font-semibold underline flex items-center gap-1 mt-0.5"
                >
                  View in Review History <ExternalLink className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>

          <button
            onClick={() => setToast({ visible: false, status: "" })}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Background Accent glow */}
      <div className="absolute -right-20 -top-20 w-60 h-60 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header section */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider mb-1">
            <span>{result.contract_id}</span>
            <span>•</span>
            <span>{result.category}</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            Review Outcome
          </h2>
        </div>

        {/* Risk Badge */}
        <div className={`flex items-center gap-2.5 px-4 py-2 rounded-xl border font-bold text-sm ${badge.bg}`}>
          {badge.icon}
          <span>{result.risk_level}</span>
        </div>
      </div>

      {/* Evidence & Standard Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Contract Evidence */}
        <div className="glass-card rounded-xl p-4 border border-slate-800/80 space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <FileText className="w-4 h-4 text-blue-400" />
            Contract Evidence
          </div>
          {result.contract_evidence ? (
            <p className="text-sm italic text-slate-200 bg-slate-950/40 p-3 rounded-lg border border-slate-800/50 leading-relaxed">
              "{result.contract_evidence}"
            </p>
          ) : (
            <p className="text-sm text-slate-500 italic bg-slate-950/40 p-3 rounded-lg border border-slate-800/50">
              No clause found in this contract excerpt.
            </p>
          )}
        </div>

        {/* Company Standard */}
        <div className="glass-card rounded-xl p-4 border border-slate-800/80 space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            Company Standard
          </div>
          {result.standard_text ? (
            <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/50 space-y-1">
              <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider block">
                Standard ID: {result.standard_id}
              </span>
              <p className="text-sm text-slate-300 leading-relaxed">{result.standard_text}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-500 italic bg-slate-950/40 p-3 rounded-lg border border-slate-800/50">
              N/A — not applicable for Not Enough Information.
            </p>
          )}
        </div>
      </div>

      {/* Reason Explanation Box */}
      <div className="glass-card rounded-xl p-4 border border-slate-800/80 space-y-2 bg-gradient-to-r from-slate-900/80 to-slate-900/40">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <span className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" />
            Deterministic Reasoning
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Source: {result.source}</span>
        </div>
        <p className="text-sm text-slate-200 leading-relaxed font-normal">{result.reason}</p>
      </div>

      {/* Non-dismissible Safety Banner */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-center gap-3 text-amber-300 text-xs font-semibold">
        <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
        <div>
          <span>Human Review Required — this is not legal advice.</span>
          <p className="text-[11px] text-amber-400/80 font-normal mt-0.5">
            Every classification must be reviewed and approved by a qualified professional before action is taken.
          </p>
        </div>
      </div>

      {/* Human Decision Action Section */}
      <div className="pt-2 border-t border-slate-800/80 space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-blue-400" />
            Reviewer Feedback / Audit Notes
          </label>
          {result.status !== "pending" && (
            <span className="text-xs px-2.5 py-1 rounded-full font-semibold uppercase bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Current Status: {result.status}
            </span>
          )}
        </div>

        <input
          type="text"
          value={reviewerNote}
          onChange={(e) => setReviewerNote(e.target.value)}
          placeholder="Add comments or escalation notes (e.g. Send to legal for renegotiation)..."
          className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
        />

        <div className="flex flex-wrap gap-3">
          <button
            disabled={submitting}
            onClick={() => handleDecision("approved")}
            className="flex-1 min-w-[120px] bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2.5 px-4 rounded-xl text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-900/20 disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            Approve
          </button>
          <button
            disabled={submitting}
            onClick={() => handleDecision("rejected")}
            className="flex-1 min-w-[120px] bg-rose-600 hover:bg-rose-500 text-white font-medium py-2.5 px-4 rounded-xl text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-rose-900/20 disabled:opacity-50"
          >
            <XCircle className="w-4 h-4" />
            Reject
          </button>
          <button
            disabled={submitting}
            onClick={() => handleDecision("marked_for_review")}
            className="flex-1 min-w-[140px] bg-amber-600 hover:bg-amber-500 text-white font-medium py-2.5 px-4 rounded-xl text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-amber-900/20 disabled:opacity-50"
          >
            <AlertTriangle className="w-4 h-4" />
            Mark for Review
          </button>
        </div>
      </div>
    </div>
  );
}
