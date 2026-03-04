#!/usr/bin/env python3
"""Extract SDD pipeline metrics from git history with conventional commits.

Parses conventional commits with feature ID scopes (e.g., feat(F6): ...)
to produce per-feature and aggregated pipeline metrics.

Usage:
    python sdd-metrics.py                      # Full report
    python sdd-metrics.py --json               # Machine-readable output
    python sdd-metrics.py --feature F6         # Single feature
    python sdd-metrics.py --period 2026-01:2026-03
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone

COMMIT_RE = re.compile(
    r"^(docs|feat|test|fix|refactor|chore)\(([^)]+)\):\s*(.+)$",
)
FEATURE_RE = re.compile(r"^F\d+$")
REWORK_RE = re.compile(r"\brevise\b", re.IGNORECASE)

TYPES_ORDER = ["docs", "feat", "test", "fix", "refactor", "chore"]


def run_git(*args: str) -> str:
    result = subprocess.run(  # noqa: S603, S607
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        msg = f"git {' '.join(args)} failed: {result.stderr.strip()}"
        raise RuntimeError(msg)
    return result.stdout


def parse_log(
    after: str | None = None,
    before: str | None = None,
) -> list[dict[str, str]]:
    """Parse git log into structured commit records."""
    cmd = ["log", "--format=%H|%aI|%s", "--no-merges"]
    if after:
        cmd.append(f"--after={after}")
    if before:
        cmd.append(f"--before={before}")

    raw = run_git(*cmd)
    commits = []
    for line in raw.strip().splitlines():
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) != 3:  # noqa: PLR2004
            continue
        sha, date_str, subject = parts
        match = COMMIT_RE.match(subject)
        if not match:
            continue
        commit_type, scope, description = match.groups()
        commits.append({
            "sha": sha,
            "date": date_str,
            "type": commit_type,
            "scope": scope,
            "description": description,
            "subject": subject,
        })
    return commits


def get_commit_stat(sha: str) -> dict[str, int]:
    """Get files changed and lines changed for a commit."""
    raw = run_git("diff-tree", "--no-commit-id", "--shortstat", sha)
    files_changed = 0
    lines_changed = 0
    if raw.strip():
        file_match = re.search(r"(\d+) files? changed", raw)
        ins_match = re.search(r"(\d+) insertions?", raw)
        del_match = re.search(r"(\d+) deletions?", raw)
        if file_match:
            files_changed = int(file_match.group(1))
        ins = int(ins_match.group(1)) if ins_match else 0
        dels = int(del_match.group(1)) if del_match else 0
        lines_changed = ins + dels
    return {"files": files_changed, "lines": lines_changed}


def classify_feature(types_seen: set[str]) -> str:
    """Classify feature status based on commit types present."""
    has_feat = "feat" in types_seen
    has_test = "test" in types_seen
    if has_feat and has_test:
        return "complete"
    if has_feat:
        return "implementing"
    return "docs-only"


def build_feature_metrics(
    commits: list[dict[str, str]],
) -> dict[str, dict[str, object]]:
    """Build per-feature metrics from parsed commits."""
    features: dict[str, list[dict[str, str]]] = defaultdict(list)
    for commit in commits:
        scope = commit["scope"]
        if FEATURE_RE.match(scope):
            features[scope].append(commit)

    metrics: dict[str, dict[str, object]] = {}
    for fid in sorted(features, key=lambda f: int(f[1:])):
        fcommits = features[fid]
        type_counts: dict[str, int] = defaultdict(int)
        types_seen: set[str] = set()
        rework_count = 0
        dates: list[datetime] = []

        first_docs: datetime | None = None
        first_feat: datetime | None = None

        for c in fcommits:
            type_counts[c["type"]] += 1
            types_seen.add(c["type"])
            dt = datetime.fromisoformat(c["date"])
            dates.append(dt)

            if REWORK_RE.search(c["description"]):
                rework_count += 1

            if c["type"] == "docs" and first_docs is None:
                first_docs = dt
            if c["type"] == "feat" and first_feat is None:
                first_feat = dt

        dates.sort()
        duration_days = (dates[-1] - dates[0]).total_seconds() / 86400

        feat_count = type_counts.get("feat", 0)
        fix_count = type_counts.get("fix", 0)
        fair = round(fix_count / feat_count, 2) if feat_count > 0 else 0.0

        spec_to_code_days: float | None = None
        if first_docs and first_feat:
            spec_to_code_days = round(
                (first_feat - first_docs).total_seconds() / 86400,
                1,
            )

        metrics[fid] = {
            "total_commits": len(fcommits),
            "by_type": dict(type_counts),
            "status": classify_feature(types_seen),
            "fair": fair,
            "duration_days": round(duration_days, 1),
            "spec_to_code_days": spec_to_code_days,
            "rework_count": rework_count,
        }
    return metrics


def build_aggregated(
    feature_metrics: dict[str, dict[str, object]],
    all_commits: list[dict[str, str]],
) -> dict[str, object]:
    """Build aggregated metrics across all features."""
    if not feature_metrics:
        return {
            "feature_count": 0,
            "avg_commits": 0,
            "avg_fixes": 0,
            "avg_fair": 0,
            "avg_duration_days": 0,
            "type_distribution": {},
            "commit_granularity": {"avg_files": 0, "avg_lines": 0},
        }

    total_commits_list = [
        int(str(m["total_commits"])) for m in feature_metrics.values()
    ]
    fix_list = [
        int(m.get("by_type", {}).get("fix", 0))  # type: ignore[union-attr]
        for m in feature_metrics.values()
    ]
    fair_list = [float(m["fair"]) for m in feature_metrics.values()]  # type: ignore[arg-type]
    duration_list = [
        float(m["duration_days"])  # type: ignore[arg-type]
        for m in feature_metrics.values()
    ]

    n = len(feature_metrics)

    type_dist: dict[str, int] = defaultdict(int)
    for c in all_commits:
        type_dist[c["type"]] += 1

    # Sample up to 50 commits for granularity stats
    sample = all_commits[:50]
    stats = [get_commit_stat(c["sha"]) for c in sample] if sample else []
    avg_files = (
        round(sum(s["files"] for s in stats) / len(stats), 1) if stats else 0
    )
    avg_lines = (
        round(sum(s["lines"] for s in stats) / len(stats), 1) if stats else 0
    )

    return {
        "feature_count": n,
        "avg_commits": round(sum(total_commits_list) / n, 1),
        "avg_fixes": round(sum(fix_list) / n, 1),
        "avg_fair": round(sum(fair_list) / n, 2),
        "avg_duration_days": round(sum(duration_list) / n, 1),
        "type_distribution": dict(type_dist),
        "commit_granularity": {"avg_files": avg_files, "avg_lines": avg_lines},
    }


def build_trends(
    feature_metrics: dict[str, dict[str, object]],
) -> dict[str, object]:
    """Compare first half vs second half of features for trend detection."""
    fids = sorted(feature_metrics, key=lambda f: int(f[1:]))
    if len(fids) < 2:  # noqa: PLR2004
        return {"insufficient_data": True}

    mid = len(fids) // 2
    first_half = [feature_metrics[f] for f in fids[:mid]]
    second_half = [feature_metrics[f] for f in fids[mid:]]

    def avg_metric(
        group: list[dict[str, object]], key: str,
    ) -> float:
        vals = [float(m[key]) for m in group]  # type: ignore[arg-type]
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    def direction(first: float, second: float, lower_better: bool) -> str:
        if abs(first - second) < 0.01:
            return "stable"
        improved = second < first if lower_better else second > first
        return "improving" if improved else "degrading"

    fair_1 = avg_metric(first_half, "fair")
    fair_2 = avg_metric(second_half, "fair")
    dur_1 = avg_metric(first_half, "duration_days")
    dur_2 = avg_metric(second_half, "duration_days")
    commits_1 = avg_metric(first_half, "total_commits")
    commits_2 = avg_metric(second_half, "total_commits")

    return {
        "first_half_features": fids[:mid],
        "second_half_features": fids[mid:],
        "fair": {
            "first": fair_1,
            "second": fair_2,
            "direction": direction(fair_1, fair_2, lower_better=True),
        },
        "duration": {
            "first": dur_1,
            "second": dur_2,
            "direction": direction(dur_1, dur_2, lower_better=True),
        },
        "commits_per_feature": {
            "first": commits_1,
            "second": commits_2,
            "direction": direction(commits_1, commits_2, lower_better=True),
        },
    }


def format_text(
    feature_metrics: dict[str, dict[str, object]],
    aggregated: dict[str, object],
    trends: dict[str, object],
) -> str:
    """Format metrics as structured text report."""
    lines: list[str] = []
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"SDD Pipeline Metrics — {now}")
    lines.append("=" * 50)

    # Feature inventory
    lines.append("")
    lines.append("## Feature Inventory")
    lines.append("")
    if not feature_metrics:
        lines.append("No features found with conventional commits.")
        return "\n".join(lines)

    for fid, m in feature_metrics.items():
        status = str(m["status"])
        total = m["total_commits"]
        by_type = m.get("by_type", {})
        type_str = ", ".join(
            f"{t}={by_type.get(t, 0)}"  # type: ignore[union-attr]
            for t in TYPES_ORDER
            if by_type.get(t, 0) > 0  # type: ignore[union-attr]
        )
        lines.append(f"  {fid:>4}  [{status:<13}]  {total:>3} commits  ({type_str})")

    # Per-feature details
    lines.append("")
    lines.append("## Per-Feature Metrics")
    lines.append("")
    lines.append(
        f"  {'ID':>4}  {'FAIR':>5}  {'Duration':>10}  "
        f"{'Spec->Code':>11}  {'Rework':>7}",
    )
    lines.append(f"  {'—' * 4}  {'—' * 5}  {'—' * 10}  {'—' * 11}  {'—' * 7}")
    for fid, m in feature_metrics.items():
        fair = m["fair"]
        dur = f"{m['duration_days']}d"
        s2c = (
            f"{m['spec_to_code_days']}d"
            if m["spec_to_code_days"] is not None
            else "n/a"
        )
        rework = m["rework_count"]
        lines.append(
            f"  {fid:>4}  {fair:>5}  {dur:>10}  {s2c:>11}  {rework:>7}",
        )

    # Aggregated
    lines.append("")
    lines.append("## Aggregated")
    lines.append("")
    lines.append(f"  Features:              {aggregated['feature_count']}")
    lines.append(f"  Avg commits/feature:   {aggregated['avg_commits']}")
    lines.append(f"  Avg fixes/feature:     {aggregated['avg_fixes']}")
    lines.append(f"  Avg FAIR:              {aggregated['avg_fair']}")
    lines.append(f"  Avg duration:          {aggregated['avg_duration_days']}d")

    gran = aggregated.get("commit_granularity", {})
    lines.append(
        f"  Commit granularity:    "
        f"~{gran.get('avg_files', 0)} files, "  # type: ignore[union-attr]
        f"~{gran.get('avg_lines', 0)} lines/commit",  # type: ignore[union-attr]
    )

    type_dist = aggregated.get("type_distribution", {})
    if type_dist:
        lines.append("")
        lines.append("  Type distribution:")
        total_typed = sum(type_dist.values())  # type: ignore[union-attr]
        for t in TYPES_ORDER:
            count = type_dist.get(t, 0)  # type: ignore[union-attr]
            if count > 0:
                pct = round(count / total_typed * 100)  # type: ignore[operator]
                lines.append(f"    {t:<10} {count:>4}  ({pct}%)")

    # Trends
    if not trends.get("insufficient_data"):
        lines.append("")
        lines.append("## Trends (first half vs second half)")
        lines.append("")
        for metric_name in ("fair", "duration", "commits_per_feature"):
            t = trends.get(metric_name, {})
            arrow = {
                "improving": "+",
                "degrading": "-",
                "stable": "=",
            }.get(t.get("direction", "stable"), "?")  # type: ignore[union-attr]
            lines.append(
                f"  {metric_name:<22} "
                f"{t.get('first', 0)} -> {t.get('second', 0)}  "  # type: ignore[union-attr]
                f"[{arrow} {t.get('direction', 'stable')}]",  # type: ignore[union-attr]
            )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract SDD pipeline metrics from git history.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--feature",
        type=str,
        default=None,
        help="Filter to a single feature (e.g., F6)",
    )
    parser.add_argument(
        "--period",
        type=str,
        default=None,
        help="Date range as START:END (e.g., 2026-01-01:2026-03-03)",
    )
    args = parser.parse_args()

    after = None
    before = None
    if args.period:
        parts = args.period.split(":")
        if len(parts) != 2:  # noqa: PLR2004
            print("Error: --period must be START:END", file=sys.stderr)
            sys.exit(1)
        after, before = parts

    try:
        commits = parse_log(after=after, before=before)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    feature_metrics = build_feature_metrics(commits)

    if args.feature:
        fid = args.feature.upper()
        if fid not in feature_metrics:
            print(f"Feature {fid} not found in commit history.", file=sys.stderr)
            sys.exit(1)
        feature_metrics = {fid: feature_metrics[fid]}

    feature_commits = [
        c for c in commits if FEATURE_RE.match(c["scope"])
    ]
    aggregated = build_aggregated(feature_metrics, feature_commits)
    trends = build_trends(feature_metrics)

    if args.json:
        output = {
            "features": feature_metrics,
            "aggregated": aggregated,
            "trends": trends,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print(format_text(feature_metrics, aggregated, trends))


if __name__ == "__main__":
    main()
