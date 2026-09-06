export const API_BASE = '/api/v1'
export const FETCH_TIMEOUT_MS = 30_000

export const OPENROUTER_MODELS = [
  { value: '', label: 'Auto-select (recommended)' },
  { value: 'google/gemma-3-27b-it:free', label: 'Gemma 3 27B (Free)' },
  { value: 'qwen/qwen-2.5-7b-instruct:free', label: 'Qwen 2.5 7B Instruct (Free)' },
  { value: 'meta-llama/llama-3.1-8b-instruct:free', label: 'Llama 3.1 8B (Free)' },
  { value: 'openai/gpt-4o-mini', label: 'GPT-4o Mini' },
] as const

export const GEMINI_MODELS = [
  { value: 'gemini-2.5-flash-lite', label: 'Gemini 2.5 Flash Lite' },
  { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
] as const

export const OLLAMA_MODELS = [
  { value: 'qwen2.5:7b', label: 'Qwen 2.5 7B (local)' },
] as const

export const LLM_PROVIDERS = [
  { value: 'gemini', label: 'Gemini (primary)' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'ollama', label: 'Ollama (local)' },
  { value: 'ollama_remote', label: 'Ollama (remote)' },
] as const

export const TOPOLOGIES = [
  { value: 'auto', label: 'Auto-detect (recommended)' },
  { value: 'sequential', label: 'Sequential (pipeline)' },
  { value: 'parallel', label: 'Parallel (fork-join)' },
  { value: 'supervisor', label: 'Supervisor (hierarchy)' },
  { value: 'swarm', label: 'Swarm (peer handoff)' },
] as const

export const PIPELINE_NODES = [
  { key: 'query_analyzer', label: 'Query Analyzer', icon: 'Search' },
  { key: 'similarity_retriever', label: 'Similarity Search', icon: 'SearchCode' },
  { key: 'needs_assessment', label: 'Needs Assessment', icon: 'ClipboardList' },
  { key: 'skill_creator', label: 'Skill Creator', icon: 'Hammer' },
  { key: 'sandbox_validator', label: 'Sandbox Validator', icon: 'FlaskConical' },
  { key: 'ai_final_filter', label: 'AI Final Filter', icon: 'Target' },
  { key: 'docker_mcp_runner', label: 'Docker MCP Runner', icon: 'Container' },
  { key: 'template_builder', label: 'Template Builder', icon: 'ClipboardList' },
  { key: 'final_output', label: 'Final Output', icon: 'Package' },
] as const
