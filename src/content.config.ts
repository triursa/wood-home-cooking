import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import path from 'node:path';

const VAULT_DIR = process.env.VAULT_DIR || path.join(process.cwd(), 'local-vault');

const cooking = defineCollection({
  loader: glob({ pattern: '**/*.md', base: VAULT_DIR }),
  schema: z.object({
    title: z.string().optional(),
    status: z.string().default('active'),
    tags: z.array(z.string()).default([]),
    description: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { cooking };