#!/usr/bin/env python3
"""
verify_corpus.py

For every progNN_*.c in this directory:
  1. compile with `<CC> -Wall -Wextra -std=c11 -Werror` (warnings are
     errors, since the spec requires zero warnings)
  2. run each of the 5 test cases from the matching progNN_*.tests.json
  3. compare actual stdout against expected_stdout byte-for-byte
  4. report a per-program and grand-total summary

Exit code is 0 iff all programs compile cleanly and all 15*5 tests pass.

Usage: python3 verify_corpus.py [--cc CC]
  CC defaults to "cc" (pass --cc gcc-15, --cc gcc, or --cc clang as needed).
This script only reads files in this directory and writes to a temporary
build directory; it does not modify any file in the corpus.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cc", default="cc", help="C compiler to use")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    try:
        cc_version = subprocess.run(
            [args.cc, "--version"], capture_output=True, text=True
        ).stdout.splitlines()[0]
    except FileNotFoundError:
        print(f"ERROR: compiler '{args.cc}' not found")
        return 1

    print(f"Using compiler: {args.cc} ({cc_version})")

    sources = sorted(glob.glob("prog[0-9][0-9]_*.c"))
    if not sources:
        print("ERROR: no prog*.c files found in this directory")
        return 1

    total_programs = 0
    total_programs_ok = 0
    total_tests = 0
    total_tests_ok = 0
    failed_programs = []

    with tempfile.TemporaryDirectory() as build_dir:
        print(f"Build dir: {build_dir}\n")

        for src in sources:
            name = src[:-2]  # strip ".c"
            json_path = f"{name}.tests.json"
            bin_path = os.path.join(build_dir, name)
            total_programs += 1

            if not os.path.isfile(json_path):
                print(f"[{name}] FAIL: missing {json_path}")
                failed_programs.append(f"{name} (missing tests.json)")
                continue

            compile_cmd = [
                args.cc, "-Wall", "-Wextra", "-std=c11", "-Werror",
                "-o", bin_path, src,
            ]
            compile_result = subprocess.run(
                compile_cmd, capture_output=True, text=True
            )
            if compile_result.returncode != 0:
                print(f"[{name}] FAIL: compilation error/warning")
                for line in compile_result.stderr.splitlines():
                    print(f"    {line}")
                failed_programs.append(f"{name} (compile)")
                continue

            with open(json_path) as f:
                spec = json.load(f)

            if spec.get("program") != name:
                print(
                    f"[{name}] WARNING: tests.json 'program' field "
                    f"'{spec.get('program')}' does not match filename"
                )

            tests = spec["tests"]
            program_tests_ok = 0

            for t in tests:
                total_tests += 1
                test_id = t["id"]
                test_args = t.get("args", [])
                test_stdin = t.get("stdin", "")
                expected = t["expected_stdout"]

                try:
                    run_result = subprocess.run(
                        [bin_path] + list(test_args),
                        input=test_stdin,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    actual = run_result.stdout
                except subprocess.TimeoutExpired:
                    actual = "<TIMEOUT>"

                if actual == expected:
                    program_tests_ok += 1
                    total_tests_ok += 1
                else:
                    print(f"[{name}] test {test_id} FAIL")
                    print(f"    args:     {test_args}")
                    print(f"    stdin:    {test_stdin!r}")
                    print(f"    expected: {expected!r}")
                    print(f"    actual:   {actual!r}")

            program_total = len(tests)
            if program_tests_ok == program_total == 5:
                total_programs_ok += 1
                print(f"[{name}] OK: {program_tests_ok}/{program_total} tests passed")
            else:
                print(
                    f"[{name}] FAIL: {program_tests_ok}/{program_total} "
                    f"tests passed (expected 5)"
                )
                failed_programs.append(
                    f"{name} (tests: {program_tests_ok}/{program_total})"
                )
            print()

    print("================ SUMMARY ================")
    print(
        f"Programs: {total_programs_ok}/{total_programs} compiled cleanly "
        f"and passed all 5 tests"
    )
    print(f"Tests:    {total_tests_ok}/{total_tests} individual test cases passed")

    if failed_programs:
        print("Failed programs:")
        for p in failed_programs:
            print(f"  - {p}")
        return 1

    print("All programs and all tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
