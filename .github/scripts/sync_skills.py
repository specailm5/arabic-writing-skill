#!/usr/bin/env python3
"""
Sync Skills Script (sync_skills.py)
-----------------------------------
Synchronizes the Agent Skills payload across the three discovery locations:
  1. Root repository:
     - SKILL.md
     - references/
     - examples/
     - scripts/   (if present)
     - resources/ (if present)
  2. .agents/skills/arabic-writing-skill/
  3. .claude/skills/arabic-writing-skill/

Resolution Strategy:
- When a file differs across the three locations:
  1. Compares Git commit distance to HEAD (git rev-list --count <hash>..HEAD):
     - Uncommitted / working-tree edits: Rank -1 (newest)
     - Committed in HEAD: Rank 0
     - Committed N commits ago: Rank N
     - Untracked on disk: Rank -1
     - Non-existent: Rank infinity (999999999)
  2. If ranks are tied, canonical priority order applies: root > agents > claude.
  3. The location with the minimum (rank, priority) tuple is chosen as the source of truth.
  4. If the winner does not exist on disk (was deleted in latest commit),
     the file is removed from the other locations.
  5. Otherwise, the winning file is copied to the other locations.

Supports:
  --check   : Exit with code 1 if files are out of sync (read-only mode for CI linting)
  --verbose : Print verbose details for every compared file
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

SKILL_DIRECTORIES = ["references", "examples", "scripts", "resources"]
SKILL_FILES = ["SKILL.md"]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Tuple of (location_name, relative_base_path, priority_index)
LOCATIONS: List[Tuple[str, Path, int]] = [
    ("root", REPO_ROOT, 0),
    ("agents", REPO_ROOT / ".agents" / "skills" / "arabic-writing-skill", 1),
    ("claude", REPO_ROOT / ".claude" / "skills" / "arabic-writing-skill", 2),
]


def file_hash(path: Path) -> Optional[str]:
    """Return SHA256 hex digest of file, or None if file doesn't exist."""
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_rank(repo_root: Path, file_path: Path) -> int:
    """
    Calculate recency rank relative to HEAD.
    Lower number means more recent:
      -1 : Modified in working tree / untracked file on disk
       0 : Committed in HEAD
       N : Committed N commits ago
     INF : Never committed and does not exist on disk
    """
    exists = file_path.is_file()
    try:
        rel_posix = file_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        rel_posix = str(file_path)

    # Check if modified in working tree compared to git index / HEAD
    try:
        diff_code = subprocess.run(
            ["git", "diff", "--quiet", "--", rel_posix],
            cwd=repo_root,
            capture_output=True,
        ).returncode
        if diff_code == 1:
            return -1
    except Exception:
        pass

    # Find the latest commit touching this file
    commit_hash = ""
    try:
        commit_hash = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--", rel_posix],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        pass

    if commit_hash:
        try:
            distance = subprocess.check_output(
                ["git", "rev-list", "--count", f"{commit_hash}..HEAD"],
                cwd=repo_root,
                stderr=subprocess.DEVNULL,
            ).decode().strip()
            return int(distance)
        except Exception:
            return 0

    if exists:
        # File exists on disk but was never committed yet
        return -1

    # File does not exist and has never been committed
    return 999999999


def discover_all_relative_files(locations: List[Tuple[str, Path, int]]) -> Set[str]:
    """Discover all relative file paths under skill elements across all locations."""
    rel_files: Set[str] = set()

    for _, base_path, _ in locations:
        if not base_path.exists():
            continue

        # Check explicit root-level skill files
        for fname in SKILL_FILES:
            target = base_path / fname
            if target.is_file():
                rel_files.add(fname)

        # Check subdirectories
        for dir_name in SKILL_DIRECTORIES:
            target_dir = base_path / dir_name
            if target_dir.is_dir():
                for root, _, files in os.walk(target_dir):
                    for file in files:
                        full_path = Path(root) / file
                        rel_path = full_path.relative_to(base_path).as_posix()
                        rel_files.add(rel_path)

    return rel_files


def sync(check_only: bool = False, verbose: bool = False) -> int:
    """Run synchronization across all locations. Returns number of out-of-sync files."""
    all_rel_paths = sorted(discover_all_relative_files(LOCATIONS))
    if verbose:
        print(f"Discovered {len(all_rel_paths)} unique relative file path(s) to check.")

    out_of_sync_count = 0
    actions_taken: List[str] = []

    for rel_path in all_rel_paths:
        file_states: List[Dict[str, Any]] = []
        for name, base_path, priority in LOCATIONS:
            path = base_path / rel_path
            f_hash = file_hash(path)
            rank = get_git_rank(REPO_ROOT, path)
            file_states.append({
                "name": name,
                "path": path,
                "priority": priority,
                "exists": path.is_file(),
                "hash": f_hash,
                "rank": rank,
            })

        # Check if all exist and have identical hashes
        hashes = [s["hash"] for s in file_states if s["exists"]]
        all_exist = len(hashes) == len(LOCATIONS)
        all_match = all_exist and len(set(hashes)) == 1

        if all_match:
            if verbose:
                print(f"  [OK] {rel_path} is identical across all locations.")
            continue

        out_of_sync_count += 1

        # Winner: smallest (rank, priority)
        winner = min(file_states, key=lambda s: (s["rank"], s["priority"]))

        if check_only:
            print(f"[OUT OF SYNC] {rel_path}")
            for s in file_states:
                status = f"hash={s['hash'][:8]} (rank={s['rank']})" if s["exists"] else "MISSING"
                print(f"    - {s['name']}: {status}")
            continue

        # Perform sync
        if winner["exists"]:
            source_file = winner["path"]
            targets_synced = []
            for s in file_states:
                if s["path"] != source_file:
                    s["path"].parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, s["path"])
                    targets_synced.append(s["name"])
            actions_taken.append(f"Updated {rel_path} from '{winner['name']}' -> {', '.join(targets_synced)}")
        else:
            # Winner was deleted
            targets_deleted = []
            for s in file_states:
                if s["exists"]:
                    s["path"].unlink()
                    targets_deleted.append(s["name"])
            actions_taken.append(f"Deleted {rel_path} (removed in '{winner['name']}') from: {', '.join(targets_deleted)}")

    if check_only:
        if out_of_sync_count > 0:
            print(f"\nError: {out_of_sync_count} file(s) are out of sync across mirrors.")
            return 1
        print("All skill files are synchronized across all locations.")
        return 0

    if actions_taken:
        print(f"Synchronized {len(actions_taken)} item(s):")
        for act in actions_taken:
            print(f"  * {act}")
    else:
        print("All skill files are already synchronized. No changes made.")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Synchronize duplicated skill files.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether files are in sync without modifying them (exits 1 if diff found).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display detailed file status.",
    )
    args = parser.parse_args()
    code = sync(check_only=args.check, verbose=args.verbose)
    sys.exit(code)


if __name__ == "__main__":
    main()
