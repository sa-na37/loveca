# Loveca DB更新プロセスメモ（2026-05-27）

## 目的

新カード追加後に、ラブカ simulator 用 DB を安全に更新する。対象は次の4系統。

- `cards_min_tokv1.csv`
- `cards_min_tokv1.json`
- `cards_compiled_v7h.json`
- `official_image_manifest.json / .tsv`
- 画像本体 `./llocg_db_out_full/card_images/` は別工程で更新する。

## 重要な結論

`llocg_db_tool_v7.py` に統合されているのは、wiki 取得、normalize、mine、audit、公式画像 manifest 作成まで。PNG 画像本体の取得は `llocg_fetch_all_card_images.py` の担当。

そのため標準手順は次の3段階に分ける。

1. DB作業フォルダで全件取得・normalize・manifest作成
2. `llocg_sim_tool_v7.py compile` で compiled DB を生成
3. 正本 `./llocg_db_out_full/` に反映後、画像 fetch を実行

## 今回確認できた更新状況

- 更新前の正本確認ログでは、`cards_min_tokv1.json` と `cards_compiled_v7h.json` はどちらも 823 枚だった。
- 今回生成された `official_image_manifest.json` は `cards_total_in_db = 993`、`cards_with_manifest = 751`、`cards_missing_manifest = 242`。
- manifest には `BP06` が含まれ、`BP06.cards_wanted = 81`。
- manifest には `LL-bp6-001` など BP06 の exact URL が含まれる。

`cards_missing_manifest = 242` は「公式画像 manifest に exact URL が載らなかったカード数」であり、DB欠損そのものではない。画像 fetch 側は manifest exact URL を優先し、残りは heuristic fallback で探索する。

## 安全な更新手順

### 0. 作業前確認

```bash
cd /Users/tekitou/Desktop/gsim/loveca

git status
python3 ./llocg_db_tool_v7.py --help 2>&1 | sed -n '1,220p'
python3 ./llocg_sim_tool_v7.py --help 2>&1 | sed -n '1,220p'
```

### 1. 作業用フォルダに全件取得

既存 `llocg_db_out_full` に直接 `all` をかけない。resume/途中出力の混入を避けるため、毎回新しい作業用 outdir を使う。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

WORK=./llocg_db_update_work_YYYYMMDD
CACHE=./.cache_llocg_update_YYYYMMDD

rm -rf "$WORK" "$CACHE"
mkdir -p "$WORK" "$CACHE"

python3 ./llocg_db_tool_v7.py all \
  --outdir "$WORK" \
  --cache "$CACHE" \
  --delay 1.0 \
  --mine-top 200 \
  --top-unknown 50
```

想定出力:

```text
$WORK/cards_min.csv
$WORK/cards_min.json
$WORK/cards_min_tokv1.csv
$WORK/cards_min_tokv1.json
$WORK/official_image_manifest.json
$WORK/official_image_manifest.tsv
```

### 2. compiled DB 生成

```bash
cd /Users/tekitou/Desktop/gsim/loveca

WORK=./llocg_db_update_work_YYYYMMDD

PATTERN_DIR=./llocg_db_out_full/patterns
if [ ! -d "$PATTERN_DIR" ]; then
  PATTERN_DIR=./llocg_db_out_full
fi

find "$PATTERN_DIR" -maxdepth 3 \( -name "cost_patterns*.yaml" -o -name "effect_patterns*.yaml" \) -print

python3 ./llocg_sim_tool_v7.py compile \
  --csv "$WORK/cards_min_tokv1.csv" \
  --out "$WORK/cards_compiled_v7h.json" \
  --patterns-dir "$PATTERN_DIR"
```

### 3. 正本反映前の整合性チェック

```bash
cd /Users/tekitou/Desktop/gsim/loveca

WORK=./llocg_db_update_work_YYYYMMDD
python3 ./check_loveca_db_integrity_20260527.py \
  --dbdir "$WORK" \
  --expect-min 990
```

作業用フォルダに checker を置かない場合は、下記のように保存先に合わせて実行する。

```bash
python3 ~/Downloads/check_loveca_db_integrity_20260527.py \
  --dbdir "$WORK" \
  --expect-min 990
```

確認観点:

- `cards_min_tokv1.csv` / `cards_min_tokv1.json` / `cards_compiled_v7h.json` の件数が一致する。
- cardnumber の重複がない。
- cardnumber の形式不正がない。
- min DB と compiled DB の cardnumber set が一致する。
- cardname / card_type が min DB と compiled DB で一致する。
- BP06 が含まれる。
- manifest が存在し、`BP06` の entry がある。

### 4. 正本へ反映

```bash
cd /Users/tekitou/Desktop/gsim/loveca

WORK=./llocg_db_update_work_YYYYMMDD

