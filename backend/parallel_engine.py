from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from file_chunker import chunk_file_by_lines
from scanner import MatchRecord, scan_chunk_for_worker


def scan_file_parallel(
    file_path: str,
    categories: List[str],
    chunk_size_lines: int = 5000,
    max_workers: int = 4,   # cloud safe
) -> List[MatchRecord]:
    """
    Scan a file using multithreading across chunks of lines.
    This is MUCH faster and stable on cloud platforms.
    """

    all_matches: List[MatchRecord] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for chunk_index, lines, start_line in chunk_file_by_lines(
            file_path, chunk_size_lines=chunk_size_lines
        ):
            payload = (chunk_index, lines, start_line, categories)
            future = executor.submit(scan_chunk_for_worker, payload)
            futures.append(future)

        for future in as_completed(futures):
            chunk_matches = future.result()
            all_matches.extend(chunk_matches)

    return all_matches
