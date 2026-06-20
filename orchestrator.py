"""
PROJECT 루트에서 실행하는 통합 오케스트레이터.
Blog_Writer / Test_Writer / Career_Planner 의 runs/ 폴더를 동시에 감시한다.
새 01_input.json이 생기면 해당 프로젝트의 파이프라인을 자동으로 실행한다.

사용법 (PROJECT 루트에서):
  python orchestrator.py
"""

import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

BASE_DIR = Path(__file__).parent

PIPELINES = {
    "Blog_Writer":    BASE_DIR / "Blog_Writer",
    "Test_Writer":    BASE_DIR / "Test_Writer",
    "Career_Planner": BASE_DIR / "Career_Planner",
}

# 각 파이프라인별 권장 실행 주기 (일) — None이면 알림 비활성화
PROMPT_INTERVALS = {
    "Blog_Writer":    7,
    "Test_Writer":    None,
    "Career_Planner": 7,
}

# 알림 체크 주기 (시간)
PROMPT_CHECK_HOURS = 6


def already_processed(run_dir: Path) -> bool:
    # 02_output.json이 이미 있으면 eval_existing.py가 먼저 콘텐츠를 주입한 것 — Generator 재실행 방지
    return (
        (run_dir / "04_next.json").exists()
        or (run_dir / "99_regen_request.json").exists()
        or (run_dir / "02_output.json").exists()
    )


def _last_run_time(project_dir: Path) -> datetime | None:
    runs_dir = project_dir / "runs"
    if not runs_dir.exists():
        return None
    for d in sorted(runs_dir.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        parts = d.name.split("_")
        if len(parts) >= 2:
            try:
                return datetime.strptime(f"{parts[0]}_{parts[1]}", "%Y%m%d_%H%M%S")
            except ValueError:
                continue
    return None


def _toast(title: str, message: str) -> None:
    script = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$n = New-Object System.Windows.Forms.NotifyIcon;"
        "$n.Icon = [System.Drawing.SystemIcons]::Information;"
        "$n.Visible = $true;"
        f"$n.ShowBalloonTip(8000, '{title}', '{message}', [System.Windows.Forms.ToolTipIcon]::Info);"
        "Start-Sleep -Seconds 9;"
        "$n.Dispose()"
    )
    subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
        creationflags=0x08000000,  # CREATE_NO_WINDOW
    )


def _prompt_loop() -> None:
    while True:
        time.sleep(PROMPT_CHECK_HOURS * 3600)
        now = datetime.now()
        for project_name, project_dir in PIPELINES.items():
            interval_days = PROMPT_INTERVALS.get(project_name)
            if interval_days is None:
                continue
            last = _last_run_time(project_dir)
            if last is None:
                msg = f"{project_name}: 아직 실행 기록이 없습니다."
                print(f"\n[orchestrator] ⏰ {msg}")
            elif (now - last).days >= interval_days:
                elapsed = (now - last).days
                msg = f"{project_name}: 마지막 실행 후 {elapsed}일이 지났습니다."
                print(f"\n[orchestrator] ⏰ {msg}")
            else:
                continue
            print(f"[orchestrator]    새 콘텐츠를 만들려면: cd {project_dir} && python pipeline/create_input.py\n")
            _toast("📝 Pipeline Orchestrator", msg)


def run_pipeline(project_name: str, run_dir: Path) -> None:
    project_dir = PIPELINES[project_name]
    print(f"\n[orchestrator] ▶ {project_name} 파이프라인 시작")
    print(f"               run: {run_dir.name}")

    result = subprocess.run(
        [sys.executable, "pipeline/main.py", str(run_dir)],
        cwd=project_dir,
    )

    status = "PASS" if result.returncode == 0 else "REJECT"
    print(f"[orchestrator] ■ {project_name} 완료 ({status}): {run_dir.name}\n")


_DEBOUNCE_SECONDS = 10


class PipelineHandler(FileSystemEventHandler):
    def __init__(self, project_name: str):
        self.project_name = project_name
        self._last_triggered: dict[str, float] = {}

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.name != "01_input.json":
            return

        run_dir = path.parent

        # watchdog이 동일 파일에 대해 이벤트를 중복 발생시키는 경우 무시
        key = str(run_dir)
        now = time.time()
        if now - self._last_triggered.get(key, 0) < _DEBOUNCE_SECONDS:
            return
        self._last_triggered[key] = now

        if already_processed(run_dir):
            print(f"[orchestrator] 이미 처리된 run 스킵: {run_dir.name}")
            return

        run_pipeline(self.project_name, run_dir)


def main() -> None:
    log_path = BASE_DIR / "orchestrator.log"
    _log = open(log_path, "a", encoding="utf-8", buffering=1)
    import sys as _sys
    _sys.stdout = _log
    _sys.stderr = _log
    print(f"\n{'='*50}")
    print(f"[orchestrator] 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    observer = Observer()

    for project_name, project_dir in PIPELINES.items():
        runs_dir = project_dir / "runs"
        runs_dir.mkdir(exist_ok=True)

        handler = PipelineHandler(project_name)
        observer.schedule(handler, str(runs_dir), recursive=True)
        print(f"[orchestrator] 감시 등록: {project_name:15s} → {runs_dir}")

    observer.start()
    print("\n[orchestrator] 모든 파이프라인 감시 시작.")
    print("[orchestrator] create_input.py로 input을 만들면 자동 실행됩니다.")
    print("[orchestrator] 종료하려면 Ctrl+C")

    intervals_str = " / ".join(f"{p}: {d}일" for p, d in PROMPT_INTERVALS.items())
    print(f"[orchestrator] 주기적 알림 활성화 ({intervals_str})\n")

    prompt_thread = threading.Thread(target=_prompt_loop, daemon=True)
    prompt_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[orchestrator] 종료")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
