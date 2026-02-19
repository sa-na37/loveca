LLCG manual UI (web) - slim package

Expected folder layout (inside your `loveca` directory):
  loveca/
    run_llocg_ui_web.py
    README.txt
    llocg_ui/
      __init__.py
      server.py
      db.py
      engine.py
      images.py

How to run:
  cd /Users/tekitou/Desktop/gsim/loveca
  python3 run_llocg_ui_web.py --root ./llocg_db_out_full --code 1RCBL --port 8000

Notes:
- Avoid keeping duplicate/old files (e.g. loveca/server.py) to prevent import drift.
- If macOS blocks execution (EPERM), remove quarantine attributes:
    xattr -dr com.apple.quarantine run_llocg_ui_web.py README.txt llocg_ui
