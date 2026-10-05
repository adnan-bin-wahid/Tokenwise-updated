export interface PruneRequest {
  query: string;
  code: string;
  threshold: number;
}

export interface PruneResponse {
  score: number;
  pruned_code: string;
  token_scores: [string, number][];
  kept_frags: number[];
  origin_token_cnt: number;
  left_token_cnt: number;
  model_input_token_cnt: number;
  error_msg: string | null;
  line_scores?: Record<string, number>;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  carbon_models_loaded: boolean;
  device: string | null;
  model_path: string;
}

export interface CarbonEstimateViewModel {
  prefillJoules: number;
  decodeJoules: number;
  totalJoules: number;
  co2Grams: number;
  carbonIntensityGPerKwh: number;
  modelFamily: string;
  prefillRoute: "xgboost_interpolation" | "ridge_extrapolation";
  decodeRoute: "xgboost_interpolation" | "ridge_extrapolation";
  featuresSource: string;
}

export interface CarbonEstimateRequest {
  input_tokens: number;
  output_tokens: number;
  model_name: string;
  model_size_b?: number;
  gpu_type?: string;
  latency_per_input_token_ms?: number;
  latency_per_output_token_ms?: number;
  mmlu_pro_score?: number;
  bbh_score?: number;
  carbon_intensity_g_per_kwh: number;
}

export interface CarbonEstimateResponse {
  prefill_joules: number;
  decode_joules: number;
  total_joules: number;
  co2_grams: number;
  carbon_intensity_g_per_kwh: number;
  model_name: string;
  prefill_route: "xgboost_interpolation" | "ridge_extrapolation";
  decode_route: "xgboost_interpolation" | "ridge_extrapolation";
  features_source: string;
}

export interface CarbonSavingsViewModel {
  prefillJoulesSaved: number;
  decodeJoulesSaved: number;
  totalJoulesSaved: number;
  co2GramsSaved: number;
}

export interface CarbonImpactViewModel {
  carbonBefore?: CarbonEstimateViewModel;
  carbonAfter?: CarbonEstimateViewModel;
  carbonSavings?: CarbonSavingsViewModel;
  carbonStatus?: "pending" | "ready" | "disabled" | "unavailable";
  carbonError?: string;
  carbonBaseline?: "formatted-context" | "source-only";
}

export interface PruneResultViewModel extends CarbonImpactViewModel {
  query: string;
  score: number;
  originalCode: string;
  prunedCode: string;
  originTokenCount: number;
  prunedTokenCount: number;
  modelInputTokenCount: number;
  reductionPercent: number;
  keptFrags: number[];
  lineScores?: Record<string, number>;
  input_trace?: PruningInputTrace;
}

export interface PruningInputTrace {
  mode: "repository" | "selected_file" | "selected_excerpt" | "conversation";
  current_query: string;
  effective_query: string;
  scope: string;
  threshold: number;
  history_text: string;
  history_source: "none" | "supplied_user_context" | "native_scoped_user_turns" | "supplied_replay";
  indexed_files?: number;
  first_line?: number;
}

export interface WorkspacePruneRequest {
  query: string;
  workspace_root: string;
  active_file?: string;
  language: string;
  current_symbol?: string;
  selected_code?: string;
  diagnostics: string[];
  threshold: number;
  local_llm_url?: string;
  local_llm_model?: string;
  token_budget?: number;
  context_hint?: string;
  max_candidates?: number;
}

export interface ContextStrategy {
  id: "all_python" | "selected" | "tokenwise";
  title: string;
  input_tokens: number;
  source_tokens: number;
  files: string[];
  context: string;
  carbon?: CarbonEstimateViewModel;
}

export interface ContextComparison {
  query: string;
  repository_fingerprint: string;
  selection_scope: string;
  methods: ContextStrategy[];
  notes: string[];
  carbonStatus?: "ready" | "disabled" | "unavailable";
  carbonError?: string;
}

export interface WorkspaceFilePruneResult {
  file_path: string;
  relation: string;
  tier: number;
  original_tokens: number;
  pruned_tokens: number;
  score: number;
  pruning_method?: string;
  effective_threshold?: number | null;
  excluded_symbols?: string[];
}

export interface WorkspacePruneResponse extends CarbonImpactViewModel {
  input_trace?: PruningInputTrace | null;
  automatic_context?: {
    query: string;
    timestamp: string;
    elapsed_ms: number;
    event_id?: string;
  };
  raw_context_tokens?: number;
  retained_source_tokens?: number;
  context_overhead_tokens?: number;
  context_mode?: "focused" | "repository_overview";
  context_hint_used?: boolean;
  comparison?: ContextComparison | null;
  indexed_files?: number;
  warnings?: string[];
  structured_goal: {
    task_type?: string;
    objective?: string;
    identifiers?: string[];
    excluded_topics?: string[];
    observed_errors?: string[];
    clarification_required?: boolean;
  };
  unified_prompt: string;
  pruned_tokens: number;
  original_tokens: number;
  files: WorkspaceFilePruneResult[];
  selected_file?: string;
  index_cache_hit?: boolean;
  context_cache_hit?: boolean;
}