cp "$WORK/cards_min_tokv1.csv" ./llocg_db_out_full/cards_min_tokv1.csv
cp "$WORK/cards_min_tokv1.json" ./llocg_db_out_full/cards_min_tokv1.json
cp "$WORK/cards_compiled_v7h.json" ./llocg_db_out_full/cards_compiled_v7h.json
cp "$WORK/official_image_manifest.json" ./llocg_db_out_full/official_image_manifest.json
cp "$WORK/official_image_manifest.tsv" ./llocg_db_out_full/official_image_manifest.tsv
```

### 5. 正本反映後の整合性チェック

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./check_loveca_db_integrity_20260527.py \
  --dbdir ./llocg_db_out_full \
  --images-dir ./llocg_db_out_full/card_images \
  --expect-min 990
```

## 2026-08-03 追記: 公式Xプレリリース画像とE番号カードの扱い

- Codex作業時の429再発防止ルールは `docs/codex_knowledge/wiki_rate_limit_prevention_20260827.md` を先に確認する。

- 公式ポスト一覧に出る `PL!N-bp7-E01` など、通し番号部分が `E` で始まるカードはエネルギーカードとして扱い、シミュレータ用DB・検索・preview manifest・画像取得対象から除外する。
- `official_preview_image_manifest.json` は、DB未収録でも公式ポスト一覧でカード番号と画像URLが直接対応している非E番号カードを `MATCHED_WIKI_OFFICIAL_POST_INDEX_PREVIEW_ONLY` として登録する。
- カード検索エンジンは、DB本体に未収録の非E番号preview-onlyカードもmanifest由来の仮カードとして検索候補に入れる。画像ファイルが既にあればプレリリース画像として表示される。
- 過去に取得済みのE番号画像ファイルは削除しなくてよい。今後のmanifest生成・欠落判定・検索索引では無視する。

## 2026-08-03 追記: プレリリース商品ページのキャッシュ再取得

- `llocg_db_tool_v7.py` の差分更新では、発売前商品を `prerelease_product` として再確認対象にしていたが、実際の `fetch()` 呼び出しで長期商品ページキャッシュを返していた。
- このため、wikiの商品ページに新しいカードページリンクが追加されても、ローカルDB更新では古い商品ページHTMLを読み続け、DB本体へ取り込めないことがあった。
- 2026-08-26再調整: 発売前商品ページをすべて `force_refresh=True` にはしない。前回の商品ページ監査で「カード個別ページから公式X投稿へのリンク」が検知された商品だけを `prerelease_active_product` として毎回HTTP再取得する。
- 未発売商品の中で最も発売日が近い商品は `prerelease_nearest_probe` として短TTLで商品ページを再確認し、商品自身のカード番号に絞って個別ページ上の公式Xリンクを確認する。その他の未発売商品は `prerelease_dormant_reused` として前回registryを再利用する。安定済み発売済み商品の長期キャッシュ再利用は維持する。
- WIKIWIKI個別カードページが429で落ちる場合でも、公式ポスト集約ページ経由のpreview manifest更新は継続する。2026-08-26確認ではPBLL02の公式ツイート対応13件、preview-only 11件、preview画像13件を取得済み。
- 2026-08-03時点のBP07 preview-only 27件の内訳:
  - 22件: 商品ページ上で既存カードページリンクあり。WIKIWIKI 429が落ち着いた状態で通常遅延のDB更新を実行すればDB本体へ取り込み対象になる。
  - 5件: 商品ページ上でも `?` の新規作成リンク。wikiカードページ未作成のため、引き続きpreview-only扱い。

## 2026-08-03 追記: プレリリース公式X公開カードの preview-only 取得

原因:

- BP07 / NSD02 のプレリリース期間中、WIKIWIKI `公式ポスト` 集約ページには公式X投稿とカード番号が出ているが、商品ページ側にはまだ全カードがリンクされていない。
- 旧処理では `公式ポスト` 集約ページ上のカード番号がローカルDBに存在しない場合、`INDEX_CARD_NOT_IN_DB` として preview manifest 登録対象から外していた。
- さらに画像fetch側も、preview manifest にカードがあっても `cards_min_tokv1` / compiled DB に存在するカードだけを処理対象にしていた。
- そのため、2026-08-03時点ではプレリリース対象86件中、DB既存31件だけが取得対象になり、DB未掲載55件は公式Xに出ていても取得できなかった。

修正後の方針:

- `llocg_build_preview_manifest_from_x.py` は、公式ポスト集約ページでカード番号とX投稿URLが直接対応している場合、DB未掲載カードも `MATCHED_WIKI_OFFICIAL_POST_INDEX_PREVIEW_ONLY` として `official_preview_image_manifest.json` に登録する。
- `llocg_update_database.py` は、preview manifest 上のカードをDB本体の存在有無で除外せず、preview画像fetch対象に含める。
- `llocg_fetch_all_card_images.py` は、`--cardnumber-file` に指定されたカードがDB本体に無くても、preview manifest に存在すれば `preview_manifest_only` の一時ターゲットとして処理する。
- この経路は preview image 用であり、カード本文・効果テキストの正本DB行を捏造しない。商品ページまたはカードページから本文が取れるようになった時点で通常DB行へ入る。

