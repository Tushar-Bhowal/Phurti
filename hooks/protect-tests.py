#!/usr/bin/env python3
import json
import os
import re
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(0)

tool = data.get("tool_name", "")
if tool not in ("Edit", "MultiEdit", "Write", "apply_patch"):
    sys.exit(0)

ti = data.get("tool_input", {}) or {}
if not isinstance(ti, dict):
    sys.exit(0)
path = ti.get("file_path", "") or ""


def is_test_file(p):
    if not isinstance(p, str):
        return False
    p = p.replace("\\", "/")
    low = "/" + p.lower().lstrip("/")
    base = os.path.basename(low)
    if "/__tests__/" in low or "/test/" in low or "/tests/" in low:
        return True
    if ".test." in base or ".spec." in base:
        return True
    if base.startswith("test_") and base.endswith(".py"):
        return True
    if base.endswith(("_test.py", "_test.go", "_test.rb", "_spec.rb", "test.ts", "test.js")):
        return True
    return False

ASSERT_RE = re.compile(
    r"(\bassert\b|\bassert_\w+|\bassertEqual\b|\bassertTrue\b|\bassertFalse\b|"
    r"\bassertRaises\b|\bassertIn\b|\bassertIs\b|\bexpect\s*\(|\.should\b|"
    r"\bEXPECT_\w+|\bASSERT_\w+|\.to\.(equal|be|deep|have|contain|throw))",
    re.IGNORECASE,
)
SKIP_RE = re.compile(
    r"(\.skip\b|\bxit\b|\bxdescribe\b|@pytest\.mark\.skip|@unittest\.skip|"
    r"\bit\.skip\b|\btest\.skip\b|\bdescribe\.skip\b|\bt\.Skip\(|\bpending\b)",
    re.IGNORECASE,
)


def count(rx, s):
    return len(rx.findall(s or ""))


def read_file(path):
    try:
        base = data.get("cwd") or os.getcwd()
        with open(os.path.join(base, path), encoding="utf-8", errors="replace") as stream:
            return stream.read()
    except OSError:
        return ""


def changes():
    if tool == "apply_patch":
        patch = ti.get("command", "")
        if not isinstance(patch, str):
            return
        current = None
        old, new = [], []
        removed = False
        for line in patch.splitlines():
            if line.startswith(("*** Update File: ", "*** Add File: ", "*** Delete File: ")) or line == "*** End Patch":
                if current is not None:
                    yield current, "\n".join(old), "\n".join(new), removed
                current, old, new, removed = None, [], [], False
                if line != "*** End Patch":
                    current = line.split(": ", 1)[1]
                    if line.startswith("*** Delete File: "):
                        old = [read_file(current)]
                        removed = True
            elif line.startswith("*** Move to: "):
                removed = not is_test_file(line.split(": ", 1)[1])
            elif current is not None:
                if line.startswith("-"):
                    old.append(line[1:])
                elif line.startswith("+"):
                    new.append(line[1:])
        if current is not None:
            yield current, "\n".join(old), "\n".join(new), removed
    elif is_test_file(path):
        if tool == "Edit":
            yield path, ti.get("old_string", ""), ti.get("new_string", ""), False
        elif tool == "MultiEdit":
            edits = ti.get("edits", []) or []
            for edit in edits:
                if isinstance(edit, dict):
                    yield path, edit.get("old_string", ""), edit.get("new_string", ""), False
        else:
            yield path, read_file(path), ti.get("content", ""), False


for file_path, old, new, removed in changes():
    if not is_test_file(file_path) or not isinstance(old, str) or not isinstance(new, str):
        continue
    reasons = []
    if removed:
        reasons.append("deletes a test file or moves it outside a recognized test path")
    if count(ASSERT_RE, new) < count(ASSERT_RE, old):
        reasons.append("removes test assertions")
    if count(SKIP_RE, new) > count(SKIP_RE, old):
        reasons.append("adds a skip/pending marker that disables a test")
    if reasons:
        sys.stderr.write(
            f"Blocked: {file_path} " + " and ".join(reasons) + ". "
            "Fix the code under test instead of weakening the suite. If the test "
            "itself is wrong, explain why and ask before changing it.\n"
        )
        sys.exit(2)

sys.exit(0)
