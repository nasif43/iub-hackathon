"use client";

import React from "react";
import { ShieldCheck, Cpu, UserCheck, Search, Scale } from "lucide-react";

export function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      {/* Hero Banner */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 relative overflow-hidden text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4" /> Safety First Architecture
        </div>
        <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight">
          Contract Review Assistant
        </h2>
        <p className="text-slate-300 text-sm max-w-2xl mx-auto leading-relaxed">
          Designed with non-negotiable architectural safety invariants for contract analysis in enterprise legal workflows.
        </p>
      </div>

      {/* Core Principles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Search className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-100 text-base">1. Verbatim Evidence</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Risk classifications require explicit, direct quotes from source contract text. If information is missing, the system abstains rather than hallucinates.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-100 text-base">2. Rule Engine Driven</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            All risk evaluation logic is derived deterministically by explicit code comparators against company standards. Generative LLMs never compute risk levels.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <UserCheck className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-100 text-base">3. Mandatory Human Review</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Every output mandates professional human verification. This tool assists decision-makers and is not legal advice.
          </p>
        </div>
      </div>

      {/* Official Disclaimer Box */}
      <div className="glass-panel p-6 rounded-2xl border border-amber-500/20 bg-amber-500/5 space-y-2">
        <h4 className="text-sm font-bold text-amber-400 flex items-center gap-2">
          <Scale className="w-4 h-4" /> Official Hackathon Disclaimer
        </h4>
        <p className="text-xs text-slate-300 leading-relaxed">
          The Contract Review Assistant is an analytical tool built to highlight deviations between contract excerpts and defined company benchmarks. It does not replace legal counsel. All audit trail records persist reviewer feedback to ensure complete transparency.
        </p>
      </div>
    </div>
  );
}
