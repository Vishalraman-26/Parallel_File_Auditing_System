from collections import defaultdict
from typing import Dict, List

from scanner import MatchRecord


def generate_report(
    sequential_matches: List[MatchRecord],
    parallel_matches: List[MatchRecord],
    time_taken_sequential: float,
    time_taken_parallel: float,
) -> Dict[str, object]:
    """
    Build the JSON report returned to the frontend.
    """
    counts: Dict[str, int] = defaultdict(int)
    for record in parallel_matches:
        counts[record.get("type", "")] += 1

    total_issues = sum(counts.values())

    samples: List[Dict[str, object]] = []
    for item in sorted(parallel_matches, key=lambda r: int(r.get("line", 0)))[:50]:
        samples.append(
            {
                "line": item.get("line"),
                "type": item.get("type"),
                "match": item.get("match"),
            }
        )

    report: Dict[str, object] = {
        "total_issues": total_issues,
        "by_category": {
            "sensitive": counts.get("sensitive", 0),
            "forbidden": counts.get("forbidden", 0),
            "policy": counts.get("policy", 0),
        },
        "samples": samples,
        "time_taken_parallel": time_taken_parallel,
        "time_taken_sequential": time_taken_sequential,
    }

    return report