この段階で 823 枚のままなら、正本へのコピー漏れ。`llocg_db_update_work_YYYYMMDD` から `llocg_db_out_full` へ再コピーする。

### 6. 画像 fetch

DB更新とは別工程。manifest exact URL を優先し、足りない分を heuristic で探す。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./llocg_fetch_all_card_images.py \
  --root ./llocg_db_out_full \
  --compiled ./llocg_db_out_full/cards_compiled_v7h.json \
  --timeout 20 \
  --sleep 0.05 \
  --jitter 0.05
```

完了後確認:

```bash
find ./llocg_db_out_full/card_images -type f -name "*.png" 2>/dev/null | wc -l

python3 ./check_loveca_db_integrity_20260527.py \
  --dbdir ./llocg_db_out_full \
  --images-dir ./llocg_db_out_full/card_images \
  --expect-min 990
```

### 7. git 反映

```bash
cd /Users/tekitou/Desktop/gsim/loveca

git status

git add ./llocg_db_out_full/cards_min_tokv1.csv \
        ./llocg_db_out_full/cards_min_tokv1.json \
        ./llocg_db_out_full/cards_compiled_v7h.json \
        ./llocg_db_out_full/official_image_manifest.json \
        ./llocg_db_out_full/official_image_manifest.tsv

git commit -m "data: update Loveca card database"
git push origin main
```

画像も git 管理する場合のみ:

```bash
git status --short ./card_images
git add ./card_images
git commit -m "data: update Loveca card images"
git push origin main
```

## 事故防止メモ

- `llocg_db_out_full` に直接 `all` をかけない。
- `cards_min_tokv1.csv` だけ更新され、`cards_min_tokv1.json` / `cards_compiled_v7h.json` が旧 823 枚のまま、という状態に注意。
- manifest の `cards_total_in_db` と DB JSON の件数が違う場合は、どちらかのコピー漏れまたは別世代混在を疑う。
- `official_image_manifest` は画像 URL リストであり、画像本体ではない。
- 画像更新は `llocg_fetch_all_card_images.py` を別途実行する。
- 画像 fetch は時間がかかるので、DB正本の整合性確認と git commit は画像とは分けてよい。


## 2026-06-03 追記: CLHS01 / CL レアリティ画像URLへの対応

`PL!HS-cl1-xxx` 系の公式画像URLは、以下の形であることを確認した。

```text
https://llofficial-cardgame.com/wordpress/wp-content/images/cardlist/CLHS01/PL!HS-cl1-001-CL.png
```

したがって、`cl1` はカード番号上の商品・セットコード、`CL` は画像ファイル末尾のレアリティトークンとして扱う。

更新した処理方針:

- `llocg_db_tool_v7.py`
  - `PL!HS-clN-xxx` を公式 expansion / folder `CLHSNN` に分類する。
  - 公式検索で拾えない場合も、既知URLパターン `CLHSNN/<cardnumber>-CL.png` を manifest fallback として生成する。
- `llocg_fetch_all_card_images.py`
  - fallback folder 候補に `CLHSNN` を追加する。
  - fallback rarity 候補に `CL` を追加する。

この修正後は、DB を取り直さなくても、既存の `cards_min_tokv1.json / csv` から image-manifest だけ再生成すれば `PL!HS-cl1-001` などの exact URL が入る。


## 2026-06-03 追記: 画像URL探索の追加対応

- `PL!HS-cl1-xxx` は `CLHS01/<cardnumber>-CL.png` として取得する。
- `PL!HS-pbN-xxx` は `PBHS` 商品フォルダを優先する。従来の `PB_PREFIX` に `PL!HS` が無かったため、PBHS を使わず `PBLS` / `PBSP` などの総当たりに落ちていた。
- 画像の正本出力先は root 直下 `./card_images/` ではなく、DB正本配下の `./llocg_db_out_full/card_images/` に統一する。
- 画像 fetch は次の形を標準にする。`--root ./llocg_db_out_full` を指定し、`--outdir` は省略する。これによりデフォルトで `./llocg_db_out_full/card_images/` へ出る。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./llocg_fetch_all_card_images.py \
  --root ./llocg_db_out_full \
  --compiled ./llocg_db_out_full/cards_compiled_v7h.json \
  --timeout 20 \
  --sleep 0.05 \
  --jitter 0.05
```

確認は次を使う。

```bash
cd /Users/tekitou/Desktop/gsim/loveca

python3 ./check_loveca_db_integrity_20260527.py \
  --dbdir ./llocg_db_out_full \
  --images-dir ./llocg_db_out_full/card_images \
  --expect-min 990
```
