"""Views for the Quant Lab showcase.

Read-only display of pre-baked results, PLUS a lightweight in-browser editor for
the "Idea & Economic Reasoning" section (no DB, no auth — the text is persisted
to quant_lab/thesis/<slug>.md and overrides the catalog default on next load).
"""
import html as html_mod
import re

from django.http import Http404
from django.shortcuts import redirect, render

from . import catalog
from .catalog import Entry


# --------------------------------------------------------------------------- #
#  Minimal markdown renderer (no external dependency)
# --------------------------------------------------------------------------- #
def _render_markdown(text: str) -> str:
    """Render the small markdown subset used in catalog thesis strings.

    Supports fenced code blocks, **bold**, *italic*, `code`, [link](url),
    # / ## / ### headings, unordered lists (- / *), ordered lists (1.), and
    paragraphs. Output is HTML-escaped first for safety.
    """
    out = html_mod.escape(text)

    # Extract fenced code blocks so inline rules don't mangle them.
    code_blocks = []

    def _stash_code(m):
        code_blocks.append(m.group(1))
        return f"\x00CODE{len(code_blocks) - 1}\x00"

    out = re.sub(r"```(?:[a-zA-Z0-9_]*)\n(.*?)```", _stash_code, out, flags=re.DOTALL)

    lines = out.split("\n")
    html_lines = []
    in_ul = in_ol = False

    for line in lines:
        stripped = line.rstrip()

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            if in_ul:
                html_lines.append("</ul>"); in_ul = False
            if in_ol:
                html_lines.append("</ol>"); in_ol = False
            level = len(m.group(1))
            html_lines.append(f"<h{level}>{m.group(2)}</h{level}>")
            continue

        # Ordered list item
        m = re.match(r"^\s*\d+\.\s+(.*)$", stripped)
        if m:
            if in_ul:
                html_lines.append("</ul>"); in_ul = False
            if not in_ol:
                html_lines.append("<ol>"); in_ol = True
            html_lines.append(f"<li>{m.group(1)}</li>")
            continue

        # Unordered list item
        m = re.match(r"^\s*[-*]\s+(.*)$", stripped)
        if m:
            if in_ol:
                html_lines.append("</ol>"); in_ol = False
            if not in_ul:
                html_lines.append("<ul>"); in_ul = True
            html_lines.append(f"<li>{m.group(1)}</li>")
            continue

        # Close any open list on a non-list line
        if in_ul:
            html_lines.append("</ul>"); in_ul = False
        if in_ol:
            html_lines.append("</ol>"); in_ol = False

        # Blank line -> paragraph break
        if stripped == "":
            html_lines.append("")
            continue

        # Code-block placeholder line -> emit as <pre><code>
        cm = re.match(r"^\x00CODE(\d+)\x00$", stripped)
        if cm:
            idx = int(cm.group(1))
            html_lines.append(f"<pre><code>{code_blocks[idx]}</code></pre>")
            continue

        html_lines.append(f"<p>{stripped}</p>")

    if in_ul:
        html_lines.append("</ul>")
    if in_ol:
        html_lines.append("</ol>")

    html_text = "\n".join(html_lines)

    # Inline formatting (catalog content was escaped above, so this is safe).
    html_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html_text)
    html_text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html_text)
    html_text = re.sub(r"`([^`]+)`", r"<code>\1</code>", html_text)
    html_text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html_text)

    # Strip stray <p></p> wrappers around block elements we generated.
    html_text = re.sub(r"<p>(<(?:pre|ul|ol|h[1-6]))", r"\1", html_text)
    html_text = re.sub(r"(</(?:pre|ul|ol|h[1-6])>)</p>", r"\1", html_text)

    return html_text


# --------------------------------------------------------------------------- #
#  Views
# --------------------------------------------------------------------------- #
def index(request):
    """Card grid grouped by category (Strategies / Research Toolkits)."""
    return render(
        request,
        "quant_lab/index.html",
        {
            "strategies": catalog.by_category("strategy"),
            "toolkits": catalog.by_category("toolkit"),
        },
    )


def _format_value(label: str, value: float) -> str:
    """Human-friendly formatting: percentages for ratios, raw for counts."""
    label_lower = label.lower()
    if any(k in label_lower for k in ("return", "cagr", "drawdown", "rate", "exposure")):
        return f"{value:.1%}"
    if "sharpe" in label_lower or "pnl" in label_lower or "turnover" in label_lower:
        return f"{value:.2f}"
    return f"{value:.3f}"


def detail(request, slug: str):
    """Thesis (markdown), metrics table, equity curve chart, provenance badge."""
    entry = catalog.get_entry(slug)
    if entry is None:
        raise Http404("No quant entry matches the given slug.")

    # Use the file-backed thesis (editable in-browser) if present.
    thesis_text = catalog.get_thesis_text(slug)

    formatted_metrics = [
        {"label": label, "value": _format_value(label, val)}
        for label, val in entry.metrics.items()
    ]

    return render(
        request,
        "quant_lab/detail.html",
        {
            "entry": entry,
            "thesis_html": _render_markdown(thesis_text),
            "metrics": formatted_metrics,
            "is_actual": entry.provenance == "actual",
            "thesis_is_overridden": thesis_text != entry.thesis,
            "github_url": catalog.github_url(entry),
        },
    )


def edit_thesis(request, slug: str):
    """In-browser markdown editor for an entry's "Idea & Economic Reasoning".

    GET  -> show a <textarea> prefilled with the current markdown.
    POST -> save the edited text to quant_lab/thesis/<slug>.md (which overrides
            the catalog default on every subsequent page load) and redirect
            back to the detail page.
    """
    entry = catalog.get_entry(slug)
    if entry is None:
        raise Http404("No quant entry matches the given slug.")

    if request.method == "POST":
        text = request.POST.get("thesis", "")
        catalog.save_thesis_text(slug, text)
        return redirect("quant_lab:detail", slug=slug)

    return render(
        request,
        "quant_lab/edit_thesis.html",
        {
            "entry": entry,
            "thesis_md": catalog.get_thesis_text(slug),
            "is_overridden": catalog.get_thesis_text(slug) != entry.thesis,
        },
    )