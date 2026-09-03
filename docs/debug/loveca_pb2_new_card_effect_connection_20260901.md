# PL!-pb2 新規カード取得・効果接続確認メモ 2026-09-01

## 実施内容

- `python3 ./llocg_update_database.py --preview-index-cache-minutes 15 --image-sleep 0.25 --keep-work` でDB更新。
- 取得後DBとバックアップを比較し、新規13件を確認。
- 新規カードの全 `effect_template` を matcher に通し、未接続0件を確認。
- 未接続だったPB2系文型をカード番号専用分岐ではなく、汎用 route / resolver として追加。

## 新規取得カードと接続状況

- 絢瀬絵里: 正面エリアに登場する相手メンバーの元々ハート数条件を接続。1デッキでは手動確認ログ、2デッキでは正面ペアが新しく成立したときだけ実カードをウェイト化。
- 南ことり: 相手メンバーの<ライブ成功時>無効化後、確認UI経由で<黄>獲得へ接続。
- 園田海未: 成功ライブカード置き場の<スコア+1>を持つμ'sカード枚数ぶんブレードを得るBODY常時を接続。
- 園田海未: エール公開カード内の<スコア+1>を持つμ'sカード枚数ぶん追加エールする自動効果を接続。
- 星空凛: 成功ライブカード置き場に<スコア+1>を持つμ'sカードがある場合、ステージのμ'sメンバーへブレードを付与する効果を接続。
- 西木野真姫: 相手ステージの元々ハート数1以下をウェイトにする効果を接続。
- 東條希: 控え室からμ'sライブ回収後、成功ライブカード置き場のμ'sカード枚数ぶんエネルギーをアクティブにする効果を接続。
- 小泉花陽: 既存の「山札上4枚から必要ハート合計8以上のμ'sライブを任意回収」経路に接続済み。
- 矢澤にこ: バトンタッチ退場時、新登場メンバーがコスト15以上のμ'sならエネルギー2枚をアクティブにする効果を接続。
- 高坂穂乃果: 自分センターエリアのμ'sメンバーへブレード2つを得る表記ゆれを既存エリア対象 route に接続。
- 園田海未: 既存の控え室メンバー回収経路に接続済み。
- 南ことり: 成功ライブカード置き場のスコア合計5ごとにブレードを得るBODY常時を接続。
- 西木野真姫: 相手ステージの元々ハート数3以下をウェイトにする効果を接続。
- Shangri-La Shower: エール公開メンバーカードがすべてPrintemps / lily white / BiBiのいずれかで統一されている場合、公開メンバーを手札に加える効果を接続。

## 直接確認

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 -m py_compile llocg_ui/engine.py llocg_dual_v2/server.py
```

結果: 成功。

```bash
cd /Users/tekitou/Desktop/gsim/loveca
python3 - <<'PY'
import json
from pathlib import Path
from llocg_ui.engine import _match_effect_template

def by_no(path):
    data=json.loads(Path(path).read_text())
    cards=data.get('cards', data)
    if isinstance(cards, dict):
        return cards
    return {str(c.get('cardnumber') or c.get('card_no') or c.get('number') or ''): c for c in cards if isinstance(c, dict)}

cur=by_no('llocg_db_out_full/cards_compiled_v7h.json')
old=by_no('llocg_db_out_full/_update_backups/backup_20260901_102429/cards_compiled_v7h.json')
new=[cn for cn in cur if cn and cn not in old]
ng=[]
for cn in new:
    ci=cur[cn]
    for ab in ci.get('abilities') or []:
        for cl in ab.get('clauses') or []:
            eff=(cl.get('effect_template') or cl.get('raw') or '').strip()
            if eff and not _match_effect_template(eff):
                ng.append((ci.get('name') or ci.get('cardname') or '', cn, eff))
print('new_cards', len(new), 'unmatched_effects', len(ng))
if ng:
    raise SystemExit(1)
PY
```

結果: `new_cards 13 unmatched_effects 0`。

直接state確認:

- 園田海未: 成功置き場に<スコア+1>μ'sカードがある状態でBODY常時ブレード加算を確認。
- 南ことり: 相手<ライブ成功時>無効化の確認pendingが出て、Apply後に<黄>が付与されることを確認。
- 西木野真姫: 元々ハート数条件の相手ウェイト人数入力pendingが出ることを確認。
- 園田海未: エール公開の<スコア+1>μ'sカードから追加エールが行われ、追加公開カードが解決領域に入ることを確認。
- Shangri-La Shower: 公開メンバーが対象ユニットで統一されている場合、`pick_from_yell` pending が出ることを確認。

## 要観察

- DB更新中、南ことりの個別wikiページ取得でHTTP 429が1件発生した。ただしDB更新自体は完了し、最終DBは13件増加した。
- 絢瀬絵里の「正面エリアには条件該当メンバーがウェイト状態で登場する」は2デッキ側にも接続済み。実ブラウザで相手が正面へ登場した瞬間のログと表示は追加目視対象。
- 南ことりの相手<ライブ成功時>無効化は、1デッキでは確認UIと自分側アイコン付与まで実装。2デッキで相手の該当<ライブ成功時>能力をライブ終了まで抑止する実カード単位の状態管理は追加確認が必要。
