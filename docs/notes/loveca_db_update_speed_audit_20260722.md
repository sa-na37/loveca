# Loveca DB update speed audit 20260722

対象ログ: ユーザー共有 `run_20260722_162844`。

## 読み取れた状況

- `[UPDATE-MODE] incremental` で既存カードページ 1060 件は再利用されており、本文ページの大量再取得は発生していない。
- `scrape` は `to process: 0` だが、商品ページ確認は `fetch=5 reuse=34`。起動引数の `--delay 10.0` により、ここだけでも最低 50 秒程度の待機が入る可能性がある。
- `normalize` / `mine` / `audit` / `compile` / `db-generation-audit` は、カード新規 0 件でも毎回フル実行されている。
- 画像系は `reprint_missing=26`、`IMAGE-FETCH-MODE targets=26`。画像取得自体は `ok_files=29 skipped=29 failed=0` で、既存ファイル確認が多い。
- `[IMAGE-MANIFEST] expansion_scan` と再録候補 enrichment が複数走っており、画像が増えない場合でも探索・照合コストが残っている。

## 短縮案

1. カード新規 0 件、商品レジストリ差分 0 件、manual overrides 差分 0 件の場合は、`normalize` / `mine` / `compile` / strict audit を省略する fast path を追加する。
2. 起動時更新では strict audit を「最終生成物が変わった場合のみ」に限定し、手動のフル更新ボタンだけで毎回 strict audit を実行する。
3. 画像取得は `missing image count` と manifest mtime/hash を比較し、前回と同じ missing set で 24 時間以内なら skip する。
4. 商品ページの `fetch=5` は prerelease / release date unknown の再確認が原因なので、起動時更新では product fetch delay を短くするのではなく、前回 429 なしの永続キャッシュを優先し、期限切れ商品だけを非同期/手動更新に回す。
5. 更新画面には `fresh_only`、画像 target、新規保存画像、画像 failed を表示し、ユーザーが「実質更新なしで時間だけかかった」ケースを判断できるようにする。

## 今回入れた対策

- 更新ログから `fresh_only`、画像 target、画像 ok/skipped/failed を拾い、更新画面に内訳表示できるようにした。
- 起動時更新確認は、更新する/あとでのどちらかを選んだら約1週間は起動時に出さないようにした。

