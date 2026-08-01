"use client";

import React, { useEffect, useState } from "react";
import { ReviewResult, CATEGORIES } from "../types/api";
import { fetchReviews } from "../lib/api";
import { History, Filter, CheckCircle2, XCircle, AlertTriangle, Clock, ChevronRight, Search } from "lucide-react";

interface HistoryPageProps {
  onSelectReview: (review: ReviewResult) => void;
}

export function HistoryPage({ onSelectReview }: HistoryPageProps) {
  const [reviews, setReviews] = useState<ReviewResult[]>([]);
  const [filterId, setFilterId] = useState("");
  const [filterContract, setFilterContract] = useState("");
  const [filterCategory, setFilterCategory] = useState("All");
  const [filterRisk, setFilterRisk] = useState("All");
  const [filterStatus, setFilterStatus] = useState("All");
  const [filterNote, setFilterNote] = useState("");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    const data = await fetchReviews(filterContract, filterStatus);
    // Ensure latest reviews are sorted at the top (by review_id descending)
    const sorted = [...data].sort((a, b) => b.review_id - a.review_id);
    setReviews(sorted);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [filterContract, filterStatus]);

  // Client-side filtering across all columns (ID, Contract, Category, Risk Level, Status, Reviewer Note)
  const filteredReviews = reviews.filter((r) => {
    if (filterId && !r.review_id.toString().includes(filterId)) return false;
    if (filterCategory !== "All" && r.category !== filterCategory) return false;
    if (filterRisk !== "All" && r.risk_level !== filterRisk) return false;
    if (filterNote && (!r.reviewer_note || !r.reviewer_note.toLowerCase().includes(filterNote.toLowerCase()))) return false;
    return true;
  });

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
          Review History
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Complete log of all past contract clause reviews. Latest reviews appear at the top. Filterable by any field.
        </p>
      </div>

      {/* Comprehensive Column Filters Bar */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
            <Filter className="w-4 h-4" /> Multi-Column Search & Filters
          </div>
          <button
            onClick={() => {
              setFilterId("");
              setFilterContract("");
              setFilterCategory("All");
              setFilterRisk("All");
              setFilterStatus("All");
              setFilterNote("");
              loadData();
            }}
            className="text-xs text-slate-400 hover:text-white underline transition"
          >
            Clear All Filters
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* ID Filter */}
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">ID</label>
            <input
              type="text"
              placeholder="e.g. 17"
              value={filterId}
              onChange={(e) => setFilterId(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Contract ID Filter */}
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Contract</label>
            <input
              type="text"
              placeholder="e.g. C-001"
              value={filterContract}
              onChange={(e) => setFilterContract(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Category Filter */}
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Category</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="All">All Categories</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Risk Level Filter */}
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Risk Level</label>
            <select
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="All">All Risks</option>
              <option value="Low Risk">Low Risk</option>
              <option value="Medium Risk">Medium Risk</option>
              <option value="High Risk">High Risk</option>
              <option value="Not Enough Information">Not Enough Info</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value="All">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="marked_for_review">Marked for Review</option>
            </select>
          </div>

          {/* Reviewer Note Filter */}
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Reviewer Note</label>
            <input
              type="text"
              placeholder="Search note text..."
              value={filterNote}
              onChange={(e) => setFilterNote(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
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
                    Loading review history...
                  </td>
                </tr>
              ) : filteredReviews.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500">
                    No reviews found matching filters.
                  </td>
                </tr>
              ) : (
                filteredReviews.map((r) => (
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
