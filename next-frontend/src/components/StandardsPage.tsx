"use client";

import React, { useEffect, useState } from "react";
import { Standard } from "@/types/api";
import { fetchStandards, createStandard } from "@/lib/api";
import { Scale, Plus, AlertCircle, Loader2 } from "lucide-react";

export function StandardsPage() {
  const [standards, setStandards] = useState<Standard[]>([]);
  const [loading, setLoading] = useState(true);
  const [id, setId] = useState("");
  const [category, setCategory] = useState("");
  const [text, setText] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    const data = await fetchStandards();
    setStandards(data);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !category || !text) {
      setError("Please fill out all fields.");
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);

    const res = await createStandard(id, category, text);
    setSaving(false);

    if (res) {
      setSuccess(`Standard '${id}' successfully saved!`);
      setId("");
      setCategory("");
      setText("");
      load();
      // Auto-reload to update categories list on next reload or page transition
      if (typeof window !== "undefined") {
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      }
    } else {
      setError("Failed to save standard. Check if ID or Category is unique/valid.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      {/* Page Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2">
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Scale className="w-5 h-5 text-blue-400" />
          Manage Company Standards
        </h2>
        <p className="text-xs text-slate-400">
          Define standard expectations and compliance guidelines. Adding a standard dynamically creates a new review category.
        </p>
      </div>

      {/* Define New Standard Form */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Plus className="w-4 h-4 text-emerald-400" />
          Define a New Standard & Category
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold">Standard ID</label>
              <input
                type="text"
                value={id}
                onChange={(e) => setId(e.target.value)}
                placeholder="e.g. STD-IND-01"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-slate-400 font-semibold">Category Name</label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g. Indemnification"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs text-slate-400 font-semibold">Standard Text Guidelines</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="e.g. Both parties should protect each other's custom works..."
              rows={4}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 text-xs text-rose-400 bg-rose-500/10 p-3 rounded-lg border border-rose-500/20">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          {success && (
            <div className="text-xs text-emerald-400 bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20">
              {success}
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-slate-100 text-sm font-semibold rounded-xl transition flex items-center gap-2 disabled:opacity-50"
          >
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Saving...
              </>
            ) : (
              "Save Standard"
            )}
          </button>
        </form>
      </div>

      {/* Existing Standards List */}
      <div className="space-y-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Currently Configured Standards
        </h3>

        {loading ? (
          <div className="flex items-center gap-2 text-sm text-slate-400 p-8 glass-panel rounded-2xl border border-slate-800 justify-center">
            <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
            Loading company standards...
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {standards.map((std) => (
              <div key={std.id} className="glass-card p-5 rounded-2xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between border-b border-slate-800/40 pb-2">
                  <span className="text-xs font-bold text-blue-400">{std.category}</span>
                  <span className="text-[10px] font-bold text-slate-500 bg-slate-900 px-2 py-0.5 rounded-md border border-slate-800">
                    {std.id}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{std.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
