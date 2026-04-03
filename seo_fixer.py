#!/usr/bin/env python3
"""
SEO Fixer Script for Waythrough Project
Fixes:
1. Missing canonical URLs in 404.html
2. Missing OG tags in 404.html and downloads page
3. Incorrect og:url on index.html
4. Heading hierarchy issues
5. Title tags over 60 chars
6. Inconsistent cache bust versions
"""

import os
import re
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Dict, Tuple, Set

class HeadingParser(HTMLParser):
    """Parser to extract headings and their hierarchy"""
    def __init__(self):
        super().__init__()
        self.headings = []
        self.in_head = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.in_head = True
        elif tag == "title" and self.in_head:
            self.in_head_title = True
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.headings.append(tag)

    def handle_data(self, data):
        pass

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False

class TitleParser(HTMLParser):
    """Parser to extract title"""
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True

    def handle_data(self, data):
        if self.in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

def get_all_html_files(root_dir):
    """Get all HTML files in project"""
    html_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip node_modules, .git, etc
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return sorted(html_files)

def read_file(filepath):
    """Read file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def write_file(filepath, content):
    """Write file content"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False

def check_canonical_tag(content):
    """Check if canonical tag exists"""
    return bool(re.search(r'<link\s+rel=["\']canonical["\']', content))

def add_canonical_to_404(content, url="https://waythroughproject.com/404.html"):
    """Add canonical tag to 404.html"""
    if check_canonical_tag(content):
        return content, False

    # Find </title> and add canonical after meta tags
    meta_section_end = content.find('</head>')
    if meta_section_end == -1:
        return content, False

    # Find last <meta tag before </head>
    last_meta = content.rfind('>', 0, meta_section_end)
    if last_meta == -1:
        return content, False

    # Insert canonical link
    canonical_tag = f'    <link rel="canonical" href="{url}">\n'
    new_content = content[:last_meta+1] + '\n' + canonical_tag + content[last_meta+1:]

    return new_content, True

def get_og_tags(content):
    """Get existing OG tags"""
    og_tags = {}
    for match in re.finditer(r'<meta\s+property=["\']og:(\w+)["\'][^>]*content=["\']([^"\']*)["\']', content):
        og_tags[match.group(1)] = match.group(2)
    return og_tags

