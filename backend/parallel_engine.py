from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from typing import List

from file_chunker import chunk_file_by_lines
from scanner import MatchRecord, scan_chunk_for_worker


def scan_file_parallel(
    file_path: str,
    categories: List[str],
    chunk_size_lines: int = 5000,
    max_workers: int | None = None,
) -> List[MatchRecord]:
    """
    Scan a file using multiprocessing across chunks of lines.
    """
    if max_workers is None:
        max_workers = max(cpu_count() - 1, 1)

    all_matches: List[MatchRecord] = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
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

