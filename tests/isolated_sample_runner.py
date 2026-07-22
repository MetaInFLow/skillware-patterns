"""Guarded runner for trusted repository samples, not an OS security sandbox.

The parent harness starts this file with ``python -I -S -B`` in a copied sample
working directory. The guards make accidental network and process use fail
closed and keep imports off the repository checkout. They do not defend against
hostile native code, interpreter exploits, or other adversarial Python objects.
"""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import traceback
import unittest


class IsolationViolation(RuntimeError):
    pass


SAMPLE = None
REAL_SOCKET = socket.socket


def blocked(kind):
    def reject(*args, **kwargs):
        raise IsolationViolation(
            f"trusted-sample isolation guard blocked {kind}; "
            "this is not an OS security sandbox"
        )

    return reject


def audit_guard(event, args):
    if event.startswith("socket."):
        raise IsolationViolation(
            "trusted-sample isolation guard blocked network access; "
            "this is not an OS security sandbox"
        )
    if event in {
        "os.exec",
        "os.fork",
        "os.forkpty",
        "os.posix_spawn",
        "os.system",
        "pty.spawn",
        "subprocess.Popen",
    }:
        raise IsolationViolation(
            "trusted-sample isolation guard blocked process creation; "
            "this is not an OS security sandbox"
        )


class GuardedSocket(REAL_SOCKET):
    def connect(self, *args, **kwargs):
        raise IsolationViolation("trusted-sample isolation guard blocked network access")

    def connect_ex(self, *args, **kwargs):
        raise IsolationViolation("trusted-sample isolation guard blocked network access")

    def send(self, *args, **kwargs):
        raise IsolationViolation("trusted-sample isolation guard blocked network access")

    def sendall(self, *args, **kwargs):
        raise IsolationViolation("trusted-sample isolation guard blocked network access")

    def sendto(self, *args, **kwargs):
        raise IsolationViolation("trusted-sample isolation guard blocked network access")


def called_from_focused_tests() -> bool:
    tests_root = (SAMPLE / "tests").resolve()
    frame = sys._getframe(1)
    while frame is not None:
        try:
            Path(frame.f_code.co_filename).resolve().relative_to(tests_root)
        except (OSError, ValueError):
            frame = frame.f_back
            continue
        return True
    return False


