import { defineConfig } from 'astro/config';
import remarkGfm from 'remark-gfm';
import remarkObsidian from 'remark-obsidian';
import rehypeRaw from 'rehype-raw';

export default defineConfig({
  site: 'https://kitchen.kaleb.one',
  output: 'static',
  integrations: [],
  markdown: {
    remarkPlugins: [remarkGfm, remarkObsidian],
    rehypePlugins: [rehypeRaw],
  },
});