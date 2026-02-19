LLCG Manual UI (Clean v4)
========================

起動:
  python3 run_llocg_ui_web.py --deck-code 1RCBL

前提:
  - playmat.jpg が loveca 直下にあること
  - 画像フォルダ: ./llocg_db_out_full/card_images
  - デッキTSV:   ./llocg_db_out_full/decklists/{code}.tsv または deck_{code}.tsv

ブラウザ:
  http://127.0.0.1:8787

操作（現行 v4）:
  - Deck(右上)クリック: 1枚ドロー（Shift+クリックで3枚）
  - 手札クリック: 選択（MAIN=1枚 / LIVESET=3枚）
  - ステージ枠クリック: 選択カードを配置（LIVEカードは不可）
  - NEXT: MAIN <-> LIVESET（LIVESET->MAIN時に turn+1, energy+1）
  - LiveSet→Resolve: ライブセットを解決領域へ（確認中はNEXTでも閉じられます）
  - ACK: 解決領域→控え室
  - 控え室クリック: 一覧ポップアップ
