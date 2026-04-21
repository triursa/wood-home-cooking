#!/usr/bin/env python3
"""
Build script for kitchen.kaleb.one
Reads markdown from second-brain-vault/domains/cooking/ and generates styled HTML.
Keeps the same amber/dark kitchen aesthetic.
"""

import os
import re
import yaml
import html
from pathlib import Path

VAULT_DIR = os.environ.get("VAULT_DIR", "/tmp/second-brain-vault/domains/cooking")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/tmp/kitchen-site")

# ── Helpers ──────────────────────────────────────────────────────────────

def read_md(path):
    """Read markdown file, return (frontmatter_dict, body_str)."""
    with open(path) as f:
        content = f.read()
    if content.startswith("---"):
        _, fm_str, body = content.split("---", 2)
        try:
            fm = yaml.safe_load(fm_str)
        except yaml.YAMLError:
            fm = {}
        return fm or {}, body.strip()
    return {}, content.strip()

def md_to_html(md_text):
    """Simple markdown-to-HTML converter for vault content."""
    # Handle horizontal rules
    md_text = re.sub(r'^---$', '<hr>', md_text, flags=re.MULTILINE)
    
    # Headers (must come before other processing)
    md_text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', md_text, flags=re.MULTILINE)
    
    # Tables
    lines = md_text.split('\n')
    result = []
    in_table = False
    table_rows = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            # Skip separator rows (|---|---|)
            if re.match(r'^\|[\s\-:|]+\|$', stripped):
                continue
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            table_rows.append(cells)
            in_table = True
        else:
            if in_table and table_rows:
                result.append(render_table(table_rows))
                table_rows = []
                in_table = False
            result.append(line)
    
    if table_rows:
        result.append(render_table(table_rows))
    
    md_text = '\n'.join(result)
    
    # Checkbox list items: - [ ] or - [x]
    md_text = re.sub(
        r'^- \[([ x])\] (.+)$',
        lambda m: f'<li class="grocery-item"><input type="checkbox" data-id="{hash(m.group(2)) % 10000}" {"checked" if m.group(1) == "x" else ""}><label>{inline_md(m.group(2))}</label></li>',
        md_text,
        flags=re.MULTILINE
    )
    
    # Unordered list items (non-checkbox)
    md_text = re.sub(
        r'^- (.+)$',
        lambda m: f'<li>{inline_md(m.group(1))}</li>',
        md_text,
        flags=re.MULTILINE
    )
    
    # Ordered list items
    md_text = re.sub(
        r'^(\d+)\. (.+)$',
        lambda m: f'<li value="{m.group(1)}">{inline_md(m.group(2))}</li>',
        md_text,
        flags=re.MULTILINE
    )
    
    # Block-level paragraph wrapping
    # Only wrap lines that aren't already HTML tags or empty
    out_lines = []
    for line in md_text.split('\n'):
        stripped = line.strip()
        if not stripped:
            out_lines.append('')
        elif stripped.startswith('<'):
            out_lines.append(line)
        else:
            out_lines.append(f'<p>{inline_md(stripped)}</p>')
    
    return '\n'.join(out_lines)

def render_table(rows):
    """Convert list of row-lists to HTML table."""
    if not rows:
        return ''
    html_str = '<div class="plan-table-wrapper"><table class="plan-table">\n'
    # First row = header
    html_str += '<thead><tr>'
    for cell in rows[0]:
        html_str += f'<th>{inline_md(cell)}</th>'
    html_str += '</tr></thead>\n'
    # Rest = body
    html_str += '<tbody>\n'
    for row in rows[1:]:
        html_str += '<tr>'
        for i, cell in enumerate(row):
            cls = ' class="day-cell"' if i == 0 else ''
            html_str += f'<td{cls}>{inline_md(cell)}</td>'
        html_str += '</tr>\n'
    html_str += '</tbody></table></div>\n'
    return html_str

def inline_md(text):
    """Process inline markdown: bold, italic, code, links."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Links [text](url)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    # Arrow links: text →
    text = re.sub(r'(\w[\w\s]*?)\s*→', r'<a href="#" class="link-arrow">\1 →</a>', text)
    # Star ratings: ★★★★☆
    text = re.sub(r'([★☆]+)', r'<span class="stars">\1</span>', text)
    return text

def esc(text):
    """HTML escape."""
    return html.escape(str(text))

def page_html(title, body_html, section=""):
    """Wrap content in the full page HTML with header/footer."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
<script src="/assets/js/main.js"></script>
<main>
  <div class="site-wrapper">
{body_html}
  </div>
