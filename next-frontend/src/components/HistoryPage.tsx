"use client";

import React, { useEffect, useState } from "react";
import { ReviewResult } from "../types/api";
import { fetchReviews } from "../lib/api";
import { History, Filter, CheckCircle2, XCircle, AlertTriangle, Clock, ExternalLink, ChevronRight } from "lucide-react";

interface HistoryPageProps {
  onSelectReview: (review: ReviewResult) => void;
}

export function HistoryPage({ onSelectReview }: HistoryPageProps) {
  const [reviews, setReviews] = useState<ReviewResult[]>([]);
  const [filterContract, setFilterContract] = useState("");
  const [filterStatus, setFilterStatus] = useState("All");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    const data = await fetchReviews(filterContract, filterStatus);
    setReviews(data);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [filterContract, filterStatus]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3 h-3" /> Approved</span>;
      case "rejected":
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20"><XCircle className="w-3 h-3" /> Rejected</span>;
      case "marked_for_review":
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20"><AlertTriangle className="w-3 h-3" /> Flagged</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20"><Clock className="w-3 h-3" /> Pending</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <History className="w-6 h-6 text-blue-400" />
          Audit Trail & History
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Click any review record to inspect its evidence in the Review Studio and update human reviewer decisions.
        </p>
      </div>

      {/* Filters Bar */}
      <div className="glass-panel p-4 rounded-xl flex flex-wrap items-center justify-between gap-4 border border-slate-800">
        <div className="flex flex-wrap items-center gap-4 flex-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <Filter className="w-4 h-4 text-blue-400" /> Filters
          </div>

          <input
            type="text"
            placeholder="Filter by Contract ID (e.g. C-001)..."
            value={filterContract}
            onChange={(e) => setFilterContract(e.target.value)}
            className="bg-slate-950/80 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 w-64"
          />

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-slate-950/80 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="All">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="marked_for_review">Marked for Review</option>
          </select>
        </div>

        <button
          onClick={loadData}
          className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg transition"
        >
          Refresh Log
        </button>
      </div>

      {/* Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                <th className="p-4">ID</th>
                <th className="p-4">Contract</th>
                <th className="p-4">Category</th>
                <th className="p-4">Risk Level</th>
                <th className="p-4">Status</th>
                <th className="p-4">Reviewer Note</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-sm">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500">
                    Loading audit records...
                  </td>
                </tr>
              ) : reviews.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500">
                    No reviews found matching criteria.
                  </td>
                </tr>
              ) : (
                reviews.map((r) => (
                  <tr 
                    key={r.review_id} 
                    onClick={() => onSelectReview(r)}
                    className="hover:bg-blue-950/20 transition cursor-pointer group"
                  >
                    <td className="p-4 font-mono text-xs text-slate-400">#{r.review_id}</td>
                    <td className="p-4 font-bold text-blue-400 group-hover:text-blue-300">{r.contract_id}</td>
                    <td className="p-4 text-slate-200 font-medium">{r.category}</td>
                    <td className="p-4">
                      <span className={`text-xs font-semibold ${
                        r.risk_level === "High Risk" ? "text-rose-400" :
                        r.risk_level === "Medium Risk" ? "text-amber-400" :
                        r.risk_level === "Low Risk" ? "text-emerald-400" : "text-slate-400"
                      }`}>
                        {r.risk_level}
                      </span>
                    </td>
                    <td className="p-4">{getStatusBadge(r.status)}</td>
                    <td className="p-4 text-xs text-slate-300 max-w-xs truncate">
                      {r.reviewer_note || <span className="text-slate-600 italic">No notes added</span>}
                    </td>
                    <td className="p-4 text-right">
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-blue-400 group-hover:translate-x-0.5 transition-transform">
                        Inspect <ChevronRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
