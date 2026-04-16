# Wood Home Cooking

A personal meal prep knowledge base and recipe library for Kaleb & Minny.

Built around managing Gout and Fatty Liver through intentional weekly cooking — not restriction, just smart defaults.

## Architecture

**Source of Truth:** `triursa/second-brain-vault` → `domains/cooking/`

This repo contains the generated HTML site. Content is pulled from the Obsidian vault's cooking domain and rendered using `scripts/build.py` — a static site generator that:

1. Reads markdown files from the vault's `domains/cooking/` structure
2. Parses frontmatter (title, status, tags) and inline metadata (serves, calories, Gout/Liver ratings)
3. Generates styled HTML pages with the amber/dark kitchen aesthetic
4. Outputs to the root for Cloudflare Pages deployment

### Sections

| Vault Path | Site Path | Content |
|-----------|-----------|---------|
| `recipes/*.md` | `/recipes/` | 9 recipes with nutrition facts, health ratings, batch cook instructions |
| `meal-plans/*.md` | `/meal-plans/` | Monthly and weekly plans with grocery lists |
| `grocery-lists/*.md` | `/grocery-lists/` | Master and weekly grocery lists with interactive checkboxes |
| `knowledge-base/*.md` | `/knowledge-base/` | Health notes, ingredient guides, dietary preferences |

## Deployment

- **Host:** Cloudflare Pages (`kitchen` project)
- **Domain:** `kitchen.kaleb.one` (CNAME proxied through Cloudflare)
- **Access:** Zero Trust — `kaleb.bays@gmail.com` + `melindajean16@gmail.com`
- **Auth:** Google SSO or one-time email PIN

### To rebuild and deploy:

```bash
# Clone vault
git clone https://github.com/triursa/second-brain-vault.git /tmp/second-brain-vault

# Build
VAULT_DIR=/tmp/second-brain-vault/domains/cooking python3 scripts/build.py

# Deploy
CLOUDFLARE_API_TOKEN=$CF_TOKEN CLOUDFLARE_ACCOUNT_ID=$ACCOUNT_ID \
  npx wrangler pages deploy /tmp/kitchen-site --project-name=kitchen --branch=main
```

## Tech

- Python static site generator (`scripts/build.py`)
- Cloudflare Pages + Zero Trust Access
- Written and maintained with Claude across conversations
- Primary cooking appliance: **Ninja Crispi Pro 4-qt**
- Primary stores: **HEB** (weekly), **Costco / Sam's Club** (bulk)

## Conventions

Every recipe card includes:
- Serving size + estimated nutrition per serving
- Gout-Friendly rating (1–5 ★)
- Fatty Liver-Friendly rating (1–5 ★)
- Ninja Crispi Pro instructions where applicable
- Meal prep and storage notes