</main>
</body>
</html>"""


# ── Recipe Parser ──────────────────────────────────────────────────────────

def parse_recipe(fm, body):
    """Parse a recipe markdown into structured data for HTML rendering."""
    title = fm.get("title", "").replace(" | Wood Home Cooking", "")
    
    data = {
        "title": title,
        "slug": "",
        "status": fm.get("status", "active"),
        "tags": fm.get("tags", []),
        "serves": "",
        "calories": "",
        "cook_method": "",
        "gout_stars": "",
        "gout_note": "",
        "liver_stars": "",
        "liver_note": "",
        "nutrition": {},
        "raw_body": body,
    }
    
    lines = body.split('\n')
    
    # Find H1 and parse its content
    for i, line in enumerate(lines):
        if line.strip().startswith('# '):
            h1_content = line.strip()[2:]
            
            # Serves: from H1 (authoritative, overrides bold-line template)
            m = re.search(r'Serves:\s*(\d+[-–]?\d*)', h1_content)
            if m:
                data["serves"] = m.group(1)
            
            # Cook: from H1 - capture just the method, stop before Gout
            m = re.search(r'Cook:\s*(.+?)(?:\s+Gout|$)', h1_content)
            if m:
                data["cook_method"] = m.group(1).strip()
            elif 'Prep:' in h1_content:
                m = re.search(r'Prep:\s*(.+?)(?:\s+Gout|$)', h1_content)
                if m:
                    data["cook_method"] = m.group(1).strip()
            
            # Also check next few lines for Cook: (garlic-herb-beef pattern)
            if not data["cook_method"]:
                for j in range(i+1, min(i+5, len(lines))):
                    nl = lines[j].strip()
                    m = re.search(r'Cook:\s*(.+?)$', nl)
                    if m:
                        data["cook_method"] = m.group(1).strip()
                        break
            
            # Gout-Friendly: from H1
            m = re.search(r'Gout-Friendly\s*(★+☆*)\s*(.*?)(?:Fatty|\s*$)', h1_content)
            if m:
                data["gout_stars"] = m.group(1)
                data["gout_note"] = m.group(2).strip().rstrip('.')
            
            # Liver-Friendly: from H1
            m = re.search(r'Fatty\s+Liver-Friendly\s*(★+☆*)\s*(.*?)$', h1_content)
            if m:
                data["liver_stars"] = m.group(1)
                data["liver_note"] = m.group(2).strip().rstrip('.')
            
            # If not found on H1, check subsequent lines
            if not data["gout_stars"]:
                for j in range(i+1, min(i+8, len(lines))):
                    l = lines[j].strip()
                    if l.startswith('## '):
                        break
                    m = re.search(r'Gout-Friendly\s*(★+☆*)\s*(.*)', l)
                    if m:
                        data["gout_stars"] = m.group(1)
                        data["gout_note"] = m.group(2).strip().rstrip('.')
                    m = re.search(r'Fatty\s+Liver-Friendly\s*(★+☆*)\s*(.*)', l)
                    if m:
                        data["liver_stars"] = m.group(1)
                        data["liver_note"] = m.group(2).strip().rstrip('.')
            break
    
    # Parse nutrition from ## Nutrition section (authoritative calorie source)
    in_nutrition = False
    for line in lines:
        s = line.strip()
        if s.startswith('## Nutrition'):
            in_nutrition = True
            continue
        if in_nutrition:
            if s.startswith('## ') or s.startswith('# '):
                break
            # Pipe-separated: ~360 Calories | ~36g Protein | ...
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                for part in parts:
                    part = part.strip()
                    m = re.match(r'~?(\d+[-–]?\d*)\s*(Calories|calories)', part)
                    if m:
                        data["nutrition"]["Calories"] = m.group(1)
                        data["calories"] = m.group(1)
                    m = re.match(r'~?(\d+\.?\d*\s*g)\s*(Protein|Carbs|Fat|Fiber|Sugar)', part)
                    if m:
                        data["nutrition"][m.group(2)] = m.group(1)
                    m = re.match(r'~?(\d+\s*mg)\s*(Sodium)', part)
                    if m:
                        data["nutrition"]["Sodium"] = m.group(1)
            # Space-separated: "~420 Calories ~52g Protein ~1g Carbs ..."
            elif 'Calories' in line:
                tokens = re.findall(r'~?(\d+[-–]?\d*(?:\.\d+)?(?:\s*g|\s*mg)?)\s*(Calories|Protein|Carbs|Fat|Fiber|Sugar|Sodium)', line)
                for val, key in tokens:
                    data["nutrition"][key] = val
                    if key == "Calories":
                        data["calories"] = val
    
    return data

def recipe_card_html(data, href):
    """Generate a recipe card for the index page."""
    # Determine label from cook method and tags
    label_parts = []
    if data.get("cook_method"):
        if "Crispi" in data["cook_method"]:
            label_parts.append("Ninja Crispi")
        elif "Stovetop" in data["cook_method"]:
            label_parts.append("Stovetop")
        elif "stovetop" in data["cook_method"].lower():
            label_parts.append("Stovetop")
        else:
            label_parts.append(data["cook_method"])
    if any(t == "recipe" for t in data.get("tags", [])):
        # Try to determine protein/veggie/breakfast
        title_lower = data["title"].lower()
        if any(w in title_lower for w in ["chicken", "beef", "shrimp", "egg"]):
            label_parts.append("Protein")
        elif any(w in title_lower for w in ["veggie", "veggies"]):
            label_parts.append("Veggie")
        elif any(w in title_lower for w in ["oats", "breakfast"]):
            label_parts.append("Breakfast")
    
    label = " · ".join(label_parts) if label_parts else "Recipe"
    
    cal_text = ""
    if data.get("calories"):
        cal_text = f"~{data['calories']} cal"
    
    serves_text = f"{data['serves']} servings" if data.get("serves") else ""
    
    gout_stars = data.get("gout_stars", "")
    liver_stars = data.get("liver_stars", "")
    
    meta_parts = [p for p in [serves_text, cal_text] if p]
    meta_html = '<span>' + '</span><span>'.join(meta_parts) + '</span>' if meta_parts else ''
    
    ratings_html = ''
    if gout_stars or liver_stars:
        ratings_html = f'''
        <div class="card-ratings">
          <div class="mini-rating">Gout <span class="stars">{gout_stars}</span></div>
          <div class="mini-rating">Liver <span class="stars">{liver_stars}</span></div>
        </div>'''
    
    return f'''<a href="{esc(href)}" class="card">
        <div class="card-label">{esc(label)}</div>
        <div class="card-title">{esc(data['title'])}</div>
        <div class="card-meta">{meta_html}</div>
        {ratings_html}
      </a>'''


def parse_recipe_sections(body_md):
    """Extract named sections from recipe body. Returns dict of section_name -> list of lines."""
    sections = {}
    current = "intro"
    sections[current] = []
    
    for line in body_md.split('\n'):
        m = re.match(r'^##\s+(.+)$', line.strip())
        if m:
            current = m.group(1).strip()
            sections[current] = []
        else:
            sections[current].append(line)
    
    return sections


def build_ingredients_html(lines):
    """Convert ingredient markdown lines into structured ing-rows, supporting sub-groups."""
    html_parts = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Sub-group header (### or bold standalone line)
        m = re.match(r'^###\s+(.+)$', stripped)
        if m:
            html_parts.append(f'<div class="ing-group-label">{esc(m.group(1))}</div>')
            continue
        # Ingredient row: - [amount] name or - name, amount
        m = re.match(r'^[-*]\s+(.+)$', stripped)
        if m:
            item = m.group(1).strip()
            # Try to split "Name – amount" or "Name, amount" or "amount name"
            # Pattern: leading quantity then name
            qty_match = re.match(r'^([\d/\.\s]+(?:g|ml|oz|lb|cup|cups|tbsp|tsp|clove|cloves|piece|pieces|slice|slices|whole|large|medium|small|handful|pinch|dash|to taste|as needed)[^\w]*)(.+)$', item, re.IGNORECASE)
            if qty_match:
                amount = qty_match.group(1).strip().rstrip(',').strip()
                name = qty_match.group(2).strip()
            else:
                # try "Name – qty" split
                dash_match = re.split(r'\s+[–—-]{1,2}\s+', item, maxsplit=1)
                if len(dash_match) == 2:
                    name, amount = dash_match[0].strip(), dash_match[1].strip()
                else:
                    name, amount = item, ""
            html_parts.append(
                f'<div class="ing-row">'
                f'<span class="ing-name">{inline_md(name)}</span>'
                + (f'<span class="ing-amount">{esc(amount)}</span>' if amount else '')
                + '</div>'
            )
            continue
        # Fallback: render as plain paragraph
        if stripped and not stripped.startswith('#'):
            html_parts.append(f'<p>{inline_md(stripped)}</p>')
    
    return '\n'.join(html_parts)


def build_steps_html(lines):
    """Convert step markdown lines into step-card divs."""
    steps = []
    step_num = 0
    current_text = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_text:
                steps.append(' '.join(current_text))
                current_text = []
            continue
        # Ordered list item
        m = re.match(r'^\d+\.\s+(.+)$', stripped)
        if m:
            if current_text:
                steps.append(' '.join(current_text))
                current_text = []
            current_text = [m.group(1)]
            continue
        # Unordered list item
        m = re.match(r'^[-*]\s+(.+)$', stripped)
        if m:
            if current_text:
                steps.append(' '.join(current_text))
                current_text = []
            current_text = [m.group(1)]
            continue
        # Continuation line
        if current_text:
            current_text.append(stripped)
        else:
            current_text = [stripped]
    
    if current_text:
        steps.append(' '.join(current_text))
    
    html_parts = []
    for i, step in enumerate(steps, 1):
        if step.strip():
            html_parts.append(
                f'<div class="step-card">'
                f'<div class="step-num">{i}</div>'
                f'<div class="step-text">{inline_md(step)}</div>'
                f'</div>'
            )
    
    return '\n'.join(html_parts)


def build_nutrition_card_html(nutrition):
    """Build the nutrition grid card."""
    if not nutrition:
        return ""
    
    # Preferred display order
    order = ["Calories", "Protein", "Carbs", "Fat", "Fiber", "Sugar", "Sodium"]
    cells = []
    for key in order:
        if key in nutrition:
            cells.append(
                f'<div class="nutrition-cell">'
                f'<span class="n-value">{esc(nutrition[key])}</span>'
                f'<span class="n-label">{esc(key)}</span>'
                f'</div>'
            )
    # Any remaining keys
    for key, val in nutrition.items():
        if key not in order:
            cells.append(
                f'<div class="nutrition-cell">'
                f'<span class="n-value">{esc(val)}</span>'
                f'<span class="n-label">{esc(key)}</span>'
                f'</div>'
            )
    
    return f'<div class="nutrition-grid">{"".join(cells)}</div>'


def recipe_page_html(data, back_href="/"):
    """Generate a full recipe detail page with split-column layout."""
    # ── Label
    label_parts = []
    if "Crispi" in data.get("cook_method", ""):
        label_parts.append("Ninja Crispi")
    elif "Stovetop" in data.get("cook_method", ""):
        label_parts.append("Stovetop")
    title_lower = data["title"].lower()
    if any(w in title_lower for w in ["chicken", "beef", "shrimp", "egg"]):
        label_parts.append("Protein")
    elif any(w in title_lower for w in ["veggie", "veggies"]):
        label_parts.append("Veggie")
    elif any(w in title_lower for w in ["oats", "breakfast"]):
        label_parts.append("Breakfast")
    label = " · ".join(label_parts) if label_parts else ""
    
    # ── Meta badges
    badge_items = []
    if data.get("serves"):
        badge_items.append(f'<span class="meta-badge">Serves {esc(data["serves"])}</span>')
    if data.get("calories"):
        badge_items.append(f'<span class="meta-badge">~{esc(data["calories"])} cal</span>')
    if data.get("cook_method"):
        badge_items.append(f'<span class="meta-badge">{esc(data["cook_method"])}</span>')
    meta_html = f'<div class="meta-badges">{"".join(badge_items)}</div>' if badge_items else ''
    
    # ── Parse body into sections
    body_md = data["raw_body"]
    body_md = re.sub(r'^# .+\n', '', body_md, count=1)
    body_md = re.sub(r'^←.*\n', '', body_md, count=1)
    
    sections = parse_recipe_sections(body_md)
    
    # ── Find ingredient section (flexible key matching)
    ing_lines = []
    steps_lines = []
    other_sections = []
    
    for sec_name, sec_lines in sections.items():
        lower = sec_name.lower()
        if lower in ('ingredients', 'ingredient list', 'what you need', 'you will need'):
            ing_lines = sec_lines
        elif lower in ('instructions', 'directions', 'steps', 'method', 'how to make it', 'preparation'):
            steps_lines = sec_lines
        elif lower == 'intro':
            pass  # skip intro metadata lines
        else:
            other_sections.append((sec_name, sec_lines))
    
    # ── Build left column: ingredients
    left_html = ""
    ing_body = build_ingredients_html(ing_lines) if ing_lines else ""
    if ing_body:
        left_html = f'''<div class="recipe-section-card">
          <div class="recipe-section-label">Ingredients</div>
          {ing_body}
        </div>'''
    
    # ── Build right column: nutrition + ratings
    right_parts = []
    
    # Nutrition
    nutr_html = build_nutrition_card_html(data.get("nutrition", {}))
    if nutr_html:
        right_parts.append(f'''<div class="recipe-section-card">
          <div class="recipe-section-label">Nutrition / serving</div>
          {nutr_html}
        </div>''')
    
    # Ratings
    gout_html = ""
    if data.get("gout_stars"):
        gout_html = f'''<div class="rating-pill">
          <div class="pill-label">Gout-Friendly</div>
          <div class="pill-stars">{data["gout_stars"]}</div>
          <div class="pill-note">{esc(data.get("gout_note", ""))}</div>
        </div>'''
    liver_html = ""
    if data.get("liver_stars"):
        liver_html = f'''<div class="rating-pill">
          <div class="pill-label">Fatty Liver</div>
          <div class="pill-stars">{data["liver_stars"]}</div>
          <div class="pill-note">{esc(data.get("liver_note", ""))}</div>
        </div>'''
    
    if gout_html or liver_html:
        right_parts.append(f'''<div class="recipe-section-card">
          <div class="recipe-section-label">Health Ratings</div>
          <div class="ratings-inner">{gout_html}{liver_html}</div>
        </div>''')
    
    right_html = '\n'.join(right_parts)
    
    # ── Split layout
    split_html = ""
    if left_html or right_html:
        split_html = f'''<div class="recipe-split">
      <div class="recipe-column">{left_html}</div>
      <div class="recipe-column">{right_html}</div>
    </div>'''
    
    # ── Steps section
    steps_html = ""
    step_cards = build_steps_html(steps_lines) if steps_lines else ""
    if step_cards:
        steps_html = f'''<div class="recipe-steps-section">
      <h2>Instructions</h2>
      {step_cards}
    </div>'''
    
    # ── Other sections (timing, notes, etc.)
    other_html_parts = []
    for sec_name, sec_lines in other_sections:
        lower = sec_name.lower()
        sec_content_md = '\n'.join(sec_lines)
        if lower == 'nutrition':
            continue  # already rendered
        elif lower in ('notes', 'chef notes', 'tips'):
            # Render as notes-box
            inner = build_ingredients_html(sec_lines)
            other_html_parts.append(f'''<div class="notes-box">
          <div class="notes-title">{esc(sec_name)}</div>
          <ul>{"".join(f"<li>{inline_md(l.strip().lstrip('-').strip())}</li>" for l in sec_lines if l.strip() and l.strip() not in ("",))}</ul>
        </div>''')
        elif lower in ('timing', 'time breakdown', 'prep time'):
            other_html_parts.append(f'<h2>{esc(sec_name)}</h2>' + md_to_html(sec_content_md))
        else:
            other_html_parts.append(f'<h2>{esc(sec_name)}</h2>' + md_to_html(sec_content_md))
    
    other_html = '\n'.join(other_html_parts)
    
    return f'''
    <a href="{esc(back_href)}" class="back-link">← Recipes</a>
    <div class="page-header">
      <div class="page-label">{esc(label)}</div>
      <h1>{esc(data['title'])}</h1>
      {meta_html}
    </div>
    {split_html}
    {steps_html}
    {other_html}'''


# ── Build ──────────────────────────────────────────────────────────────────

def build():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Copy CSS and JS assets
    assets_css = os.path.join(OUTPUT_DIR, "assets", "css")
    assets_js = os.path.join(OUTPUT_DIR, "assets", "js")
    os.makedirs(assets_css, exist_ok=True)
    os.makedirs(assets_js, exist_ok=True)
    
    # Write the CSS (same styling) — look for it relative to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    site_root = os.path.dirname(script_dir)  # scripts/ -> repo root
    css_path = os.path.join(site_root, "assets", "css", "style.css")
    if not os.path.exists(css_path):
        css_path = os.path.join(script_dir, "assets", "css", "style.css")
    with open(css_path) as f:
        css = f.read()
    with open(os.path.join(assets_css, "style.css"), "w") as f:
        f.write(css)
    
    # Write JS - update BASE to '/' since we're on a custom domain
    js = """// Shared layout injection
