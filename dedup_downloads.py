#!/usr/bin/env python3
"""중복 정리 스크립트 (내용 해시 기준 + 멀티스레드/복구 지원).

기본은 내용이 같은 중복 *파일*을 찾고, --folders 를 주면 내용이
완전히 같은 중복 *폴더*(같은 상대경로 + 같은 파일 내용)를 찾습니다.
--restore 옵션으로 휴지통(_duplicates_trash)에 있는 파일들을 원래 위치로 원상복구합니다.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_DIR = "/storage/emulated/0/Download"
CHUNK = 1024 * 1024
PARTIAL_SIZE = 64 * 1024  # 64KB
LARGE_FILE_LIMIT = 10 * 1024 * 1024  # 10MB 이상 시 부분 해시 1차 적용
TRASH_NAME = "_duplicates_trash"
UNDO_LOG_NAME = "undo_log.json"

# 이름 끝의 " (숫자)" 패턴 (예: "사진 (2)", "report(3)") — 다운로드 사본 표시
NAME_SUFFIX_RE = re.compile(r"^(.+?)\s*\((\d+)\)$")


def human(size):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f}{unit}"
        size /= 1024


def file_hash(path, partial=False):
    """파일의 SHA-256 해시를 계산한다. 읽기 실패 시 None 반환."""
    try:
        sz = os.path.getsize(path)
        h = hashlib.sha256()
        with open(path, "rb") as f:
            if partial and sz > LARGE_FILE_LIMIT:
                # 앞 64KB + 뒤 64KB 읽어 부분 해시 계산
                h.update(f.read(PARTIAL_SIZE))
                if sz > PARTIAL_SIZE:
                    f.seek(max(0, sz - PARTIAL_SIZE))
                    h.update(f.read(PARTIAL_SIZE))
            else:
                while True:
                    chunk = f.read(CHUNK)
                    if not chunk:
                        break
                    h.update(chunk)
        return h.hexdigest()
    except OSError as e:
        print(f"[건너뜀] 읽기 실패: {path} ({e})")
        return None


def keeper(paths):
    """가장 얕고 짧은 경로를 남길 대상으로 고른다."""
    return min(paths, key=lambda p: (p.count(os.sep), len(p), p))


def iter_files(root, recursive):
    if recursive:
        for dirpath, _, names in os.walk(root):
            if TRASH_NAME in dirpath.split(os.sep):
                continue
            for name in names:
                yield os.path.join(dirpath, name)
    else:
        for name in os.listdir(root):
            if name == TRASH_NAME:
                continue
            yield os.path.join(root, name)


def is_ancestor(ancestor, path):
    """ancestor 가 path 의 상위 폴더면 True."""
    a = os.path.normpath(ancestor)
    p = os.path.normpath(path)
    return p != a and p.startswith(a + os.sep)


def load_undo_log(trash_dir):
    log_path = os.path.join(trash_dir, UNDO_LOG_NAME)
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_undo_log(trash_dir, undo_map):
    log_path = os.path.join(trash_dir, UNDO_LOG_NAME)
    os.makedirs(trash_dir, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(undo_map, f, ensure_ascii=False, indent=2)


def move_to_trash(path, trash_dir):
    os.makedirs(trash_dir, exist_ok=True)
    dest = os.path.join(trash_dir, os.path.basename(path))
    base, ext = os.path.splitext(dest)
    i = 1
    while os.path.exists(dest):
        dest = f"{base}_{i}{ext}"
        i += 1
    
    # 원래 위치 트랜잭션 기록
    undo_map = load_undo_log(trash_dir)
    undo_map[dest] = path
    shutil.move(path, dest)
    save_undo_log(trash_dir, undo_map)
    return dest


def restore_from_trash(root):
    """_duplicates_trash 내 파일들을 원래 위치로 원상복구한다."""
    trash_dir = os.path.join(root, TRASH_NAME)
    log_path = os.path.join(trash_dir, UNDO_LOG_NAME)
    if not os.path.exists(log_path):
        print(f"복구할 트랜잭션 기록이 없습니다: {log_path}")
        return

    undo_map = load_undo_log(trash_dir)
    if not undo_map:
        print("복구할 항목이 없습니다.")
        return

    restored_count = 0
    failed_count = 0
    remaining_undo = dict(undo_map)

    print(f"\n[원상복구 시작: 총 {len(undo_map)}개 항목]")
    for dest, orig in list(undo_map.items()):
        if not os.path.exists(dest):
            print(f"  [건너뜀] 휴지통에 파일 없음: {dest}")
            remaining_undo.pop(dest, None)
            continue
        try:
            os.makedirs(os.path.dirname(orig), exist_ok=True)
            shutil.move(dest, orig)
            print(f"  [복구됨] {os.path.basename(dest)} -> {orig}")
            restored_count += 1
            remaining_undo.pop(dest, None)
        except OSError as e:
            print(f"  [복구실패] {dest} ({e})")
            failed_count += 1

    save_undo_log(trash_dir, remaining_undo)
    print("\n" + "=" * 50)
    print(f"복구 완료: {restored_count}개 성공, {failed_count}개 실패")


def remove_path(path, args, trash_dir):
    """삭제(또는 휴지통 이동)를 수행하고 결과 메시지를 출력한다."""
    if not args.delete:
        print(f"  삭제예정: {path}")
        return
    try:
        if args.trash:
            dest = move_to_trash(path, trash_dir)
            print(f"  이동함:  {path} -> {dest}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"  삭제함:  {path}")
        else:
            os.remove(path)
            print(f"  삭제함:  {path}")
    except OSError as e:
        print(f"  [실패]  {path} ({e})")


# ---------------------------------------------------------------- 파일 모드


def dedup_files(root, args):
    by_size = defaultdict(list)
    for path in iter_files(root, args.recursive):
        if not os.path.isfile(path) or os.path.islink(path):
            continue
        try:
            by_size[os.path.getsize(path)].append(path)
        except OSError:
            continue

    workers = args.workers or min(8, os.cpu_count() or 4)
    by_hash = defaultdict(list)

    for size, paths in by_size.items():
        if len(paths) < 2:
            continue

        # 10MB 이상 대용량 파일은 1차로 부분 해시 검사
        candidate_groups = defaultdict(list)
        if size > LARGE_FILE_LIMIT:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_path = {executor.submit(file_hash, p, True): p for p in paths}
                for future in as_completed(future_to_path):
                    p = future_to_path[future]
                    ph = future.result()
                    if ph:
                        candidate_groups[ph].append(p)
        else:
            candidate_groups["ALL"] = paths

        # 후보군에 대해 최종 전체 해시 검사 (병렬)
        for phash, cpaths in candidate_groups.items():
            if len(cpaths) < 2:
                continue
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_path = {executor.submit(file_hash, p, False): p for p in cpaths}
                for future in as_completed(future_to_path):
                    p = future_to_path[future]
                    fhash = future.result()
                    if fhash:
                        by_hash[(size, fhash)].append(p)

    trash_dir = os.path.join(root, TRASH_NAME)
    groups = freed = removed = 0

    for (size, _), paths in sorted(by_hash.items(), key=lambda kv: -kv[0][0]):
        if len(paths) < 2:
            continue
        groups += 1
        keep = keeper(paths)
        print(f"\n[중복 파일 {len(paths)}개 · 각 {human(size)}]")
        print(f"  남김:   {keep}")
        for p in paths:
            if p == keep:
                continue
            freed += size
            removed += 1
            remove_path(p, args, trash_dir)

    summarize(args, groups, removed, freed, "파일")


# ---------------------------------------------------------------- 폴더 모드


def folder_signatures(root, workers):
    """각 하위 폴더의 (서명, 누적 크기) 를 계산한다 (병렬 해시 적용)."""
    entries = defaultdict(list)  # dir -> ["rel\0hash", ...]
    sizes = defaultdict(int)     # dir -> 누적 바이트

    files = [f for f in iter_files(root, recursive=True) if os.path.isfile(f) and not os.path.islink(f)]
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_fpath = {executor.submit(file_hash, fpath, False): fpath for f in files}
        for future in as_completed(future_to_fpath):
            fpath = future_to_fpath[future]
            h = future.result()
            if not h:
                continue
            try:
                sz = os.path.getsize(fpath)
            except OSError:
                continue

            d = os.path.dirname(fpath)
            while True:
                rel = os.path.relpath(fpath, d)
                entries[d].append(rel + "\0" + h)
                sizes[d] += sz
                if os.path.normpath(d) == os.path.normpath(root):
                    break
                parent = os.path.dirname(d)
                if parent == d:
                    break
                d = parent

    signatures = {}
    for d, items in entries.items():
        if os.path.normpath(d) == os.path.normpath(root):
            continue  # root 자신은 삭제 대상에서 제외
        blob = "\n".join(sorted(items)).encode("utf-8", "surrogatepass")
        signatures[d] = (hashlib.sha256(blob).hexdigest(), sizes[d])
    return signatures


def dedup_folders(root, args):
    workers = args.workers or min(8, os.cpu_count() or 4)
    signatures = folder_signatures(root, workers)

    by_sig = defaultdict(list)
    for d, (sig, _) in signatures.items():
        by_sig[sig].append(d)

    remove_candidates = set()
    plan = []  # (size, keep, [remove...])
    for sig, dirs in by_sig.items():
        if len(dirs) < 2:
            continue
        keep = keeper(dirs)
        remove = [d for d in dirs if d != keep]
        size = signatures[keep][1]
        plan.append((size, keep, remove))
        remove_candidates.update(remove)

    trash_dir = os.path.join(root, TRASH_NAME)
    groups = freed = removed = 0

    for size, keep, remove in sorted(plan, key=lambda t: -t[0]):
        effective = [
            d for d in remove
            if not any(is_ancestor(other, d) for other in remove_candidates)
        ]
        if not effective:
            continue
        groups += 1
        print(f"\n[중복 폴더 {len(effective) + 1}개 · 각 {human(size)}]")
        print(f"  남김:   {keep}")
        for d in effective:
            freed += signatures[d][1]
            removed += 1
            remove_path(d, args, trash_dir)

    summarize(args, groups, removed, freed, "폴더")


# ---------------------------------------------------------------- 이름 모드


def dedup_by_name(root, args):
    """이름 끝의 ' (숫자)' 사본을 중복으로 본다 (내용은 비교하지 않음)."""
    groups = defaultdict(list)
    for path in iter_files(root, args.recursive):
        if not os.path.isfile(path) or os.path.islink(path):
            continue
        stem, ext = os.path.splitext(os.path.basename(path))
        m = NAME_SUFFIX_RE.match(stem)
        if m:
            base, num = m.group(1), int(m.group(2))
        else:
            base, num = stem, -1
        groups[(os.path.dirname(path), base, ext.lower())].append((num, path))

    trash_dir = os.path.join(root, TRASH_NAME)
    total_groups = removed = freed = 0

    for (_, base, ext), members in sorted(groups.items()):
        if len(members) < 2:
            continue
        members.sort()
        keep = members[0][1]
        total_groups += 1
        print(f"\n[이름 중복 {len(members)}개 · {base}{ext}]")
        print(f"  남김:   {keep}")
        for _, p in members[1:]:
            try:
                freed += os.path.getsize(p)
            except OSError:
                pass
            removed += 1
            remove_path(p, args, trash_dir)

    summarize(args, total_groups, removed, freed, "파일")


# ---------------------------------------------------------------- 공통


def summarize(args, groups, removed, freed, unit):
    print("\n" + "=" * 50)
    if groups == 0:
        print(f"중복 {unit}가 없습니다.")
        return
    print(f"중복 그룹: {groups}개")
    print(f"{'삭제한' if args.delete else '삭제 예정'} {unit}: {removed}개")
    print(f"{'확보한' if args.delete else '확보 가능한'} 용량: {human(freed)}")
    if not args.delete:
        print("\n실제로 지우려면 --delete 를 붙여 다시 실행하세요.")
        print("안전하게 하려면 --delete --trash 로 휴지통 이동을 권장합니다.")


def main():
    ap = argparse.ArgumentParser(description="내용이 같은 중복 파일/폴더 정리")
    ap.add_argument("directory", nargs="?", default=DEFAULT_DIR,
                    help="검사할 폴더 (기본: %(default)s)")
    ap.add_argument("--folders", action="store_true",
                    help="파일 대신 내용이 같은 중복 '폴더'를 찾는다 (항상 재귀)")
    ap.add_argument("--by-name", dest="by_name", action="store_true",
                    help="이름 끝 ' (숫자)' 사본을 중복으로 본다 (내용 비교 안 함)")
    ap.add_argument("--delete", action="store_true", help="실제로 삭제 실행")
    ap.add_argument("--trash", action="store_true",
                    help="삭제 대신 _duplicates_trash 폴더로 이동")
    ap.add_argument("--recursive", action="store_true",
                    help="하위 폴더까지 검사 (파일 모드 전용)")
    ap.add_argument("--restore", action="store_true",
                    help="휴지통(_duplicates_trash) 항목을 원래 위치로 원상복구")
    ap.add_argument("--workers", type=int, default=None,
                    help="병렬 처리에 사용할 최대 스레드 수 (기본: 자동)")
    args = ap.parse_args()

    root = os.path.abspath(args.directory)
    if not os.path.isdir(root):
        print(f"[오류] 폴더를 찾을 수 없습니다: {root}")
        sys.exit(1)

    if args.restore:
        restore_from_trash(root)
    elif args.folders:
        dedup_folders(root, args)
    elif args.by_name:
        dedup_by_name(root, args)
    else:
        dedup_files(root, args)


if __name__ == "__main__":
    main()
