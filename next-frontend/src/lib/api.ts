import { Contract, Clause, ReviewResult, ReviewDecisionRequest } from "../types/api";

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
