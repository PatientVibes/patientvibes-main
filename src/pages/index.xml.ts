import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export const prerender = true;

export async function GET(context: APIContext) {
  const notes = await getCollection('notes', e => !e.data.draft);
  const sorted = notes.sort((a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime());

  return rss({
    title: 'patientvibes — notes',
    description: 'A workshop for patient things. Notes on agents, the tools they need, and the harnesses that keep them honest.',
    site: context.site!,
    items: sorted.map(e => ({
      title: e.data.title,
      link: `/notes/${e.id.replace(/\.md$/, '')}/`,
      pubDate: e.data.pubDate,
      description: e.data.summary,
      author: 'chris.paul.moore@gmail.com (Chris Moore)',
    })),
    customData: '<language>en-us</language>',
  });
}
