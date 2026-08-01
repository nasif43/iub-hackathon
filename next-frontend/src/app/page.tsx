"use client";

import React, { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { ResultCard } from "@/components/ResultCard";
import { HistoryPage } from "@/components/HistoryPage";
import { AboutPage } from "@/components/AboutPage";
import { Contract, Clause, ReviewResult, CATEGORIES } from "@/types/api";
import { fetchContracts, fetchContractClauses, runReview } from "@/lib/api";
import { 
  FileCheck2, 
  Sparkles, 
  ChevronRight, 
  Building2, 
  Layers, 
  Info,
  Play
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"review" | "history" | "about">("review");
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [clausesMap, setClausesMap] = useState<Record<string, Clause>>({});
  const [activeCategory, setActiveCategory] = useState<string>(CATEGORIES[0]);
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null);
  const [loadingContracts, setLoadingContracts] = useState(true);
  const [reviewing, setReviewing] = useState(false);

  // Load contracts on mount
  useEffect(() => {
    async function load() {
      setLoadingContracts(true);
      const data = await fetchContracts();
      setContracts(data);
      if (data.length > 0) {
        setSelectedContract(data[0]);
      }
      setLoadingContracts(false);
    }
    load();
  }, []);

  // Fetch clauses when selected contract changes
  useEffect(() => {
    if (!selectedContract) return;
    async function loadClauses() {
      const map = await fetchContractClauses(selectedContract.id);
      setClausesMap(map);
    }
    loadClauses();
  }, [selectedContract]);

  const handleRunReview = async (category: string) => {
    if (!selectedContract) return;
    setReviewing(true);
    const result = await runReview(selectedContract.id, category);
    setReviewResult(result);
    setReviewing(false);
  };

  const selectedClause = clausesMap[activeCategory];
  const isPresent = selectedClause ? selectedClause.present : true;

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        {activeTab === "review" && (
          <div className="space-y-8">
            {/* Top Workspace Header */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Contract Selector Panel */}
              <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3 md:col-span-1">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-blue-400" />
                  Select Target Contract
                </label>
                {loadingContracts ? (
                  <div className="h-10 bg-slate-900 animate-pulse rounded-xl" />
                ) : (
                  <select
                    value={selectedContract?.id || ""}
                    onChange={(e) => {
                      const found = contracts.find((c) => c.id === e.target.value);
                      if (found) {
                        setSelectedContract(found);
                        setReviewResult(null);
                      }
                    }}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm font-medium text-slate-100 focus:outline-none focus:border-blue-500 transition cursor-pointer"
                  >
                    {contracts.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.id} — {c.title}
                      </option>
                    ))}
                  </select>
                )}

                {selectedContract && (
                  <div className="pt-2 text-xs text-slate-400 space-y-1">
                    <p className="font-semibold text-slate-300 truncate">{selectedContract.title}</p>
                    <p className="text-slate-400 truncate">Parties: {selectedContract.parties}</p>
                  </div>
                )}
              </div>

              {/* Demo Shortcut Quick-Select Cards */}
              <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3 md:col-span-2 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider flex items-center gap-2">
                      <Sparkles className="w-4 h-4" /> Demo Flow Shortcuts
                    </span>
                    <span className="text-[10px] text-slate-500">Hackathon Verification Specs</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Quickly switch between Happy Path (C-001 High Risk) and Abstention Path (C-004 Not Enough Info).
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                  <button
                    onClick={() => {
                      const c1 = contracts.find((c) => c.id === "C-001");
                      if (c1) {
                        setSelectedContract(c1);
                        setActiveCategory("Automatic Renewal");
                        handleRunReview("Automatic Renewal");
                      }
                    }}
                    className="glass-card p-3 rounded-xl border border-slate-800 hover:border-blue-500/50 text-left transition group"
                  >
                    <div className="flex items-center justify-between text-xs font-bold text-slate-200">
                      <span>C-001 (Happy Path)</span>
                      <ChevronRight className="w-4 h-4 text-blue-400 group-hover:translate-x-1 transition-transform" />
                    </div>
                    <span className="text-[11px] text-rose-400 font-semibold block mt-0.5">High Risk • Automatic Renewal</span>
                  </button>

                  <button
                    onClick={() => {
                      const c4 = contracts.find((c) => c.id === "C-004");
                      if (c4) {
                        setSelectedContract(c4);
                        setActiveCategory("Automatic Renewal");
                        handleRunReview("Automatic Renewal");
                      }
                    }}
                    className="glass-card p-3 rounded-xl border border-slate-800 hover:border-indigo-500/50 text-left transition group"
                  >
                    <div className="flex items-center justify-between text-xs font-bold text-slate-200">
                      <span>C-004 (Abstention MI-01)</span>
                      <ChevronRight className="w-4 h-4 text-indigo-400 group-hover:translate-x-1 transition-transform" />
                    </div>
                    <span className="text-[11px] text-slate-400 font-semibold block mt-0.5">Not Enough Info • Category Absent</span>
                  </button>
                </div>
              </div>
            </div>

            {/* 7 Category Tabs & Analysis Section */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <Layers className="w-4 h-4 text-blue-400" />
                Select Fixed Clause Category
              </div>

              <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
                {CATEGORIES.map((cat) => {
                  const isActive = activeCategory === cat;
                  const clauseInfo = clausesMap[cat];
                  const clauseAbsent = clauseInfo && !clauseInfo.present;

                  return (
                    <button
                      key={cat}
                      onClick={() => {
                        setActiveCategory(cat);
                        setReviewResult(null);
                      }}
                      className={`px-4 py-2.5 rounded-xl text-xs font-semibold transition whitespace-nowrap flex items-center gap-2 ${
                        isActive
                          ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
                          : "glass-card text-slate-300 hover:text-white hover:bg-slate-800/80 border border-slate-800"
                      }`}
                    >
                      {cat}
                      {clauseAbsent && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700">
                          Absent
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Action Trigger Area */}
              <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                    Category: {activeCategory}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {!isPresent
                      ? "Clause absent from contract excerpt. Demonstrates rule-engine abstention path."
                      : "Clause present. Click to run deterministic fact extraction and benchmark comparator."}
                  </p>
                </div>

                <button
                  disabled={reviewing || !selectedContract}
                  onClick={() => handleRunReview(activeCategory)}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-3 px-6 rounded-xl text-sm transition shadow-xl shadow-blue-600/20 flex items-center gap-2 disabled:opacity-50"
                >
                  <Play className="w-4 h-4 fill-current" />
                  {reviewing ? "Evaluating Rules..." : `Run Review for ${activeCategory}`}
                </button>
              </div>
            </div>

            {/* Result Card Component Output */}
            {reviewResult && (
              <ResultCard
                result={reviewResult}
                onDecisionUpdated={(updated) => setReviewResult(updated)}
              />
            )}
          </div>
        )}

        {activeTab === "history" && <HistoryPage />}

        {activeTab === "about" && <AboutPage />}
      </main>
    </div>
  );
}
