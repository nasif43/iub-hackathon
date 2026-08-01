export interface Contract {
  id: string;
  title: string;
  parties: string;
}

export interface ContractDetail extends Contract {
  raw_text: string;
  dataset_note: string | null;
}

export interface Clause {
  category: string;
  present: boolean;
  heading: string | null;
  text: string | null;
}

export interface Standard {
  id: string;
  category: string;
  text: string;
}

export interface ReviewResult {
  review_id: number;
  contract_id: string;
  category: string;
  risk_level: "Low Risk" | "Medium Risk" | "High Risk" | "Not Enough Information";
  reason: string;
  contract_evidence: string | null;
  standard_id: string | null;
  standard_text: string | null;
  source: "rule_engine" | "rule_engine+llm";
  status: "pending" | "approved" | "rejected" | "marked_for_review";
  reviewer_note: string | null;
  timestamp?: string;
  human_review: "Required";
}

export interface ReviewDecisionRequest {
  status: "approved" | "rejected" | "marked_for_review";
  reviewer_note?: string;
}

export const CATEGORIES = [
  "Payment",
  "Termination",
  "Data Protection",
  "Confidentiality",
  "Automatic Renewal",
  "Intellectual Property",
  "Limitation of Liability",
] as const;
