from typing import Generator, List, Tuple


def chunk_file_by_lines(
    file_path: str, chunk_size_lines: int = 5000
) -> Generator[Tuple[int, List[str], int], None, None]:
    """
    Read a text file lazily and yield chunks of lines.

    Each yielded value is a tuple of:
    - chunk index
    - list of lines for this chunk
    - starting line number for this chunk (1-based)
    """
    chunk_index = 0
    current_chunk = []
    current_start_line = 1
    line_counter = 0

    with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            current_chunk.append(line)
            line_counter += 1

            if line_counter >= chunk_size_lines:
                yield chunk_index, current_chunk, current_start_line
                chunk_index += 1
                current_chunk = []
                current_start_line = current_start_line + line_counter
                line_counter = 0

        if current_chunk:
            yield chunk_index, current_chunk, current_start_line

