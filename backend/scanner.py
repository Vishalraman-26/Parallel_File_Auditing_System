from typing import Dict, List, Tuple

from file_chunker import chunk_file_by_lines
from regex_rules import PatternEntry, get_rules_for_categories

MatchRecord = Dict[str, object]


def _scan_lines(lines, start_line_number, active_rules):
    matches = []
    line_number = start_line_number

    for text in lines:
        for category, patterns in active_rules.items():
            for rule_name, compiled_pattern in patterns:
                for hit in compiled_pattern.finditer(text):
                    matches.append(
                        {
                            "line": line_number,
                            "type": category,
                            "match": hit.group(0),
                            "rule": rule_name,
                        }
                    )
        line_number += 1

    return matches


def scan_file_sequential_with_progress(file_path: str, categories: List[str], scan_state):
    active_rules = get_rules_for_categories(categories)
    all_matches = []

    chunks = list(chunk_file_by_lines(file_path))
    total = len(chunks)

    for idx, (_, lines, start_line) in enumerate(chunks):
        all_matches.extend(_scan_lines(lines, start_line, active_rules))

        # 🔥 UPDATE REAL PROGRESS (0–80%)
        scan_state["progress"] = int((idx + 1) / total * 80)

    return all_matches


# keep this for parallel engine
def scan_chunk_for_worker(payload: Tuple[int, List[str], int, List[str]]):
    _, lines, start_line, categories = payload
    active_rules = get_rules_for_categories(categories)
    return _scan_lines(lines, start_line, active_rules)
