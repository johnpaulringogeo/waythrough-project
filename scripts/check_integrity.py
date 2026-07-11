#!/usr/bin/env python3
"""
Repo integrity check — guards against silent file truncation / NUL-padding,
the class of corruption behind the May 2026 bulk commit that damaged 34 HTML
files via a sandbox-mount defect (repaired in 7f38c39). Nothing structural
would catch a recurrence, so this script runs in CI on every push
(.github/workflows/integrity-check.yml) and again after each weekly
auto-publish (.github/workflows/publish-blog.yml).

Checks — the script exits nonzero and lists every offender if any of these
fail:

  * Each *.html file OUTSIDE blog/drafts/ must be non-empty, contain no NUL
    (0x00) bytes, and end with </html> (trailing whitespace allowed).
  * sitemap.xml   must end with </urlset> (trailing whitespace allowed).
  * blog/feed.xml must end with </rss>    (trailing whitespace allowed).

blog/drafts/ is exempt (work-in-progress posts). The empty / NUL checks are
scoped to these text files on purpose, so tracked binary assets (images,
fonts, .ico) are never mis-flagged.

File selection:

  * No argument: ask git — from the repo containing the current directory —
    for tracked files PLUS untracked-but-not-ignored files
    (`git ls-files -co --exclude-standard`). Including the untracked set is
    what lets the weekly publisher catch a freshly written post that has not
    been committed yet. Listed files absent on disk (e.g. one mid-rename) are
    skipped. This is the mode CI uses.

  * One directory argument: walk it and check every file underneath. Use this
    to validate *committed* content without trusting the working tree.

Run it locally before committing (recommended on this repo, whose working
tree carries hundreds of phantom CRLF-only modifications that must not be
trusted for byte-level checks — always validate the committed blobs, never
the working copy):

    # check everything at HEAD, straight from the object store:
    git archive HEAD | tar -x -C /tmp/head-export
    python scripts/check_integrity.py /tmp/head-export

    # or spot-check a single committed blob:
    git show HEAD:sitemap.xml | tail -c 40

Exit status: 0 = clean, 1 = offenders found (listed on stderr), 2 = usage error.
"""

import os
import subprocess
import sys

DRAFTS_PREFIX = "blog/drafts/"

# Files (repo-relative) that must end with a specific closing tag.
XML_RULES = {
    "sitemap.xml": b"</urlset>",
    "blog/feed.xml": b"</rss>",
}


def is_applicable(relpath):
    """True if the path is subject to a rule (a non-draft .html or a named XML)."""
    rel = relpath.replace(os.sep, "/")
    if rel in XML_RULES:
        return True
    return rel.endswith(".html") and not rel.startswith(DRAFTS_PREFIX)


def problems_for(relpath, data):
    """Return a list of problem strings for an applicable file ([] == OK)."""
    rel = relpath.replace(os.sep, "/")
    if len(data.strip()) == 0:
        return ["file is empty"]
    problems = []
    if b"\x00" in data:
        problems.append("contains %d NUL byte(s)" % data.count(b"\x00"))
    closing = XML_RULES.get(rel, b"</html>")
    if not data.rstrip().endswith(closing):
        problems.append("does not end with %s" % closing.decode())
    return problems


def git_file_list(root):
    """Tracked + untracked-not-ignored files under root (repo-relative)."""
    def run(args):
        result = subprocess.run(["git", "-C", root] + args,
                                capture_output=True, text=True)
        if result.returncode != 0:
            return []
        return [line for line in result.stdout.split("\n") if line]
    files = set(run(["ls-files"]))
    files |= set(run(["ls-files", "-o", "--exclude-standard"]))
    return sorted(files)


def walk_file_list(root):
    """Every file under root (root-relative), skipping any .git directory."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(out)


def main(argv):
    if len(argv) > 2:
        print("usage: check_integrity.py [DIRECTORY]", file=sys.stderr)
        return 2

    if len(argv) == 2:
        root = os.path.abspath(argv[1])
        if not os.path.isdir(root):
            print("error: %s is not a directory" % root, file=sys.stderr)
            return 2
        relpaths = walk_file_list(root)
    else:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True)
        if top.returncode != 0:
            print("error: not inside a git repository and no directory given",
                  file=sys.stderr)
            return 2
        root = top.stdout.strip()
        relpaths = git_file_list(root)

    offenders = []
    checked = 0
    for rel in relpaths:
        if not is_applicable(rel):
            continue
        abspath = os.path.join(root, rel)
        if not os.path.isfile(abspath):
            continue
        checked += 1
        with open(abspath, "rb") as handle:
            data = handle.read()
        problems = problems_for(rel, data)
        if problems:
            offenders.append((rel.replace(os.sep, "/"), problems))

    if offenders:
        print("Repo integrity check FAILED - %d offender(s) of %d file(s) "
              "checked:" % (len(offenders), checked), file=sys.stderr)
        for rel, problems in sorted(offenders):
            print("  %s - %s" % (rel, "; ".join(problems)), file=sys.stderr)
        return 1

    print("Repo integrity check passed - %d files checked, no problems."
          % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
