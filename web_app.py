#!/usr/bin/env python3
"""and-hub Mobile Web App — 스마트폰 브라우저에 예쁜 모바일 앱 화면을 띄워주는 경량 서버.

외부 라이브러리(pip) 설치 필요 없이 파이썬 표준 라이브러리(http.server)만으로 동작합니다.
스마트폰 화면에서 터치 한 번으로 스캔, 중복 정리, 원위치 복구, 휴지통 비우기를 수행합니다.
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import dedup_downloads as dedup

PORT = 8088
DEFAULT_DIR = "/storage/emulated/0/Download"
if sys.platform.startswith("win"):
    DEFAULT_DIR = os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\Default"), "Downloads")

HTML_PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>and-hub 중복 파일 정리기</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text-main: #f8fafc;
      --text-sub: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --border: #334155;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text-main); min-height: 100vh; padding: 16px; display: flex; flex-direction: column; align-items: center; }
    .container { width: 100%; max-width: 480px; display: flex; flex-direction: column; gap: 14px; }
    .header { text-align: center; padding: 12px 0; }
    .header h1 { font-size: 20px; font-weight: 700; color: #60a5fa; display: flex; align-items: center; justify-content: center; gap: 8px; }
    .header p { font-size: 12px; color: var(--text-sub); margin-top: 4px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.25); }
    .label { font-size: 13px; color: var(--text-sub); font-weight: 600; margin-bottom: 6px; display: block; }
    .input-box { width: 100%; background: #0f172a; border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; color: #fff; font-size: 13px; }
    .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .btn { border: none; border-radius: 10px; padding: 14px 8px; font-size: 14px; font-weight: 700; color: #fff; cursor: pointer; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; transition: all 0.2s; }
    .btn:active { transform: scale(0.97); filter: brightness(0.9); }
    .btn-primary { background: var(--primary); }
    .btn-success { background: var(--success); }
    .btn-warning { background: var(--warning); color: #000; }
    .btn-danger { background: var(--danger); }
    .btn-full { grid-column: span 2; }
    .log-box { background: #0b0f19; border: 1px solid var(--border); border-radius: 8px; padding: 12px; font-family: monospace; font-size: 12px; max-height: 220px; overflow-y: auto; white-space: pre-wrap; line-height: 1.5; color: #cbd5e1; }
    .stat-badge { display: flex; justify-content: space-between; font-size: 12px; padding: 8px 12px; background: #0f172a; border-radius: 8px; border: 1px solid var(--border); }
    .loader { display: none; text-align: center; color: #60a5fa; font-size: 13px; font-weight: 600; padding: 6px 0; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📱 and-hub 중복 파일 정리기</h1>
      <p>스마트폰 다운로드 서랍 초고속 자동 정리 도우미</p>
    </div>

    <div class="card">
      <label class="label">📂 대상 폴더 경로</label>
      <input type="text" id="targetDir" class="input-box" value="DEFAULT_DIR_PLACEHOLDER">
    </div>

    <div class="card">
      <label class="label">⚡ 원터치 작업 메뉴</label>
      <div class="btn-grid">
        <button class="btn btn-primary" onclick="runAction('scan')">
          <span>🔍 1. 중복 스캔</span>
          <span style="font-size: 11px; font-weight: normal; opacity: 0.85;">(지우지 않고 미리보기)</span>
        </button>
        <button class="btn btn-success" onclick="runAction('clean')">
          <span>🗑️ 2. 안전 정리</span>
          <span style="font-size: 11px; font-weight: normal; opacity: 0.85;">(휴지통으로 이동)</span>
        </button>
        <button class="btn btn-warning" onclick="runAction('restore')">
          <span>⏪ 3. 원위치 복구</span>
          <span style="font-size: 11px; font-weight: normal; opacity: 0.85;">(실수 정리 롤백)</span>
        </button>
        <button class="btn btn-danger" onclick="runAction('empty_trash')">
          <span>🧹 4. 휴지통 비우기</span>
          <span style="font-size: 11px; font-weight: normal; opacity: 0.85;">(용량 완전 확보)</span>
        </button>
      </div>
      <div id="loader" class="loader">⏳ 검사 및 정리 작업 실행 중...</div>
    </div>

    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <label class="label" style="margin: 0;">📜 실시간 작업 로그</label>
        <button onclick="clearLog()" style="background: none; border: none; color: #64748b; font-size: 11px; cursor: pointer;">로그 지우기</button>
      </div>
      <div id="logBox" class="log-box">준비 완료. 작업 버튼을 터치하세요.</div>
    </div>
  </div>

  <script>
    async function runAction(act) {
      const dir = document.getElementById('targetDir').value.trim();
      if (!dir) { alert('대상 폴더 경로를 입력하세요.'); return; }
      
      const loader = document.getElementById('loader');
      const logBox = document.getElementById('logBox');
      loader.style.display = 'block';
      logBox.innerText += `\\n==> [${act.toUpperCase()} 요청 시작] 대상: ${dir}\\n`;
      logBox.scrollTop = logBox.scrollHeight;

      try {
        const res = await fetch(`/api/${act}?dir=${encodeURIComponent(dir)}`);
        const data = await res.json();
        logBox.innerText += `\\n${data.output}\\n`;
        logBox.scrollTop = logBox.scrollHeight;
      } catch (err) {
        logBox.innerText += `\\n[오류] 통신 실패: ${err.message}\\n`;
      } finally {
        loader.style.display = 'none';
      }
    }

    function clearLog() {
      document.getElementById('logBox').innerText = '로그가 초기화되었습니다.';
    }
  </script>
</body>
</html>
"""


class DedupRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        target_dir = query.get("dir", [DEFAULT_DIR])[0]

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html_content = HTML_PAGE.replace("DEFAULT_DIR_PLACEHOLDER", DEFAULT_DIR)
            self.wfile.write(html_content.encode("utf-8"))
            return

        # API Endpoints
        if path.startswith("/api/"):
            action = path.replace("/api/", "")
            output = self.handle_api(action, target_dir)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "output": output}, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def handle_api(self, action, target_dir):
        if not os.path.exists(target_dir):
            return f"[오류] 폴더를 찾을 수 없습니다: {target_dir}"

        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            try:
                if action == "scan":
                    print(f"=== [1/3] 내용 중복 파일 스캔 ===")
                    args_file = type("Args", (), {"recursive": True, "delete": False, "trash": False, "interactive": False, "workers": 4})()
                    dedup.dedup_files(target_dir, args_file)
                    print(f"\n=== [2/3] 이름 사본 스캔 ===")
                    args_name = type("Args", (), {"recursive": True, "delete": False, "trash": False, "interactive": False, "workers": 4})()
                    dedup.dedup_by_name(target_dir, args_name)
                    print(f"\n=== [3/3] 중복 폴더 스캔 ===")
                    args_folder = type("Args", (), {"recursive": True, "delete": False, "trash": False, "interactive": False, "workers": 4})()
                    dedup.dedup_folders(target_dir, args_folder)
                
                elif action == "clean":
                    print(f"=== [안전 정리: 파일 + 이름사본 + 중복폴더] ===")
                    args = type("Args", (), {"recursive": True, "delete": True, "trash": True, "interactive": False, "workers": 4})()
                    dedup.dedup_files(target_dir, args)
                    dedup.dedup_by_name(target_dir, args)
                    dedup.dedup_folders(target_dir, args)
                    print("\n[완료] 중복 파일들이 _duplicates_trash 폴더로 안전하게 이동되었습니다.")

                elif action == "restore":
                    print(f"=== [원위치 복구 실행] ===")
                    dedup.restore_from_trash(target_dir)

                elif action == "empty_trash":
                    trash_dir = os.path.join(target_dir, dedup.TRASH_NAME)
                    if os.path.exists(trash_dir):
                        shutil.rmtree(trash_dir)
                        print(f"[휴지통 비우기 완료] {trash_dir} 완전 삭제됨. 용량이 확보되었습니다.")
                    else:
                        print(f"비울 휴지통이 없습니다: {trash_dir}")

            except Exception as e:
                print(f"[실행 오류] {e}")

        return f.getvalue()

    def log_message(self, format, *args):
        # 불필요한 콘솔 HTTP 요청 로그 숨김
        pass


def open_browser():
    time.sleep(0.5)
    url = f"http://localhost:{PORT}"
    # Android Termux 환경에서는 termux-open-url 우선 시도
    try:
        subprocess.run(["termux-open-url", url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        webbrowser.open(url)


def main():
    print(f"==> and-hub 모바일 웹앱 서버 시작: http://localhost:{PORT}")
    threading.Thread(target=open_browser, daemon=True).start()
    server = HTTPServer(("0.0.0.0", PORT), DedupRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버가 종료되었습니다.")


if __name__ == "__main__":
    main()
