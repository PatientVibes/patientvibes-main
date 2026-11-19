// Static site: copy site/ to dist/ (Cloudflare Pages output dir).
import { cpSync, rmSync } from 'node:fs';
rmSync('dist', { recursive: true, force: true });
cpSync('site', 'dist', { recursive: true });
console.log('copied site/ -> dist/');
