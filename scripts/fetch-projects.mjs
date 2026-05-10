#!/usr/bin/env node
// Fetches https://agents.patientvibes.io/api/projects.json at build time.
// Saves to .cache/projects.json. Falls back to __fixtures__/projects.json
// if the fetch fails (so a Cloudflare build doesn't fail because the
// sibling site is briefly down).
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ENDPOINT = 'https://agents.patientvibes.io/api/projects.json';
const TIMEOUT_MS = 8000;

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cacheDir = path.join(repoRoot, '.cache');
const cachePath = path.join(cacheDir, 'projects.json');
const fixturePath = path.join(repoRoot, '__fixtures__', 'projects.json');

async function main() {
  await mkdir(cacheDir, { recursive: true });

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(ENDPOINT, { signal: controller.signal });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.text();
    JSON.parse(json); // validate it parses
    await writeFile(cachePath, json, 'utf-8');
    console.log(`[fetch-projects] OK · cached ${json.length} bytes from ${ENDPOINT}`);
  } catch (err) {
    clearTimeout(timer);
    console.warn(`[fetch-projects] FAILED (${err.message}) — using fixture`);
    try {
      const fixture = await readFile(fixturePath, 'utf-8');
      JSON.parse(fixture);
      await writeFile(cachePath, fixture, 'utf-8');
      console.log('[fetch-projects] OK · cached from __fixtures__/projects.json');
    } catch (fxErr) {
      console.error(`[fetch-projects] FATAL: no fixture available (${fxErr.message})`);
      process.exit(1);
    }
  }
}

main();