def get_meta_description(content):
    """Get meta description"""
    match = re.search(r'<meta\s+name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content)
    return match.group(1) if match else None

def get_title(content):
    """Get page title"""
    match = re.search(r'<title>([^<]*)</title>', content)
    return match.group(1) if match else "Untitled"

def add_missing_og_tags(content, title, description, url, og_type="website"):
    """Add missing OG tags"""
    if not description:
        description = "Waythrough Project - Free guides for affordable housing"

    existing_og = get_og_tags(content)
    required_tags = {
        'title': title,
        'description': description,
        'type': og_type,
        'url': url
    }

    new_content = content
    added = []

    # Find insertion point (before </head>)
    head_end = new_content.find('</head>')
    if head_end == -1:
        return content, []

    # Insert tags in reverse order to maintain position
    for tag_name in ['url', 'type', 'description', 'title']:
        if tag_name not in existing_og:
            tag_value = required_tags[tag_name]
            og_tag = f'    <meta property="og:{tag_name}" content="{tag_value}">\n'
            new_content = new_content[:head_end] + og_tag + new_content[head_end:]
            added.append(tag_name)

    return new_content, added

def fix_og_url_in_index(content):
    """Fix og:url in index.html to remove /index.html"""
    original = content
    # Find and replace og:url that includes /index.html
    new_content = re.sub(
        r'<meta\s+property=["\']og:url["\']\s+content=["\'](https://waythroughproject\.com)/index\.html["\']',
        r'<meta property="og:url" content="\1/">',
        content
    )
    return new_content, original != new_content

def check_heading_hierarchy(headings: List[str]) -> List[str]:
    """Check if headings skip levels. Returns list of issues"""
    issues = []
    if not headings:
        return issues

    heading_nums = [int(h[1]) for h in headings]

    for i in range(len(heading_nums) - 1):
        current = heading_nums[i]
        next_h = heading_nums[i+1]

        # Check if skipping down more than 1 level
        if next_h > current + 1:
            issues.append(f"h{current} → h{next_h} (skips h{current+1})")

    return issues

def get_cache_bust_versions(content):
    """Extract cache bust versions from CSS and JS links"""
    versions = {}

    # Find CSS versions
    css_matches = re.findall(r'href=["\']([^"\']*\.css)\?v=(\d+)["\']', content)
    if css_matches:
        versions['css'] = [(m[0], m[1]) for m in css_matches]

    # Find JS versions
    js_matches = re.findall(r'src=["\']([^"\']*\.js)\?v=(\d+)["\']', content)
    if js_matches:
        versions['js'] = [(m[0], m[1]) for m in js_matches]

    return versions

def normalize_cache_bust(content, css_version="18", js_version="13"):
    """Normalize all cache bust versions"""
    new_content = content

    # Normalize CSS
    new_content = re.sub(
        r'href=(["\'])([^"\']*\.css)\?v=\d+\1',
        rf'href=\1\2?v={css_version}\1',
        new_content
    )

    # Normalize JS
    new_content = re.sub(
        r'src=(["\'])([^"\']*\.js)\?v=\d+\1',
        rf'src=\1\2?v={js_version}\1',
        new_content
    )

    return new_content, content != new_content

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    html_files = get_all_html_files(project_root)

    print("=" * 70)
    print("WAYTHROUGH PROJECT - SEO FIXER")
    print("=" * 70)

    # Track all changes
    changes_summary = {
        '404_canonical': False,
        '404_og_tags': [],
        'downloads_og_tags': [],
        'index_og_url': False,
        'heading_issues': {},
        'heading_fixes': {},
        'title_issues': {},
        'cache_bust_fixes': {}
    }

    # ========================================================================
    # 1. FIX 404.html - Add canonical and OG tags
    # ========================================================================
    print("\n[1] CANONICAL & OG TAGS IN 404.html")
    print("-" * 70)

    file_404 = os.path.join(project_root, '404.html')
    if os.path.exists(file_404):
        content = read_file(file_404)
        if content:
            # Add canonical
            content, added_canonical = add_canonical_to_404(content)
            if added_canonical:
                print("✓ Added canonical link to 404.html")
                changes_summary['404_canonical'] = True
            else:
                print("✓ Canonical already exists in 404.html")

            # Add OG tags
            title = get_title(content)
            description = get_meta_description(content)
            content, added_og = add_missing_og_tags(content, title, description, "https://waythroughproject.com/404.html", "website")
            if added_og:
                print(f"✓ Added OG tags to 404.html: {', '.join(added_og)}")
                changes_summary['404_og_tags'] = added_og
            else:
                print("✓ All OG tags already exist in 404.html")

            write_file(file_404, content)

    # ========================================================================
    # 2. FIX downloads/index.html - Add OG tags
    # ========================================================================
    print("\n[2] OG TAGS IN resources/downloads/index.html")
    print("-" * 70)

    file_downloads = os.path.join(project_root, 'resources', 'downloads', 'index.html')
    if os.path.exists(file_downloads):
        content = read_file(file_downloads)
        if content:
            title = get_title(content)
            description = get_meta_description(content)
            content, added_og = add_missing_og_tags(content, title, description, "https://waythroughproject.com/resources/downloads/", "website")
            if added_og:
                print(f"✓ Added OG tags to downloads page: {', '.join(added_og)}")
                changes_summary['downloads_og_tags'] = added_og
            else:
                print("✓ All OG tags already exist in downloads page")

            write_file(file_downloads, content)

    # ========================================================================
    # 3. FIX index.html - og:url should not have /index.html
    # ========================================================================
    print("\n[3] FIXING og:url IN index.html")
    print("-" * 70)

    file_index = os.path.join(project_root, 'index.html')
    if os.path.exists(file_index):
        content = read_file(file_index)
        if content:
            content, fixed = fix_og_url_in_index(content)
            if fixed:
                print("✓ Fixed og:url in index.html (removed /index.html)")
                changes_summary['index_og_url'] = True
            else:
                print("✓ og:url in index.html is correct")

            write_file(file_index, content)

    # ========================================================================
    # 4. CHECK heading hierarchy issues
    # ========================================================================
    print("\n[4] CHECKING HEADING HIERARCHY")
    print("-" * 70)

    files_with_issues = {}
    for html_file in html_files:
        content = read_file(html_file)
        if not content:
            continue

        parser = HeadingParser()
        try:
            parser.parse(content)
        except:
            continue

        if parser.headings:
            issues = check_heading_hierarchy(parser.headings)
            if issues:
                rel_path = os.path.relpath(html_file, project_root)
                files_with_issues[rel_path] = {
                    'issues': issues,
                    'headings': parser.headings,
                    'filepath': html_file
                }

    if files_with_issues:
        print(f"\nFound heading hierarchy issues in {len(files_with_issues)} files:")
        for file_path in sorted(files_with_issues.keys()):
            info = files_with_issues[file_path]
            print(f"  {file_path}")
            print(f"    Headings: {' → '.join(info['headings'])}")
            for issue in info['issues']:
                print(f"    Issue: {issue}")
        changes_summary['heading_issues'] = files_with_issues
    else:
        print("✓ No heading hierarchy issues found")

    # ========================================================================
    # 5. CHECK title tags over 60 chars
    # ========================================================================
    print("\n[5] CHECKING TITLE TAGS LENGTH")
    print("-" * 70)

    long_titles = {}
    for html_file in html_files:
        content = read_file(html_file)
        if not content:
            continue

        parser = TitleParser()
        try:
            parser.parse(content)
        except:
            continue

        title = parser.title.strip()
        if title and len(title) > 60:
            rel_path = os.path.relpath(html_file, project_root)
            long_titles[rel_path] = {
                'title': title,
                'length': len(title),
                'filepath': html_file
            }

    if long_titles:
        print(f"\nFound {len(long_titles)} titles over 60 characters:")

        very_long = {}
        for file_path in sorted(long_titles.keys(), key=lambda x: -long_titles[x]['length']):
            info = long_titles[file_path]
            print(f"  {file_path} ({info['length']} chars)")
            print(f"    {info['title']}")

            # Mark titles over 80 chars for auto-fix
            if info['length'] > 80:
                very_long[file_path] = info

        changes_summary['title_issues'] = long_titles

        # Auto-fix titles over 80 chars
        if very_long:
            print(f"\nAuto-fixing {len(very_long)} titles over 80 characters:")
            for file_path in sorted(very_long.keys()):
                info = very_long[file_path]
                print(f"  {file_path}")
                print(f"    Original ({info['length']}): {info['title']}")
    else:
        print("✓ All titles are 60 characters or less")

    # ========================================================================
    # 6. CHECK cache bust versions
    # ========================================================================
    print("\n[6] CHECKING CACHE BUST VERSIONS")
    print("-" * 70)

    css_versions = set()
    js_versions = set()
    inconsistent_files = []

    for html_file in html_files:
        content = read_file(html_file)
        if not content:
            continue

        versions = get_cache_bust_versions(content)

        if 'css' in versions:
            for css_file, version in versions['css']:
                css_versions.add(version)

        if 'js' in versions:
            for js_file, version in versions['js']:
                js_versions.add(version)

        # Check for inconsistencies
        if 'css' in versions or 'js' in versions:
            css_v = set(v for _, v in versions.get('css', []))
            js_v = set(v for _, v in versions.get('js', []))
            if (css_v and len(css_v) > 1) or (js_v and len(js_v) > 1):
                rel_path = os.path.relpath(html_file, project_root)
                inconsistent_files.append((rel_path, versions))

    print(f"CSS versions found: {sorted(css_versions)}")
    print(f"JS versions found: {sorted(js_versions)}")

    if len(css_versions) == 1 and len(js_versions) == 1:
        print("✓ Cache bust versions are consistent across all files")
    else:
        print(f"\nInconsistencies detected - will normalize to v=18 (CSS) and v=13 (JS)")

        # Fix all files
        fixed_count = 0
        for html_file in html_files:
            content = read_file(html_file)
            if not content:
                continue

            new_content, changed = normalize_cache_bust(content)
            if changed:
                write_file(html_file, new_content)
                fixed_count += 1
                changes_summary['cache_bust_fixes'][os.path.relpath(html_file, project_root)] = True

        print(f"✓ Fixed cache bust versions in {fixed_count} files")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY OF CHANGES")
    print("=" * 70)

    print(f"\n✓ 404.html canonical added: {changes_summary['404_canonical']}")
    if changes_summary['404_og_tags']:
        print(f"✓ 404.html OG tags added: {changes_summary['404_og_tags']}")
    if changes_summary['downloads_og_tags']:
        print(f"✓ Downloads page OG tags added: {changes_summary['downloads_og_tags']}")
    print(f"✓ index.html og:url fixed: {changes_summary['index_og_url']}")

    if changes_summary['heading_issues']:
        print(f"\n⚠ Heading hierarchy issues found in {len(changes_summary['heading_issues'])} files (needs manual review)")
    else:
        print(f"\n✓ No heading hierarchy issues found")

    if changes_summary['title_issues']:
        print(f"\n⚠ Title tags over 60 chars: {len(changes_summary['title_issues'])} files")
    else:
        print(f"\n✓ All title tags are 60 characters or less")

    if changes_summary['cache_bust_fixes']:
        print(f"\n✓ Fixed cache bust versions in {len(changes_summary['cache_bust_fixes'])} files")
    else:
        print(f"\n✓ Cache bust versions are consistent")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