def controlled_test_run(command, **kwargs):
    if not called_from_focused_tests():
        raise IsolationViolation(
            "trusted-sample isolation guard blocked subprocess.run; "
            "this is not an OS security sandbox"
        )
    if not isinstance(command, (list, tuple)) or len(command) < 2:
        raise IsolationViolation("focused tests may invoke only their copied demo")

    try:
        executable = Path(command[0]).resolve()
        demo_path = Path(command[1]).resolve()
    except (OSError, TypeError, ValueError) as exc:
        raise IsolationViolation(
            "focused tests may invoke only their copied demo"
        ) from exc
    expected_demo = (SAMPLE / "scripts/run_demo.py").resolve()
    if executable != Path(sys.executable).resolve() or demo_path != expected_demo:
        raise IsolationViolation("focused tests may invoke only their copied demo")

    allowed_keywords = {
        "capture_output",
        "check",
        "cwd",
        "env",
        "text",
        "timeout",
    }
    unknown = set(kwargs) - allowed_keywords
    if unknown:
        raise IsolationViolation(
            "unsupported in-process CLI test options: " + ", ".join(sorted(unknown))
        )
    if kwargs.get("capture_output") is not True:
        raise IsolationViolation("focused CLI tests must capture output")

    requested_cwd = Path(kwargs.get("cwd", SAMPLE)).resolve()
    try:
        requested_cwd.relative_to(SAMPLE.resolve())
    except ValueError as exc:
        raise IsolationViolation("focused CLI test cwd must stay inside the sample") from exc

    stdout = StringIO()
    stderr = StringIO()
    previous_argv = sys.argv[:]
    previous_cwd = Path.cwd()
    previous_environment = os.environ.copy()
    returncode = 0
    try:
        sys.argv = [str(expected_demo), *[str(value) for value in command[2:]]]
        os.chdir(requested_cwd)
        if kwargs.get("env") is not None:
            os.environ.clear()
            os.environ.update(kwargs["env"])
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                runpy.run_path(str(expected_demo), run_name="__main__")
            except SystemExit as exc:
                if exc.code is None:
                    returncode = 0
                elif isinstance(exc.code, int):
                    returncode = exc.code
                else:
                    print(exc.code, file=sys.stderr)
                    returncode = 1
            except BaseException:
                traceback.print_exc()
                returncode = 1
    finally:
        sys.argv = previous_argv
        os.chdir(previous_cwd)
        os.environ.clear()
        os.environ.update(previous_environment)

    captured_stdout = stdout.getvalue()
    captured_stderr = stderr.getvalue()
    if kwargs.get("text") is not True:
        io_encoding = (kwargs.get("env") or {}).get("PYTHONIOENCODING", "utf-8")
        encoding, _, error_mode = io_encoding.partition(":")
        captured_stdout = captured_stdout.encode(
            encoding or "utf-8", errors=error_mode or "strict"
        )
        captured_stderr = captured_stderr.encode(
            encoding or "utf-8", errors=error_mode or "strict"
        )

    completed = subprocess.CompletedProcess(
        command,
        returncode,
        stdout=captured_stdout,
        stderr=captured_stderr,
    )
    if kwargs.get("check") and returncode:
        raise subprocess.CalledProcessError(
            returncode,
            command,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return completed


def install_guards() -> None:
    sys.addaudithook(audit_guard)

    socket.socket = GuardedSocket
    socket.create_connection = blocked("network connection")
    socket.getaddrinfo = blocked("DNS lookup")
    socket.gethostbyaddr = blocked("DNS lookup")
    socket.gethostbyname = blocked("DNS lookup")
    socket.gethostbyname_ex = blocked("DNS lookup")
    socket.getnameinfo = blocked("DNS lookup")

    subprocess.Popen = blocked("subprocess.Popen")
    subprocess.call = blocked("subprocess.call")
    subprocess.check_call = blocked("subprocess.check_call")
    subprocess.check_output = blocked("subprocess.check_output")
    subprocess.getoutput = blocked("subprocess.getoutput")
    subprocess.getstatusoutput = blocked("subprocess.getstatusoutput")
    subprocess.run = controlled_test_run

    os.system = blocked("os.system")
    os.popen = blocked("os.popen")
    for name in dir(os):
        if name.startswith("spawn"):
            setattr(os, name, blocked(f"os.{name}"))


def constrain_sys_path(sample: Path) -> None:
    roots = {Path(sys.base_prefix).resolve(), Path(sys.prefix).resolve()}
    standard_library = []
    for entry in sys.path:
        if not entry:
            continue
        candidate = Path(entry).resolve()
        if "site-packages" in candidate.parts or "dist-packages" in candidate.parts:
            continue
        if any(candidate == root or root in candidate.parents for root in roots):
            standard_library.append(str(candidate))
    sys.path[:] = [str(sample), *standard_library]


def run_demo(sample: Path) -> int:
    demo = sample / "scripts/run_demo.py"
    sys.argv = [str(demo)]
    try:
        runpy.run_path(str(demo), run_name="__main__")
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 1
    return 0


def run_tests(sample: Path) -> int:
    suite = unittest.defaultTestLoader.discover(str(sample / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv) -> int:
    global SAMPLE

    if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
        print("runner requires python -I -S -B", file=sys.stderr)
        return 2
    if len(argv) != 3 or argv[1] not in {"demo", "tests"}:
        print("usage: isolated_sample_runner.py {demo|tests} SAMPLE", file=sys.stderr)
        return 2

    SAMPLE = Path(argv[2]).resolve()
    if not SAMPLE.is_dir():
        print("sample directory does not exist", file=sys.stderr)
        return 2
    os.chdir(SAMPLE)
    constrain_sys_path(SAMPLE)
    install_guards()
    if argv[1] == "demo":
        return run_demo(SAMPLE)
    return run_tests(SAMPLE)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
