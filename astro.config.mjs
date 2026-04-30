import { defineConfig } from 'astro/config';
import remarkGfm from 'remark-gfm';
import remarkObsidian from 'remark-obsidian';
import rehypeRaw from 'rehype-raw';

export default defineConfig({
  site: 'https://kitchen.kaleb.one',
  output: 'static',
  integrations: [],
  build: {
    format: 'file',
  },
  markdown: {
    remarkPlugins: [remarkGfm, remarkObsidian],
    // rehype-raw is intentional: vault Obsidian markdown contains embedded HTML
    // (tables, details/summary, iframes) that must be preserved
    rehypePlugins: [rehypeRaw],
  },
});