import { Contract, Clause, ReviewResult, ReviewDecisionRequest, Standard, QuestionResult } from "../types/api";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";


export async function fetchContracts(): Promise<Contract[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/contracts`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("fetchContracts error:", error);
    return [];
  }
}

export async function fetchContractClauses(contractId: string): Promise<Record<string, Clause>> {
  try {
    const res = await fetch(`${BACKEND_URL}/contracts/${contractId}/clauses`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data: Clause[] = await res.json();
    const clauseMap: Record<string, Clause> = {};
    data.forEach((c) => {
      clauseMap[c.category] = c;
    });
    return clauseMap;
  } catch (error) {
    console.error("fetchContractClauses error:", error);
    return {};
  }
}

export async function runReview(contractId: string, category: string): Promise<ReviewResult | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contract_id: contractId, category }),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("runReview error:", error);
    return null;
  }
}

export async function fetchReviews(contractId?: string, status?: string): Promise<ReviewResult[]> {
  try {
    const url = new URL(`${BACKEND_URL}/reviews`);
    if (contractId) url.searchParams.append("contract_id", contractId);
    if (status && status !== "All") url.searchParams.append("status", status);

    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("fetchReviews error:", error);
    return [];
  }
}

export async function recordDecision(
  reviewId: number,
  decision: ReviewDecisionRequest
): Promise<ReviewResult | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/reviews/${reviewId}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(decision),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("recordDecision error:", error);
    return null;
  }
}

export async function uploadContract(
  title: string,
  parties: string,
  rawText: string
): Promise<Contract | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/contracts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, parties, raw_text: rawText }),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("uploadContract error:", error);
    return null;
  }
}

export async function createStandard(
  id: string,
  category: string,
  text: string
): Promise<Standard | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/standards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, category, text }),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("createStandard error:", error);
    return null;
  }
}

export async function fetchStandards(): Promise<Standard[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/standards`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("fetchStandards error:", error);
    return [];
  }
}

export async function askQuestion(
  contractId: string,
  question: string
): Promise<QuestionResult | null> {
  try {
    const res = await fetch(`${BACKEND_URL}/questions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contract_id: contractId, question }),
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error("askQuestion error:", error);
    return null;
  }
}


