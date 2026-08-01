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
  Loader2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  RefreshCw,
  Zap
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"review" | "history" | "about">("review");
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [clausesMap, setClausesMap] = useState<Record<string, Clause>>({});
  const [activeCategory, setActiveCategory] = useState<string>(CATEGORIES[0]);
  
  // Store all review results for the active contract: category -> ReviewResult
  const [allReviewResults, setAllReviewResults] = useState<Record<string, ReviewResult>>({});
  
  const [loadingContracts, setLoadingContracts] = useState(true);
  const [analyzingAll, setAnalyzingAll] = useState(false);

  // Load contract list on mount
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

  // Autonomous batch review runner whenever selected contract changes
  useEffect(() => {
    if (!selectedContract) return;

    let isMounted = true;
    async function runBatchAnalysis() {
      setAnalyzingAll(true);
      setAllReviewResults({});

      // 1. Fetch detected clauses map for contract
      if (!selectedContract) return;
      const contractId = selectedContract.id;
      const map = await fetchContractClauses(contractId);
      if (!isMounted) return;
      setClausesMap(map);

      // 2. Autonomously execute reviews for all 7 fixed categories in parallel
      const results: Record<string, ReviewResult> = {};
      const promises = CATEGORIES.map(async (cat) => {
        const res = await runReview(contractId, cat);
        if (res) {
          results[cat] = res;
        }
      });

      await Promise.all(promises);
      if (isMounted) {
        setAllReviewResults(results);
        setAnalyzingAll(false);
      }
    }

    runBatchAnalysis();

    return () => {
      isMounted = false;
    };
  }, [selectedContract]);

  // Handle direct navigation from Review History table to Review Studio
  const handleSelectReviewFromHistory = (review: ReviewResult) => {
    const foundContract = contracts.find((c) => c.id === review.contract_id);
    if (foundContract) {
      setSelectedContract(foundContract);
    }
    setActiveCategory(review.category);
    setAllReviewResults((prev) => ({
      ...prev,
      [review.category]: review,
    }));
    setActiveTab("review");
  };

  const getRiskBadgeSmall = (risk?: string) => {
    switch (risk) {
      case "Low Risk":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3 h-3" /> Low Risk</span>;
      case "Medium Risk":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20"><AlertTriangle className="w-3 h-3" /> Medium Risk</span>;
      case "High Risk":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20"><XCircle className="w-3 h-3" /> High Risk</span>;
      case "Not Enough Information":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-500/10 text-slate-400 border border-slate-500/20"><HelpCircle className="w-3 h-3" /> Not Enough Info</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-800 text-slate-400"><Loader2 className="w-3 h-3 animate-spin" /> Evaluating...</span>;
    }
  };

  const activeResult = allReviewResults[activeCategory];

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        {activeTab === "review" && (
          <div className="space-y-8">
            {/* Target Contract Selection Panel - Full Width */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3 w-full">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-blue-400" />
                  Select Target Contract To Review
                </span>
                {analyzingAll && (
                  <span className="flex items-center gap-1 text-[10px] text-blue-400 font-bold animate-pulse">
                    <Loader2 className="w-3 h-3 animate-spin" /> Batch Reviewing All 7 Clauses
                  </span>
                )}
              </label>

              {loadingContracts ? (
                <div className="h-12 bg-slate-900 animate-pulse rounded-xl" />
              ) : (
                <select
                  value={selectedContract?.id || ""}
                  onChange={(e) => {
                    const found = contracts.find((c) => c.id === e.target.value);
                    if (found) {
                      setSelectedContract(found);
                    }
                  }}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text.base font-semibold text-slate-100 focus:outline-none focus:border-blue-500 transition cursor-pointer"
                >
                  {contracts.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.id} — {c.title} ({c.parties})
                    </option>
                  ))}
                </select>
              )}

              {selectedContract && (
                <div className="pt-2 text-xs text-slate-400 flex flex-wrap items-center justify-between gap-2 border-t border-slate-800/50">
                  <p className="font-semibold text-slate-200">{selectedContract.title}</p>
                  <p className="text-slate-400">Parties: <span className="text-slate-300">{selectedContract.parties}</span></p>
                </div>
              )}
            </div>

            {/* Autonomous Overview Grid: All 7 Categories At A Glance */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  <Layers className="w-4 h-4 text-blue-400" />
                  Autonomous Risk Matrix Overview (7 Fixed Clauses)
                </div>
                {analyzingAll && (
                  <span className="text-xs text-blue-400 flex items-center gap-2 bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" /> Evaluating all 7 clause categories...
                  </span>
                )}
              </div>

              {/* 7 Category Cards Overview Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {CATEGORIES.map((cat) => {
                  const res = allReviewResults[cat];
                  const isSelected = activeCategory === cat;
                  const clauseInfo = clausesMap[cat];
                  const isAbsent = clauseInfo && !clauseInfo.present;

                  return (
                    <button
                      key={cat}
                      onClick={() => setActiveCategory(cat)}
                      className={`glass-card p-4 rounded-xl border text-left transition duration-200 flex flex-col justify-between h-28 ${
                        isSelected
                          ? "border-blue-500 bg-blue-950/30 shadow-lg shadow-blue-500/10 ring-1 ring-blue-500/50"
                          : "border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/60"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-xs font-bold text-slate-200 line-clamp-1">{cat}</span>
                        {isAbsent && (
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 shrink-0">
                            Absent
                          </span>
                        )}
                      </div>

                      <div className="mt-2">
                        {analyzingAll && !res ? (
                          <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                            <Loader2 className="w-3 h-3 animate-spin text-blue-400" />
                            <span>Analyzing...</span>
                          </div>
                        ) : (
                          getRiskBadgeSmall(res?.risk_level)
                        )}
                      </div>

                      <span className="text-[10px] text-slate-500 flex items-center justify-between pt-1 border-t border-slate-800/40">
                        <span>Click to inspect details</span>
                        <ChevronRight className="w-3 h-3 text-slate-500" />
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Detailed Result Inspection Card */}
            <div className="pt-2">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  Detailed Clause Inspection: <span className="text-blue-400">{activeCategory}</span>
                </h3>
              </div>

              {analyzingAll && !activeResult ? (
                <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center space-y-3">
                  <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto text-blue-400" />
                  <p className="text-sm text-slate-300 font-medium">Running deterministic rule evaluation for {activeCategory}...</p>
                  <p className="text-xs text-slate-500">Extracting numeric facts and checking verbatim contract quotes against company standards.</p>
                </div>
              ) : activeResult ? (
                <ResultCard
                  result={activeResult}
                  onDecisionUpdated={(updated) => {
                    setAllReviewResults((prev) => ({
                      ...prev,
                      [activeCategory]: updated,
                    }));
                  }}
                  onGoToHistory={() => setActiveTab("history")}
                />
              ) : (
                <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center text-slate-500 text-sm">
                  Select a contract above to trigger autonomous review.
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "history" && (
          <HistoryPage onSelectReview={handleSelectReviewFromHistory} />
        )}

        {activeTab === "about" && <AboutPage />}
      </main>
    </div>
  );
}
