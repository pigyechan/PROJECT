"""
runs/ 디렉터리를 감시하다가 새 01_input.json이 생기면 main.py를 자동 실행한다.

사용법 (Blog_Writer/ 루트에서):
  python pipeline/watcher.py
"""

import subprocess
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class RunHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.name != "01_input.json":
            return

        run_dir = path.parent

        # 이미 처리 완료된 run이면 스킵
        if (run_dir / "04_next.json").exists() or (run_dir / "99_regen_request.json").exists():
            print(f"[watcher] 이미 처리된 run, 스킵: {run_dir.name}")
            return

        print(f"\n[watcher] 새 input 감지 → 파이프라인 시작: {run_dir.name}")
        result = subprocess.run(
            [sys.executable, "pipeline/main.py", str(run_dir)],
            cwd=Path.cwd(),
        )
        if result.returncode == 0:
            print(f"[watcher] 완료 (PASS): {run_dir.name}")
        else:
            print(f"[watcher] 완료 (REJECT): {run_dir.name}")


def main() -> None:
    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)

    handler = RunHandler()
    observer = Observer()
    observer.schedule(handler, str(runs_dir), recursive=True)
    observer.start()

    print(f"[watcher] 감시 시작: {runs_dir.resolve()}")
    print("[watcher] create_input.py로 input을 만들면 자동으로 파이프라인이 실행됩니다.")
    print("[watcher] 종료하려면 Ctrl+C\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[watcher] 종료")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
