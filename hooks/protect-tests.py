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

is_antigravity = "--host" in sys.argv and "antigravity" in sys.argv
if "toolCall" in data or "workspacePaths" in data:
    is_antigravity = True

tool_call = data.get("toolCall") if isinstance(data.get("toolCall"), dict) else {}
tool = data.get("tool_name", "") or tool_call.get("name", "")
if tool not in ("Edit", "MultiEdit", "Write", "apply_patch", "edit_file", "write_file"):
    if is_antigravity:
        print(json.dumps({"decision": "allow"}))
    sys.exit(0)

ti = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else (tool_call.get("args") if isinstance(tool_call.get("args"), dict) else {})
path = ti.get("file_path", "") or ti.get("Path", "")


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
        full_path = path if os.path.isabs(path) else os.path.join(base, path)
        with open(full_path, encoding="utf-8", errors="replace") as stream:
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
    elif tool == "edit_file":
        target_path = ti.get("Path", "")
        if is_test_file(target_path):
            yield target_path, ti.get("Target", ""), ti.get("Replacement", ""), False
    elif tool == "write_file":
        target_path = ti.get("Path", "")
        if is_test_file(target_path):
            old_content = read_file(target_path)
            new_content = (old_content + ti.get("Content", "")) if ti.get("Append") else ti.get("Content", "")
            yield target_path, old_content, new_content, False
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
        msg = (
            f"Blocked: {file_path} " + " and ".join(reasons) + ". "
            "Fix the code under test instead of weakening the suite. If the test "
            "itself is wrong, explain why and ask before changing it."
        )
        if is_antigravity:
            print(json.dumps({"decision": "deny", "reason": msg}))
            sys.exit(0)
        sys.stderr.write(msg + "\n")
        sys.exit(2)

if is_antigravity:
    print(json.dumps({"decision": "allow"}))
sys.exit(0)
