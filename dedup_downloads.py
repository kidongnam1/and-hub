#!/usr/bin/env python3
"""중복 파일 정리 스크립트 (내용 해시 기준)."""

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict

DEFAULT_DIR = "/storage/emulated/0/Download"
CHUNK = 1024 * 1024


def human(size):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f}{unit}"
        size /= 1024


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def keeper(paths):
    return min(paths, key=lambda p: (len(os.path.basename(p)), len(p), p))


def main():
    ap = argparse.ArgumentParser(description="내용이 같은 중복 파일 정리")
    ap.add_argument("directory", nargs="?", default=DEFAULT_DIR)
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--trash", action="store_true")
    ap.add_argument("--recursive", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.directory)
    if not os.path.isdir(root):
        print(f"[오류] 폴더를 찾을 수 없습니다: {root}")
        sys.exit(1)

    by_size = defaultdict(list)
    if args.recursive:
        walker = ((dp, fn) for dp, _, fns in os.walk(root) for fn in fns)
    else:
        walker = ((root, fn) for fn in os.listdir(root))

    for dirpath, name in walker:
        path = os.path.join(dirpath, name)
        if not os.path.isfile(path) or os.path.islink(path):
            continue
        try:
            by_size[os.path.getsize(path)].append(path)
        except OSError:
            continue

    by_hash = defaultdict(list)
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for p in paths:
            try:
                by_hash[(size, file_hash(p))].append(p)
            except OSError as e:
                print(f"[건너뜀] 읽기 실패: {p} ({e})")

    trash_dir = os.path.join(root, "_duplicates_trash")
    total_groups = 0
    total_freed = 0
    total_removed = 0

    for (size, _), paths in sorted(by_hash.items(), key=lambda kv: -kv[0][0]):
        if len(paths) < 2:
            continue
        total_groups += 1
        keep = keeper(paths)
        remove = [p for p in paths if p != keep]

        print(f"\n[중복 {len(paths)}개 · 각 {human(size)}]")
        print(f"  남김:   {keep}")
        for p in remove:
            total_freed += size
            total_removed += 1
            if not args.delete:
                print(f"  삭제예정: {p}")
                continue
            try:
                if args.trash:
                    os.makedirs(trash_dir, exist_ok=True)
                    dest = os.path.join(trash_dir, os.path.basename(p))
                    i = 1
                    base, ext = os.path.splitext(dest)
                    while os.path.exists(dest):
                        dest = f"{base}_{i}{ext}"
                        i += 1
                    shutil.move(p, dest)
                    print(f"  이동함:  {p} -> {dest}")
                else:
                    os.remove(p)
                    print(f"  삭제함:  {p}")
            except OSError as e:
                print(f"  [실패]  {p} ({e})")

    print("\n" + "=" * 50)
    if total_groups == 0:
        print("중복 파일이 없습니다.")
        return
    print(f"중복 그룹: {total_groups}개")
    print(f"{'삭제한' if args.delete else '삭제 예정'} 파일: {total_removed}개")
    print(f"{'확보한' if args.delete else '확보 가능한'} 용량: {human(total_freed)}")
    if not args.delete:
        print("\n실제로 지우려면 --delete 를 붙여 다시 실행하세요.")


if __name__ == "__main__":
    main()
