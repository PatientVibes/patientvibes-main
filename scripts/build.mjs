// Static site: copy site/ to dist/ (Cloudflare Pages output dir), then stamp the
// data URLs in index.html with a version so a new page never reads cached old data.
import { cpSync, rmSync, readFileSync, writeFileSync } from 'node:fs';
rmSync('dist', { recursive: true, force: true });
cpSync('site', 'dist', { recursive: true });
const v = (process.env.CF_PAGES_COMMIT_SHA || Date.now().toString(36)).slice(0, 10);
const html = readFileSync('dist/index.html', 'utf8');
const stamped = html.replace(/'data\/([\w.]+\.json|[\w.]+\.geojson)'/g, `'data/$1?v=${v}'`);
if (stamped === html) throw new Error('build: no data URLs found to version');
writeFileSync('dist/index.html', stamped);
console.log(`copied site/ -> dist/, data version ${v}`);