(function() {
  const BASE = '';
  const root = '/';
  const path = window.location.pathname;

  function r(p) { return root + p; }

  function isActive(section) {
    return path.includes('/' + section + '/') ? 'class="active"' : '';
  }

  const header = `
<header class="site-header">
  <div class="site-wrapper">
    <a href="${root}" class="site-title">Wood Home Cooking <span>/ Kaleb &amp; Minny</span></a>
    <nav>
      <a href="${r('recipes/')}" ${isActive('recipes')}>Recipes</a>
      <a href="${r('meal-plans/')}" ${isActive('meal-plans')}>Meal Plans</a>
      <a href="${r('grocery-lists/')}" ${isActive('grocery-lists')}>Grocery Lists</a>
      <a href="${r('knowledge-base/')}" ${isActive('knowledge-base')}>Guidelines</a>
    </nav>
  </div>
</header>`;

  const footer = `
<footer>
  <div class="site-wrapper">
    Wood Home Cooking &mdash; Kaleb &amp; Minny &mdash; Kyle, TX
  </div>
</footer>`;

  document.body.insertAdjacentHTML('afterbegin', header);
  document.body.insertAdjacentHTML('beforeend', footer);

  // Grocery checkbox persistence (session only — resets when tab closes)
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.grocery-list input[type="checkbox"]').forEach(cb => {
      const key = 'g_' + path + '_' + cb.dataset.id;
      if (sessionStorage.getItem(key) === '1') {
        cb.checked = true;
        cb.closest('li').classList.add('checked');
      }
      cb.addEventListener('change', () => {
        cb.closest('li').classList.toggle('checked', cb.checked);
        cb.checked ? sessionStorage.setItem(key, '1') : sessionStorage.removeItem(key);
      });
    });
    const btn = document.querySelector('.reset-btn');
    if (btn) btn.addEventListener('click', () => {
      document.querySelectorAll('.grocery-list input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
        cb.closest('li').classList.remove('checked');
        sessionStorage.removeItem('g_' + path + '_' + cb.dataset.id);
      });
    });
  });
})();"""
    with open(os.path.join(assets_js, "main.js"), "w") as f:
        f.write(js)
    
    # ── Index page ──
    index_html = build_index()
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(index_html)
    
    # ── Recipe pages ──
    recipes = build_recipes()
    
    # ── Meal plan pages ──
    meal_plans = build_meal_plans()
    
    # ── Grocery list pages ──
    grocery_lists = build_grocery_lists()
    
    # ── Knowledge base pages ──
    knowledge_base = build_knowledge_base()
    
    # Write .nojekyll
    with open(os.path.join(OUTPUT_DIR, ".nojekyll"), "w") as f:
        f.write("")
    
    print(f"\n✅ Built {OUTPUT_DIR}/")
    print(f"   Recipes: {len(recipes)}")
    print(f"   Meal Plans: {len(meal_plans)}")
    print(f"   Grocery Lists: {len(grocery_lists)}")
    print(f"   Knowledge Base: {len(knowledge_base)}")

def build_index():
    """Build the main dashboard page."""
    # Collect recipe cards
    recipes_dir = os.path.join(VAULT_DIR, "recipes")
    recipe_cards = []
    recipe_data = []
    
    if os.path.isdir(recipes_dir):
        for fname in sorted(os.listdir(recipes_dir)):
            if not fname.endswith('.md') or fname == 'index.md':
                continue
            fpath = os.path.join(recipes_dir, fname)
            fm, body = read_md(fpath)
            if fm.get("status") == "active" and "recipe" in fm.get("tags", []):
                data = parse_recipe(fm, body)
                slug = fname.replace('.md', '')
                data["slug"] = slug
                recipe_data.append(data)
                href = f"/recipes/{slug}.html"
                recipe_cards.append(recipe_card_html(data, href))
    
    # Collect meal plan cards
    meal_plan_cards = []
    mp_dir = os.path.join(VAULT_DIR, "meal-plans")
    if os.path.isdir(mp_dir):
        for fname in sorted(os.listdir(mp_dir), reverse=True):
            if not fname.endswith('.md') or fname == 'index.md':
                continue
            fpath = os.path.join(mp_dir, fname)
            fm, body = read_md(fpath)
            if fm.get("status") == "active" and "meal-plan" in fm.get("tags", []):
                title = fm.get("title", "").replace(" | Wood Home Cooking", "")
                # Extract month/year from filename
                slug = fname.replace('.md', '')
                # Parse metadata from body
                week_match = re.search(r'Week\s+(\d+)', title) or re.search(r'Week\s+(\d+)', body[:200])
                cal_match = re.search(r'1,800.*?2,000\s+cal', body[:500])
                batch_match = re.search(r'Monday\s+batch\s+cook', body[:500], re.IGNORECASE)
                
                meta_parts = []
                if week_match:
                    meta_parts.append(f"Week {week_match.group(1)} logged")
                if cal_match:
                    meta_parts.append("1,800–2,000 cal/day")
                if batch_match:
                    meta_parts.append("Monday batch cook")
                meta_html = '<span>' + '</span><span>'.join(meta_parts) + '</span>' if meta_parts else ''
                
                # Determine label (monthly vs weekly)
                if re.match(r'\d{4}-\d{2}$', slug):
                    label = "Monthly Plan"
                else:
                    label = "Weekly Plan"
                
                href = f"/meal-plans/{slug}.html"
                meal_plan_cards.append(f'''<a href="{esc(href)}" class="card">
          <div class="card-label">{esc(label)}</div>
          <div class="card-title">{esc(title)}</div>
          <div class="card-meta">{meta_html}</div>
        </a>''')
    
    # Collect grocery list cards
    grocery_cards = []
    gl_dir = os.path.join(VAULT_DIR, "grocery-lists")
    if os.path.isdir(gl_dir):
        for fname in sorted(os.listdir(gl_dir)):
            if not fname.endswith('.md') or fname == 'index.md':
                continue
            fpath = os.path.join(gl_dir, fname)
            fm, body = read_md(fpath)
            if fm.get("status") == "active" and "grocery" in fm.get("tags", []):
                title = fm.get("title", "").replace(" | Wood Home Cooking", "")
                slug = fname.replace('.md', '')
                
                # Determine store type from content
                stores = []
                if "Costco" in body or "Sam's" in body:
                    stores.append("Costco/Sam's")
                if "HEB" in body or "H-E-B" in body:
                    stores.append("HEB")
                
                label = " · ".join(stores) if stores else "Grocery List"
                store_text = " + ".join([s + " spices" if s == "HEB" else s for s in stores]) if stores else ""
                
                href = f"/grocery-lists/{slug}.html"
                grocery_cards.append(f'''<a href="{esc(href)}" class="card">
          <div class="card-label">{esc(label)}</div>
          <div class="card-title">{esc(title)}</div>
          <div class="card-meta"><span>{esc(store_text)}</span></div>
        </a>''')
    
    # Build the HTML
    recipes_section = ""
    if recipe_cards:
        recipes_section = f'''
    <h2>Recipe Library</h2>
    <div class="card-grid">
      {chr(10).join(recipe_cards)}
    </div>'''
    
    mealplans_section = ""
    if meal_plan_cards:
        mealplans_section = f'''
    <h2>Meal Plans</h2>
    <div class="card-grid">
      {chr(10).join(meal_plan_cards)}
    </div>'''
    
    grocery_section = ""
    if grocery_cards:
        grocery_section = f'''
    <h2>Grocery Lists</h2>
    <div class="card-grid">
      {chr(10).join(grocery_cards)}
    </div>'''
    
    body = f'''
    <div class="hero">
      <h1 class="hero-title">Wood Home<br><em>Cooking</em></h1>
      <p class="hero-sub">Kaleb &amp; Minny's weekly meal prep system. Built around the Ninja Crispi Pro, Monday batch cook, and eating well with Gout and Fatty Liver in mind.</p>
      <div class="badge-row">
        <span class=\"badge clay\">1,800–2,000 cal / day</span>
        <span class="badge">Monday batch cook</span>
        <span class="badge">Gout &amp; Fatty Liver friendly</span>
      </div>
    </div>
    {recipes_section}
    {mealplans_section}
    {grocery_section}'''
    
    return page_html("Wood Home Cooking", body)

def build_recipes():
    """Build individual recipe pages."""
    recipes_dir = os.path.join(VAULT_DIR, "recipes")
    out_dir = os.path.join(OUTPUT_DIR, "recipes")
    os.makedirs(out_dir, exist_ok=True)
    
    built = []
    if not os.path.isdir(recipes_dir):
        return built
    
    # Build recipe index page
    index_fm, index_body = read_md(os.path.join(recipes_dir, "index.md"))
    index_title = index_fm.get("title", "Recipes").replace(" | Wood Home Cooking", "")
    index_html = md_to_html(index_body) if index_body else ""
    
    for fname in sorted(os.listdir(recipes_dir)):
        if not fname.endswith('.md') or fname == 'index.md':
            continue
        fpath = os.path.join(recipes_dir, fname)
        fm, body = read_md(fpath)
        if fm.get("status") != "active" or "recipe" not in fm.get("tags", []):
            continue
        
        data = parse_recipe(fm, body)
        slug = fname.replace('.md', '')
        html_content = recipe_page_html(data, back_href="/recipes/")
        full_html = page_html(data["title"] + " | Wood Home Cooking", html_content, section="recipes")
        
        with open(os.path.join(out_dir, f"{slug}.html"), "w") as f:
            f.write(full_html)
        built.append(slug)
    
    # Recipe index page
    # Collect cards for the index
    recipe_cards = []
    for fname in sorted(os.listdir(recipes_dir)):
        if not fname.endswith('.md') or fname == 'index.md':
            continue
        fpath = os.path.join(recipes_dir, fname)
        fm, body = read_md(fpath)
        if fm.get("status") == "active" and "recipe" in fm.get("tags", []):
            data = parse_recipe(fm, body)
            slug = fname.replace('.md', '')
            recipe_cards.append(recipe_card_html(data, f"/recipes/{slug}.html"))
    
    cards_html = f'''
    <h2>All Recipes</h2>
    <div class="card-grid">
      {chr(10).join(recipe_cards)}
    </div>'''
    
    index_full = page_html(index_title + " | Wood Home Cooking", cards_html, section="recipes")
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(index_full)
    
    return built

def build_meal_plans():
    """Build meal plan pages."""
    mp_dir = os.path.join(VAULT_DIR, "meal-plans")
    out_dir = os.path.join(OUTPUT_DIR, "meal-plans")
    os.makedirs(out_dir, exist_ok=True)
    
    built = []
    if not os.path.isdir(mp_dir):
        return built
    
    for fname in sorted(os.listdir(mp_dir), reverse=True):
        if not fname.endswith('.md') or fname == 'index.md':
            continue
        fpath = os.path.join(mp_dir, fname)
        fm, body = read_md(fpath)
        # Include all meal plans regardless of status/tag strictness
        
        title = fm.get("title", "").replace(" | Wood Home Cooking", "")
        if not title:
            title = fname.replace('.md', '').replace('-', ' ').title()
        slug = fname.replace('.md', '')
        
        # Convert markdown to HTML
        # Remove "← Meal Plans" navigation line
        clean_body = re.sub(r'^←.*\n', '', body, count=1)
        body_html = md_to_html(clean_body)
        
        # Determine label
        label = "Monthly Plan" if re.match(r'\d{4}-\d{2}$', slug) else "Weekly Plan"
        
        html_content = f'''
    <a href="/meal-plans/" class="back-link">← Meal Plans</a>
    <div class="page-header">
      <div class="page-label">{esc(label)}</div>
      <h1>{esc(title)}</h1>
    </div>
    {body_html}'''
        
        full_html = page_html(title + " | Wood Home Cooking", html_content, section="meal-plans")
        with open(os.path.join(out_dir, f"{slug}.html"), "w") as f:
            f.write(full_html)
        built.append(slug)
    
    # Meal plans index
    cards = []
    for fname in sorted(os.listdir(mp_dir), reverse=True):
        if not fname.endswith('.md') or fname == 'index.md':
            continue
        fpath = os.path.join(mp_dir, fname)
        fm, body = read_md(fpath)
        title = fm.get("title", "").replace(" | Wood Home Cooking", "")
        if not title:
            title = fname.replace('.md', '').replace('-', ' ').title()
        slug = fname.replace('.md', '')
        label = "Monthly Plan" if re.match(r'\d{4}-\d{2}$', slug) else "Weekly Plan"
        cards.append(f'''<a href="/meal-plans/{esc(slug)}.html" class="card">
          <div class="card-label">{esc(label)}</div>
          <div class="card-title">{esc(title)}</div>
        </a>''')
    
    cards_html = f'''
    <h2>Meal Plans</h2>
    <div class="card-grid">
      {chr(10).join(cards)}
    </div>'''
    
    index_html = page_html("Meal Plans | Wood Home Cooking", cards_html, section="meal-plans")
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(index_html)
    
    return built

def build_grocery_lists():
    """Build grocery list pages."""
    gl_dir = os.path.join(VAULT_DIR, "grocery-lists")
    out_dir = os.path.join(OUTPUT_DIR, "grocery-lists")
    os.makedirs(out_dir, exist_ok=True)
    
    built = []
    if not os.path.isdir(gl_dir):
        return built
    
    for fname in sorted(os.listdir(gl_dir)):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(gl_dir, fname)
        fm, body = read_md(fpath)
        # Skip index and OLD files; include everything else regardless of tags
        if fname == 'index.md' or fname.startswith('OLD_'):
            continue
        
        title = fm.get("title", "").replace(" | Wood Home Cooking", "")
        if not title:
            title = fname.replace('.md', '').replace('-', ' ').title()
        slug = fname.replace('.md', '')
        
        # Process grocery list markdown
        # Replace ## sections with grocery-section divs
        body_html = md_to_html(body)
        
        # Wrap list items in grocery-list ul
        # Find all consecutive <li class="grocery-item"> and wrap them
        body_html = re.sub(
            r'(<li class="grocery-item">.*?</li>(?:\s*<li class="grocery-item">.*?</li>)+)',
            lambda m: '<ul class="grocery-list">' + m.group(1) + '</ul>',
            body_html,
            flags=re.DOTALL
        )
        
        # Add reset button
        reset_btn = '<button class="reset-btn">Reset all checkboxes</button>'
        
        html_content = f'''
    <a href="/grocery-lists/" class="back-link">← Grocery Lists</a>
    <div class="page-header">
      <div class="page-label">Grocery List</div>
      <h1>{esc(title)}</h1>
    </div>
    {reset_btn}
    {body_html}'''
        
        full_html = page_html(title + " | Wood Home Cooking", html_content, section="grocery-lists")
        with open(os.path.join(out_dir, f"{slug}.html"), "w") as f:
            f.write(full_html)
        built.append(slug)
    
    # Grocery index
    cards = []
    for fname in sorted(os.listdir(gl_dir)):
        if not fname.endswith('.md') or fname == 'index.md' or fname.startswith('OLD_'):
            continue
        fpath = os.path.join(gl_dir, fname)
        fm, body = read_md(fpath)
        title = fm.get("title", "").replace(" | Wood Home Cooking", "")
        if not title:
            title = fname.replace('.md', '').replace('-', ' ').title()
        slug = fname.replace('.md', '')
        stores = []
        with open(fpath) as f:
            content = f.read()
        if "Costco" in content or "Sam's" in content:
            stores.append("Costco/Sam's")
        if "HEB" in content or "H-E-B" in content:
            stores.append("HEB")
        label = " · ".join(stores) if stores else "Grocery"
        cards.append(f'''<a href="/grocery-lists/{esc(slug)}.html" class="card">
          <div class="card-label">{esc(label)}</div>
          <div class="card-title">{esc(title)}</div>
        </a>''')
    
    cards_html = f'''
    <h2>Grocery Lists</h2>
    <div class="card-grid">
      {chr(10).join(cards)}
    </div>'''
    
    index_html = page_html("Grocery Lists | Wood Home Cooking", cards_html, section="grocery-lists")
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(index_html)
    
    return built

def build_knowledge_base():
    """Build knowledge base pages."""
    kb_dir = os.path.join(VAULT_DIR, "knowledge-base")
    out_dir = os.path.join(OUTPUT_DIR, "knowledge-base")
    os.makedirs(out_dir, exist_ok=True)
    
    built = []
    if not os.path.isdir(kb_dir):
        return built
    
    cards = []
    for fname in sorted(os.listdir(kb_dir)):
        if not fname.endswith('.md') or fname == 'index.md':
            continue
        fpath = os.path.join(kb_dir, fname)
        fm, body = read_md(fpath)
        # KB files may lack frontmatter; include them all
        
        title = fm.get("title", "").replace(" | Wood Home Cooking", "")
        if not title:
            # Derive from filename
            title = fname.replace('.md', '').replace('-', ' ').title()
        slug = fname.replace('.md', '')
        
        body_html = md_to_html(body)
        
        html_content = f'''
    <a href="/knowledge-base/" class="back-link">← Guidelines</a>
    <div class="page-header">
      <div class="page-label">Knowledge Base</div>
      <h1>{esc(title)}</h1>
    </div>
    {body_html}'''
        
        full_html = page_html(title + " | Wood Home Cooking", html_content, section="knowledge-base")
        with open(os.path.join(out_dir, f"{slug}.html"), "w") as f:
            f.write(full_html)
        built.append(slug)
        
        cards.append(f'''<a href="/knowledge-base/{esc(slug)}.html" class="card">
          <div class="card-label">Guideline</div>
          <div class="card-title">{esc(title)}</div>
        </a>''')
    
    # KB index
    cards_html = f'''
    <h2>Guidelines &amp; Knowledge Base</h2>
    <div class="card-grid">
      {chr(10).join(cards)}
    </div>'''
    
    index_html = page_html("Guidelines | Wood Home Cooking", cards_html, section="knowledge-base")
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(index_html)
    
    return built

if __name__ == "__main__":
    build()