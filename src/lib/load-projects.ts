import { readFile } from 'node:fs/promises';
import path from 'node:path';

export interface Project {
  id: string;
  kind: 'tool' | 'harness' | 'skill';
  name: string;
  status: string;
  last_run: string;
  summary: string;
  url: string;
  githubUrl: string;
}

interface Catalog {
  generatedAt: string;
  count: number;
  projects: Project[];
}

let cached: Catalog | null = null;

export async function loadProjects(): Promise<Catalog> {
  if (cached) return cached;
  const cachePath = path.resolve(process.cwd(), '.cache/projects.json');
  const raw = await readFile(cachePath, 'utf-8');
  cached = JSON.parse(raw);
  return cached!;
}

export function byKind(projects: Project[], kind: Project['kind']): Project[] {
  return projects.filter(p => p.kind === kind);
}

// Maps catalog status → display state + label.
// 'dev' or version tags (v1.x) → live; 'unavailable' → draft/offline; everything else → build.
export function displayStatus(status: string): { state: 'live' | 'build' | 'draft' | 'shipped'; label: string } {
  if (status === 'unavailable') return { state: 'draft', label: 'offline' };
  if (status === 'fixture') return { state: 'draft', label: 'fixture' };
  if (status === 'dev' || status.startsWith('v')) return { state: 'live', label: status };
  return { state: 'build', label: status };
}

// Pretty-print an ISO timestamp as "2026 · 04".
export function formatYearMonth(iso: string): string {
  const d = new Date(iso);
  return `${d.getUTCFullYear()} · ${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
}

// Build a short id like "T–01", "H–01", "S–01" from kind + 1-based index.
export function shortId(kind: Project['kind'], index1: number): string {
  const letter = kind === 'tool' ? 'T' : kind === 'harness' ? 'H' : 'S';
  return `${letter}–${String(index1).padStart(2, '0')}`;
}
