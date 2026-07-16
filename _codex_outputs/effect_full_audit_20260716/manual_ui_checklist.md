# Manual UI checklist

These cases have static implementation mapping but require browser/UI and state verification before PASS.

## LL-PR-004
- `LL-PR-004#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/LL-PR-004_A01_T01_LL-PR-004.command`
- `LL-PR-004#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/LL-PR-004_A01_T02_LL-PR-004.command`
- `LL-PR-004#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/LL-PR-004_A01_T03_LL-PR-004.command`
- `LL-PR-004#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/LL-PR-004_A01_T04_LL-PR-004.command`
- `LL-PR-004#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/LL-PR-004_A01_T05_LL-PR-004.command`
- `LL-PR-004#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-PR-004_A01_T06_LL-PR-004.command`

## LL-bp1-001
- `LL-bp1-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/LL-bp1-001_A01_T01_LL-bp1-001.command`
- `LL-bp1-001#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/LL-bp1-001_A02_T01_LL-bp1-001.command`
- `LL-bp1-001#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/LL-bp1-001_A02_T02_LL-bp1-001.command`
- `LL-bp1-001#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/LL-bp1-001_A02_T03_LL-bp1-001.command`
- `LL-bp1-001#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/LL-bp1-001_A02_T04_LL-bp1-001.command`
- `LL-bp1-001#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/LL-bp1-001_A02_T05_LL-bp1-001.command`
- `LL-bp1-001#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-bp1-001_A02_T06_LL-bp1-001.command`

## LL-bp2-001
- `LL-bp2-001#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/LL-bp2-001_A01_T01_LL-bp2-001.command`
- `LL-bp2-001#A01#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/LL-bp2-001_A01_T02_LL-bp2-001.command`
- `LL-bp2-001#A01#T03` 常時 / 条件消失で解除 / command: `debug_commands/LL-bp2-001_A01_T03_LL-bp2-001.command`
- `LL-bp2-001#A03#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/LL-bp2-001_A03_T01_LL-bp2-001.command`
- `LL-bp2-001#A03#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/LL-bp2-001_A03_T02_LL-bp2-001.command`
- `LL-bp2-001#A03#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/LL-bp2-001_A03_T03_LL-bp2-001.command`
- `LL-bp2-001#A03#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/LL-bp2-001_A03_T04_LL-bp2-001.command`
- `LL-bp2-001#A03#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/LL-bp2-001_A03_T05_LL-bp2-001.command`
- `LL-bp2-001#A03#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-bp2-001_A03_T06_LL-bp2-001.command`

## LL-bp3-001
- `LL-bp3-001#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/LL-bp3-001_A01_T01_LL-bp3-001.command`
- `LL-bp3-001#A01#T02` 起動 / 任意処理を実行 / command: `debug_commands/LL-bp3-001_A01_T02_LL-bp3-001.command`
- `LL-bp3-001#A01#T03` 起動 / 任意処理を実行しない / command: `debug_commands/LL-bp3-001_A01_T03_LL-bp3-001.command`
- `LL-bp3-001#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/LL-bp3-001_A01_T04_LL-bp3-001.command`
- `LL-bp3-001#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/LL-bp3-001_A01_T05_LL-bp3-001.command`
- `LL-bp3-001#A01#T06` 起動 / 回数制限超過 / command: `debug_commands/LL-bp3-001_A01_T06_LL-bp3-001.command`
- `LL-bp3-001#A01#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/LL-bp3-001_A01_T07_LL-bp3-001.command`
- `LL-bp3-001#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/LL-bp3-001_A02_T01_LL-bp3-001.command`
- `LL-bp3-001#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/LL-bp3-001_A02_T02_LL-bp3-001.command`
- `LL-bp3-001#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/LL-bp3-001_A02_T03_LL-bp3-001.command`
- `LL-bp3-001#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/LL-bp3-001_A02_T04_LL-bp3-001.command`
- `LL-bp3-001#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/LL-bp3-001_A02_T05_LL-bp3-001.command`
- `LL-bp3-001#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-bp3-001_A02_T06_LL-bp3-001.command`

## LL-bp4-001
- `LL-bp4-001#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/LL-bp4-001_A01_T01_LL-bp4-001.command`

## LL-bp5-001
- `LL-bp5-001#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/LL-bp5-001_A01_T01_LL-bp5-001.command`
- `LL-bp5-001#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/LL-bp5-001_A01_T02_LL-bp5-001.command`
- `LL-bp5-001#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/LL-bp5-001_A01_T03_LL-bp5-001.command`
- `LL-bp5-001#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-bp5-001_A01_T04_LL-bp5-001.command`

## LL-bp5-002
- `LL-bp5-002#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/LL-bp5-002_A01_T01_LL-bp5-002.command`
- `LL-bp5-002#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/LL-bp5-002_A01_T02_LL-bp5-002.command`
- `LL-bp5-002#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/LL-bp5-002_A01_T03_LL-bp5-002.command`
- `LL-bp5-002#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/LL-bp5-002_A01_T04_LL-bp5-002.command`
- `LL-bp5-002#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/LL-bp5-002_A01_T05_LL-bp5-002.command`
- `LL-bp5-002#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-bp5-002_A01_T06_LL-bp5-002.command`
- `LL-bp5-002#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/LL-bp5-002_A02_T01_LL-bp5-002.command`
- `LL-bp5-002#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-bp5-002_A02_T02_LL-bp5-002.command`

## LL-bp6-001
- `LL-bp6-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/LL-bp6-001_A01_T01_LL-bp6-001.command`
- `LL-bp6-001#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/LL-bp6-001_A02_T01_LL-bp6-001.command`
- `LL-bp6-001#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/LL-bp6-001_A02_T02_LL-bp6-001.command`
- `LL-bp6-001#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/LL-bp6-001_A02_T03_LL-bp6-001.command`
- `LL-bp6-001#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/LL-bp6-001_A02_T04_LL-bp6-001.command`
- `LL-bp6-001#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/LL-bp6-001_A02_T05_LL-bp6-001.command`
- `LL-bp6-001#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-bp6-001_A02_T06_LL-bp6-001.command`

## LL-bp7-001
- `LL-bp7-001#A02#T01` 登場 / 成立・通常解決 / command: `debug_commands/LL-bp7-001_A02_T01_LL-bp7-001.command`
- `LL-bp7-001#A03#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/LL-bp7-001_A03_T01_LL-bp7-001.command`
- `LL-bp7-001#A03#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/LL-bp7-001_A03_T02_LL-bp7-001.command`

## PL!-PR-001
- `PL!-PR-001#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_-PR-001_A01_T01_PL_-PR-001.command`
- `PL!-PR-001#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_-PR-001_A01_T02_PL_-PR-001.command`
- `PL!-PR-001#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_-PR-001_A01_T03_PL_-PR-001.command`
- `PL!-PR-001#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_-PR-001_A01_T04_PL_-PR-001.command`
- `PL!-PR-001#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_-PR-001_A01_T05_PL_-PR-001.command`

## PL!-PR-002
- `PL!-PR-002#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_-PR-002_A01_T01_PL_-PR-002.command`
- `PL!-PR-002#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_-PR-002_A01_T02_PL_-PR-002.command`
- `PL!-PR-002#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_-PR-002_A01_T03_PL_-PR-002.command`
- `PL!-PR-002#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_-PR-002_A01_T04_PL_-PR-002.command`
- `PL!-PR-002#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_-PR-002_A01_T05_PL_-PR-002.command`

## PL!-PR-003
- `PL!-PR-003#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-PR-003_A01_T01_PL_-PR-003.command`
- `PL!-PR-003#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-PR-003_A01_T02_PL_-PR-003.command`
- `PL!-PR-003#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-PR-003_A01_T03_PL_-PR-003.command`
- `PL!-PR-003#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_-PR-003_A01_T04_PL_-PR-003.command`
- `PL!-PR-003#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-PR-003_A01_T05_PL_-PR-003.command`

## PL!-PR-004
- `PL!-PR-004#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-PR-004_A01_T01_PL_-PR-004.command`
- `PL!-PR-004#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-PR-004_A01_T02_PL_-PR-004.command`
- `PL!-PR-004#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-PR-004_A01_T03_PL_-PR-004.command`
- `PL!-PR-004#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_-PR-004_A01_T04_PL_-PR-004.command`
- `PL!-PR-004#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-PR-004_A01_T05_PL_-PR-004.command`

## PL!-PR-007
- `PL!-PR-007#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-PR-007_A01_T01_PL_-PR-007.command`
- `PL!-PR-007#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-PR-007_A01_T02_PL_-PR-007.command`
- `PL!-PR-007#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-PR-007_A01_T03_PL_-PR-007.command`
- `PL!-PR-007#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-PR-007_A01_T04_PL_-PR-007.command`
- `PL!-PR-007#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-PR-007_A01_T05_PL_-PR-007.command`

## PL!-PR-009
- `PL!-PR-009#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-PR-009_A01_T01_PL_-PR-009.command`
- `PL!-PR-009#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-PR-009_A01_T02_PL_-PR-009.command`
- `PL!-PR-009#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-PR-009_A01_T03_PL_-PR-009.command`
- `PL!-PR-009#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-PR-009_A01_T04_PL_-PR-009.command`
- `PL!-PR-009#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-PR-009_A01_T05_PL_-PR-009.command`

## PL!-PR-012
- `PL!-PR-012#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-PR-012_A01_T01_PL_-PR-012.command`
- `PL!-PR-012#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-PR-012_A01_T02_PL_-PR-012.command`
- `PL!-PR-012#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-PR-012_A01_T03_PL_-PR-012.command`
- `PL!-PR-012#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_-PR-012_A01_T04_PL_-PR-012.command`
- `PL!-PR-012#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-PR-012_A01_T05_PL_-PR-012.command`

## PL!-PR-014
- `PL!-PR-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-PR-014_A01_T01_PL_-PR-014.command`
- `PL!-PR-014#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-PR-014_A01_T02_PL_-PR-014.command`
- `PL!-PR-014#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-PR-014_A01_T03_PL_-PR-014.command`

## PL!-PR-015
- `PL!-PR-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-PR-015_A01_T01_PL_-PR-015.command`
- `PL!-PR-015#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-PR-015_A01_T02_PL_-PR-015.command`
- `PL!-PR-015#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-PR-015_A01_T03_PL_-PR-015.command`

## PL!-PR-017
- `PL!-PR-017#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-PR-017_A01_T01_PL_-PR-017.command`
- `PL!-PR-017#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_-PR-017_A01_T02_PL_-PR-017.command`
- `PL!-PR-017#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_-PR-017_A01_T03_PL_-PR-017.command`
- `PL!-PR-017#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_-PR-017_A01_T04_PL_-PR-017.command`
- `PL!-PR-017#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_-PR-017_A01_T05_PL_-PR-017.command`

## PL!-PR-018
- `PL!-PR-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-PR-018_A01_T01_PL_-PR-018.command`

## PL!-PR-021
- `PL!-PR-021#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-PR-021_A01_T01_PL_-PR-021.command`
- `PL!-PR-021#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-PR-021_A01_T02_PL_-PR-021.command`
- `PL!-PR-021#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-PR-021_A01_T03_PL_-PR-021.command`
- `PL!-PR-021#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-PR-021_A01_T04_PL_-PR-021.command`
- `PL!-PR-021#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-PR-021_A01_T05_PL_-PR-021.command`

## PL!-bp3-001
- `PL!-bp3-001#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp3-001_A01_T01_PL_-bp3-001.command`
- `PL!-bp3-001#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp3-001_A01_T02_PL_-bp3-001.command`
- `PL!-bp3-001#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp3-001_A01_T03_PL_-bp3-001.command`
- `PL!-bp3-001#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_-bp3-001_A01_T04_PL_-bp3-001.command`
- `PL!-bp3-001#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-bp3-001_A01_T05_PL_-bp3-001.command`
- `PL!-bp3-001#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-001_A02_T01_PL_-bp3-001.command`
- `PL!-bp3-001#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp3-001_A02_T02_PL_-bp3-001.command`
- `PL!-bp3-001#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-001_A02_T03_PL_-bp3-001.command`
- `PL!-bp3-001#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-001_A02_T04_PL_-bp3-001.command`

## PL!-bp3-002
- `PL!-bp3-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-002_A01_T01_PL_-bp3-002.command`
- `PL!-bp3-002#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp3-002_A01_T02_PL_-bp3-002.command`
- `PL!-bp3-002#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-002_A01_T03_PL_-bp3-002.command`
- `PL!-bp3-002#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp3-002_A01_T04_PL_-bp3-002.command`
- `PL!-bp3-002#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp3-002_A01_T05_PL_-bp3-002.command`

## PL!-bp3-003
- `PL!-bp3-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-003_A01_T01_PL_-bp3-003.command`
- `PL!-bp3-003#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp3-003_A01_T02_PL_-bp3-003.command`
- `PL!-bp3-003#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-003_A01_T03_PL_-bp3-003.command`
- `PL!-bp3-003#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp3-003_A01_T04_PL_-bp3-003.command`
- `PL!-bp3-003#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp3-003_A01_T05_PL_-bp3-003.command`

## PL!-bp3-004
- `PL!-bp3-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-004_A01_T01_PL_-bp3-004.command`
- `PL!-bp3-004#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-004_A02_T01_PL_-bp3-004.command`
- `PL!-bp3-004#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp3-004_A02_T02_PL_-bp3-004.command`
- `PL!-bp3-004#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp3-004_A02_T03_PL_-bp3-004.command`
- `PL!-bp3-004#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-004_A02_T04_PL_-bp3-004.command`

## PL!-bp3-005
- `PL!-bp3-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-005_A01_T01_PL_-bp3-005.command`

## PL!-bp3-006
- `PL!-bp3-006#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-006_A01_T01_PL_-bp3-006.command`
- `PL!-bp3-006#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp3-006_A01_T02_PL_-bp3-006.command`
- `PL!-bp3-006#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-006_A01_T03_PL_-bp3-006.command`
- `PL!-bp3-006#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp3-006_A01_T04_PL_-bp3-006.command`
- `PL!-bp3-006#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp3-006_A01_T05_PL_-bp3-006.command`
- `PL!-bp3-006#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-006_A01_T06_PL_-bp3-006.command`

## PL!-bp3-007
- `PL!-bp3-007#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-007_A01_T01_PL_-bp3-007.command`
- `PL!-bp3-007#A01#T02` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp3-007_A01_T02_PL_-bp3-007.command`
- `PL!-bp3-007#A01#T03` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp3-007_A01_T03_PL_-bp3-007.command`
- `PL!-bp3-007#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-007_A01_T04_PL_-bp3-007.command`

## PL!-bp3-008
- `PL!-bp3-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp3-008_A01_T01_PL_-bp3-008.command`
- `PL!-bp3-008#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp3-008_A01_T02_PL_-bp3-008.command`
- `PL!-bp3-008#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp3-008_A01_T03_PL_-bp3-008.command`
- `PL!-bp3-008#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_-bp3-008_A01_T04_PL_-bp3-008.command`
- `PL!-bp3-008#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-bp3-008_A01_T05_PL_-bp3-008.command`
- `PL!-bp3-008#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-008_A02_T01_PL_-bp3-008.command`
- `PL!-bp3-008#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp3-008_A02_T02_PL_-bp3-008.command`
- `PL!-bp3-008#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-008_A02_T03_PL_-bp3-008.command`
- `PL!-bp3-008#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp3-008_A02_T04_PL_-bp3-008.command`
- `PL!-bp3-008#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp3-008_A02_T05_PL_-bp3-008.command`
- `PL!-bp3-008#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-008_A02_T06_PL_-bp3-008.command`

## PL!-bp3-009
- `PL!-bp3-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-009_A01_T01_PL_-bp3-009.command`
- `PL!-bp3-009#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp3-009_A01_T02_PL_-bp3-009.command`
- `PL!-bp3-009#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp3-009_A01_T03_PL_-bp3-009.command`
- `PL!-bp3-009#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp3-009_A02_T01_PL_-bp3-009.command`
- `PL!-bp3-009#A02#T02` 起動 / 任意処理を実行 / command: `debug_commands/PL_-bp3-009_A02_T02_PL_-bp3-009.command`
- `PL!-bp3-009#A02#T03` 起動 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-009_A02_T03_PL_-bp3-009.command`
- `PL!-bp3-009#A02#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp3-009_A02_T04_PL_-bp3-009.command`
- `PL!-bp3-009#A02#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp3-009_A02_T05_PL_-bp3-009.command`
- `PL!-bp3-009#A02#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_-bp3-009_A02_T06_PL_-bp3-009.command`
- `PL!-bp3-009#A02#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-bp3-009_A02_T07_PL_-bp3-009.command`

## PL!-bp3-010
- `PL!-bp3-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-010_A01_T01_PL_-bp3-010.command`
- `PL!-bp3-010#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp3-010_A01_T02_PL_-bp3-010.command`
- `PL!-bp3-010#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp3-010_A01_T03_PL_-bp3-010.command`

## PL!-bp3-011
- `PL!-bp3-011#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-011_A01_T01_PL_-bp3-011.command`
- `PL!-bp3-011#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp3-011_A01_T02_PL_-bp3-011.command`
- `PL!-bp3-011#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-011_A01_T03_PL_-bp3-011.command`
- `PL!-bp3-011#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-011_A01_T04_PL_-bp3-011.command`

## PL!-bp3-012
- `PL!-bp3-012#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-012_A01_T01_PL_-bp3-012.command`
- `PL!-bp3-012#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp3-012_A01_T02_PL_-bp3-012.command`
- `PL!-bp3-012#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-012_A01_T03_PL_-bp3-012.command`
- `PL!-bp3-012#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-012_A01_T04_PL_-bp3-012.command`

## PL!-bp3-013
- `PL!-bp3-013#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-013_A01_T01_PL_-bp3-013.command`
- `PL!-bp3-013#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp3-013_A01_T02_PL_-bp3-013.command`
- `PL!-bp3-013#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-013_A01_T03_PL_-bp3-013.command`
- `PL!-bp3-013#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-013_A01_T04_PL_-bp3-013.command`

## PL!-bp3-014
- `PL!-bp3-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-014_A01_T01_PL_-bp3-014.command`
- `PL!-bp3-014#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp3-014_A01_T02_PL_-bp3-014.command`
- `PL!-bp3-014#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-014_A01_T03_PL_-bp3-014.command`
- `PL!-bp3-014#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp3-014_A01_T04_PL_-bp3-014.command`
- `PL!-bp3-014#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp3-014_A01_T05_PL_-bp3-014.command`

## PL!-bp3-017
- `PL!-bp3-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-017_A01_T01_PL_-bp3-017.command`
- `PL!-bp3-017#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp3-017_A01_T02_PL_-bp3-017.command`
- `PL!-bp3-017#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-017_A01_T03_PL_-bp3-017.command`
- `PL!-bp3-017#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp3-017_A01_T04_PL_-bp3-017.command`
- `PL!-bp3-017#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp3-017_A01_T05_PL_-bp3-017.command`

## PL!-bp3-018
- `PL!-bp3-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp3-018_A01_T01_PL_-bp3-018.command`
- `PL!-bp3-018#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp3-018_A01_T02_PL_-bp3-018.command`
- `PL!-bp3-018#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-018_A01_T03_PL_-bp3-018.command`
- `PL!-bp3-018#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp3-018_A01_T04_PL_-bp3-018.command`
- `PL!-bp3-018#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp3-018_A01_T05_PL_-bp3-018.command`

## PL!-bp3-019
- `PL!-bp3-019#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-019_A01_T01_PL_-bp3-019.command`
- `PL!-bp3-019#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp3-019_A01_T02_PL_-bp3-019.command`
- `PL!-bp3-019#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp3-019_A01_T03_PL_-bp3-019.command`
- `PL!-bp3-019#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-019_A01_T04_PL_-bp3-019.command`

## PL!-bp3-022
- `PL!-bp3-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-022_A01_T01_PL_-bp3-022.command`
- `PL!-bp3-022#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-022_A01_T02_PL_-bp3-022.command`

## PL!-bp3-023
- `PL!-bp3-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-023_A01_T01_PL_-bp3-023.command`
- `PL!-bp3-023#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp3-023_A01_T02_PL_-bp3-023.command`
- `PL!-bp3-023#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp3-023_A01_T03_PL_-bp3-023.command`
- `PL!-bp3-023#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-023_A01_T04_PL_-bp3-023.command`

## PL!-bp3-024
- `PL!-bp3-024#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-024_A01_T01_PL_-bp3-024.command`
- `PL!-bp3-024#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp3-024_A01_T02_PL_-bp3-024.command`
- `PL!-bp3-024#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp3-024_A01_T03_PL_-bp3-024.command`
- `PL!-bp3-024#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp3-024_A01_T04_PL_-bp3-024.command`
- `PL!-bp3-024#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-024_A01_T05_PL_-bp3-024.command`
- `PL!-bp3-024#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-024_A01_T06_PL_-bp3-024.command`
- `PL!-bp3-024#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-024_A02_T01_PL_-bp3-024.command`
- `PL!-bp3-024#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp3-024_A02_T02_PL_-bp3-024.command`
- `PL!-bp3-024#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp3-024_A02_T03_PL_-bp3-024.command`
- `PL!-bp3-024#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-024_A02_T04_PL_-bp3-024.command`

## PL!-bp3-025
- `PL!-bp3-025#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-025_A01_T01_PL_-bp3-025.command`
- `PL!-bp3-025#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_-bp3-025_A01_T02_PL_-bp3-025.command`
- `PL!-bp3-025#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_-bp3-025_A01_T03_PL_-bp3-025.command`
- `PL!-bp3-025#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-025_A01_T04_PL_-bp3-025.command`

## PL!-bp3-026
- `PL!-bp3-026#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-026_A01_T01_PL_-bp3-026.command`
- `PL!-bp3-026#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp3-026_A01_T02_PL_-bp3-026.command`
- `PL!-bp3-026#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp3-026_A01_T03_PL_-bp3-026.command`
- `PL!-bp3-026#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp3-026_A01_T04_PL_-bp3-026.command`
- `PL!-bp3-026#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp3-026_A01_T05_PL_-bp3-026.command`
- `PL!-bp3-026#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-026_A01_T06_PL_-bp3-026.command`
- `PL!-bp3-026#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp3-026_A02_T01_PL_-bp3-026.command`
- `PL!-bp3-026#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_-bp3-026_A02_T02_PL_-bp3-026.command`
- `PL!-bp3-026#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_-bp3-026_A02_T03_PL_-bp3-026.command`
- `PL!-bp3-026#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp3-026_A02_T04_PL_-bp3-026.command`

## PL!-bp4-001
- `PL!-bp4-001#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-001_A01_T01_PL_-bp4-001.command`
- `PL!-bp4-001#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp4-001_A01_T02_PL_-bp4-001.command`
- `PL!-bp4-001#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp4-001_A01_T03_PL_-bp4-001.command`
- `PL!-bp4-001#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-001_A01_T04_PL_-bp4-001.command`

## PL!-bp4-003
- `PL!-bp4-003#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp4-003_A01_T01_PL_-bp4-003.command`
- `PL!-bp4-003#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp4-003_A01_T02_PL_-bp4-003.command`
- `PL!-bp4-003#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp4-003_A01_T03_PL_-bp4-003.command`

## PL!-bp4-004
- `PL!-bp4-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp4-004_A01_T01_PL_-bp4-004.command`
- `PL!-bp4-004#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp4-004_A01_T02_PL_-bp4-004.command`
- `PL!-bp4-004#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp4-004_A01_T03_PL_-bp4-004.command`

## PL!-bp4-005
- `PL!-bp4-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp4-005_A01_T01_PL_-bp4-005.command`
- `PL!-bp4-005#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-005_A02_T01_PL_-bp4-005.command`
- `PL!-bp4-005#A02#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp4-005_A02_T02_PL_-bp4-005.command`
- `PL!-bp4-005#A02#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp4-005_A02_T03_PL_-bp4-005.command`
- `PL!-bp4-005#A03#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-005_A03_T01_PL_-bp4-005.command`
- `PL!-bp4-005#A03#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp4-005_A03_T02_PL_-bp4-005.command`
- `PL!-bp4-005#A03#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp4-005_A03_T03_PL_-bp4-005.command`
- `PL!-bp4-005#A03#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-005_A03_T04_PL_-bp4-005.command`

## PL!-bp4-006
- `PL!-bp4-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp4-006_A01_T01_PL_-bp4-006.command`
- `PL!-bp4-006#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp4-006_A01_T02_PL_-bp4-006.command`
- `PL!-bp4-006#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp4-006_A01_T03_PL_-bp4-006.command`

## PL!-bp4-007
- `PL!-bp4-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp4-007_A01_T01_PL_-bp4-007.command`
- `PL!-bp4-007#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp4-007_A01_T02_PL_-bp4-007.command`
- `PL!-bp4-007#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp4-007_A01_T03_PL_-bp4-007.command`
- `PL!-bp4-007#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp4-007_A01_T04_PL_-bp4-007.command`
- `PL!-bp4-007#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp4-007_A01_T05_PL_-bp4-007.command`

## PL!-bp4-008
- `PL!-bp4-008#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-008_A01_T01_PL_-bp4-008.command`
- `PL!-bp4-008#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp4-008_A01_T02_PL_-bp4-008.command`
- `PL!-bp4-008#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp4-008_A01_T03_PL_-bp4-008.command`
- `PL!-bp4-008#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp4-008_A01_T04_PL_-bp4-008.command`
- `PL!-bp4-008#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp4-008_A01_T05_PL_-bp4-008.command`

## PL!-bp4-009
- `PL!-bp4-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp4-009_A01_T01_PL_-bp4-009.command`

## PL!-bp4-010
- `PL!-bp4-010#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-010_A01_T01_PL_-bp4-010.command`
- `PL!-bp4-010#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp4-010_A01_T02_PL_-bp4-010.command`
- `PL!-bp4-010#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp4-010_A01_T03_PL_-bp4-010.command`
- `PL!-bp4-010#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp4-010_A01_T04_PL_-bp4-010.command`
- `PL!-bp4-010#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp4-010_A01_T05_PL_-bp4-010.command`
- `PL!-bp4-010#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-010_A01_T06_PL_-bp4-010.command`

## PL!-bp4-011
- `PL!-bp4-011#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-011_A01_T01_PL_-bp4-011.command`
- `PL!-bp4-011#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp4-011_A01_T02_PL_-bp4-011.command`
- `PL!-bp4-011#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp4-011_A01_T03_PL_-bp4-011.command`
- `PL!-bp4-011#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp4-011_A01_T04_PL_-bp4-011.command`
- `PL!-bp4-011#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp4-011_A01_T05_PL_-bp4-011.command`
- `PL!-bp4-011#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-011_A01_T06_PL_-bp4-011.command`

## PL!-bp4-013
- `PL!-bp4-013#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-013_A01_T01_PL_-bp4-013.command`
- `PL!-bp4-013#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp4-013_A01_T02_PL_-bp4-013.command`
- `PL!-bp4-013#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp4-013_A01_T03_PL_-bp4-013.command`
- `PL!-bp4-013#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp4-013_A01_T04_PL_-bp4-013.command`
- `PL!-bp4-013#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp4-013_A01_T05_PL_-bp4-013.command`
- `PL!-bp4-013#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-013_A01_T06_PL_-bp4-013.command`

## PL!-bp4-014
- `PL!-bp4-014#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-014_A01_T01_PL_-bp4-014.command`
- `PL!-bp4-014#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-014_A01_T02_PL_-bp4-014.command`

## PL!-bp4-016
- `PL!-bp4-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp4-016_A01_T01_PL_-bp4-016.command`
- `PL!-bp4-016#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp4-016_A01_T02_PL_-bp4-016.command`
- `PL!-bp4-016#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp4-016_A01_T03_PL_-bp4-016.command`

## PL!-bp4-017
- `PL!-bp4-017#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-017_A01_T01_PL_-bp4-017.command`
- `PL!-bp4-017#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp4-017_A01_T02_PL_-bp4-017.command`
- `PL!-bp4-017#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp4-017_A01_T03_PL_-bp4-017.command`
- `PL!-bp4-017#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp4-017_A01_T04_PL_-bp4-017.command`
- `PL!-bp4-017#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp4-017_A01_T05_PL_-bp4-017.command`
- `PL!-bp4-017#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-017_A01_T06_PL_-bp4-017.command`

## PL!-bp4-019
- `PL!-bp4-019#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-019_A01_T01_PL_-bp4-019.command`
- `PL!-bp4-019#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp4-019_A01_T02_PL_-bp4-019.command`
- `PL!-bp4-019#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp4-019_A01_T03_PL_-bp4-019.command`
- `PL!-bp4-019#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp4-019_A01_T04_PL_-bp4-019.command`
- `PL!-bp4-019#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp4-019_A01_T05_PL_-bp4-019.command`

## PL!-bp4-020
- `PL!-bp4-020#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-020_A01_T01_PL_-bp4-020.command`
- `PL!-bp4-020#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp4-020_A01_T02_PL_-bp4-020.command`
- `PL!-bp4-020#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp4-020_A01_T03_PL_-bp4-020.command`
- `PL!-bp4-020#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-020_A01_T04_PL_-bp4-020.command`
- `PL!-bp4-020#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-020_A02_T01_PL_-bp4-020.command`
- `PL!-bp4-020#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp4-020_A02_T02_PL_-bp4-020.command`
- `PL!-bp4-020#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp4-020_A02_T03_PL_-bp4-020.command`
- `PL!-bp4-020#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp4-020_A02_T04_PL_-bp4-020.command`
- `PL!-bp4-020#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp4-020_A02_T05_PL_-bp4-020.command`

## PL!-bp4-021
- `PL!-bp4-021#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-021_A01_T01_PL_-bp4-021.command`
- `PL!-bp4-021#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp4-021_A01_T02_PL_-bp4-021.command`
- `PL!-bp4-021#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp4-021_A01_T03_PL_-bp4-021.command`
- `PL!-bp4-021#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-021_A01_T04_PL_-bp4-021.command`

## PL!-bp4-022
- `PL!-bp4-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-022_A01_T01_PL_-bp4-022.command`
- `PL!-bp4-022#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp4-022_A01_T02_PL_-bp4-022.command`
- `PL!-bp4-022#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp4-022_A01_T03_PL_-bp4-022.command`
- `PL!-bp4-022#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-022_A01_T04_PL_-bp4-022.command`

## PL!-bp4-023
- `PL!-bp4-023#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-023_A01_T01_PL_-bp4-023.command`
- `PL!-bp4-023#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_-bp4-023_A01_T02_PL_-bp4-023.command`
- `PL!-bp4-023#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_-bp4-023_A01_T03_PL_-bp4-023.command`
- `PL!-bp4-023#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-023_A01_T04_PL_-bp4-023.command`

## PL!-bp4-024
- `PL!-bp4-024#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp4-024_A01_T01_PL_-bp4-024.command`
- `PL!-bp4-024#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp4-024_A01_T02_PL_-bp4-024.command`
- `PL!-bp4-024#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp4-024_A01_T03_PL_-bp4-024.command`
- `PL!-bp4-024#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp4-024_A01_T04_PL_-bp4-024.command`

## PL!-bp5-001
- `PL!-bp5-001#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-001_A01_T01_PL_-bp5-001.command`
- `PL!-bp5-001#A01#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_-bp5-001_A01_T02_PL_-bp5-001.command`
- `PL!-bp5-001#A01#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_-bp5-001_A01_T03_PL_-bp5-001.command`
- `PL!-bp5-001#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp5-001_A01_T04_PL_-bp5-001.command`

## PL!-bp5-002
- `PL!-bp5-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp5-002_A01_T01_PL_-bp5-002.command`
- `PL!-bp5-002#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp5-002_A01_T02_PL_-bp5-002.command`
- `PL!-bp5-002#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp5-002_A01_T03_PL_-bp5-002.command`

## PL!-bp5-003
- `PL!-bp5-003#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-003_A01_T01_PL_-bp5-003.command`
- `PL!-bp5-003#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp5-003_A01_T02_PL_-bp5-003.command`
- `PL!-bp5-003#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp5-003_A01_T03_PL_-bp5-003.command`
- `PL!-bp5-003#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp5-003_A01_T04_PL_-bp5-003.command`
- `PL!-bp5-003#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp5-003_A01_T05_PL_-bp5-003.command`
- `PL!-bp5-003#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp5-003_A02_T01_PL_-bp5-003.command`
- `PL!-bp5-003#A02#T02` 起動 / 条件不成立 / command: `debug_commands/PL_-bp5-003_A02_T02_PL_-bp5-003.command`
- `PL!-bp5-003#A02#T03` 起動 / 境界値 / command: `debug_commands/PL_-bp5-003_A02_T03_PL_-bp5-003.command`
- `PL!-bp5-003#A02#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp5-003_A02_T04_PL_-bp5-003.command`
- `PL!-bp5-003#A02#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp5-003_A02_T05_PL_-bp5-003.command`
- `PL!-bp5-003#A02#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_-bp5-003_A02_T06_PL_-bp5-003.command`
- `PL!-bp5-003#A02#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-bp5-003_A02_T07_PL_-bp5-003.command`

## PL!-bp5-004
- `PL!-bp5-004#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp5-004_A01_T01_PL_-bp5-004.command`
- `PL!-bp5-004#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp5-004_A01_T02_PL_-bp5-004.command`
- `PL!-bp5-004#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp5-004_A01_T03_PL_-bp5-004.command`
- `PL!-bp5-004#A02#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_-bp5-004_A02_T01_PL_-bp5-004.command`
- `PL!-bp5-004#A02#T02` 自動 / 条件不成立 / command: `debug_commands/PL_-bp5-004_A02_T02_PL_-bp5-004.command`
- `PL!-bp5-004#A02#T03` 自動 / 境界値 / command: `debug_commands/PL_-bp5-004_A02_T03_PL_-bp5-004.command`
- `PL!-bp5-004#A02#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_-bp5-004_A02_T04_PL_-bp5-004.command`
- `PL!-bp5-004#A02#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_-bp5-004_A02_T05_PL_-bp5-004.command`
- `PL!-bp5-004#A02#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_-bp5-004_A02_T06_PL_-bp5-004.command`
- `PL!-bp5-004#A02#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_-bp5-004_A02_T07_PL_-bp5-004.command`

## PL!-bp5-005
- `PL!-bp5-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp5-005_A01_T01_PL_-bp5-005.command`
- `PL!-bp5-005#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp5-005_A01_T02_PL_-bp5-005.command`
- `PL!-bp5-005#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp5-005_A01_T03_PL_-bp5-005.command`

## PL!-bp5-006
- `PL!-bp5-006#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-006_A01_T01_PL_-bp5-006.command`
- `PL!-bp5-006#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp5-006_A01_T02_PL_-bp5-006.command`
- `PL!-bp5-006#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp5-006_A01_T03_PL_-bp5-006.command`
- `PL!-bp5-006#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp5-006_A01_T04_PL_-bp5-006.command`

## PL!-bp5-007
- `PL!-bp5-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp5-007_A01_T01_PL_-bp5-007.command`
- `PL!-bp5-007#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp5-007_A01_T02_PL_-bp5-007.command`
- `PL!-bp5-007#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp5-007_A01_T03_PL_-bp5-007.command`
- `PL!-bp5-007#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp5-007_A01_T04_PL_-bp5-007.command`
- `PL!-bp5-007#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp5-007_A01_T05_PL_-bp5-007.command`

## PL!-bp5-008
- `PL!-bp5-008#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-008_A01_T01_PL_-bp5-008.command`
- `PL!-bp5-008#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp5-008_A01_T02_PL_-bp5-008.command`
- `PL!-bp5-008#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp5-008_A01_T03_PL_-bp5-008.command`
- `PL!-bp5-008#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp5-008_A01_T04_PL_-bp5-008.command`
- `PL!-bp5-008#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp5-008_A01_T05_PL_-bp5-008.command`

## PL!-bp5-009
- `PL!-bp5-009#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp5-009_A01_T01_PL_-bp5-009.command`
- `PL!-bp5-009#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp5-009_A01_T02_PL_-bp5-009.command`
- `PL!-bp5-009#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp5-009_A01_T03_PL_-bp5-009.command`
- `PL!-bp5-009#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_-bp5-009_A01_T04_PL_-bp5-009.command`
- `PL!-bp5-009#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-bp5-009_A01_T05_PL_-bp5-009.command`

## PL!-bp5-010
- `PL!-bp5-010#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-010_A01_T01_PL_-bp5-010.command`
- `PL!-bp5-010#A01#T02` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-bp5-010_A01_T02_PL_-bp5-010.command`
- `PL!-bp5-010#A01#T03` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-bp5-010_A01_T03_PL_-bp5-010.command`
- `PL!-bp5-010#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp5-010_A01_T04_PL_-bp5-010.command`

## PL!-bp5-011
- `PL!-bp5-011#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-011_A01_T01_PL_-bp5-011.command`
- `PL!-bp5-011#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp5-011_A01_T02_PL_-bp5-011.command`
- `PL!-bp5-011#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp5-011_A01_T03_PL_-bp5-011.command`
- `PL!-bp5-011#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp5-011_A01_T04_PL_-bp5-011.command`

## PL!-bp5-013
- `PL!-bp5-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp5-013_A01_T01_PL_-bp5-013.command`

## PL!-bp5-014
- `PL!-bp5-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp5-014_A01_T01_PL_-bp5-014.command`
- `PL!-bp5-014#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp5-014_A01_T02_PL_-bp5-014.command`
- `PL!-bp5-014#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp5-014_A01_T03_PL_-bp5-014.command`

## PL!-bp5-015
- `PL!-bp5-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp5-015_A01_T01_PL_-bp5-015.command`
- `PL!-bp5-015#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp5-015_A01_T02_PL_-bp5-015.command`
- `PL!-bp5-015#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp5-015_A01_T03_PL_-bp5-015.command`

## PL!-bp5-020
- `PL!-bp5-020#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-020_A01_T01_PL_-bp5-020.command`
- `PL!-bp5-020#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp5-020_A01_T02_PL_-bp5-020.command`
- `PL!-bp5-020#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp5-020_A01_T03_PL_-bp5-020.command`
- `PL!-bp5-020#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp5-020_A01_T04_PL_-bp5-020.command`
- `PL!-bp5-020#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp5-020_A01_T05_PL_-bp5-020.command`
- `PL!-bp5-020#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp5-020_A01_T06_PL_-bp5-020.command`

## PL!-bp5-021
- `PL!-bp5-021#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-021_A01_T01_PL_-bp5-021.command`
- `PL!-bp5-021#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp5-021_A01_T02_PL_-bp5-021.command`
- `PL!-bp5-021#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp5-021_A01_T03_PL_-bp5-021.command`
- `PL!-bp5-021#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp5-021_A01_T04_PL_-bp5-021.command`
- `PL!-bp5-021#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp5-021_A01_T05_PL_-bp5-021.command`
- `PL!-bp5-021#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp5-021_A01_T06_PL_-bp5-021.command`

## PL!-bp5-022
- `PL!-bp5-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-022_A01_T01_PL_-bp5-022.command`
- `PL!-bp5-022#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp5-022_A01_T02_PL_-bp5-022.command`

## PL!-bp5-023
- `PL!-bp5-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-023_A01_T01_PL_-bp5-023.command`
- `PL!-bp5-023#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp5-023_A01_T02_PL_-bp5-023.command`

## PL!-bp5-111
- `PL!-bp5-111#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-111_A01_T01_PL_-bp5-111.command`
- `PL!-bp5-111#A01#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp5-111_A01_T02_PL_-bp5-111.command`
- `PL!-bp5-111#A01#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp5-111_A01_T03_PL_-bp5-111.command`

## PL!-bp5-222
- `PL!-bp5-222#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp5-222_A01_T01_PL_-bp5-222.command`
- `PL!-bp5-222#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp5-222_A01_T02_PL_-bp5-222.command`
- `PL!-bp5-222#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp5-222_A01_T03_PL_-bp5-222.command`

## PL!-bp5-333
- `PL!-bp5-333#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp5-333_A01_T01_PL_-bp5-333.command`
- `PL!-bp5-333#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp5-333_A01_T02_PL_-bp5-333.command`
- `PL!-bp5-333#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp5-333_A01_T03_PL_-bp5-333.command`
- `PL!-bp5-333#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp5-333_A01_T04_PL_-bp5-333.command`
- `PL!-bp5-333#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp5-333_A01_T05_PL_-bp5-333.command`
- `PL!-bp5-333#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp5-333_A02_T01_PL_-bp5-333.command`
- `PL!-bp5-333#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp5-333_A02_T02_PL_-bp5-333.command`
- `PL!-bp5-333#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp5-333_A02_T03_PL_-bp5-333.command`
- `PL!-bp5-333#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp5-333_A02_T04_PL_-bp5-333.command`
- `PL!-bp5-333#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp5-333_A02_T05_PL_-bp5-333.command`

## PL!-bp6-001
- `PL!-bp6-001#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-001_A01_T01_PL_-bp6-001.command`
- `PL!-bp6-001#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp6-001_A01_T02_PL_-bp6-001.command`
- `PL!-bp6-001#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp6-001_A01_T03_PL_-bp6-001.command`
- `PL!-bp6-001#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp6-001_A01_T04_PL_-bp6-001.command`
- `PL!-bp6-001#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp6-001_A01_T05_PL_-bp6-001.command`
- `PL!-bp6-001#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-001_A01_T06_PL_-bp6-001.command`
- `PL!-bp6-001#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-001_A02_T01_PL_-bp6-001.command`
- `PL!-bp6-001#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_-bp6-001_A02_T02_PL_-bp6-001.command`
- `PL!-bp6-001#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_-bp6-001_A02_T03_PL_-bp6-001.command`
- `PL!-bp6-001#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-001_A02_T04_PL_-bp6-001.command`

## PL!-bp6-002
- `PL!-bp6-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp6-002_A01_T01_PL_-bp6-002.command`

## PL!-bp6-003
- `PL!-bp6-003#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-003_A01_T01_PL_-bp6-003.command`
- `PL!-bp6-003#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-bp6-003_A01_T02_PL_-bp6-003.command`
- `PL!-bp6-003#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-bp6-003_A01_T03_PL_-bp6-003.command`
- `PL!-bp6-003#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-bp6-003_A01_T04_PL_-bp6-003.command`
- `PL!-bp6-003#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-bp6-003_A01_T05_PL_-bp6-003.command`
- `PL!-bp6-003#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-003_A01_T06_PL_-bp6-003.command`
- `PL!-bp6-003#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-003_A02_T01_PL_-bp6-003.command`
- `PL!-bp6-003#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-003_A02_T02_PL_-bp6-003.command`

## PL!-bp6-004
- `PL!-bp6-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp6-004_A01_T01_PL_-bp6-004.command`
- `PL!-bp6-004#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp6-004_A01_T02_PL_-bp6-004.command`
- `PL!-bp6-004#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp6-004_A01_T03_PL_-bp6-004.command`

## PL!-bp6-005
- `PL!-bp6-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp6-005_A01_T01_PL_-bp6-005.command`
- `PL!-bp6-005#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-bp6-005_A01_T02_PL_-bp6-005.command`
- `PL!-bp6-005#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-bp6-005_A01_T03_PL_-bp6-005.command`
- `PL!-bp6-005#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-bp6-005_A01_T04_PL_-bp6-005.command`
- `PL!-bp6-005#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-bp6-005_A01_T05_PL_-bp6-005.command`

## PL!-bp6-006
- `PL!-bp6-006#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp6-006_A01_T01_PL_-bp6-006.command`
- `PL!-bp6-006#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_-bp6-006_A01_T02_PL_-bp6-006.command`
- `PL!-bp6-006#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_-bp6-006_A01_T03_PL_-bp6-006.command`
- `PL!-bp6-006#A01#T04` 起動 / 任意処理を実行 / command: `debug_commands/PL_-bp6-006_A01_T04_PL_-bp6-006.command`
- `PL!-bp6-006#A01#T05` 起動 / 任意処理を実行しない / command: `debug_commands/PL_-bp6-006_A01_T05_PL_-bp6-006.command`
- `PL!-bp6-006#A01#T06` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp6-006_A01_T06_PL_-bp6-006.command`
- `PL!-bp6-006#A01#T07` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp6-006_A01_T07_PL_-bp6-006.command`
- `PL!-bp6-006#A01#T08` 起動 / 回数制限超過 / command: `debug_commands/PL_-bp6-006_A01_T08_PL_-bp6-006.command`
- `PL!-bp6-006#A01#T09` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-bp6-006_A01_T09_PL_-bp6-006.command`

## PL!-bp6-007
- `PL!-bp6-007#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-007_A01_T01_PL_-bp6-007.command`
- `PL!-bp6-007#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_-bp6-007_A01_T02_PL_-bp6-007.command`
- `PL!-bp6-007#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_-bp6-007_A01_T03_PL_-bp6-007.command`
- `PL!-bp6-007#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-007_A01_T04_PL_-bp6-007.command`

## PL!-bp6-008
- `PL!-bp6-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp6-008_A01_T01_PL_-bp6-008.command`
- `PL!-bp6-008#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp6-008_A01_T02_PL_-bp6-008.command`
- `PL!-bp6-008#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp6-008_A01_T03_PL_-bp6-008.command`
- `PL!-bp6-008#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_-bp6-008_A01_T04_PL_-bp6-008.command`
- `PL!-bp6-008#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-bp6-008_A01_T05_PL_-bp6-008.command`

## PL!-bp6-010
- `PL!-bp6-010#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-bp6-010_A01_T01_PL_-bp6-010.command`
- `PL!-bp6-010#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-bp6-010_A01_T02_PL_-bp6-010.command`
- `PL!-bp6-010#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-bp6-010_A01_T03_PL_-bp6-010.command`

## PL!-bp6-011
- `PL!-bp6-011#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-011_A01_T01_PL_-bp6-011.command`
- `PL!-bp6-011#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-011_A01_T02_PL_-bp6-011.command`

## PL!-bp6-012
- `PL!-bp6-012#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-012_A01_T01_PL_-bp6-012.command`
- `PL!-bp6-012#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp6-012_A01_T02_PL_-bp6-012.command`
- `PL!-bp6-012#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp6-012_A01_T03_PL_-bp6-012.command`
- `PL!-bp6-012#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp6-012_A01_T04_PL_-bp6-012.command`
- `PL!-bp6-012#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp6-012_A01_T05_PL_-bp6-012.command`

## PL!-bp6-013
- `PL!-bp6-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-bp6-013_A01_T01_PL_-bp6-013.command`
- `PL!-bp6-013#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-bp6-013_A01_T02_PL_-bp6-013.command`
- `PL!-bp6-013#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-bp6-013_A01_T03_PL_-bp6-013.command`

## PL!-bp6-014
- `PL!-bp6-014#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-014_A01_T01_PL_-bp6-014.command`
- `PL!-bp6-014#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp6-014_A01_T02_PL_-bp6-014.command`
- `PL!-bp6-014#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp6-014_A01_T03_PL_-bp6-014.command`
- `PL!-bp6-014#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp6-014_A01_T04_PL_-bp6-014.command`
- `PL!-bp6-014#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp6-014_A01_T05_PL_-bp6-014.command`

## PL!-bp6-015
- `PL!-bp6-015#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-015_A01_T01_PL_-bp6-015.command`
- `PL!-bp6-015#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-bp6-015_A01_T02_PL_-bp6-015.command`
- `PL!-bp6-015#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-bp6-015_A01_T03_PL_-bp6-015.command`
- `PL!-bp6-015#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-bp6-015_A01_T04_PL_-bp6-015.command`
- `PL!-bp6-015#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-bp6-015_A01_T05_PL_-bp6-015.command`

## PL!-bp6-016
- `PL!-bp6-016#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-016_A01_T01_PL_-bp6-016.command`
- `PL!-bp6-016#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-016_A01_T02_PL_-bp6-016.command`

## PL!-bp6-021
- `PL!-bp6-021#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-021_A01_T01_PL_-bp6-021.command`
- `PL!-bp6-021#A01#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_-bp6-021_A01_T02_PL_-bp6-021.command`
- `PL!-bp6-021#A01#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_-bp6-021_A01_T03_PL_-bp6-021.command`
- `PL!-bp6-021#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-021_A01_T04_PL_-bp6-021.command`

## PL!-bp6-023
- `PL!-bp6-023#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-bp6-023_A01_T01_PL_-bp6-023.command`
- `PL!-bp6-023#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_-bp6-023_A01_T02_PL_-bp6-023.command`
- `PL!-bp6-023#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_-bp6-023_A01_T03_PL_-bp6-023.command`
- `PL!-bp6-023#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-bp6-023_A01_T04_PL_-bp6-023.command`

## PL!-pb1-001
- `PL!-pb1-001#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-pb1-001_A01_T01_PL_-pb1-001.command`
- `PL!-pb1-001#A01#T02` 起動 / 任意処理を実行 / command: `debug_commands/PL_-pb1-001_A01_T02_PL_-pb1-001.command`
- `PL!-pb1-001#A01#T03` 起動 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-001_A01_T03_PL_-pb1-001.command`
- `PL!-pb1-001#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_-pb1-001_A01_T04_PL_-pb1-001.command`
- `PL!-pb1-001#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_-pb1-001_A01_T05_PL_-pb1-001.command`
- `PL!-pb1-001#A01#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_-pb1-001_A01_T06_PL_-pb1-001.command`
- `PL!-pb1-001#A01#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-pb1-001_A01_T07_PL_-pb1-001.command`

## PL!-pb1-002
- `PL!-pb1-002#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-002_A01_T01_PL_-pb1-002.command`
- `PL!-pb1-002#A01#T02` 登場 / ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-pb1-002_A01_T02_PL_-pb1-002.command`
- `PL!-pb1-002#A01#T03` 登場 / ライブ開始時 / 境界値 / command: `debug_commands/PL_-pb1-002_A01_T03_PL_-pb1-002.command`

## PL!-pb1-003
- `PL!-pb1-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-003_A01_T01_PL_-pb1-003.command`
- `PL!-pb1-003#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-pb1-003_A01_T02_PL_-pb1-003.command`
- `PL!-pb1-003#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-003_A01_T03_PL_-pb1-003.command`
- `PL!-pb1-003#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-pb1-003_A01_T04_PL_-pb1-003.command`
- `PL!-pb1-003#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-pb1-003_A01_T05_PL_-pb1-003.command`

## PL!-pb1-004
- `PL!-pb1-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-004_A01_T01_PL_-pb1-004.command`
- `PL!-pb1-004#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-pb1-004_A01_T02_PL_-pb1-004.command`
- `PL!-pb1-004#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-pb1-004_A01_T03_PL_-pb1-004.command`
- `PL!-pb1-004#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_-pb1-004_A01_T04_PL_-pb1-004.command`
- `PL!-pb1-004#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-004_A01_T05_PL_-pb1-004.command`

## PL!-pb1-005
- `PL!-pb1-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-005_A01_T01_PL_-pb1-005.command`
- `PL!-pb1-005#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-pb1-005_A01_T02_PL_-pb1-005.command`
- `PL!-pb1-005#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-pb1-005_A01_T03_PL_-pb1-005.command`

## PL!-pb1-006
- `PL!-pb1-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-006_A01_T01_PL_-pb1-006.command`
- `PL!-pb1-006#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-pb1-006_A01_T02_PL_-pb1-006.command`
- `PL!-pb1-006#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-pb1-006_A01_T03_PL_-pb1-006.command`
- `PL!-pb1-006#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_-pb1-006_A01_T04_PL_-pb1-006.command`
- `PL!-pb1-006#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-006_A01_T05_PL_-pb1-006.command`

## PL!-pb1-007
- `PL!-pb1-007#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-pb1-007_A01_T01_PL_-pb1-007.command`
- `PL!-pb1-007#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_-pb1-007_A01_T02_PL_-pb1-007.command`
- `PL!-pb1-007#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_-pb1-007_A01_T03_PL_-pb1-007.command`
- `PL!-pb1-007#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_-pb1-007_A01_T04_PL_-pb1-007.command`
- `PL!-pb1-007#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_-pb1-007_A01_T05_PL_-pb1-007.command`
- `PL!-pb1-007#A01#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_-pb1-007_A01_T06_PL_-pb1-007.command`
- `PL!-pb1-007#A01#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_-pb1-007_A01_T07_PL_-pb1-007.command`

## PL!-pb1-008
- `PL!-pb1-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-008_A01_T01_PL_-pb1-008.command`
- `PL!-pb1-008#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-pb1-008_A01_T02_PL_-pb1-008.command`
- `PL!-pb1-008#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-008_A01_T03_PL_-pb1-008.command`
- `PL!-pb1-008#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_-pb1-008_A01_T04_PL_-pb1-008.command`
- `PL!-pb1-008#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_-pb1-008_A01_T05_PL_-pb1-008.command`

## PL!-pb1-009
- `PL!-pb1-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-009_A01_T01_PL_-pb1-009.command`
- `PL!-pb1-009#A02#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-009_A02_T01_PL_-pb1-009.command`
- `PL!-pb1-009#A02#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-pb1-009_A02_T02_PL_-pb1-009.command`
- `PL!-pb1-009#A02#T03` 登場 / 境界値 / command: `debug_commands/PL_-pb1-009_A02_T03_PL_-pb1-009.command`

## PL!-pb1-010
- `PL!-pb1-010#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-010_A01_T01_PL_-pb1-010.command`
- `PL!-pb1-010#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-pb1-010_A01_T02_PL_-pb1-010.command`
- `PL!-pb1-010#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-010_A01_T03_PL_-pb1-010.command`
- `PL!-pb1-010#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-pb1-010_A01_T04_PL_-pb1-010.command`
- `PL!-pb1-010#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-pb1-010_A01_T05_PL_-pb1-010.command`
- `PL!-pb1-010#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-pb1-010_A01_T06_PL_-pb1-010.command`

## PL!-pb1-011
- `PL!-pb1-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-011_A01_T01_PL_-pb1-011.command`
- `PL!-pb1-011#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-pb1-011_A01_T02_PL_-pb1-011.command`
- `PL!-pb1-011#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-pb1-011_A01_T03_PL_-pb1-011.command`

## PL!-pb1-012
- `PL!-pb1-012#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-012_A01_T01_PL_-pb1-012.command`
- `PL!-pb1-012#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_-pb1-012_A01_T02_PL_-pb1-012.command`
- `PL!-pb1-012#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-012_A01_T03_PL_-pb1-012.command`

## PL!-pb1-014
- `PL!-pb1-014#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-014_A01_T01_PL_-pb1-014.command`
- `PL!-pb1-014#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_-pb1-014_A01_T02_PL_-pb1-014.command`
- `PL!-pb1-014#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_-pb1-014_A01_T03_PL_-pb1-014.command`
- `PL!-pb1-014#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-pb1-014_A01_T04_PL_-pb1-014.command`
- `PL!-pb1-014#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_-pb1-014_A01_T05_PL_-pb1-014.command`

## PL!-pb1-015
- `PL!-pb1-015#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-015_A01_T01_PL_-pb1-015.command`
- `PL!-pb1-015#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-pb1-015_A01_T02_PL_-pb1-015.command`
- `PL!-pb1-015#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-015_A01_T03_PL_-pb1-015.command`
- `PL!-pb1-015#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-pb1-015_A01_T04_PL_-pb1-015.command`
- `PL!-pb1-015#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-pb1-015_A01_T05_PL_-pb1-015.command`

## PL!-pb1-016
- `PL!-pb1-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-016_A01_T01_PL_-pb1-016.command`

## PL!-pb1-017
- `PL!-pb1-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-017_A01_T01_PL_-pb1-017.command`
- `PL!-pb1-017#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-pb1-017_A01_T02_PL_-pb1-017.command`
- `PL!-pb1-017#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-pb1-017_A01_T03_PL_-pb1-017.command`
- `PL!-pb1-017#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_-pb1-017_A01_T04_PL_-pb1-017.command`
- `PL!-pb1-017#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-pb1-017_A01_T05_PL_-pb1-017.command`
- `PL!-pb1-017#A01#T06` 登場 / コスト支払い可能 / command: `debug_commands/PL_-pb1-017_A01_T06_PL_-pb1-017.command`
- `PL!-pb1-017#A01#T07` 登場 / コスト支払い不能 / command: `debug_commands/PL_-pb1-017_A01_T07_PL_-pb1-017.command`

## PL!-pb1-018
- `PL!-pb1-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-pb1-018_A01_T01_PL_-pb1-018.command`

## PL!-pb1-019
- `PL!-pb1-019#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-pb1-019_A01_T01_PL_-pb1-019.command`
- `PL!-pb1-019#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-pb1-019_A01_T02_PL_-pb1-019.command`
- `PL!-pb1-019#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-pb1-019_A01_T03_PL_-pb1-019.command`

## PL!-pb1-024
- `PL!-pb1-024#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-pb1-024_A01_T01_PL_-pb1-024.command`
- `PL!-pb1-024#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-pb1-024_A01_T02_PL_-pb1-024.command`
- `PL!-pb1-024#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-pb1-024_A01_T03_PL_-pb1-024.command`

## PL!-pb1-025
- `PL!-pb1-025#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-pb1-025_A01_T01_PL_-pb1-025.command`
- `PL!-pb1-025#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-pb1-025_A01_T02_PL_-pb1-025.command`
- `PL!-pb1-025#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-pb1-025_A01_T03_PL_-pb1-025.command`

## PL!-pb1-028
- `PL!-pb1-028#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-028_A01_T01_PL_-pb1-028.command`
- `PL!-pb1-028#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-pb1-028_A01_T02_PL_-pb1-028.command`
- `PL!-pb1-028#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-pb1-028_A01_T03_PL_-pb1-028.command`
- `PL!-pb1-028#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-pb1-028_A01_T04_PL_-pb1-028.command`

## PL!-pb1-029
- `PL!-pb1-029#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-029_A01_T01_PL_-pb1-029.command`
- `PL!-pb1-029#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-pb1-029_A01_T02_PL_-pb1-029.command`
- `PL!-pb1-029#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-pb1-029_A01_T03_PL_-pb1-029.command`
- `PL!-pb1-029#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-pb1-029_A01_T04_PL_-pb1-029.command`

## PL!-pb1-030
- `PL!-pb1-030#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-030_A01_T01_PL_-pb1-030.command`
- `PL!-pb1-030#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-pb1-030_A01_T02_PL_-pb1-030.command`
- `PL!-pb1-030#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-pb1-030_A01_T03_PL_-pb1-030.command`
- `PL!-pb1-030#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-pb1-030_A01_T04_PL_-pb1-030.command`
- `PL!-pb1-030#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-030_A02_T01_PL_-pb1-030.command`
- `PL!-pb1-030#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_-pb1-030_A02_T02_PL_-pb1-030.command`
- `PL!-pb1-030#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_-pb1-030_A02_T03_PL_-pb1-030.command`
- `PL!-pb1-030#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-pb1-030_A02_T04_PL_-pb1-030.command`

## PL!-pb1-031
- `PL!-pb1-031#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-031_A01_T01_PL_-pb1-031.command`
- `PL!-pb1-031#A01#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_-pb1-031_A01_T02_PL_-pb1-031.command`
- `PL!-pb1-031#A01#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_-pb1-031_A01_T03_PL_-pb1-031.command`
- `PL!-pb1-031#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-pb1-031_A01_T04_PL_-pb1-031.command`

## PL!-pb1-032
- `PL!-pb1-032#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-pb1-032_A01_T01_PL_-pb1-032.command`
- `PL!-pb1-032#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_-pb1-032_A01_T02_PL_-pb1-032.command`
- `PL!-pb1-032#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_-pb1-032_A01_T03_PL_-pb1-032.command`
- `PL!-pb1-032#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-pb1-032_A01_T04_PL_-pb1-032.command`

## PL!-sd1-001
- `PL!-sd1-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-001_A01_T01_PL_-sd1-001.command`
- `PL!-sd1-001#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-sd1-001_A01_T02_PL_-sd1-001.command`
- `PL!-sd1-001#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-sd1-001_A01_T03_PL_-sd1-001.command`
- `PL!-sd1-001#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_-sd1-001_A02_T01_PL_-sd1-001.command`
- `PL!-sd1-001#A02#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_-sd1-001_A02_T02_PL_-sd1-001.command`
- `PL!-sd1-001#A02#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_-sd1-001_A02_T03_PL_-sd1-001.command`

## PL!-sd1-002
- `PL!-sd1-002#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-sd1-002_A01_T01_PL_-sd1-002.command`
- `PL!-sd1-002#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-sd1-002_A01_T02_PL_-sd1-002.command`
- `PL!-sd1-002#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-sd1-002_A01_T03_PL_-sd1-002.command`

## PL!-sd1-003
- `PL!-sd1-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-003_A01_T01_PL_-sd1-003.command`
- `PL!-sd1-003#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-sd1-003_A02_T01_PL_-sd1-003.command`
- `PL!-sd1-003#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-sd1-003_A02_T02_PL_-sd1-003.command`
- `PL!-sd1-003#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-sd1-003_A02_T03_PL_-sd1-003.command`
- `PL!-sd1-003#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_-sd1-003_A02_T04_PL_-sd1-003.command`
- `PL!-sd1-003#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_-sd1-003_A02_T05_PL_-sd1-003.command`
- `PL!-sd1-003#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-sd1-003_A02_T06_PL_-sd1-003.command`

## PL!-sd1-004
- `PL!-sd1-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-004_A01_T01_PL_-sd1-004.command`

## PL!-sd1-005
- `PL!-sd1-005#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-sd1-005_A01_T01_PL_-sd1-005.command`
- `PL!-sd1-005#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-sd1-005_A01_T02_PL_-sd1-005.command`
- `PL!-sd1-005#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-sd1-005_A01_T03_PL_-sd1-005.command`

## PL!-sd1-006
- `PL!-sd1-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-006_A01_T01_PL_-sd1-006.command`
- `PL!-sd1-006#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-sd1-006_A01_T02_PL_-sd1-006.command`
- `PL!-sd1-006#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-sd1-006_A01_T03_PL_-sd1-006.command`
- `PL!-sd1-006#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_-sd1-006_A01_T04_PL_-sd1-006.command`
- `PL!-sd1-006#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_-sd1-006_A01_T05_PL_-sd1-006.command`
- `PL!-sd1-006#A01#T06` 登場 / コスト支払い可能 / command: `debug_commands/PL_-sd1-006_A01_T06_PL_-sd1-006.command`
- `PL!-sd1-006#A01#T07` 登場 / コスト支払い不能 / command: `debug_commands/PL_-sd1-006_A01_T07_PL_-sd1-006.command`

## PL!-sd1-007
- `PL!-sd1-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-007_A01_T01_PL_-sd1-007.command`
- `PL!-sd1-007#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_-sd1-007_A01_T02_PL_-sd1-007.command`
- `PL!-sd1-007#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_-sd1-007_A01_T03_PL_-sd1-007.command`

## PL!-sd1-008
- `PL!-sd1-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_-sd1-008_A01_T01_PL_-sd1-008.command`
- `PL!-sd1-008#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_-sd1-008_A01_T02_PL_-sd1-008.command`
- `PL!-sd1-008#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_-sd1-008_A01_T03_PL_-sd1-008.command`

## PL!-sd1-009
- `PL!-sd1-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-sd1-009_A01_T01_PL_-sd1-009.command`
- `PL!-sd1-009#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_-sd1-009_A01_T02_PL_-sd1-009.command`
- `PL!-sd1-009#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_-sd1-009_A01_T03_PL_-sd1-009.command`
- `PL!-sd1-009#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_-sd1-009_A01_T04_PL_-sd1-009.command`
- `PL!-sd1-009#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_-sd1-009_A01_T05_PL_-sd1-009.command`
- `PL!-sd1-009#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-sd1-009_A01_T06_PL_-sd1-009.command`

## PL!-sd1-011
- `PL!-sd1-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-011_A01_T01_PL_-sd1-011.command`
- `PL!-sd1-011#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-sd1-011_A01_T02_PL_-sd1-011.command`
- `PL!-sd1-011#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-sd1-011_A01_T03_PL_-sd1-011.command`

## PL!-sd1-012
- `PL!-sd1-012#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-012_A01_T01_PL_-sd1-012.command`
- `PL!-sd1-012#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-sd1-012_A01_T02_PL_-sd1-012.command`
- `PL!-sd1-012#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-sd1-012_A01_T03_PL_-sd1-012.command`

## PL!-sd1-015
- `PL!-sd1-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-015_A01_T01_PL_-sd1-015.command`
- `PL!-sd1-015#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-sd1-015_A01_T02_PL_-sd1-015.command`
- `PL!-sd1-015#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-sd1-015_A01_T03_PL_-sd1-015.command`

## PL!-sd1-016
- `PL!-sd1-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_-sd1-016_A01_T01_PL_-sd1-016.command`
- `PL!-sd1-016#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_-sd1-016_A01_T02_PL_-sd1-016.command`
- `PL!-sd1-016#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_-sd1-016_A01_T03_PL_-sd1-016.command`

## PL!-sd1-019
- `PL!-sd1-019#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_-sd1-019_A01_T01_PL_-sd1-019.command`
- `PL!-sd1-019#A01#T02` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_-sd1-019_A01_T02_PL_-sd1-019.command`
- `PL!-sd1-019#A01#T03` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_-sd1-019_A01_T03_PL_-sd1-019.command`
- `PL!-sd1-019#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-sd1-019_A01_T04_PL_-sd1-019.command`

## PL!-sd1-022
- `PL!-sd1-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_-sd1-022_A01_T01_PL_-sd1-022.command`
- `PL!-sd1-022#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_-sd1-022_A01_T02_PL_-sd1-022.command`

## PL!HS-PR-001
- `PL!HS-PR-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-001_A01_T01_PL_HS-PR-001.command`
- `PL!HS-PR-001#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-001_A01_T02_PL_HS-PR-001.command`
- `PL!HS-PR-001#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-001_A01_T03_PL_HS-PR-001.command`
- `PL!HS-PR-001#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-001_A02_T01_PL_HS-PR-001.command`
- `PL!HS-PR-001#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-001_A02_T02_PL_HS-PR-001.command`
- `PL!HS-PR-001#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-001_A02_T03_PL_HS-PR-001.command`
- `PL!HS-PR-001#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-001_A02_T04_PL_HS-PR-001.command`
- `PL!HS-PR-001#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-001_A02_T05_PL_HS-PR-001.command`
- `PL!HS-PR-001#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-001_A02_T06_PL_HS-PR-001.command`

## PL!HS-PR-002
- `PL!HS-PR-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-002_A01_T01_PL_HS-PR-002.command`
- `PL!HS-PR-002#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-002_A01_T02_PL_HS-PR-002.command`
- `PL!HS-PR-002#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-002_A01_T03_PL_HS-PR-002.command`
- `PL!HS-PR-002#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-002_A02_T01_PL_HS-PR-002.command`
- `PL!HS-PR-002#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-002_A02_T02_PL_HS-PR-002.command`
- `PL!HS-PR-002#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-002_A02_T03_PL_HS-PR-002.command`
- `PL!HS-PR-002#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-002_A02_T04_PL_HS-PR-002.command`
- `PL!HS-PR-002#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-002_A02_T05_PL_HS-PR-002.command`
- `PL!HS-PR-002#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-002_A02_T06_PL_HS-PR-002.command`

## PL!HS-PR-005
- `PL!HS-PR-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-005_A01_T01_PL_HS-PR-005.command`
- `PL!HS-PR-005#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-005_A01_T02_PL_HS-PR-005.command`
- `PL!HS-PR-005#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-005_A01_T03_PL_HS-PR-005.command`
- `PL!HS-PR-005#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-005_A02_T01_PL_HS-PR-005.command`
- `PL!HS-PR-005#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-005_A02_T02_PL_HS-PR-005.command`
- `PL!HS-PR-005#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-005_A02_T03_PL_HS-PR-005.command`
- `PL!HS-PR-005#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-005_A02_T04_PL_HS-PR-005.command`
- `PL!HS-PR-005#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-005_A02_T05_PL_HS-PR-005.command`
- `PL!HS-PR-005#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-005_A02_T06_PL_HS-PR-005.command`

## PL!HS-PR-014
- `PL!HS-PR-014#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-014_A01_T01_PL_HS-PR-014.command`
- `PL!HS-PR-014#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-014_A01_T02_PL_HS-PR-014.command`
- `PL!HS-PR-014#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-014_A01_T03_PL_HS-PR-014.command`

## PL!HS-PR-016
- `PL!HS-PR-016#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-016_A01_T01_PL_HS-PR-016.command`
- `PL!HS-PR-016#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-016_A01_T02_PL_HS-PR-016.command`
- `PL!HS-PR-016#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-016_A01_T03_PL_HS-PR-016.command`
- `PL!HS-PR-016#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-016_A01_T04_PL_HS-PR-016.command`
- `PL!HS-PR-016#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-016_A01_T05_PL_HS-PR-016.command`
- `PL!HS-PR-016#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-016_A01_T06_PL_HS-PR-016.command`

## PL!HS-PR-017
- `PL!HS-PR-017#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-017_A01_T01_PL_HS-PR-017.command`
- `PL!HS-PR-017#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-017_A01_T02_PL_HS-PR-017.command`
- `PL!HS-PR-017#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-017_A01_T03_PL_HS-PR-017.command`
- `PL!HS-PR-017#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-017_A01_T04_PL_HS-PR-017.command`
- `PL!HS-PR-017#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-017_A01_T05_PL_HS-PR-017.command`
- `PL!HS-PR-017#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-017_A01_T06_PL_HS-PR-017.command`

## PL!HS-PR-018
- `PL!HS-PR-018#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-018_A01_T01_PL_HS-PR-018.command`
- `PL!HS-PR-018#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-018_A01_T02_PL_HS-PR-018.command`
- `PL!HS-PR-018#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-018_A01_T03_PL_HS-PR-018.command`
- `PL!HS-PR-018#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-018_A01_T04_PL_HS-PR-018.command`
- `PL!HS-PR-018#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-018_A01_T05_PL_HS-PR-018.command`
- `PL!HS-PR-018#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-018_A01_T06_PL_HS-PR-018.command`

## PL!HS-PR-019
- `PL!HS-PR-019#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-019_A01_T01_PL_HS-PR-019.command`
- `PL!HS-PR-019#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-PR-019_A01_T02_PL_HS-PR-019.command`
- `PL!HS-PR-019#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-PR-019_A01_T03_PL_HS-PR-019.command`
- `PL!HS-PR-019#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-019_A01_T04_PL_HS-PR-019.command`
- `PL!HS-PR-019#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-019_A01_T05_PL_HS-PR-019.command`

## PL!HS-PR-020
- `PL!HS-PR-020#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-020_A01_T01_PL_HS-PR-020.command`
- `PL!HS-PR-020#A01#T02` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-020_A01_T02_PL_HS-PR-020.command`
- `PL!HS-PR-020#A01#T03` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-020_A01_T03_PL_HS-PR-020.command`
- `PL!HS-PR-020#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-020_A01_T04_PL_HS-PR-020.command`

## PL!HS-PR-021
- `PL!HS-PR-021#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-021_A01_T01_PL_HS-PR-021.command`
- `PL!HS-PR-021#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-PR-021_A01_T02_PL_HS-PR-021.command`
- `PL!HS-PR-021#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-PR-021_A01_T03_PL_HS-PR-021.command`
- `PL!HS-PR-021#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-021_A01_T04_PL_HS-PR-021.command`
- `PL!HS-PR-021#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-021_A01_T05_PL_HS-PR-021.command`

## PL!HS-PR-022
- `PL!HS-PR-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-022_A01_T01_PL_HS-PR-022.command`
- `PL!HS-PR-022#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-022_A01_T02_PL_HS-PR-022.command`
- `PL!HS-PR-022#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-022_A01_T03_PL_HS-PR-022.command`
- `PL!HS-PR-022#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-022_A01_T04_PL_HS-PR-022.command`
- `PL!HS-PR-022#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-022_A01_T05_PL_HS-PR-022.command`
- `PL!HS-PR-022#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-022_A01_T06_PL_HS-PR-022.command`

## PL!HS-PR-023
- `PL!HS-PR-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-023_A01_T01_PL_HS-PR-023.command`
- `PL!HS-PR-023#A01#T02` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-023_A01_T02_PL_HS-PR-023.command`
- `PL!HS-PR-023#A01#T03` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-023_A01_T03_PL_HS-PR-023.command`
- `PL!HS-PR-023#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-023_A01_T04_PL_HS-PR-023.command`

## PL!HS-PR-026
- `PL!HS-PR-026#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-026_A01_T01_PL_HS-PR-026.command`
- `PL!HS-PR-026#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-026_A01_T02_PL_HS-PR-026.command`
- `PL!HS-PR-026#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-026_A01_T03_PL_HS-PR-026.command`

## PL!HS-PR-027
- `PL!HS-PR-027#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-027_A01_T01_PL_HS-PR-027.command`
- `PL!HS-PR-027#A01#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-027_A01_T02_PL_HS-PR-027.command`
- `PL!HS-PR-027#A01#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-027_A01_T03_PL_HS-PR-027.command`
- `PL!HS-PR-027#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-027_A01_T04_PL_HS-PR-027.command`

## PL!HS-PR-028
- `PL!HS-PR-028#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-028_A01_T01_PL_HS-PR-028.command`
- `PL!HS-PR-028#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-PR-028_A01_T02_PL_HS-PR-028.command`
- `PL!HS-PR-028#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-PR-028_A01_T03_PL_HS-PR-028.command`
- `PL!HS-PR-028#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-028_A01_T04_PL_HS-PR-028.command`

## PL!HS-PR-029
- `PL!HS-PR-029#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-029_A01_T01_PL_HS-PR-029.command`
- `PL!HS-PR-029#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-029_A01_T02_PL_HS-PR-029.command`
- `PL!HS-PR-029#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-029_A01_T03_PL_HS-PR-029.command`
- `PL!HS-PR-029#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-029_A01_T04_PL_HS-PR-029.command`
- `PL!HS-PR-029#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-029_A01_T05_PL_HS-PR-029.command`
- `PL!HS-PR-029#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-PR-029_A01_T06_PL_HS-PR-029.command`

## PL!HS-PR-031
- `PL!HS-PR-031#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-031_A01_T01_PL_HS-PR-031.command`
- `PL!HS-PR-031#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-PR-031_A01_T02_PL_HS-PR-031.command`
- `PL!HS-PR-031#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-PR-031_A01_T03_PL_HS-PR-031.command`
- `PL!HS-PR-031#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-PR-031_A01_T04_PL_HS-PR-031.command`
- `PL!HS-PR-031#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-PR-031_A01_T05_PL_HS-PR-031.command`

## PL!HS-PR-032
- `PL!HS-PR-032#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-032_A01_T01_PL_HS-PR-032.command`

## PL!HS-PR-035
- `PL!HS-PR-035#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-035_A01_T01_PL_HS-PR-035.command`
- `PL!HS-PR-035#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-PR-035_A01_T02_PL_HS-PR-035.command`
- `PL!HS-PR-035#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-PR-035_A01_T03_PL_HS-PR-035.command`

## PL!HS-PR-036
- `PL!HS-PR-036#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-PR-036_A01_T01_PL_HS-PR-036.command`
- `PL!HS-PR-036#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-PR-036_A01_T02_PL_HS-PR-036.command`
- `PL!HS-PR-036#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-PR-036_A01_T03_PL_HS-PR-036.command`

## PL!HS-bp1-001
- `PL!HS-bp1-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-001_A01_T01_PL_HS-bp1-001.command`

## PL!HS-bp1-002
- `PL!HS-bp1-002#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-002_A01_T01_PL_HS-bp1-002.command`
- `PL!HS-bp1-002#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-002_A01_T02_PL_HS-bp1-002.command`
- `PL!HS-bp1-002#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-002_A01_T03_PL_HS-bp1-002.command`

## PL!HS-bp1-003
- `PL!HS-bp1-003#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-003_A02_T01_PL_HS-bp1-003.command`
- `PL!HS-bp1-003#A02#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-003_A02_T02_PL_HS-bp1-003.command`
- `PL!HS-bp1-003#A02#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-003_A02_T03_PL_HS-bp1-003.command`
- `PL!HS-bp1-003#A02#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_HS-bp1-003_A02_T04_PL_HS-bp1-003.command`
- `PL!HS-bp1-003#A02#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp1-003_A02_T05_PL_HS-bp1-003.command`

## PL!HS-bp1-004
- `PL!HS-bp1-004#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-004_A01_T01_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-004_A01_T02_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-004_A01_T03_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_HS-bp1-004_A01_T04_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp1-004_A01_T05_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-004_A02_T01_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp1-004_A02_T02_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp1-004_A02_T03_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-004_A02_T04_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-004_A02_T05_PL_HS-bp1-004.command`
- `PL!HS-bp1-004#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp1-004_A02_T06_PL_HS-bp1-004.command`

## PL!HS-bp1-005
- `PL!HS-bp1-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-005_A01_T01_PL_HS-bp1-005.command`
- `PL!HS-bp1-005#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp1-005_A01_T02_PL_HS-bp1-005.command`
- `PL!HS-bp1-005#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp1-005_A01_T03_PL_HS-bp1-005.command`
- `PL!HS-bp1-005#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-005_A01_T04_PL_HS-bp1-005.command`
- `PL!HS-bp1-005#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-005_A01_T05_PL_HS-bp1-005.command`

## PL!HS-bp1-006
- `PL!HS-bp1-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-006_A01_T01_PL_HS-bp1-006.command`
- `PL!HS-bp1-006#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-006_A02_T01_PL_HS-bp1-006.command`
- `PL!HS-bp1-006#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp1-006_A02_T02_PL_HS-bp1-006.command`
- `PL!HS-bp1-006#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp1-006_A02_T03_PL_HS-bp1-006.command`
- `PL!HS-bp1-006#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp1-006_A02_T04_PL_HS-bp1-006.command`
- `PL!HS-bp1-006#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp1-006_A02_T05_PL_HS-bp1-006.command`
- `PL!HS-bp1-006#A02#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-006_A02_T06_PL_HS-bp1-006.command`
- `PL!HS-bp1-006#A02#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-006_A02_T07_PL_HS-bp1-006.command`
- `PL!HS-bp1-006#A02#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp1-006_A02_T08_PL_HS-bp1-006.command`

## PL!HS-bp1-007
- `PL!HS-bp1-007#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-007_A01_T01_PL_HS-bp1-007.command`
- `PL!HS-bp1-007#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-007_A01_T02_PL_HS-bp1-007.command`
- `PL!HS-bp1-007#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-007_A01_T03_PL_HS-bp1-007.command`
- `PL!HS-bp1-007#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_HS-bp1-007_A01_T04_PL_HS-bp1-007.command`
- `PL!HS-bp1-007#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp1-007_A01_T05_PL_HS-bp1-007.command`

## PL!HS-bp1-008
- `PL!HS-bp1-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-008_A01_T01_PL_HS-bp1-008.command`
- `PL!HS-bp1-008#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp1-008_A01_T02_PL_HS-bp1-008.command`
- `PL!HS-bp1-008#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp1-008_A01_T03_PL_HS-bp1-008.command`

## PL!HS-bp1-009
- `PL!HS-bp1-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-009_A01_T01_PL_HS-bp1-009.command`
- `PL!HS-bp1-009#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-009_A01_T02_PL_HS-bp1-009.command`
- `PL!HS-bp1-009#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-009_A01_T03_PL_HS-bp1-009.command`

## PL!HS-bp1-010
- `PL!HS-bp1-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-010_A01_T01_PL_HS-bp1-010.command`

## PL!HS-bp1-011
- `PL!HS-bp1-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-011_A01_T01_PL_HS-bp1-011.command`
- `PL!HS-bp1-011#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp1-011_A01_T02_PL_HS-bp1-011.command`
- `PL!HS-bp1-011#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp1-011_A01_T03_PL_HS-bp1-011.command`

## PL!HS-bp1-014
- `PL!HS-bp1-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-014_A01_T01_PL_HS-bp1-014.command`

## PL!HS-bp1-021
- `PL!HS-bp1-021#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-021_A01_T01_PL_HS-bp1-021.command`
- `PL!HS-bp1-021#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp1-021_A01_T02_PL_HS-bp1-021.command`

## PL!HS-bp1-022
- `PL!HS-bp1-022#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-022_A01_T01_PL_HS-bp1-022.command`
- `PL!HS-bp1-022#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-bp1-022_A01_T02_PL_HS-bp1-022.command`
- `PL!HS-bp1-022#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-bp1-022_A01_T03_PL_HS-bp1-022.command`
- `PL!HS-bp1-022#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp1-022_A01_T04_PL_HS-bp1-022.command`

## PL!HS-bp1-023
- `PL!HS-bp1-023#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp1-023_A01_T01_PL_HS-bp1-023.command`
- `PL!HS-bp1-023#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-bp1-023_A01_T02_PL_HS-bp1-023.command`
- `PL!HS-bp1-023#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-bp1-023_A01_T03_PL_HS-bp1-023.command`
- `PL!HS-bp1-023#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp1-023_A01_T04_PL_HS-bp1-023.command`

## PL!HS-bp2-001
- `PL!HS-bp2-001#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-001_A01_T01_PL_HS-bp2-001.command`
- `PL!HS-bp2-001#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-001_A01_T02_PL_HS-bp2-001.command`
- `PL!HS-bp2-001#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-001_A01_T03_PL_HS-bp2-001.command`
- `PL!HS-bp2-001#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_HS-bp2-001_A01_T04_PL_HS-bp2-001.command`
- `PL!HS-bp2-001#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp2-001_A01_T05_PL_HS-bp2-001.command`

## PL!HS-bp2-002
- `PL!HS-bp2-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-002_A01_T01_PL_HS-bp2-002.command`
- `PL!HS-bp2-002#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-002_A01_T02_PL_HS-bp2-002.command`
- `PL!HS-bp2-002#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-002_A01_T03_PL_HS-bp2-002.command`
- `PL!HS-bp2-002#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-002_A02_T01_PL_HS-bp2-002.command`
- `PL!HS-bp2-002#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-002_A02_T02_PL_HS-bp2-002.command`
- `PL!HS-bp2-002#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_HS-bp2-002_A02_T03_PL_HS-bp2-002.command`
- `PL!HS-bp2-002#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-bp2-002_A02_T04_PL_HS-bp2-002.command`
- `PL!HS-bp2-002#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-bp2-002_A02_T05_PL_HS-bp2-002.command`

## PL!HS-bp2-003
- `PL!HS-bp2-003#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-003_A01_T01_PL_HS-bp2-003.command`
- `PL!HS-bp2-003#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-003_A01_T02_PL_HS-bp2-003.command`
- `PL!HS-bp2-003#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-003_A01_T03_PL_HS-bp2-003.command`
- `PL!HS-bp2-003#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-003_A01_T04_PL_HS-bp2-003.command`
- `PL!HS-bp2-003#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-003_A01_T05_PL_HS-bp2-003.command`
- `PL!HS-bp2-003#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-003_A01_T06_PL_HS-bp2-003.command`

## PL!HS-bp2-004
- `PL!HS-bp2-004#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-004_A01_T01_PL_HS-bp2-004.command`
- `PL!HS-bp2-004#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-004_A01_T02_PL_HS-bp2-004.command`
- `PL!HS-bp2-004#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-004_A01_T03_PL_HS-bp2-004.command`

## PL!HS-bp2-005
- `PL!HS-bp2-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-005_A01_T01_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp2-005_A01_T02_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp2-005_A01_T03_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-005_A01_T04_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-005_A01_T05_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-005_A02_T01_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-005_A02_T02_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-005_A02_T03_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-005_A02_T04_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-005_A02_T05_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A02#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-005_A02_T06_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A02#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-005_A02_T07_PL_HS-bp2-005.command`
- `PL!HS-bp2-005#A02#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-005_A02_T08_PL_HS-bp2-005.command`

## PL!HS-bp2-006
- `PL!HS-bp2-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-006_A01_T01_PL_HS-bp2-006.command`
- `PL!HS-bp2-006#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-006_A02_T01_PL_HS-bp2-006.command`
- `PL!HS-bp2-006#A02#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-bp2-006_A02_T02_PL_HS-bp2-006.command`
- `PL!HS-bp2-006#A02#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-bp2-006_A02_T03_PL_HS-bp2-006.command`

## PL!HS-bp2-007
- `PL!HS-bp2-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-007_A01_T01_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp2-007_A01_T02_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp2-007_A01_T03_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-007_A02_T01_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-007_A02_T02_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-007_A02_T03_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-007_A02_T04_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-007_A02_T05_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A02#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-007_A02_T06_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A02#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-007_A02_T07_PL_HS-bp2-007.command`
- `PL!HS-bp2-007#A02#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-007_A02_T08_PL_HS-bp2-007.command`

## PL!HS-bp2-008
- `PL!HS-bp2-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-008_A01_T01_PL_HS-bp2-008.command`
- `PL!HS-bp2-008#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp2-008_A01_T02_PL_HS-bp2-008.command`
- `PL!HS-bp2-008#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp2-008_A01_T03_PL_HS-bp2-008.command`
- `PL!HS-bp2-008#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-008_A01_T04_PL_HS-bp2-008.command`
- `PL!HS-bp2-008#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-008_A01_T05_PL_HS-bp2-008.command`

## PL!HS-bp2-009
- `PL!HS-bp2-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-009_A01_T01_PL_HS-bp2-009.command`
- `PL!HS-bp2-009#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp2-009_A01_T02_PL_HS-bp2-009.command`
- `PL!HS-bp2-009#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp2-009_A01_T03_PL_HS-bp2-009.command`
- `PL!HS-bp2-009#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-009_A01_T04_PL_HS-bp2-009.command`
- `PL!HS-bp2-009#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-009_A01_T05_PL_HS-bp2-009.command`
- `PL!HS-bp2-009#A01#T06` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-009_A01_T06_PL_HS-bp2-009.command`
- `PL!HS-bp2-009#A01#T07` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-009_A01_T07_PL_HS-bp2-009.command`

## PL!HS-bp2-010
- `PL!HS-bp2-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-010_A01_T01_PL_HS-bp2-010.command`
- `PL!HS-bp2-010#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-010_A01_T02_PL_HS-bp2-010.command`
- `PL!HS-bp2-010#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-010_A01_T03_PL_HS-bp2-010.command`

## PL!HS-bp2-011
- `PL!HS-bp2-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-011_A01_T01_PL_HS-bp2-011.command`

## PL!HS-bp2-012
- `PL!HS-bp2-012#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-012_A01_T01_PL_HS-bp2-012.command`
- `PL!HS-bp2-012#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp2-012_A01_T02_PL_HS-bp2-012.command`
- `PL!HS-bp2-012#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp2-012_A01_T03_PL_HS-bp2-012.command`

## PL!HS-bp2-013
- `PL!HS-bp2-013#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-013_A01_T01_PL_HS-bp2-013.command`
- `PL!HS-bp2-013#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp2-013_A01_T02_PL_HS-bp2-013.command`
- `PL!HS-bp2-013#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp2-013_A01_T03_PL_HS-bp2-013.command`

## PL!HS-bp2-014
- `PL!HS-bp2-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-014_A01_T01_PL_HS-bp2-014.command`
- `PL!HS-bp2-014#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-014_A01_T02_PL_HS-bp2-014.command`
- `PL!HS-bp2-014#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-014_A01_T03_PL_HS-bp2-014.command`

## PL!HS-bp2-015
- `PL!HS-bp2-015#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-015_A01_T01_PL_HS-bp2-015.command`
- `PL!HS-bp2-015#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp2-015_A01_T02_PL_HS-bp2-015.command`
- `PL!HS-bp2-015#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp2-015_A01_T03_PL_HS-bp2-015.command`

## PL!HS-bp2-016
- `PL!HS-bp2-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-016_A01_T01_PL_HS-bp2-016.command`
- `PL!HS-bp2-016#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-016_A01_T02_PL_HS-bp2-016.command`
- `PL!HS-bp2-016#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-016_A01_T03_PL_HS-bp2-016.command`

## PL!HS-bp2-017
- `PL!HS-bp2-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-017_A01_T01_PL_HS-bp2-017.command`
- `PL!HS-bp2-017#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp2-017_A01_T02_PL_HS-bp2-017.command`
- `PL!HS-bp2-017#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp2-017_A01_T03_PL_HS-bp2-017.command`

## PL!HS-bp2-018
- `PL!HS-bp2-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-018_A01_T01_PL_HS-bp2-018.command`
- `PL!HS-bp2-018#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp2-018_A01_T02_PL_HS-bp2-018.command`
- `PL!HS-bp2-018#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp2-018_A01_T03_PL_HS-bp2-018.command`
- `PL!HS-bp2-018#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp2-018_A01_T04_PL_HS-bp2-018.command`
- `PL!HS-bp2-018#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp2-018_A01_T05_PL_HS-bp2-018.command`

## PL!HS-bp2-019
- `PL!HS-bp2-019#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-019_A01_T01_PL_HS-bp2-019.command`
- `PL!HS-bp2-019#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-019_A01_T02_PL_HS-bp2-019.command`
- `PL!HS-bp2-019#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-019_A01_T03_PL_HS-bp2-019.command`
- `PL!HS-bp2-019#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp2-019_A01_T04_PL_HS-bp2-019.command`
- `PL!HS-bp2-019#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp2-019_A01_T05_PL_HS-bp2-019.command`
- `PL!HS-bp2-019#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-019_A01_T06_PL_HS-bp2-019.command`

## PL!HS-bp2-020
- `PL!HS-bp2-020#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-020_A02_T01_PL_HS-bp2-020.command`
- `PL!HS-bp2-020#A02#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-020_A02_T02_PL_HS-bp2-020.command`

## PL!HS-bp2-021
- `PL!HS-bp2-021#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-021_A01_T01_PL_HS-bp2-021.command`
- `PL!HS-bp2-021#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-021_A01_T02_PL_HS-bp2-021.command`
- `PL!HS-bp2-021#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-021_A01_T03_PL_HS-bp2-021.command`
- `PL!HS-bp2-021#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-021_A01_T04_PL_HS-bp2-021.command`

## PL!HS-bp2-022
- `PL!HS-bp2-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-022_A01_T01_PL_HS-bp2-022.command`
- `PL!HS-bp2-022#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-022_A01_T02_PL_HS-bp2-022.command`
- `PL!HS-bp2-022#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-022_A01_T03_PL_HS-bp2-022.command`
- `PL!HS-bp2-022#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-022_A01_T04_PL_HS-bp2-022.command`

## PL!HS-bp2-023
- `PL!HS-bp2-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-023_A01_T01_PL_HS-bp2-023.command`
- `PL!HS-bp2-023#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-023_A01_T02_PL_HS-bp2-023.command`
- `PL!HS-bp2-023#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-023_A01_T03_PL_HS-bp2-023.command`
- `PL!HS-bp2-023#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-023_A01_T04_PL_HS-bp2-023.command`

## PL!HS-bp2-024
- `PL!HS-bp2-024#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-024_A01_T01_PL_HS-bp2-024.command`
- `PL!HS-bp2-024#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-024_A01_T02_PL_HS-bp2-024.command`
- `PL!HS-bp2-024#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-024_A01_T03_PL_HS-bp2-024.command`
- `PL!HS-bp2-024#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-024_A01_T04_PL_HS-bp2-024.command`

## PL!HS-bp2-025
- `PL!HS-bp2-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-025_A01_T01_PL_HS-bp2-025.command`
- `PL!HS-bp2-025#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-025_A01_T02_PL_HS-bp2-025.command`
- `PL!HS-bp2-025#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-025_A01_T03_PL_HS-bp2-025.command`
- `PL!HS-bp2-025#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-025_A01_T04_PL_HS-bp2-025.command`

## PL!HS-bp2-026
- `PL!HS-bp2-026#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp2-026_A01_T01_PL_HS-bp2-026.command`
- `PL!HS-bp2-026#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp2-026_A01_T02_PL_HS-bp2-026.command`
- `PL!HS-bp2-026#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp2-026_A01_T03_PL_HS-bp2-026.command`
- `PL!HS-bp2-026#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp2-026_A01_T04_PL_HS-bp2-026.command`

## PL!HS-bp5-001
- `PL!HS-bp5-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-001_A01_T01_PL_HS-bp5-001.command`
- `PL!HS-bp5-001#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp5-001_A01_T02_PL_HS-bp5-001.command`
- `PL!HS-bp5-001#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp5-001_A01_T03_PL_HS-bp5-001.command`
- `PL!HS-bp5-001#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp5-001_A01_T04_PL_HS-bp5-001.command`
- `PL!HS-bp5-001#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp5-001_A01_T05_PL_HS-bp5-001.command`

## PL!HS-bp5-002
- `PL!HS-bp5-002#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-002_A01_T01_PL_HS-bp5-002.command`
- `PL!HS-bp5-002#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_HS-bp5-002_A01_T02_PL_HS-bp5-002.command`
- `PL!HS-bp5-002#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_HS-bp5-002_A01_T03_PL_HS-bp5-002.command`
- `PL!HS-bp5-002#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-bp5-002_A01_T04_PL_HS-bp5-002.command`
- `PL!HS-bp5-002#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-bp5-002_A01_T05_PL_HS-bp5-002.command`
- `PL!HS-bp5-002#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-002_A02_T01_PL_HS-bp5-002.command`
- `PL!HS-bp5-002#A02#T02` 起動 / 回数制限超過 / command: `debug_commands/PL_HS-bp5-002_A02_T02_PL_HS-bp5-002.command`
- `PL!HS-bp5-002#A02#T03` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp5-002_A02_T03_PL_HS-bp5-002.command`

## PL!HS-bp5-003
- `PL!HS-bp5-003#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-003_A01_T01_PL_HS-bp5-003.command`
- `PL!HS-bp5-003#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp5-003_A01_T02_PL_HS-bp5-003.command`
- `PL!HS-bp5-003#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp5-003_A01_T03_PL_HS-bp5-003.command`
- `PL!HS-bp5-003#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-003_A02_T01_PL_HS-bp5-003.command`
- `PL!HS-bp5-003#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp5-003_A02_T02_PL_HS-bp5-003.command`
- `PL!HS-bp5-003#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp5-003_A02_T03_PL_HS-bp5-003.command`
- `PL!HS-bp5-003#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp5-003_A02_T04_PL_HS-bp5-003.command`
- `PL!HS-bp5-003#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp5-003_A02_T05_PL_HS-bp5-003.command`
- `PL!HS-bp5-003#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-003_A02_T06_PL_HS-bp5-003.command`

## PL!HS-bp5-004
- `PL!HS-bp5-004#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-004_A01_T01_PL_HS-bp5-004.command`
- `PL!HS-bp5-004#A01#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-bp5-004_A01_T02_PL_HS-bp5-004.command`
- `PL!HS-bp5-004#A01#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-bp5-004_A01_T03_PL_HS-bp5-004.command`

## PL!HS-bp5-005
- `PL!HS-bp5-005#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-005_A01_T01_PL_HS-bp5-005.command`
- `PL!HS-bp5-005#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp5-005_A01_T02_PL_HS-bp5-005.command`
- `PL!HS-bp5-005#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp5-005_A01_T03_PL_HS-bp5-005.command`
- `PL!HS-bp5-005#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp5-005_A01_T04_PL_HS-bp5-005.command`
- `PL!HS-bp5-005#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp5-005_A01_T05_PL_HS-bp5-005.command`
- `PL!HS-bp5-005#A01#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp5-005_A01_T06_PL_HS-bp5-005.command`
- `PL!HS-bp5-005#A01#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp5-005_A01_T07_PL_HS-bp5-005.command`
- `PL!HS-bp5-005#A01#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-005_A01_T08_PL_HS-bp5-005.command`

## PL!HS-bp5-006
- `PL!HS-bp5-006#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-006_A01_T01_PL_HS-bp5-006.command`
- `PL!HS-bp5-006#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp5-006_A01_T02_PL_HS-bp5-006.command`
- `PL!HS-bp5-006#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp5-006_A01_T03_PL_HS-bp5-006.command`
- `PL!HS-bp5-006#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp5-006_A01_T04_PL_HS-bp5-006.command`
- `PL!HS-bp5-006#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp5-006_A01_T05_PL_HS-bp5-006.command`
- `PL!HS-bp5-006#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-006_A01_T06_PL_HS-bp5-006.command`

## PL!HS-bp5-007
- `PL!HS-bp5-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-007_A01_T01_PL_HS-bp5-007.command`
- `PL!HS-bp5-007#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp5-007_A01_T02_PL_HS-bp5-007.command`
- `PL!HS-bp5-007#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp5-007_A01_T03_PL_HS-bp5-007.command`
- `PL!HS-bp5-007#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-007_A02_T01_PL_HS-bp5-007.command`
- `PL!HS-bp5-007#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_HS-bp5-007_A02_T02_PL_HS-bp5-007.command`
- `PL!HS-bp5-007#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_HS-bp5-007_A02_T03_PL_HS-bp5-007.command`
- `PL!HS-bp5-007#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-bp5-007_A02_T04_PL_HS-bp5-007.command`
- `PL!HS-bp5-007#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-bp5-007_A02_T05_PL_HS-bp5-007.command`

## PL!HS-bp5-008
- `PL!HS-bp5-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-008_A01_T01_PL_HS-bp5-008.command`
- `PL!HS-bp5-008#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp5-008_A01_T02_PL_HS-bp5-008.command`
- `PL!HS-bp5-008#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp5-008_A01_T03_PL_HS-bp5-008.command`

## PL!HS-bp5-011
- `PL!HS-bp5-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-011_A01_T01_PL_HS-bp5-011.command`

## PL!HS-bp5-013
- `PL!HS-bp5-013#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-013_A01_T01_PL_HS-bp5-013.command`
- `PL!HS-bp5-013#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp5-013_A01_T02_PL_HS-bp5-013.command`
- `PL!HS-bp5-013#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp5-013_A01_T03_PL_HS-bp5-013.command`
- `PL!HS-bp5-013#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp5-013_A01_T04_PL_HS-bp5-013.command`
- `PL!HS-bp5-013#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp5-013_A01_T05_PL_HS-bp5-013.command`
- `PL!HS-bp5-013#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-013_A01_T06_PL_HS-bp5-013.command`

## PL!HS-bp5-014
- `PL!HS-bp5-014#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-014_A01_T01_PL_HS-bp5-014.command`
- `PL!HS-bp5-014#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp5-014_A01_T02_PL_HS-bp5-014.command`
- `PL!HS-bp5-014#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp5-014_A01_T03_PL_HS-bp5-014.command`
- `PL!HS-bp5-014#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_HS-bp5-014_A01_T04_PL_HS-bp5-014.command`
- `PL!HS-bp5-014#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp5-014_A01_T05_PL_HS-bp5-014.command`
- `PL!HS-bp5-014#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_HS-bp5-014_A01_T06_PL_HS-bp5-014.command`
- `PL!HS-bp5-014#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp5-014_A01_T07_PL_HS-bp5-014.command`

## PL!HS-bp5-016
- `PL!HS-bp5-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-016_A01_T01_PL_HS-bp5-016.command`
- `PL!HS-bp5-016#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp5-016_A01_T02_PL_HS-bp5-016.command`
- `PL!HS-bp5-016#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp5-016_A01_T03_PL_HS-bp5-016.command`
- `PL!HS-bp5-016#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp5-016_A01_T04_PL_HS-bp5-016.command`
- `PL!HS-bp5-016#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp5-016_A01_T05_PL_HS-bp5-016.command`

## PL!HS-bp5-017
- `PL!HS-bp5-017#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-017_A01_T01_PL_HS-bp5-017.command`
- `PL!HS-bp5-017#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp5-017_A01_T02_PL_HS-bp5-017.command`
- `PL!HS-bp5-017#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp5-017_A01_T03_PL_HS-bp5-017.command`
- `PL!HS-bp5-017#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp5-017_A01_T04_PL_HS-bp5-017.command`
- `PL!HS-bp5-017#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp5-017_A01_T05_PL_HS-bp5-017.command`
- `PL!HS-bp5-017#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-017_A01_T06_PL_HS-bp5-017.command`

## PL!HS-bp5-018
- `PL!HS-bp5-018#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-018_A02_T01_PL_HS-bp5-018.command`
- `PL!HS-bp5-018#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp5-018_A02_T02_PL_HS-bp5-018.command`
- `PL!HS-bp5-018#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp5-018_A02_T03_PL_HS-bp5-018.command`
- `PL!HS-bp5-018#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-018_A02_T04_PL_HS-bp5-018.command`

## PL!HS-bp5-019
- `PL!HS-bp5-019#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-019_A01_T01_PL_HS-bp5-019.command`
- `PL!HS-bp5-019#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-019_A01_T02_PL_HS-bp5-019.command`

## PL!HS-bp5-020
- `PL!HS-bp5-020#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-020_A01_T01_PL_HS-bp5-020.command`
- `PL!HS-bp5-020#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp5-020_A01_T02_PL_HS-bp5-020.command`
- `PL!HS-bp5-020#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp5-020_A01_T03_PL_HS-bp5-020.command`
- `PL!HS-bp5-020#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-020_A01_T04_PL_HS-bp5-020.command`

## PL!HS-bp5-021
- `PL!HS-bp5-021#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-021_A01_T01_PL_HS-bp5-021.command`
- `PL!HS-bp5-021#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp5-021_A01_T02_PL_HS-bp5-021.command`
- `PL!HS-bp5-021#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp5-021_A01_T03_PL_HS-bp5-021.command`
- `PL!HS-bp5-021#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-021_A01_T04_PL_HS-bp5-021.command`
- `PL!HS-bp5-021#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp5-021_A02_T01_PL_HS-bp5-021.command`
- `PL!HS-bp5-021#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp5-021_A02_T02_PL_HS-bp5-021.command`
- `PL!HS-bp5-021#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp5-021_A02_T03_PL_HS-bp5-021.command`
- `PL!HS-bp5-021#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp5-021_A02_T04_PL_HS-bp5-021.command`

## PL!HS-bp6-001
- `PL!HS-bp6-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-001_A01_T01_PL_HS-bp6-001.command`
- `PL!HS-bp6-001#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-001_A02_T01_PL_HS-bp6-001.command`
- `PL!HS-bp6-001#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-001_A02_T02_PL_HS-bp6-001.command`

## PL!HS-bp6-002
- `PL!HS-bp6-002#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-002_A01_T01_PL_HS-bp6-002.command`
- `PL!HS-bp6-002#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-002_A01_T02_PL_HS-bp6-002.command`
- `PL!HS-bp6-002#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_HS-bp6-002_A01_T03_PL_HS-bp6-002.command`
- `PL!HS-bp6-002#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-bp6-002_A01_T04_PL_HS-bp6-002.command`
- `PL!HS-bp6-002#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-bp6-002_A01_T05_PL_HS-bp6-002.command`

## PL!HS-bp6-003
- `PL!HS-bp6-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-003_A01_T01_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp6-003_A01_T02_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp6-003_A01_T03_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-003_A01_T04_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-003_A01_T05_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-003_A02_T01_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-003_A02_T02_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-003_A02_T03_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp6-003_A02_T04_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp6-003_A02_T05_PL_HS-bp6-003.command`
- `PL!HS-bp6-003#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-003_A02_T06_PL_HS-bp6-003.command`

## PL!HS-bp6-004
- `PL!HS-bp6-004#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-004_A01_T01_PL_HS-bp6-004.command`
- `PL!HS-bp6-004#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-004_A02_T01_PL_HS-bp6-004.command`
- `PL!HS-bp6-004#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-004_A02_T02_PL_HS-bp6-004.command`
- `PL!HS-bp6-004#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp6-004_A02_T03_PL_HS-bp6-004.command`
- `PL!HS-bp6-004#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-004_A02_T04_PL_HS-bp6-004.command`
- `PL!HS-bp6-004#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-004_A02_T05_PL_HS-bp6-004.command`
- `PL!HS-bp6-004#A02#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp6-004_A02_T06_PL_HS-bp6-004.command`
- `PL!HS-bp6-004#A02#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp6-004_A02_T07_PL_HS-bp6-004.command`
- `PL!HS-bp6-004#A02#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-004_A02_T08_PL_HS-bp6-004.command`

## PL!HS-bp6-005
- `PL!HS-bp6-005#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-005_A01_T01_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-005_A01_T02_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp6-005_A01_T03_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-005_A01_T04_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-005_A01_T05_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A01#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp6-005_A01_T06_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A01#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp6-005_A01_T07_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A01#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-005_A01_T08_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-005_A02_T01_PL_HS-bp6-005.command`
- `PL!HS-bp6-005#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-005_A02_T02_PL_HS-bp6-005.command`

## PL!HS-bp6-006
- `PL!HS-bp6-006#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-006_A01_T01_PL_HS-bp6-006.command`
- `PL!HS-bp6-006#A01#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-bp6-006_A01_T02_PL_HS-bp6-006.command`
- `PL!HS-bp6-006#A01#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-bp6-006_A01_T03_PL_HS-bp6-006.command`
- `PL!HS-bp6-006#A03#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-006_A03_T01_PL_HS-bp6-006.command`
- `PL!HS-bp6-006#A03#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-006_A03_T02_PL_HS-bp6-006.command`

## PL!HS-bp6-008
- `PL!HS-bp6-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-008_A01_T01_PL_HS-bp6-008.command`
- `PL!HS-bp6-008#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-008_A02_T01_PL_HS-bp6-008.command`
- `PL!HS-bp6-008#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-008_A02_T02_PL_HS-bp6-008.command`
- `PL!HS-bp6-008#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp6-008_A02_T03_PL_HS-bp6-008.command`
- `PL!HS-bp6-008#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-008_A02_T04_PL_HS-bp6-008.command`

## PL!HS-bp6-009
- `PL!HS-bp6-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-009_A01_T01_PL_HS-bp6-009.command`
- `PL!HS-bp6-009#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-009_A01_T02_PL_HS-bp6-009.command`
- `PL!HS-bp6-009#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp6-009_A01_T03_PL_HS-bp6-009.command`
- `PL!HS-bp6-009#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-009_A01_T04_PL_HS-bp6-009.command`
- `PL!HS-bp6-009#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-009_A01_T05_PL_HS-bp6-009.command`
- `PL!HS-bp6-009#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-009_A01_T06_PL_HS-bp6-009.command`

## PL!HS-bp6-010
- `PL!HS-bp6-010#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-010_A01_T01_PL_HS-bp6-010.command`
- `PL!HS-bp6-010#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-010_A01_T02_PL_HS-bp6-010.command`
- `PL!HS-bp6-010#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-010_A01_T03_PL_HS-bp6-010.command`
- `PL!HS-bp6-010#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp6-010_A01_T04_PL_HS-bp6-010.command`
- `PL!HS-bp6-010#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp6-010_A01_T05_PL_HS-bp6-010.command`
- `PL!HS-bp6-010#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-010_A01_T06_PL_HS-bp6-010.command`

## PL!HS-bp6-011
- `PL!HS-bp6-011#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-011_A01_T01_PL_HS-bp6-011.command`
- `PL!HS-bp6-011#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-bp6-011_A01_T02_PL_HS-bp6-011.command`
- `PL!HS-bp6-011#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-bp6-011_A01_T03_PL_HS-bp6-011.command`
- `PL!HS-bp6-011#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_HS-bp6-011_A01_T04_PL_HS-bp6-011.command`
- `PL!HS-bp6-011#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp6-011_A01_T05_PL_HS-bp6-011.command`

## PL!HS-bp6-012
- `PL!HS-bp6-012#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-012_A01_T01_PL_HS-bp6-012.command`
- `PL!HS-bp6-012#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp6-012_A01_T02_PL_HS-bp6-012.command`
- `PL!HS-bp6-012#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp6-012_A01_T03_PL_HS-bp6-012.command`

## PL!HS-bp6-013
- `PL!HS-bp6-013#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-013_A01_T01_PL_HS-bp6-013.command`

## PL!HS-bp6-015
- `PL!HS-bp6-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-015_A01_T01_PL_HS-bp6-015.command`
- `PL!HS-bp6-015#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-bp6-015_A01_T02_PL_HS-bp6-015.command`
- `PL!HS-bp6-015#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-bp6-015_A01_T03_PL_HS-bp6-015.command`

## PL!HS-bp6-016
- `PL!HS-bp6-016#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-016_A01_T01_PL_HS-bp6-016.command`
- `PL!HS-bp6-016#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-bp6-016_A01_T02_PL_HS-bp6-016.command`
- `PL!HS-bp6-016#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-bp6-016_A01_T03_PL_HS-bp6-016.command`
- `PL!HS-bp6-016#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_HS-bp6-016_A01_T04_PL_HS-bp6-016.command`
- `PL!HS-bp6-016#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp6-016_A01_T05_PL_HS-bp6-016.command`

## PL!HS-bp6-017
- `PL!HS-bp6-017#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-017_A01_T01_PL_HS-bp6-017.command`
- `PL!HS-bp6-017#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp6-017_A01_T02_PL_HS-bp6-017.command`
- `PL!HS-bp6-017#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp6-017_A01_T03_PL_HS-bp6-017.command`
- `PL!HS-bp6-017#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-017_A01_T04_PL_HS-bp6-017.command`
- `PL!HS-bp6-017#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-017_A01_T05_PL_HS-bp6-017.command`

## PL!HS-bp6-018
- `PL!HS-bp6-018#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-018_A01_T01_PL_HS-bp6-018.command`
- `PL!HS-bp6-018#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp6-018_A01_T02_PL_HS-bp6-018.command`
- `PL!HS-bp6-018#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp6-018_A01_T03_PL_HS-bp6-018.command`
- `PL!HS-bp6-018#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-018_A01_T04_PL_HS-bp6-018.command`
- `PL!HS-bp6-018#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-018_A01_T05_PL_HS-bp6-018.command`

## PL!HS-bp6-019
- `PL!HS-bp6-019#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-019_A01_T01_PL_HS-bp6-019.command`
- `PL!HS-bp6-019#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp6-019_A01_T02_PL_HS-bp6-019.command`
- `PL!HS-bp6-019#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp6-019_A01_T03_PL_HS-bp6-019.command`

## PL!HS-bp6-020
- `PL!HS-bp6-020#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-020_A01_T01_PL_HS-bp6-020.command`

## PL!HS-bp6-022
- `PL!HS-bp6-022#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-022_A01_T01_PL_HS-bp6-022.command`
- `PL!HS-bp6-022#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-bp6-022_A01_T02_PL_HS-bp6-022.command`
- `PL!HS-bp6-022#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-bp6-022_A01_T03_PL_HS-bp6-022.command`

## PL!HS-bp6-025
- `PL!HS-bp6-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-025_A01_T01_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-025_A01_T02_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-025_A01_T03_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-bp6-025_A01_T04_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-bp6-025_A01_T05_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-025_A01_T06_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-025_A02_T01_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-025_A02_T02_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-bp6-025_A02_T03_PL_HS-bp6-025.command`
- `PL!HS-bp6-025#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-025_A02_T04_PL_HS-bp6-025.command`

## PL!HS-bp6-027
- `PL!HS-bp6-027#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-027_A01_T01_PL_HS-bp6-027.command`
- `PL!HS-bp6-027#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-bp6-027_A01_T02_PL_HS-bp6-027.command`
- `PL!HS-bp6-027#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-bp6-027_A01_T03_PL_HS-bp6-027.command`
- `PL!HS-bp6-027#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-027_A01_T04_PL_HS-bp6-027.command`
- `PL!HS-bp6-027#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-027_A01_T05_PL_HS-bp6-027.command`
- `PL!HS-bp6-027#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_HS-bp6-027_A01_T06_PL_HS-bp6-027.command`
- `PL!HS-bp6-027#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-bp6-027_A01_T07_PL_HS-bp6-027.command`

## PL!HS-bp6-028
- `PL!HS-bp6-028#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-028_A01_T01_PL_HS-bp6-028.command`
- `PL!HS-bp6-028#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-028_A01_T02_PL_HS-bp6-028.command`
- `PL!HS-bp6-028#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-bp6-028_A01_T03_PL_HS-bp6-028.command`
- `PL!HS-bp6-028#A01#T04` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-028_A01_T04_PL_HS-bp6-028.command`
- `PL!HS-bp6-028#A01#T05` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-028_A01_T05_PL_HS-bp6-028.command`
- `PL!HS-bp6-028#A01#T06` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-028_A01_T06_PL_HS-bp6-028.command`

## PL!HS-bp6-029
- `PL!HS-bp6-029#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-029_A01_T01_PL_HS-bp6-029.command`
- `PL!HS-bp6-029#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-029_A01_T02_PL_HS-bp6-029.command`
- `PL!HS-bp6-029#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp6-029_A01_T03_PL_HS-bp6-029.command`
- `PL!HS-bp6-029#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-029_A01_T04_PL_HS-bp6-029.command`

## PL!HS-bp6-030
- `PL!HS-bp6-030#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-030_A01_T01_PL_HS-bp6-030.command`
- `PL!HS-bp6-030#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-030_A01_T02_PL_HS-bp6-030.command`

## PL!HS-bp6-031
- `PL!HS-bp6-031#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-031_A01_T01_PL_HS-bp6-031.command`
- `PL!HS-bp6-031#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-bp6-031_A01_T02_PL_HS-bp6-031.command`
- `PL!HS-bp6-031#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-bp6-031_A01_T03_PL_HS-bp6-031.command`
- `PL!HS-bp6-031#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-bp6-031_A01_T04_PL_HS-bp6-031.command`
- `PL!HS-bp6-031#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-bp6-031_A01_T05_PL_HS-bp6-031.command`
- `PL!HS-bp6-031#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-031_A01_T06_PL_HS-bp6-031.command`

## PL!HS-bp6-032
- `PL!HS-bp6-032#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-bp6-032_A01_T01_PL_HS-bp6-032.command`
- `PL!HS-bp6-032#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-bp6-032_A01_T02_PL_HS-bp6-032.command`

## PL!HS-cl1-001
- `PL!HS-cl1-001#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-001_A01_T01_PL_HS-cl1-001.command`
- `PL!HS-cl1-001#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-cl1-001_A01_T02_PL_HS-cl1-001.command`

## PL!HS-cl1-002
- `PL!HS-cl1-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-002_A01_T01_PL_HS-cl1-002.command`
- `PL!HS-cl1-002#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-cl1-002_A01_T02_PL_HS-cl1-002.command`
- `PL!HS-cl1-002#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-cl1-002_A01_T03_PL_HS-cl1-002.command`

## PL!HS-cl1-003
- `PL!HS-cl1-003#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-003_A01_T01_PL_HS-cl1-003.command`
- `PL!HS-cl1-003#A01#T02` 起動 / 任意処理を実行 / command: `debug_commands/PL_HS-cl1-003_A01_T02_PL_HS-cl1-003.command`
- `PL!HS-cl1-003#A01#T03` 起動 / 任意処理を実行しない / command: `debug_commands/PL_HS-cl1-003_A01_T03_PL_HS-cl1-003.command`
- `PL!HS-cl1-003#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-cl1-003_A01_T04_PL_HS-cl1-003.command`
- `PL!HS-cl1-003#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-cl1-003_A01_T05_PL_HS-cl1-003.command`
- `PL!HS-cl1-003#A01#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_HS-cl1-003_A01_T06_PL_HS-cl1-003.command`
- `PL!HS-cl1-003#A01#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_HS-cl1-003_A01_T07_PL_HS-cl1-003.command`

## PL!HS-cl1-005
- `PL!HS-cl1-005#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-005_A01_T01_PL_HS-cl1-005.command`
- `PL!HS-cl1-005#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-cl1-005_A01_T02_PL_HS-cl1-005.command`
- `PL!HS-cl1-005#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-cl1-005_A01_T03_PL_HS-cl1-005.command`
- `PL!HS-cl1-005#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-cl1-005_A01_T04_PL_HS-cl1-005.command`
- `PL!HS-cl1-005#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-cl1-005_A01_T05_PL_HS-cl1-005.command`
- `PL!HS-cl1-005#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-cl1-005_A01_T06_PL_HS-cl1-005.command`

## PL!HS-cl1-006
- `PL!HS-cl1-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-006_A01_T01_PL_HS-cl1-006.command`
- `PL!HS-cl1-006#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-cl1-006_A01_T02_PL_HS-cl1-006.command`
- `PL!HS-cl1-006#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-cl1-006_A01_T03_PL_HS-cl1-006.command`

## PL!HS-cl1-007
- `PL!HS-cl1-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-007_A01_T01_PL_HS-cl1-007.command`
- `PL!HS-cl1-007#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-cl1-007_A01_T02_PL_HS-cl1-007.command`
- `PL!HS-cl1-007#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-cl1-007_A01_T03_PL_HS-cl1-007.command`

## PL!HS-cl1-008
- `PL!HS-cl1-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-008_A01_T01_PL_HS-cl1-008.command`
- `PL!HS-cl1-008#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-cl1-008_A01_T02_PL_HS-cl1-008.command`
- `PL!HS-cl1-008#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-cl1-008_A01_T03_PL_HS-cl1-008.command`

## PL!HS-cl1-009
- `PL!HS-cl1-009#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-009_A01_T01_PL_HS-cl1-009.command`
- `PL!HS-cl1-009#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-cl1-009_A01_T02_PL_HS-cl1-009.command`

## PL!HS-cl1-010
- `PL!HS-cl1-010#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-010_A01_T01_PL_HS-cl1-010.command`
- `PL!HS-cl1-010#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-cl1-010_A01_T02_PL_HS-cl1-010.command`
- `PL!HS-cl1-010#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-cl1-010_A01_T03_PL_HS-cl1-010.command`
- `PL!HS-cl1-010#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-cl1-010_A01_T04_PL_HS-cl1-010.command`

## PL!HS-cl1-012
- `PL!HS-cl1-012#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-cl1-012_A01_T01_PL_HS-cl1-012.command`
- `PL!HS-cl1-012#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-cl1-012_A01_T02_PL_HS-cl1-012.command`
- `PL!HS-cl1-012#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-cl1-012_A01_T03_PL_HS-cl1-012.command`
- `PL!HS-cl1-012#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-cl1-012_A01_T04_PL_HS-cl1-012.command`

## PL!HS-pb1-001
- `PL!HS-pb1-001#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-001_A02_T01_PL_HS-pb1-001.command`
- `PL!HS-pb1-001#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-001_A02_T02_PL_HS-pb1-001.command`
- `PL!HS-pb1-001#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-001_A02_T03_PL_HS-pb1-001.command`
- `PL!HS-pb1-001#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-pb1-001_A02_T04_PL_HS-pb1-001.command`
- `PL!HS-pb1-001#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-pb1-001_A02_T05_PL_HS-pb1-001.command`
- `PL!HS-pb1-001#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-001_A02_T06_PL_HS-pb1-001.command`

## PL!HS-pb1-002
- `PL!HS-pb1-002#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-002_A02_T01_PL_HS-pb1-002.command`
- `PL!HS-pb1-002#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-002_A02_T02_PL_HS-pb1-002.command`
- `PL!HS-pb1-002#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-002_A02_T03_PL_HS-pb1-002.command`
- `PL!HS-pb1-002#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-002_A02_T04_PL_HS-pb1-002.command`

## PL!HS-pb1-003
- `PL!HS-pb1-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-003_A01_T01_PL_HS-pb1-003.command`
- `PL!HS-pb1-003#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-003_A01_T02_PL_HS-pb1-003.command`
- `PL!HS-pb1-003#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-003_A01_T03_PL_HS-pb1-003.command`

## PL!HS-pb1-004
- `PL!HS-pb1-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-004_A01_T01_PL_HS-pb1-004.command`
- `PL!HS-pb1-004#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-pb1-004_A01_T02_PL_HS-pb1-004.command`
- `PL!HS-pb1-004#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-pb1-004_A01_T03_PL_HS-pb1-004.command`

## PL!HS-pb1-005
- `PL!HS-pb1-005#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-005_A01_T01_PL_HS-pb1-005.command`
- `PL!HS-pb1-005#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-005_A01_T02_PL_HS-pb1-005.command`
- `PL!HS-pb1-005#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-pb1-005_A01_T03_PL_HS-pb1-005.command`
- `PL!HS-pb1-005#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-005_A01_T04_PL_HS-pb1-005.command`
- `PL!HS-pb1-005#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-005_A01_T05_PL_HS-pb1-005.command`
- `PL!HS-pb1-005#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-005_A01_T06_PL_HS-pb1-005.command`

## PL!HS-pb1-006
- `PL!HS-pb1-006#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-006_A01_T01_PL_HS-pb1-006.command`
- `PL!HS-pb1-006#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-006_A01_T02_PL_HS-pb1-006.command`
- `PL!HS-pb1-006#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-pb1-006_A01_T03_PL_HS-pb1-006.command`
- `PL!HS-pb1-006#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-006_A01_T04_PL_HS-pb1-006.command`
- `PL!HS-pb1-006#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-006_A01_T05_PL_HS-pb1-006.command`
- `PL!HS-pb1-006#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-006_A01_T06_PL_HS-pb1-006.command`

## PL!HS-pb1-007
- `PL!HS-pb1-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-007_A01_T01_PL_HS-pb1-007.command`
- `PL!HS-pb1-007#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-pb1-007_A01_T02_PL_HS-pb1-007.command`
- `PL!HS-pb1-007#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-pb1-007_A01_T03_PL_HS-pb1-007.command`

## PL!HS-pb1-008
- `PL!HS-pb1-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-008_A01_T01_PL_HS-pb1-008.command`

## PL!HS-pb1-009
- `PL!HS-pb1-009#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-009_A02_T01_PL_HS-pb1-009.command`
- `PL!HS-pb1-009#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-009_A02_T02_PL_HS-pb1-009.command`
- `PL!HS-pb1-009#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-pb1-009_A02_T03_PL_HS-pb1-009.command`
- `PL!HS-pb1-009#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-009_A02_T04_PL_HS-pb1-009.command`

## PL!HS-pb1-010
- `PL!HS-pb1-010#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-010_A01_T01_PL_HS-pb1-010.command`
- `PL!HS-pb1-010#A01#T02` 登場 / ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-010_A01_T02_PL_HS-pb1-010.command`
- `PL!HS-pb1-010#A01#T03` 登場 / ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-pb1-010_A01_T03_PL_HS-pb1-010.command`

## PL!HS-pb1-011
- `PL!HS-pb1-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-011_A01_T01_PL_HS-pb1-011.command`
- `PL!HS-pb1-011#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-pb1-011_A01_T02_PL_HS-pb1-011.command`
- `PL!HS-pb1-011#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-pb1-011_A01_T03_PL_HS-pb1-011.command`

## PL!HS-pb1-012
- `PL!HS-pb1-012#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-012_A01_T01_PL_HS-pb1-012.command`
- `PL!HS-pb1-012#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-pb1-012_A01_T02_PL_HS-pb1-012.command`
- `PL!HS-pb1-012#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-pb1-012_A01_T03_PL_HS-pb1-012.command`
- `PL!HS-pb1-012#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-012_A01_T04_PL_HS-pb1-012.command`
- `PL!HS-pb1-012#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-012_A01_T05_PL_HS-pb1-012.command`

## PL!HS-pb1-013
- `PL!HS-pb1-013#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-013_A01_T01_PL_HS-pb1-013.command`
- `PL!HS-pb1-013#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-013_A01_T02_PL_HS-pb1-013.command`
- `PL!HS-pb1-013#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-013_A01_T03_PL_HS-pb1-013.command`
- `PL!HS-pb1-013#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-013_A01_T04_PL_HS-pb1-013.command`
- `PL!HS-pb1-013#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-013_A02_T01_PL_HS-pb1-013.command`
- `PL!HS-pb1-013#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-013_A02_T02_PL_HS-pb1-013.command`
- `PL!HS-pb1-013#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-pb1-013_A02_T03_PL_HS-pb1-013.command`
- `PL!HS-pb1-013#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-013_A02_T04_PL_HS-pb1-013.command`

## PL!HS-pb1-014
- `PL!HS-pb1-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-014_A01_T01_PL_HS-pb1-014.command`
- `PL!HS-pb1-014#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-pb1-014_A01_T02_PL_HS-pb1-014.command`
- `PL!HS-pb1-014#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-pb1-014_A01_T03_PL_HS-pb1-014.command`

## PL!HS-pb1-016
- `PL!HS-pb1-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-016_A01_T01_PL_HS-pb1-016.command`
- `PL!HS-pb1-016#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-016_A01_T02_PL_HS-pb1-016.command`
- `PL!HS-pb1-016#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-016_A01_T03_PL_HS-pb1-016.command`

## PL!HS-pb1-018
- `PL!HS-pb1-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-018_A01_T01_PL_HS-pb1-018.command`
- `PL!HS-pb1-018#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-pb1-018_A01_T02_PL_HS-pb1-018.command`
- `PL!HS-pb1-018#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-pb1-018_A01_T03_PL_HS-pb1-018.command`

## PL!HS-pb1-019
- `PL!HS-pb1-019#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-019_A01_T01_PL_HS-pb1-019.command`
- `PL!HS-pb1-019#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-pb1-019_A01_T02_PL_HS-pb1-019.command`
- `PL!HS-pb1-019#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-pb1-019_A01_T03_PL_HS-pb1-019.command`

## PL!HS-pb1-020
- `PL!HS-pb1-020#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-020_A01_T01_PL_HS-pb1-020.command`
- `PL!HS-pb1-020#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-pb1-020_A01_T02_PL_HS-pb1-020.command`
- `PL!HS-pb1-020#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-pb1-020_A01_T03_PL_HS-pb1-020.command`

## PL!HS-pb1-021
- `PL!HS-pb1-021#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-021_A01_T01_PL_HS-pb1-021.command`
- `PL!HS-pb1-021#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-021_A01_T02_PL_HS-pb1-021.command`
- `PL!HS-pb1-021#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-pb1-021_A01_T03_PL_HS-pb1-021.command`
- `PL!HS-pb1-021#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-021_A01_T04_PL_HS-pb1-021.command`

## PL!HS-pb1-022
- `PL!HS-pb1-022#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-022_A01_T01_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-022_A01_T02_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_HS-pb1-022_A01_T03_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-pb1-022_A01_T04_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-pb1-022_A01_T05_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-022_A02_T01_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-022_A02_T02_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_HS-pb1-022_A02_T03_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_HS-pb1-022_A02_T04_PL_HS-pb1-022.command`
- `PL!HS-pb1-022#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_HS-pb1-022_A02_T05_PL_HS-pb1-022.command`

## PL!HS-pb1-024
- `PL!HS-pb1-024#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-024_A01_T01_PL_HS-pb1-024.command`
- `PL!HS-pb1-024#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-024_A01_T02_PL_HS-pb1-024.command`
- `PL!HS-pb1-024#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-024_A01_T03_PL_HS-pb1-024.command`

## PL!HS-pb1-025
- `PL!HS-pb1-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-025_A01_T01_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-025_A01_T02_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-pb1-025_A01_T03_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-025_A01_T04_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-025_A01_T05_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-025_A01_T06_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-025_A02_T01_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-025_A02_T02_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-pb1-025_A02_T03_PL_HS-pb1-025.command`
- `PL!HS-pb1-025#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-025_A02_T04_PL_HS-pb1-025.command`

## PL!HS-pb1-026
- `PL!HS-pb1-026#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-026_A01_T01_PL_HS-pb1-026.command`
- `PL!HS-pb1-026#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-026_A01_T02_PL_HS-pb1-026.command`
- `PL!HS-pb1-026#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-pb1-026_A01_T03_PL_HS-pb1-026.command`
- `PL!HS-pb1-026#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-026_A01_T04_PL_HS-pb1-026.command`

## PL!HS-pb1-027
- `PL!HS-pb1-027#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-027_A01_T01_PL_HS-pb1-027.command`
- `PL!HS-pb1-027#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-027_A01_T02_PL_HS-pb1-027.command`
- `PL!HS-pb1-027#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-pb1-027_A01_T03_PL_HS-pb1-027.command`
- `PL!HS-pb1-027#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-027_A01_T04_PL_HS-pb1-027.command`

## PL!HS-pb1-028
- `PL!HS-pb1-028#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-028_A01_T01_PL_HS-pb1-028.command`
- `PL!HS-pb1-028#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-028_A01_T02_PL_HS-pb1-028.command`

## PL!HS-pb1-029
- `PL!HS-pb1-029#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-029_A01_T01_PL_HS-pb1-029.command`
- `PL!HS-pb1-029#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-pb1-029_A01_T02_PL_HS-pb1-029.command`
- `PL!HS-pb1-029#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-pb1-029_A01_T03_PL_HS-pb1-029.command`
- `PL!HS-pb1-029#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-029_A01_T04_PL_HS-pb1-029.command`

## PL!HS-pb1-030
- `PL!HS-pb1-030#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-pb1-030_A01_T01_PL_HS-pb1-030.command`
- `PL!HS-pb1-030#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-pb1-030_A01_T02_PL_HS-pb1-030.command`
- `PL!HS-pb1-030#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-pb1-030_A01_T03_PL_HS-pb1-030.command`
- `PL!HS-pb1-030#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-pb1-030_A01_T04_PL_HS-pb1-030.command`

## PL!HS-sd1-001
- `PL!HS-sd1-001#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-001_A01_T01_PL_HS-sd1-001.command`
- `PL!HS-sd1-001#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_HS-sd1-001_A01_T02_PL_HS-sd1-001.command`
- `PL!HS-sd1-001#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_HS-sd1-001_A01_T03_PL_HS-sd1-001.command`

## PL!HS-sd1-002
- `PL!HS-sd1-002#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-002_A01_T01_PL_HS-sd1-002.command`
- `PL!HS-sd1-002#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_HS-sd1-002_A01_T02_PL_HS-sd1-002.command`
- `PL!HS-sd1-002#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_HS-sd1-002_A01_T03_PL_HS-sd1-002.command`
- `PL!HS-sd1-002#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-sd1-002_A01_T04_PL_HS-sd1-002.command`
- `PL!HS-sd1-002#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-sd1-002_A01_T05_PL_HS-sd1-002.command`
- `PL!HS-sd1-002#A01#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-002_A01_T06_PL_HS-sd1-002.command`
- `PL!HS-sd1-002#A01#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-002_A01_T07_PL_HS-sd1-002.command`
- `PL!HS-sd1-002#A01#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-sd1-002_A01_T08_PL_HS-sd1-002.command`

## PL!HS-sd1-003
- `PL!HS-sd1-003#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-003_A01_T01_PL_HS-sd1-003.command`
- `PL!HS-sd1-003#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-sd1-003_A01_T02_PL_HS-sd1-003.command`
- `PL!HS-sd1-003#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-sd1-003_A01_T03_PL_HS-sd1-003.command`
- `PL!HS-sd1-003#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-003_A01_T04_PL_HS-sd1-003.command`
- `PL!HS-sd1-003#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-003_A01_T05_PL_HS-sd1-003.command`
- `PL!HS-sd1-003#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-sd1-003_A01_T06_PL_HS-sd1-003.command`

## PL!HS-sd1-004
- `PL!HS-sd1-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-004_A01_T01_PL_HS-sd1-004.command`
- `PL!HS-sd1-004#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-004_A01_T02_PL_HS-sd1-004.command`
- `PL!HS-sd1-004#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-004_A01_T03_PL_HS-sd1-004.command`

## PL!HS-sd1-005
- `PL!HS-sd1-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-005_A01_T01_PL_HS-sd1-005.command`
- `PL!HS-sd1-005#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-sd1-005_A01_T02_PL_HS-sd1-005.command`
- `PL!HS-sd1-005#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-sd1-005_A01_T03_PL_HS-sd1-005.command`

## PL!HS-sd1-006
- `PL!HS-sd1-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-006_A01_T01_PL_HS-sd1-006.command`
- `PL!HS-sd1-006#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-sd1-006_A01_T02_PL_HS-sd1-006.command`
- `PL!HS-sd1-006#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-sd1-006_A01_T03_PL_HS-sd1-006.command`
- `PL!HS-sd1-006#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-006_A02_T01_PL_HS-sd1-006.command`
- `PL!HS-sd1-006#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-sd1-006_A02_T02_PL_HS-sd1-006.command`
- `PL!HS-sd1-006#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-sd1-006_A02_T03_PL_HS-sd1-006.command`
- `PL!HS-sd1-006#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-006_A02_T04_PL_HS-sd1-006.command`
- `PL!HS-sd1-006#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-006_A02_T05_PL_HS-sd1-006.command`
- `PL!HS-sd1-006#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-sd1-006_A02_T06_PL_HS-sd1-006.command`

## PL!HS-sd1-008
- `PL!HS-sd1-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-008_A01_T01_PL_HS-sd1-008.command`
- `PL!HS-sd1-008#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-008_A02_T01_PL_HS-sd1-008.command`
- `PL!HS-sd1-008#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-sd1-008_A02_T02_PL_HS-sd1-008.command`
- `PL!HS-sd1-008#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-sd1-008_A02_T03_PL_HS-sd1-008.command`
- `PL!HS-sd1-008#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-008_A02_T04_PL_HS-sd1-008.command`
- `PL!HS-sd1-008#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-008_A02_T05_PL_HS-sd1-008.command`
- `PL!HS-sd1-008#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-sd1-008_A02_T06_PL_HS-sd1-008.command`

## PL!HS-sd1-009
- `PL!HS-sd1-009#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-009_A01_T01_PL_HS-sd1-009.command`
- `PL!HS-sd1-009#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-009_A01_T02_PL_HS-sd1-009.command`
- `PL!HS-sd1-009#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-009_A01_T03_PL_HS-sd1-009.command`

## PL!HS-sd1-013
- `PL!HS-sd1-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-013_A01_T01_PL_HS-sd1-013.command`
- `PL!HS-sd1-013#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_HS-sd1-013_A01_T02_PL_HS-sd1-013.command`
- `PL!HS-sd1-013#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_HS-sd1-013_A01_T03_PL_HS-sd1-013.command`
- `PL!HS-sd1-013#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_HS-sd1-013_A01_T04_PL_HS-sd1-013.command`
- `PL!HS-sd1-013#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_HS-sd1-013_A01_T05_PL_HS-sd1-013.command`

## PL!HS-sd1-014
- `PL!HS-sd1-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-014_A01_T01_PL_HS-sd1-014.command`
- `PL!HS-sd1-014#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-014_A01_T02_PL_HS-sd1-014.command`
- `PL!HS-sd1-014#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-014_A01_T03_PL_HS-sd1-014.command`

## PL!HS-sd1-015
- `PL!HS-sd1-015#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-015_A01_T01_PL_HS-sd1-015.command`
- `PL!HS-sd1-015#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-015_A01_T02_PL_HS-sd1-015.command`
- `PL!HS-sd1-015#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-015_A01_T03_PL_HS-sd1-015.command`

## PL!HS-sd1-017
- `PL!HS-sd1-017#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-017_A01_T01_PL_HS-sd1-017.command`
- `PL!HS-sd1-017#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-sd1-017_A01_T02_PL_HS-sd1-017.command`
- `PL!HS-sd1-017#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-sd1-017_A01_T03_PL_HS-sd1-017.command`
- `PL!HS-sd1-017#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-sd1-017_A01_T04_PL_HS-sd1-017.command`

## PL!HS-sd1-018
- `PL!HS-sd1-018#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-018_A01_T01_PL_HS-sd1-018.command`
- `PL!HS-sd1-018#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_HS-sd1-018_A01_T02_PL_HS-sd1-018.command`
- `PL!HS-sd1-018#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_HS-sd1-018_A01_T03_PL_HS-sd1-018.command`
- `PL!HS-sd1-018#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-sd1-018_A01_T04_PL_HS-sd1-018.command`

## PL!HS-sd1-020
- `PL!HS-sd1-020#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_HS-sd1-020_A02_T01_PL_HS-sd1-020.command`
- `PL!HS-sd1-020#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_HS-sd1-020_A02_T02_PL_HS-sd1-020.command`
- `PL!HS-sd1-020#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_HS-sd1-020_A02_T03_PL_HS-sd1-020.command`
- `PL!HS-sd1-020#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_HS-sd1-020_A02_T04_PL_HS-sd1-020.command`
- `PL!HS-sd1-020#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_HS-sd1-020_A02_T05_PL_HS-sd1-020.command`
- `PL!HS-sd1-020#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_HS-sd1-020_A02_T06_PL_HS-sd1-020.command`

## PL!N-PR-004
- `PL!N-PR-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-004_A01_T01_PL_N-PR-004.command`
- `PL!N-PR-004#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-PR-004_A01_T02_PL_N-PR-004.command`
- `PL!N-PR-004#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-PR-004_A01_T03_PL_N-PR-004.command`

## PL!N-PR-005
- `PL!N-PR-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-005_A01_T01_PL_N-PR-005.command`

## PL!N-PR-006
- `PL!N-PR-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-006_A01_T01_PL_N-PR-006.command`
- `PL!N-PR-006#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-PR-006_A01_T02_PL_N-PR-006.command`
- `PL!N-PR-006#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-PR-006_A01_T03_PL_N-PR-006.command`

## PL!N-PR-007
- `PL!N-PR-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-007_A01_T01_PL_N-PR-007.command`

## PL!N-PR-009
- `PL!N-PR-009#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-PR-009_A01_T01_PL_N-PR-009.command`
- `PL!N-PR-009#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-PR-009_A01_T02_PL_N-PR-009.command`
- `PL!N-PR-009#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-PR-009_A01_T03_PL_N-PR-009.command`

## PL!N-PR-011
- `PL!N-PR-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-011_A01_T01_PL_N-PR-011.command`

## PL!N-PR-012
- `PL!N-PR-012#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-PR-012_A01_T01_PL_N-PR-012.command`
- `PL!N-PR-012#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-PR-012_A01_T02_PL_N-PR-012.command`
- `PL!N-PR-012#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-PR-012_A01_T03_PL_N-PR-012.command`

## PL!N-PR-013
- `PL!N-PR-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-013_A01_T01_PL_N-PR-013.command`
- `PL!N-PR-013#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-PR-013_A01_T02_PL_N-PR-013.command`
- `PL!N-PR-013#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-PR-013_A01_T03_PL_N-PR-013.command`

## PL!N-PR-014
- `PL!N-PR-014#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-PR-014_A01_T01_PL_N-PR-014.command`
- `PL!N-PR-014#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-PR-014_A01_T02_PL_N-PR-014.command`
- `PL!N-PR-014#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-PR-014_A01_T03_PL_N-PR-014.command`

## PL!N-PR-019
- `PL!N-PR-019#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-PR-019_A01_T01_PL_N-PR-019.command`
- `PL!N-PR-019#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-PR-019_A01_T02_PL_N-PR-019.command`
- `PL!N-PR-019#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-PR-019_A01_T03_PL_N-PR-019.command`

## PL!N-PR-020
- `PL!N-PR-020#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_N-PR-020_A01_T01_PL_N-PR-020.command`
- `PL!N-PR-020#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_N-PR-020_A01_T02_PL_N-PR-020.command`
- `PL!N-PR-020#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_N-PR-020_A01_T03_PL_N-PR-020.command`
- `PL!N-PR-020#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_N-PR-020_A01_T04_PL_N-PR-020.command`
- `PL!N-PR-020#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_N-PR-020_A01_T05_PL_N-PR-020.command`

## PL!N-PR-021
- `PL!N-PR-021#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-PR-021_A01_T01_PL_N-PR-021.command`
- `PL!N-PR-021#A01#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_N-PR-021_A01_T02_PL_N-PR-021.command`
- `PL!N-PR-021#A01#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_N-PR-021_A01_T03_PL_N-PR-021.command`
- `PL!N-PR-021#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-PR-021_A01_T04_PL_N-PR-021.command`

## PL!N-PR-022
- `PL!N-PR-022#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-022_A01_T01_PL_N-PR-022.command`
- `PL!N-PR-022#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-PR-022_A01_T02_PL_N-PR-022.command`
- `PL!N-PR-022#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-PR-022_A01_T03_PL_N-PR-022.command`
- `PL!N-PR-022#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-PR-022_A01_T04_PL_N-PR-022.command`
- `PL!N-PR-022#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-PR-022_A01_T05_PL_N-PR-022.command`

## PL!N-PR-023
- `PL!N-PR-023#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_N-PR-023_A01_T01_PL_N-PR-023.command`
- `PL!N-PR-023#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_N-PR-023_A01_T02_PL_N-PR-023.command`
- `PL!N-PR-023#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_N-PR-023_A01_T03_PL_N-PR-023.command`
- `PL!N-PR-023#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_N-PR-023_A01_T04_PL_N-PR-023.command`
- `PL!N-PR-023#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_N-PR-023_A01_T05_PL_N-PR-023.command`
- `PL!N-PR-023#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_N-PR-023_A01_T06_PL_N-PR-023.command`
- `PL!N-PR-023#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_N-PR-023_A01_T07_PL_N-PR-023.command`

## PL!N-PR-026
- `PL!N-PR-026#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-026_A01_T01_PL_N-PR-026.command`

## PL!N-PR-028
- `PL!N-PR-028#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-028_A01_T01_PL_N-PR-028.command`
- `PL!N-PR-028#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-PR-028_A01_T02_PL_N-PR-028.command`
- `PL!N-PR-028#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-PR-028_A01_T03_PL_N-PR-028.command`
- `PL!N-PR-028#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-PR-028_A01_T04_PL_N-PR-028.command`
- `PL!N-PR-028#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-PR-028_A01_T05_PL_N-PR-028.command`

## PL!N-PR-032
- `PL!N-PR-032#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-PR-032_A01_T01_PL_N-PR-032.command`
- `PL!N-PR-032#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-PR-032_A01_T02_PL_N-PR-032.command`
- `PL!N-PR-032#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-PR-032_A01_T03_PL_N-PR-032.command`

## PL!N-bp1-001
- `PL!N-bp1-001#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-001_A01_T01_PL_N-bp1-001.command`
- `PL!N-bp1-001#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp1-001_A01_T02_PL_N-bp1-001.command`
- `PL!N-bp1-001#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp1-001_A01_T03_PL_N-bp1-001.command`
- `PL!N-bp1-001#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-001_A01_T04_PL_N-bp1-001.command`
- `PL!N-bp1-001#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-001_A01_T05_PL_N-bp1-001.command`
- `PL!N-bp1-001#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp1-001_A01_T06_PL_N-bp1-001.command`

## PL!N-bp1-002
- `PL!N-bp1-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-002_A01_T01_PL_N-bp1-002.command`
- `PL!N-bp1-002#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-bp1-002_A01_T02_PL_N-bp1-002.command`
- `PL!N-bp1-002#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-bp1-002_A01_T03_PL_N-bp1-002.command`

## PL!N-bp1-003
- `PL!N-bp1-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-003_A01_T01_PL_N-bp1-003.command`
- `PL!N-bp1-003#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-003_A01_T02_PL_N-bp1-003.command`
- `PL!N-bp1-003#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-003_A01_T03_PL_N-bp1-003.command`
- `PL!N-bp1-003#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-003_A02_T01_PL_N-bp1-003.command`
- `PL!N-bp1-003#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp1-003_A02_T02_PL_N-bp1-003.command`
- `PL!N-bp1-003#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp1-003_A02_T03_PL_N-bp1-003.command`
- `PL!N-bp1-003#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-003_A02_T04_PL_N-bp1-003.command`
- `PL!N-bp1-003#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-003_A02_T05_PL_N-bp1-003.command`
- `PL!N-bp1-003#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp1-003_A02_T06_PL_N-bp1-003.command`

## PL!N-bp1-004
- `PL!N-bp1-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-004_A01_T01_PL_N-bp1-004.command`
- `PL!N-bp1-004#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-bp1-004_A01_T02_PL_N-bp1-004.command`
- `PL!N-bp1-004#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-bp1-004_A01_T03_PL_N-bp1-004.command`

## PL!N-bp1-005
- `PL!N-bp1-005#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-005_A01_T01_PL_N-bp1-005.command`
- `PL!N-bp1-005#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp1-005_A01_T02_PL_N-bp1-005.command`
- `PL!N-bp1-005#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp1-005_A01_T03_PL_N-bp1-005.command`
- `PL!N-bp1-005#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-005_A01_T04_PL_N-bp1-005.command`
- `PL!N-bp1-005#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-005_A01_T05_PL_N-bp1-005.command`
- `PL!N-bp1-005#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp1-005_A01_T06_PL_N-bp1-005.command`

## PL!N-bp1-006
- `PL!N-bp1-006#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-006_A01_T01_PL_N-bp1-006.command`
- `PL!N-bp1-006#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_N-bp1-006_A01_T02_PL_N-bp1-006.command`
- `PL!N-bp1-006#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_N-bp1-006_A01_T03_PL_N-bp1-006.command`
- `PL!N-bp1-006#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-006_A01_T04_PL_N-bp1-006.command`
- `PL!N-bp1-006#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-006_A01_T05_PL_N-bp1-006.command`
- `PL!N-bp1-006#A01#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp1-006_A01_T06_PL_N-bp1-006.command`
- `PL!N-bp1-006#A01#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp1-006_A01_T07_PL_N-bp1-006.command`
- `PL!N-bp1-006#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-006_A02_T01_PL_N-bp1-006.command`
- `PL!N-bp1-006#A02#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-006_A02_T02_PL_N-bp1-006.command`
- `PL!N-bp1-006#A02#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-006_A02_T03_PL_N-bp1-006.command`
- `PL!N-bp1-006#A02#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp1-006_A02_T04_PL_N-bp1-006.command`
- `PL!N-bp1-006#A02#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp1-006_A02_T05_PL_N-bp1-006.command`

## PL!N-bp1-007
- `PL!N-bp1-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-007_A01_T01_PL_N-bp1-007.command`
- `PL!N-bp1-007#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-007_A01_T02_PL_N-bp1-007.command`
- `PL!N-bp1-007#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-007_A01_T03_PL_N-bp1-007.command`

## PL!N-bp1-009
- `PL!N-bp1-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-009_A01_T01_PL_N-bp1-009.command`
- `PL!N-bp1-009#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-009_A01_T02_PL_N-bp1-009.command`
- `PL!N-bp1-009#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-009_A01_T03_PL_N-bp1-009.command`

## PL!N-bp1-010
- `PL!N-bp1-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-010_A01_T01_PL_N-bp1-010.command`
- `PL!N-bp1-010#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-010_A01_T02_PL_N-bp1-010.command`
- `PL!N-bp1-010#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-010_A01_T03_PL_N-bp1-010.command`

## PL!N-bp1-011
- `PL!N-bp1-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-011_A01_T01_PL_N-bp1-011.command`
- `PL!N-bp1-011#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-bp1-011_A01_T02_PL_N-bp1-011.command`
- `PL!N-bp1-011#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-bp1-011_A01_T03_PL_N-bp1-011.command`
- `PL!N-bp1-011#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-011_A01_T04_PL_N-bp1-011.command`
- `PL!N-bp1-011#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-011_A01_T05_PL_N-bp1-011.command`

## PL!N-bp1-012
- `PL!N-bp1-012#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-012_A01_T01_PL_N-bp1-012.command`
- `PL!N-bp1-012#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_N-bp1-012_A01_T02_PL_N-bp1-012.command`
- `PL!N-bp1-012#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_N-bp1-012_A01_T03_PL_N-bp1-012.command`
- `PL!N-bp1-012#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_N-bp1-012_A01_T04_PL_N-bp1-012.command`
- `PL!N-bp1-012#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_N-bp1-012_A01_T05_PL_N-bp1-012.command`
- `PL!N-bp1-012#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-012_A02_T01_PL_N-bp1-012.command`
- `PL!N-bp1-012#A02#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-012_A02_T02_PL_N-bp1-012.command`
- `PL!N-bp1-012#A02#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-012_A02_T03_PL_N-bp1-012.command`
- `PL!N-bp1-012#A02#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp1-012_A02_T04_PL_N-bp1-012.command`
- `PL!N-bp1-012#A02#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp1-012_A02_T05_PL_N-bp1-012.command`

## PL!N-bp1-014
- `PL!N-bp1-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-014_A01_T01_PL_N-bp1-014.command`

## PL!N-bp1-015
- `PL!N-bp1-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-015_A01_T01_PL_N-bp1-015.command`

## PL!N-bp1-019
- `PL!N-bp1-019#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-019_A01_T01_PL_N-bp1-019.command`

## PL!N-bp1-026
- `PL!N-bp1-026#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-026_A01_T01_PL_N-bp1-026.command`
- `PL!N-bp1-026#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp1-026_A01_T02_PL_N-bp1-026.command`
- `PL!N-bp1-026#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp1-026_A01_T03_PL_N-bp1-026.command`
- `PL!N-bp1-026#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp1-026_A01_T04_PL_N-bp1-026.command`

## PL!N-bp1-027
- `PL!N-bp1-027#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-027_A01_T01_PL_N-bp1-027.command`
- `PL!N-bp1-027#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp1-027_A01_T02_PL_N-bp1-027.command`

## PL!N-bp1-028
- `PL!N-bp1-028#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-028_A01_T01_PL_N-bp1-028.command`
- `PL!N-bp1-028#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp1-028_A01_T02_PL_N-bp1-028.command`
- `PL!N-bp1-028#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp1-028_A01_T03_PL_N-bp1-028.command`
- `PL!N-bp1-028#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp1-028_A01_T04_PL_N-bp1-028.command`
- `PL!N-bp1-028#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp1-028_A01_T05_PL_N-bp1-028.command`
- `PL!N-bp1-028#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp1-028_A01_T06_PL_N-bp1-028.command`

## PL!N-bp1-029
- `PL!N-bp1-029#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp1-029_A01_T01_PL_N-bp1-029.command`
- `PL!N-bp1-029#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp1-029_A01_T02_PL_N-bp1-029.command`
- `PL!N-bp1-029#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp1-029_A01_T03_PL_N-bp1-029.command`
- `PL!N-bp1-029#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp1-029_A01_T04_PL_N-bp1-029.command`

## PL!N-bp3-001
- `PL!N-bp3-001#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-001_A01_T01_PL_N-bp3-001.command`
- `PL!N-bp3-001#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp3-001_A01_T02_PL_N-bp3-001.command`
- `PL!N-bp3-001#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp3-001_A01_T03_PL_N-bp3-001.command`
- `PL!N-bp3-001#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-001_A01_T04_PL_N-bp3-001.command`
- `PL!N-bp3-001#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-001_A01_T05_PL_N-bp3-001.command`
- `PL!N-bp3-001#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-001_A01_T06_PL_N-bp3-001.command`

## PL!N-bp3-002
- `PL!N-bp3-002#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-002_A01_T01_PL_N-bp3-002.command`
- `PL!N-bp3-002#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-002_A01_T02_PL_N-bp3-002.command`
- `PL!N-bp3-002#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-002_A01_T03_PL_N-bp3-002.command`
- `PL!N-bp3-002#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-002_A01_T04_PL_N-bp3-002.command`
- `PL!N-bp3-002#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-002_A01_T05_PL_N-bp3-002.command`
- `PL!N-bp3-002#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-002_A01_T06_PL_N-bp3-002.command`

## PL!N-bp3-003
- `PL!N-bp3-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-003_A01_T01_PL_N-bp3-003.command`

## PL!N-bp3-004
- `PL!N-bp3-004#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-004_A01_T01_PL_N-bp3-004.command`
- `PL!N-bp3-004#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-004_A01_T02_PL_N-bp3-004.command`
- `PL!N-bp3-004#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-004_A01_T03_PL_N-bp3-004.command`
- `PL!N-bp3-004#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp3-004_A01_T04_PL_N-bp3-004.command`
- `PL!N-bp3-004#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp3-004_A01_T05_PL_N-bp3-004.command`

## PL!N-bp3-005
- `PL!N-bp3-005#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-005_A01_T01_PL_N-bp3-005.command`
- `PL!N-bp3-005#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_N-bp3-005_A01_T02_PL_N-bp3-005.command`
- `PL!N-bp3-005#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_N-bp3-005_A01_T03_PL_N-bp3-005.command`
- `PL!N-bp3-005#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-005_A01_T04_PL_N-bp3-005.command`
- `PL!N-bp3-005#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-005_A01_T05_PL_N-bp3-005.command`
- `PL!N-bp3-005#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-005_A02_T01_PL_N-bp3-005.command`
- `PL!N-bp3-005#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp3-005_A02_T02_PL_N-bp3-005.command`
- `PL!N-bp3-005#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp3-005_A02_T03_PL_N-bp3-005.command`
- `PL!N-bp3-005#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-005_A02_T04_PL_N-bp3-005.command`
- `PL!N-bp3-005#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-005_A02_T05_PL_N-bp3-005.command`
- `PL!N-bp3-005#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-005_A02_T06_PL_N-bp3-005.command`

## PL!N-bp3-006
- `PL!N-bp3-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-006_A01_T01_PL_N-bp3-006.command`

## PL!N-bp3-007
- `PL!N-bp3-007#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-007_A01_T01_PL_N-bp3-007.command`
- `PL!N-bp3-007#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_N-bp3-007_A01_T02_PL_N-bp3-007.command`
- `PL!N-bp3-007#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_N-bp3-007_A01_T03_PL_N-bp3-007.command`
- `PL!N-bp3-007#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-007_A01_T04_PL_N-bp3-007.command`
- `PL!N-bp3-007#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-007_A01_T05_PL_N-bp3-007.command`

## PL!N-bp3-008
- `PL!N-bp3-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-008_A01_T01_PL_N-bp3-008.command`
- `PL!N-bp3-008#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-008_A01_T02_PL_N-bp3-008.command`
- `PL!N-bp3-008#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-008_A01_T03_PL_N-bp3-008.command`
- `PL!N-bp3-008#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp3-008_A01_T04_PL_N-bp3-008.command`
- `PL!N-bp3-008#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp3-008_A01_T05_PL_N-bp3-008.command`
- `PL!N-bp3-008#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-008_A02_T01_PL_N-bp3-008.command`
- `PL!N-bp3-008#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp3-008_A02_T02_PL_N-bp3-008.command`
- `PL!N-bp3-008#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp3-008_A02_T03_PL_N-bp3-008.command`
- `PL!N-bp3-008#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-008_A02_T04_PL_N-bp3-008.command`
- `PL!N-bp3-008#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-008_A02_T05_PL_N-bp3-008.command`
- `PL!N-bp3-008#A02#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-008_A02_T06_PL_N-bp3-008.command`
- `PL!N-bp3-008#A02#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-008_A02_T07_PL_N-bp3-008.command`
- `PL!N-bp3-008#A02#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-008_A02_T08_PL_N-bp3-008.command`

## PL!N-bp3-009
- `PL!N-bp3-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-009_A01_T01_PL_N-bp3-009.command`
- `PL!N-bp3-009#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp3-009_A01_T02_PL_N-bp3-009.command`
- `PL!N-bp3-009#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp3-009_A01_T03_PL_N-bp3-009.command`
- `PL!N-bp3-009#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-009_A01_T04_PL_N-bp3-009.command`
- `PL!N-bp3-009#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-009_A01_T05_PL_N-bp3-009.command`
- `PL!N-bp3-009#A01#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-009_A01_T06_PL_N-bp3-009.command`
- `PL!N-bp3-009#A01#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-009_A01_T07_PL_N-bp3-009.command`
- `PL!N-bp3-009#A01#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-009_A01_T08_PL_N-bp3-009.command`

## PL!N-bp3-010
- `PL!N-bp3-010#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-010_A01_T01_PL_N-bp3-010.command`
- `PL!N-bp3-010#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-010_A01_T02_PL_N-bp3-010.command`
- `PL!N-bp3-010#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-010_A01_T03_PL_N-bp3-010.command`
- `PL!N-bp3-010#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-010_A01_T04_PL_N-bp3-010.command`

## PL!N-bp3-011
- `PL!N-bp3-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-011_A01_T01_PL_N-bp3-011.command`
- `PL!N-bp3-011#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-bp3-011_A01_T02_PL_N-bp3-011.command`
- `PL!N-bp3-011#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-bp3-011_A01_T03_PL_N-bp3-011.command`
- `PL!N-bp3-011#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-011_A01_T04_PL_N-bp3-011.command`
- `PL!N-bp3-011#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-011_A01_T05_PL_N-bp3-011.command`

## PL!N-bp3-012
- `PL!N-bp3-012#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-012_A01_T01_PL_N-bp3-012.command`
- `PL!N-bp3-012#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-012_A01_T02_PL_N-bp3-012.command`
- `PL!N-bp3-012#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-012_A01_T03_PL_N-bp3-012.command`

## PL!N-bp3-013
- `PL!N-bp3-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-013_A01_T01_PL_N-bp3-013.command`
- `PL!N-bp3-013#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-bp3-013_A01_T02_PL_N-bp3-013.command`
- `PL!N-bp3-013#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-bp3-013_A01_T03_PL_N-bp3-013.command`

## PL!N-bp3-014
- `PL!N-bp3-014#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-014_A01_T01_PL_N-bp3-014.command`
- `PL!N-bp3-014#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-014_A01_T02_PL_N-bp3-014.command`
- `PL!N-bp3-014#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-014_A01_T03_PL_N-bp3-014.command`
- `PL!N-bp3-014#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-014_A01_T04_PL_N-bp3-014.command`

## PL!N-bp3-015
- `PL!N-bp3-015#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-015_A01_T01_PL_N-bp3-015.command`
- `PL!N-bp3-015#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-015_A01_T02_PL_N-bp3-015.command`
- `PL!N-bp3-015#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-015_A01_T03_PL_N-bp3-015.command`
- `PL!N-bp3-015#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-015_A01_T04_PL_N-bp3-015.command`

## PL!N-bp3-017
- `PL!N-bp3-017#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-017_A01_T01_PL_N-bp3-017.command`
- `PL!N-bp3-017#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-017_A01_T02_PL_N-bp3-017.command`
- `PL!N-bp3-017#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-017_A01_T03_PL_N-bp3-017.command`
- `PL!N-bp3-017#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-017_A01_T04_PL_N-bp3-017.command`
- `PL!N-bp3-017#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-017_A01_T05_PL_N-bp3-017.command`

## PL!N-bp3-022
- `PL!N-bp3-022#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-022_A01_T01_PL_N-bp3-022.command`
- `PL!N-bp3-022#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-022_A01_T02_PL_N-bp3-022.command`
- `PL!N-bp3-022#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-022_A01_T03_PL_N-bp3-022.command`
- `PL!N-bp3-022#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-022_A01_T04_PL_N-bp3-022.command`
- `PL!N-bp3-022#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-022_A01_T05_PL_N-bp3-022.command`

## PL!N-bp3-023
- `PL!N-bp3-023#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-023_A01_T01_PL_N-bp3-023.command`
- `PL!N-bp3-023#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-023_A01_T02_PL_N-bp3-023.command`
- `PL!N-bp3-023#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-023_A01_T03_PL_N-bp3-023.command`
- `PL!N-bp3-023#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp3-023_A01_T04_PL_N-bp3-023.command`
- `PL!N-bp3-023#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp3-023_A01_T05_PL_N-bp3-023.command`

## PL!N-bp3-024
- `PL!N-bp3-024#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-024_A01_T01_PL_N-bp3-024.command`

## PL!N-bp3-025
- `PL!N-bp3-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-025_A01_T01_PL_N-bp3-025.command`
- `PL!N-bp3-025#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp3-025_A01_T02_PL_N-bp3-025.command`
- `PL!N-bp3-025#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp3-025_A01_T03_PL_N-bp3-025.command`
- `PL!N-bp3-025#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp3-025_A01_T04_PL_N-bp3-025.command`
- `PL!N-bp3-025#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp3-025_A01_T05_PL_N-bp3-025.command`
- `PL!N-bp3-025#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-025_A01_T06_PL_N-bp3-025.command`

## PL!N-bp3-026
- `PL!N-bp3-026#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-026_A01_T01_PL_N-bp3-026.command`
- `PL!N-bp3-026#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp3-026_A01_T02_PL_N-bp3-026.command`
- `PL!N-bp3-026#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp3-026_A01_T03_PL_N-bp3-026.command`
- `PL!N-bp3-026#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-026_A01_T04_PL_N-bp3-026.command`

## PL!N-bp3-027
- `PL!N-bp3-027#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-027_A01_T01_PL_N-bp3-027.command`
- `PL!N-bp3-027#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp3-027_A01_T02_PL_N-bp3-027.command`
- `PL!N-bp3-027#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp3-027_A01_T03_PL_N-bp3-027.command`
- `PL!N-bp3-027#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-027_A01_T04_PL_N-bp3-027.command`

## PL!N-bp3-028
- `PL!N-bp3-028#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-028_A01_T01_PL_N-bp3-028.command`
- `PL!N-bp3-028#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp3-028_A01_T02_PL_N-bp3-028.command`
- `PL!N-bp3-028#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp3-028_A01_T03_PL_N-bp3-028.command`
- `PL!N-bp3-028#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-028_A01_T04_PL_N-bp3-028.command`

## PL!N-bp3-030
- `PL!N-bp3-030#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-030_A01_T01_PL_N-bp3-030.command`
- `PL!N-bp3-030#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp3-030_A01_T02_PL_N-bp3-030.command`
- `PL!N-bp3-030#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp3-030_A01_T03_PL_N-bp3-030.command`
- `PL!N-bp3-030#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-030_A01_T04_PL_N-bp3-030.command`

## PL!N-bp3-031
- `PL!N-bp3-031#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp3-031_A01_T01_PL_N-bp3-031.command`
- `PL!N-bp3-031#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp3-031_A01_T02_PL_N-bp3-031.command`

## PL!N-bp4-001
- `PL!N-bp4-001#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-001_A01_T01_PL_N-bp4-001.command`
- `PL!N-bp4-001#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp4-001_A01_T02_PL_N-bp4-001.command`
- `PL!N-bp4-001#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp4-001_A01_T03_PL_N-bp4-001.command`
- `PL!N-bp4-001#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-001_A01_T04_PL_N-bp4-001.command`

## PL!N-bp4-002
- `PL!N-bp4-002#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-002_A01_T01_PL_N-bp4-002.command`
- `PL!N-bp4-002#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-002_A01_T02_PL_N-bp4-002.command`

## PL!N-bp4-003
- `PL!N-bp4-003#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-003_A01_T01_PL_N-bp4-003.command`
- `PL!N-bp4-003#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp4-003_A01_T02_PL_N-bp4-003.command`
- `PL!N-bp4-003#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp4-003_A01_T03_PL_N-bp4-003.command`
- `PL!N-bp4-003#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-003_A01_T04_PL_N-bp4-003.command`

## PL!N-bp4-004
- `PL!N-bp4-004#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-004_A01_T01_PL_N-bp4-004.command`
- `PL!N-bp4-004#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-004_A01_T02_PL_N-bp4-004.command`
- `PL!N-bp4-004#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-004_A01_T03_PL_N-bp4-004.command`
- `PL!N-bp4-004#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-004_A01_T04_PL_N-bp4-004.command`
- `PL!N-bp4-004#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-004_A02_T01_PL_N-bp4-004.command`
- `PL!N-bp4-004#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-004_A02_T02_PL_N-bp4-004.command`
- `PL!N-bp4-004#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-004_A02_T03_PL_N-bp4-004.command`
- `PL!N-bp4-004#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-004_A02_T04_PL_N-bp4-004.command`

## PL!N-bp4-005
- `PL!N-bp4-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-005_A01_T01_PL_N-bp4-005.command`
- `PL!N-bp4-005#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-005_A01_T02_PL_N-bp4-005.command`
- `PL!N-bp4-005#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-005_A01_T03_PL_N-bp4-005.command`
- `PL!N-bp4-005#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp4-005_A01_T04_PL_N-bp4-005.command`
- `PL!N-bp4-005#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp4-005_A01_T05_PL_N-bp4-005.command`

## PL!N-bp4-006
- `PL!N-bp4-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-006_A01_T01_PL_N-bp4-006.command`
- `PL!N-bp4-006#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-bp4-006_A01_T02_PL_N-bp4-006.command`
- `PL!N-bp4-006#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-bp4-006_A01_T03_PL_N-bp4-006.command`
- `PL!N-bp4-006#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp4-006_A01_T04_PL_N-bp4-006.command`
- `PL!N-bp4-006#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp4-006_A01_T05_PL_N-bp4-006.command`

## PL!N-bp4-007
- `PL!N-bp4-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-007_A01_T01_PL_N-bp4-007.command`
- `PL!N-bp4-007#A03#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-007_A03_T01_PL_N-bp4-007.command`
- `PL!N-bp4-007#A03#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-007_A03_T02_PL_N-bp4-007.command`

## PL!N-bp4-009
- `PL!N-bp4-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-009_A01_T01_PL_N-bp4-009.command`
- `PL!N-bp4-009#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp4-009_A01_T02_PL_N-bp4-009.command`
- `PL!N-bp4-009#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp4-009_A01_T03_PL_N-bp4-009.command`
- `PL!N-bp4-009#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-009_A01_T04_PL_N-bp4-009.command`

## PL!N-bp4-010
- `PL!N-bp4-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-010_A01_T01_PL_N-bp4-010.command`
- `PL!N-bp4-010#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-bp4-010_A01_T02_PL_N-bp4-010.command`
- `PL!N-bp4-010#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-bp4-010_A01_T03_PL_N-bp4-010.command`
- `PL!N-bp4-010#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-010_A02_T01_PL_N-bp4-010.command`
- `PL!N-bp4-010#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp4-010_A02_T02_PL_N-bp4-010.command`
- `PL!N-bp4-010#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp4-010_A02_T03_PL_N-bp4-010.command`
- `PL!N-bp4-010#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-010_A02_T04_PL_N-bp4-010.command`
- `PL!N-bp4-010#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-010_A02_T05_PL_N-bp4-010.command`
- `PL!N-bp4-010#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-010_A02_T06_PL_N-bp4-010.command`

## PL!N-bp4-011
- `PL!N-bp4-011#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-011_A01_T01_PL_N-bp4-011.command`
- `PL!N-bp4-011#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-011_A01_T02_PL_N-bp4-011.command`
- `PL!N-bp4-011#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-011_A01_T03_PL_N-bp4-011.command`
- `PL!N-bp4-011#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp4-011_A01_T04_PL_N-bp4-011.command`
- `PL!N-bp4-011#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp4-011_A01_T05_PL_N-bp4-011.command`
- `PL!N-bp4-011#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-011_A01_T06_PL_N-bp4-011.command`
- `PL!N-bp4-011#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-011_A02_T01_PL_N-bp4-011.command`
- `PL!N-bp4-011#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp4-011_A02_T02_PL_N-bp4-011.command`
- `PL!N-bp4-011#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp4-011_A02_T03_PL_N-bp4-011.command`
- `PL!N-bp4-011#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-011_A02_T04_PL_N-bp4-011.command`

## PL!N-bp4-013
- `PL!N-bp4-013#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-013_A01_T01_PL_N-bp4-013.command`
- `PL!N-bp4-013#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-013_A01_T02_PL_N-bp4-013.command`
- `PL!N-bp4-013#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-013_A01_T03_PL_N-bp4-013.command`
- `PL!N-bp4-013#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp4-013_A01_T04_PL_N-bp4-013.command`
- `PL!N-bp4-013#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp4-013_A01_T05_PL_N-bp4-013.command`
- `PL!N-bp4-013#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-013_A01_T06_PL_N-bp4-013.command`

## PL!N-bp4-016
- `PL!N-bp4-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-016_A01_T01_PL_N-bp4-016.command`
- `PL!N-bp4-016#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-016_A01_T02_PL_N-bp4-016.command`
- `PL!N-bp4-016#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-016_A01_T03_PL_N-bp4-016.command`
- `PL!N-bp4-016#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp4-016_A01_T04_PL_N-bp4-016.command`
- `PL!N-bp4-016#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp4-016_A01_T05_PL_N-bp4-016.command`

## PL!N-bp4-017
- `PL!N-bp4-017#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-017_A01_T01_PL_N-bp4-017.command`
- `PL!N-bp4-017#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp4-017_A01_T02_PL_N-bp4-017.command`
- `PL!N-bp4-017#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp4-017_A01_T03_PL_N-bp4-017.command`

## PL!N-bp4-020
- `PL!N-bp4-020#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-020_A01_T01_PL_N-bp4-020.command`
- `PL!N-bp4-020#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp4-020_A01_T02_PL_N-bp4-020.command`
- `PL!N-bp4-020#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp4-020_A01_T03_PL_N-bp4-020.command`

## PL!N-bp4-021
- `PL!N-bp4-021#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-021_A01_T01_PL_N-bp4-021.command`

## PL!N-bp4-023
- `PL!N-bp4-023#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-023_A01_T01_PL_N-bp4-023.command`
- `PL!N-bp4-023#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-023_A01_T02_PL_N-bp4-023.command`
- `PL!N-bp4-023#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-023_A01_T03_PL_N-bp4-023.command`
- `PL!N-bp4-023#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp4-023_A01_T04_PL_N-bp4-023.command`
- `PL!N-bp4-023#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp4-023_A01_T05_PL_N-bp4-023.command`

## PL!N-bp4-025
- `PL!N-bp4-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-025_A01_T01_PL_N-bp4-025.command`
- `PL!N-bp4-025#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-025_A01_T02_PL_N-bp4-025.command`
- `PL!N-bp4-025#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-025_A01_T03_PL_N-bp4-025.command`
- `PL!N-bp4-025#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-025_A01_T04_PL_N-bp4-025.command`
- `PL!N-bp4-025#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-025_A02_T01_PL_N-bp4-025.command`
- `PL!N-bp4-025#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp4-025_A02_T02_PL_N-bp4-025.command`
- `PL!N-bp4-025#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp4-025_A02_T03_PL_N-bp4-025.command`
- `PL!N-bp4-025#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-025_A02_T04_PL_N-bp4-025.command`

## PL!N-bp4-027
- `PL!N-bp4-027#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-027_A01_T01_PL_N-bp4-027.command`
- `PL!N-bp4-027#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-027_A01_T02_PL_N-bp4-027.command`

## PL!N-bp4-028
- `PL!N-bp4-028#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-028_A01_T01_PL_N-bp4-028.command`
- `PL!N-bp4-028#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp4-028_A01_T02_PL_N-bp4-028.command`
- `PL!N-bp4-028#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp4-028_A01_T03_PL_N-bp4-028.command`
- `PL!N-bp4-028#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-028_A01_T04_PL_N-bp4-028.command`

## PL!N-bp4-029
- `PL!N-bp4-029#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-029_A01_T01_PL_N-bp4-029.command`
- `PL!N-bp4-029#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp4-029_A01_T02_PL_N-bp4-029.command`
- `PL!N-bp4-029#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp4-029_A01_T03_PL_N-bp4-029.command`
- `PL!N-bp4-029#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp4-029_A01_T04_PL_N-bp4-029.command`
- `PL!N-bp4-029#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp4-029_A01_T05_PL_N-bp4-029.command`
- `PL!N-bp4-029#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-029_A01_T06_PL_N-bp4-029.command`

## PL!N-bp4-031
- `PL!N-bp4-031#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp4-031_A01_T01_PL_N-bp4-031.command`
- `PL!N-bp4-031#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp4-031_A01_T02_PL_N-bp4-031.command`
- `PL!N-bp4-031#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp4-031_A01_T03_PL_N-bp4-031.command`
- `PL!N-bp4-031#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp4-031_A01_T04_PL_N-bp4-031.command`

## PL!N-bp5-004
- `PL!N-bp5-004#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-004_A01_T01_PL_N-bp5-004.command`
- `PL!N-bp5-004#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp5-004_A01_T02_PL_N-bp5-004.command`
- `PL!N-bp5-004#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp5-004_A01_T03_PL_N-bp5-004.command`
- `PL!N-bp5-004#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-bp5-004_A01_T04_PL_N-bp5-004.command`
- `PL!N-bp5-004#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-bp5-004_A01_T05_PL_N-bp5-004.command`

## PL!N-bp5-005
- `PL!N-bp5-005#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-005_A01_T01_PL_N-bp5-005.command`
- `PL!N-bp5-005#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_N-bp5-005_A01_T02_PL_N-bp5-005.command`
- `PL!N-bp5-005#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_N-bp5-005_A01_T03_PL_N-bp5-005.command`

## PL!N-bp5-006
- `PL!N-bp5-006#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-006_A01_T01_PL_N-bp5-006.command`
- `PL!N-bp5-006#A01#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_N-bp5-006_A01_T02_PL_N-bp5-006.command`
- `PL!N-bp5-006#A01#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_N-bp5-006_A01_T03_PL_N-bp5-006.command`
- `PL!N-bp5-006#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-006_A02_T01_PL_N-bp5-006.command`
- `PL!N-bp5-006#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp5-006_A02_T02_PL_N-bp5-006.command`
- `PL!N-bp5-006#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp5-006_A02_T03_PL_N-bp5-006.command`
- `PL!N-bp5-006#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-006_A02_T04_PL_N-bp5-006.command`

## PL!N-bp5-007
- `PL!N-bp5-007#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-007_A01_T01_PL_N-bp5-007.command`
- `PL!N-bp5-007#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp5-007_A01_T02_PL_N-bp5-007.command`
- `PL!N-bp5-007#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp5-007_A01_T03_PL_N-bp5-007.command`
- `PL!N-bp5-007#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp5-007_A01_T04_PL_N-bp5-007.command`
- `PL!N-bp5-007#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp5-007_A01_T05_PL_N-bp5-007.command`
- `PL!N-bp5-007#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-007_A01_T06_PL_N-bp5-007.command`
- `PL!N-bp5-007#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-007_A02_T01_PL_N-bp5-007.command`
- `PL!N-bp5-007#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp5-007_A02_T02_PL_N-bp5-007.command`
- `PL!N-bp5-007#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp5-007_A02_T03_PL_N-bp5-007.command`
- `PL!N-bp5-007#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-007_A02_T04_PL_N-bp5-007.command`

## PL!N-bp5-008
- `PL!N-bp5-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-008_A01_T01_PL_N-bp5-008.command`
- `PL!N-bp5-008#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp5-008_A01_T02_PL_N-bp5-008.command`
- `PL!N-bp5-008#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp5-008_A01_T03_PL_N-bp5-008.command`
- `PL!N-bp5-008#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp5-008_A01_T04_PL_N-bp5-008.command`
- `PL!N-bp5-008#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp5-008_A01_T05_PL_N-bp5-008.command`

## PL!N-bp5-009
- `PL!N-bp5-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-009_A01_T01_PL_N-bp5-009.command`
- `PL!N-bp5-009#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp5-009_A01_T02_PL_N-bp5-009.command`
- `PL!N-bp5-009#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp5-009_A01_T03_PL_N-bp5-009.command`

## PL!N-bp5-010
- `PL!N-bp5-010#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-010_A01_T01_PL_N-bp5-010.command`
- `PL!N-bp5-010#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp5-010_A01_T02_PL_N-bp5-010.command`
- `PL!N-bp5-010#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp5-010_A01_T03_PL_N-bp5-010.command`
- `PL!N-bp5-010#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-010_A01_T04_PL_N-bp5-010.command`

## PL!N-bp5-012
- `PL!N-bp5-012#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-012_A01_T01_PL_N-bp5-012.command`
- `PL!N-bp5-012#A01#T02` 起動 / 任意処理を実行 / command: `debug_commands/PL_N-bp5-012_A01_T02_PL_N-bp5-012.command`
- `PL!N-bp5-012#A01#T03` 起動 / 任意処理を実行しない / command: `debug_commands/PL_N-bp5-012_A01_T03_PL_N-bp5-012.command`
- `PL!N-bp5-012#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp5-012_A01_T04_PL_N-bp5-012.command`
- `PL!N-bp5-012#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp5-012_A01_T05_PL_N-bp5-012.command`
- `PL!N-bp5-012#A01#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp5-012_A01_T06_PL_N-bp5-012.command`
- `PL!N-bp5-012#A01#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp5-012_A01_T07_PL_N-bp5-012.command`
- `PL!N-bp5-012#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-012_A02_T01_PL_N-bp5-012.command`
- `PL!N-bp5-012#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp5-012_A02_T02_PL_N-bp5-012.command`
- `PL!N-bp5-012#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp5-012_A02_T03_PL_N-bp5-012.command`
- `PL!N-bp5-012#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-012_A02_T04_PL_N-bp5-012.command`

## PL!N-bp5-013
- `PL!N-bp5-013#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-013_A01_T01_PL_N-bp5-013.command`
- `PL!N-bp5-013#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp5-013_A01_T02_PL_N-bp5-013.command`
- `PL!N-bp5-013#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp5-013_A01_T03_PL_N-bp5-013.command`
- `PL!N-bp5-013#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp5-013_A01_T04_PL_N-bp5-013.command`
- `PL!N-bp5-013#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp5-013_A01_T05_PL_N-bp5-013.command`
- `PL!N-bp5-013#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-013_A01_T06_PL_N-bp5-013.command`

## PL!N-bp5-014
- `PL!N-bp5-014#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-014_A01_T01_PL_N-bp5-014.command`
- `PL!N-bp5-014#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp5-014_A01_T02_PL_N-bp5-014.command`
- `PL!N-bp5-014#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp5-014_A01_T03_PL_N-bp5-014.command`
- `PL!N-bp5-014#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp5-014_A01_T04_PL_N-bp5-014.command`
- `PL!N-bp5-014#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp5-014_A01_T05_PL_N-bp5-014.command`

## PL!N-bp5-015
- `PL!N-bp5-015#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-015_A01_T01_PL_N-bp5-015.command`
- `PL!N-bp5-015#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp5-015_A01_T02_PL_N-bp5-015.command`
- `PL!N-bp5-015#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp5-015_A01_T03_PL_N-bp5-015.command`
- `PL!N-bp5-015#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp5-015_A01_T04_PL_N-bp5-015.command`
- `PL!N-bp5-015#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp5-015_A01_T05_PL_N-bp5-015.command`
- `PL!N-bp5-015#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-015_A01_T06_PL_N-bp5-015.command`

## PL!N-bp5-016
- `PL!N-bp5-016#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-016_A01_T01_PL_N-bp5-016.command`
- `PL!N-bp5-016#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-016_A01_T02_PL_N-bp5-016.command`

## PL!N-bp5-019
- `PL!N-bp5-019#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-019_A01_T01_PL_N-bp5-019.command`
- `PL!N-bp5-019#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp5-019_A01_T02_PL_N-bp5-019.command`
- `PL!N-bp5-019#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp5-019_A01_T03_PL_N-bp5-019.command`

## PL!N-bp5-021
- `PL!N-bp5-021#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-021_A01_T01_PL_N-bp5-021.command`

## PL!N-bp5-022
- `PL!N-bp5-022#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-022_A01_T01_PL_N-bp5-022.command`
- `PL!N-bp5-022#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-bp5-022_A01_T02_PL_N-bp5-022.command`
- `PL!N-bp5-022#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-bp5-022_A01_T03_PL_N-bp5-022.command`

## PL!N-bp5-023
- `PL!N-bp5-023#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-023_A01_T01_PL_N-bp5-023.command`
- `PL!N-bp5-023#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-023_A01_T02_PL_N-bp5-023.command`

## PL!N-bp5-026
- `PL!N-bp5-026#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-026_A01_T01_PL_N-bp5-026.command`
- `PL!N-bp5-026#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp5-026_A01_T02_PL_N-bp5-026.command`
- `PL!N-bp5-026#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp5-026_A01_T03_PL_N-bp5-026.command`
- `PL!N-bp5-026#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-026_A01_T04_PL_N-bp5-026.command`
- `PL!N-bp5-026#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-026_A02_T01_PL_N-bp5-026.command`
- `PL!N-bp5-026#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp5-026_A02_T02_PL_N-bp5-026.command`
- `PL!N-bp5-026#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp5-026_A02_T03_PL_N-bp5-026.command`
- `PL!N-bp5-026#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-026_A02_T04_PL_N-bp5-026.command`

## PL!N-bp5-027
- `PL!N-bp5-027#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-027_A01_T01_PL_N-bp5-027.command`
- `PL!N-bp5-027#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp5-027_A01_T02_PL_N-bp5-027.command`
- `PL!N-bp5-027#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp5-027_A01_T03_PL_N-bp5-027.command`
- `PL!N-bp5-027#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-027_A01_T04_PL_N-bp5-027.command`

## PL!N-bp5-028
- `PL!N-bp5-028#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-028_A01_T01_PL_N-bp5-028.command`
- `PL!N-bp5-028#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp5-028_A01_T02_PL_N-bp5-028.command`
- `PL!N-bp5-028#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp5-028_A01_T03_PL_N-bp5-028.command`
- `PL!N-bp5-028#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-028_A01_T04_PL_N-bp5-028.command`

## PL!N-bp5-029
- `PL!N-bp5-029#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp5-029_A01_T01_PL_N-bp5-029.command`
- `PL!N-bp5-029#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-bp5-029_A01_T02_PL_N-bp5-029.command`
- `PL!N-bp5-029#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-bp5-029_A01_T03_PL_N-bp5-029.command`
- `PL!N-bp5-029#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp5-029_A01_T04_PL_N-bp5-029.command`
- `PL!N-bp5-029#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp5-029_A01_T05_PL_N-bp5-029.command`
- `PL!N-bp5-029#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp5-029_A01_T06_PL_N-bp5-029.command`

## PL!N-bp7-003
- `PL!N-bp7-003#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-bp7-003_A01_T01_PL_N-bp7-003.command`
- `PL!N-bp7-003#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_N-bp7-003_A01_T02_PL_N-bp7-003.command`
- `PL!N-bp7-003#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_N-bp7-003_A01_T03_PL_N-bp7-003.command`
- `PL!N-bp7-003#A01#T04` 起動 / 任意処理を実行 / command: `debug_commands/PL_N-bp7-003_A01_T04_PL_N-bp7-003.command`
- `PL!N-bp7-003#A01#T05` 起動 / 任意処理を実行しない / command: `debug_commands/PL_N-bp7-003_A01_T05_PL_N-bp7-003.command`
- `PL!N-bp7-003#A01#T06` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-bp7-003_A01_T06_PL_N-bp7-003.command`
- `PL!N-bp7-003#A01#T07` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-bp7-003_A01_T07_PL_N-bp7-003.command`
- `PL!N-bp7-003#A01#T08` 起動 / 回数制限超過 / command: `debug_commands/PL_N-bp7-003_A01_T08_PL_N-bp7-003.command`
- `PL!N-bp7-003#A01#T09` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-bp7-003_A01_T09_PL_N-bp7-003.command`
- `PL!N-bp7-003#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-bp7-003_A02_T01_PL_N-bp7-003.command`
- `PL!N-bp7-003#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-bp7-003_A02_T02_PL_N-bp7-003.command`
- `PL!N-bp7-003#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-bp7-003_A02_T03_PL_N-bp7-003.command`
- `PL!N-bp7-003#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp7-003_A02_T04_PL_N-bp7-003.command`

## PL!N-bp7-007
- `PL!N-bp7-007#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_N-bp7-007_A01_T01_PL_N-bp7-007.command`
- `PL!N-bp7-007#A01#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_N-bp7-007_A01_T02_PL_N-bp7-007.command`
- `PL!N-bp7-007#A01#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_N-bp7-007_A01_T03_PL_N-bp7-007.command`
- `PL!N-bp7-007#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_N-bp7-007_A02_T01_PL_N-bp7-007.command`
- `PL!N-bp7-007#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_N-bp7-007_A02_T02_PL_N-bp7-007.command`
- `PL!N-bp7-007#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_N-bp7-007_A02_T03_PL_N-bp7-007.command`
- `PL!N-bp7-007#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_N-bp7-007_A02_T04_PL_N-bp7-007.command`
- `PL!N-bp7-007#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_N-bp7-007_A02_T05_PL_N-bp7-007.command`
- `PL!N-bp7-007#A03#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp7-007_A03_T01_PL_N-bp7-007.command`
- `PL!N-bp7-007#A03#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp7-007_A03_T02_PL_N-bp7-007.command`

## PL!N-bp7-009
- `PL!N-bp7-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-bp7-009_A01_T01_PL_N-bp7-009.command`

## PL!N-bp7-019
- `PL!N-bp7-019#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_N-bp7-019_A01_T01_PL_N-bp7-019.command`
- `PL!N-bp7-019#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_N-bp7-019_A01_T02_PL_N-bp7-019.command`
- `PL!N-bp7-019#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_N-bp7-019_A01_T03_PL_N-bp7-019.command`

## PL!N-bp7-027
- `PL!N-bp7-027#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-bp7-027_A01_T01_PL_N-bp7-027.command`
- `PL!N-bp7-027#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_N-bp7-027_A01_T02_PL_N-bp7-027.command`
- `PL!N-bp7-027#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_N-bp7-027_A01_T03_PL_N-bp7-027.command`
- `PL!N-bp7-027#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-bp7-027_A01_T04_PL_N-bp7-027.command`

## PL!N-pb1-001
- `PL!N-pb1-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-001_A01_T01_PL_N-pb1-001.command`
- `PL!N-pb1-001#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-pb1-001_A01_T02_PL_N-pb1-001.command`
- `PL!N-pb1-001#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-pb1-001_A01_T03_PL_N-pb1-001.command`
- `PL!N-pb1-001#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-001_A01_T04_PL_N-pb1-001.command`
- `PL!N-pb1-001#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-001_A01_T05_PL_N-pb1-001.command`
- `PL!N-pb1-001#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-001_A02_T01_PL_N-pb1-001.command`
- `PL!N-pb1-001#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_N-pb1-001_A02_T02_PL_N-pb1-001.command`
- `PL!N-pb1-001#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_N-pb1-001_A02_T03_PL_N-pb1-001.command`
- `PL!N-pb1-001#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_N-pb1-001_A02_T04_PL_N-pb1-001.command`
- `PL!N-pb1-001#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_N-pb1-001_A02_T05_PL_N-pb1-001.command`

## PL!N-pb1-002
- `PL!N-pb1-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-002_A01_T01_PL_N-pb1-002.command`

## PL!N-pb1-004
- `PL!N-pb1-004#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-004_A02_T01_PL_N-pb1-004.command`
- `PL!N-pb1-004#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-pb1-004_A02_T02_PL_N-pb1-004.command`
- `PL!N-pb1-004#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-pb1-004_A02_T03_PL_N-pb1-004.command`
- `PL!N-pb1-004#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-004_A02_T04_PL_N-pb1-004.command`

## PL!N-pb1-006
- `PL!N-pb1-006#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-006_A01_T01_PL_N-pb1-006.command`
- `PL!N-pb1-006#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-006_A01_T02_PL_N-pb1-006.command`
- `PL!N-pb1-006#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-006_A01_T03_PL_N-pb1-006.command`

## PL!N-pb1-008
- `PL!N-pb1-008#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-008_A01_T01_PL_N-pb1-008.command`
- `PL!N-pb1-008#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_N-pb1-008_A01_T02_PL_N-pb1-008.command`
- `PL!N-pb1-008#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_N-pb1-008_A01_T03_PL_N-pb1-008.command`
- `PL!N-pb1-008#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_N-pb1-008_A01_T04_PL_N-pb1-008.command`
- `PL!N-pb1-008#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_N-pb1-008_A01_T05_PL_N-pb1-008.command`
- `PL!N-pb1-008#A02#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-008_A02_T01_PL_N-pb1-008.command`

## PL!N-pb1-009
- `PL!N-pb1-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-009_A01_T01_PL_N-pb1-009.command`
- `PL!N-pb1-009#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-pb1-009_A01_T02_PL_N-pb1-009.command`
- `PL!N-pb1-009#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-pb1-009_A01_T03_PL_N-pb1-009.command`
- `PL!N-pb1-009#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-pb1-009_A01_T04_PL_N-pb1-009.command`
- `PL!N-pb1-009#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-pb1-009_A01_T05_PL_N-pb1-009.command`
- `PL!N-pb1-009#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-009_A01_T06_PL_N-pb1-009.command`

## PL!N-pb1-011
- `PL!N-pb1-011#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-011_A01_T01_PL_N-pb1-011.command`
- `PL!N-pb1-011#A01#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_N-pb1-011_A01_T02_PL_N-pb1-011.command`
- `PL!N-pb1-011#A01#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_N-pb1-011_A01_T03_PL_N-pb1-011.command`
- `PL!N-pb1-011#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-011_A02_T01_PL_N-pb1-011.command`
- `PL!N-pb1-011#A02#T02` 起動 / 条件不成立 / command: `debug_commands/PL_N-pb1-011_A02_T02_PL_N-pb1-011.command`
- `PL!N-pb1-011#A02#T03` 起動 / 境界値 / command: `debug_commands/PL_N-pb1-011_A02_T03_PL_N-pb1-011.command`
- `PL!N-pb1-011#A02#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-011_A02_T04_PL_N-pb1-011.command`
- `PL!N-pb1-011#A02#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-011_A02_T05_PL_N-pb1-011.command`
- `PL!N-pb1-011#A02#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_N-pb1-011_A02_T06_PL_N-pb1-011.command`
- `PL!N-pb1-011#A02#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-pb1-011_A02_T07_PL_N-pb1-011.command`

## PL!N-pb1-012
- `PL!N-pb1-012#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-012_A02_T01_PL_N-pb1-012.command`
- `PL!N-pb1-012#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-012_A02_T02_PL_N-pb1-012.command`

## PL!N-pb1-013
- `PL!N-pb1-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-013_A01_T01_PL_N-pb1-013.command`
- `PL!N-pb1-013#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-013_A01_T02_PL_N-pb1-013.command`
- `PL!N-pb1-013#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-013_A01_T03_PL_N-pb1-013.command`

## PL!N-pb1-014
- `PL!N-pb1-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-014_A01_T01_PL_N-pb1-014.command`
- `PL!N-pb1-014#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-pb1-014_A01_T02_PL_N-pb1-014.command`
- `PL!N-pb1-014#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-pb1-014_A01_T03_PL_N-pb1-014.command`

## PL!N-pb1-015
- `PL!N-pb1-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-015_A01_T01_PL_N-pb1-015.command`
- `PL!N-pb1-015#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-015_A01_T02_PL_N-pb1-015.command`
- `PL!N-pb1-015#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-015_A01_T03_PL_N-pb1-015.command`

## PL!N-pb1-016
- `PL!N-pb1-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-016_A01_T01_PL_N-pb1-016.command`

## PL!N-pb1-017
- `PL!N-pb1-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-017_A01_T01_PL_N-pb1-017.command`
- `PL!N-pb1-017#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-017_A01_T02_PL_N-pb1-017.command`
- `PL!N-pb1-017#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-017_A01_T03_PL_N-pb1-017.command`

## PL!N-pb1-018
- `PL!N-pb1-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-018_A01_T01_PL_N-pb1-018.command`

## PL!N-pb1-019
- `PL!N-pb1-019#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-019_A01_T01_PL_N-pb1-019.command`
- `PL!N-pb1-019#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-pb1-019_A01_T02_PL_N-pb1-019.command`
- `PL!N-pb1-019#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-pb1-019_A01_T03_PL_N-pb1-019.command`

## PL!N-pb1-020
- `PL!N-pb1-020#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-020_A01_T01_PL_N-pb1-020.command`
- `PL!N-pb1-020#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-pb1-020_A01_T02_PL_N-pb1-020.command`
- `PL!N-pb1-020#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-pb1-020_A01_T03_PL_N-pb1-020.command`

## PL!N-pb1-021
- `PL!N-pb1-021#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-021_A01_T01_PL_N-pb1-021.command`

## PL!N-pb1-022
- `PL!N-pb1-022#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-022_A01_T01_PL_N-pb1-022.command`
- `PL!N-pb1-022#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_N-pb1-022_A01_T02_PL_N-pb1-022.command`
- `PL!N-pb1-022#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_N-pb1-022_A01_T03_PL_N-pb1-022.command`

## PL!N-pb1-023
- `PL!N-pb1-023#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-023_A01_T01_PL_N-pb1-023.command`
- `PL!N-pb1-023#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-023_A01_T02_PL_N-pb1-023.command`
- `PL!N-pb1-023#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-023_A01_T03_PL_N-pb1-023.command`

## PL!N-pb1-024
- `PL!N-pb1-024#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-024_A01_T01_PL_N-pb1-024.command`

## PL!N-pb1-028
- `PL!N-pb1-028#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-028_A01_T01_PL_N-pb1-028.command`
- `PL!N-pb1-028#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-028_A01_T02_PL_N-pb1-028.command`
- `PL!N-pb1-028#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-028_A01_T03_PL_N-pb1-028.command`

## PL!N-pb1-034
- `PL!N-pb1-034#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-034_A01_T01_PL_N-pb1-034.command`
- `PL!N-pb1-034#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-pb1-034_A01_T02_PL_N-pb1-034.command`
- `PL!N-pb1-034#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-pb1-034_A01_T03_PL_N-pb1-034.command`
- `PL!N-pb1-034#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-034_A01_T04_PL_N-pb1-034.command`

## PL!N-pb1-035
- `PL!N-pb1-035#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-035_A01_T01_PL_N-pb1-035.command`
- `PL!N-pb1-035#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-pb1-035_A01_T02_PL_N-pb1-035.command`
- `PL!N-pb1-035#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-pb1-035_A01_T03_PL_N-pb1-035.command`

## PL!N-pb1-036
- `PL!N-pb1-036#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-036_A01_T01_PL_N-pb1-036.command`
- `PL!N-pb1-036#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-pb1-036_A01_T02_PL_N-pb1-036.command`
- `PL!N-pb1-036#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-pb1-036_A01_T03_PL_N-pb1-036.command`
- `PL!N-pb1-036#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-036_A01_T04_PL_N-pb1-036.command`

## PL!N-pb1-037
- `PL!N-pb1-037#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-037_A01_T01_PL_N-pb1-037.command`
- `PL!N-pb1-037#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-pb1-037_A01_T02_PL_N-pb1-037.command`
- `PL!N-pb1-037#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-pb1-037_A01_T03_PL_N-pb1-037.command`
- `PL!N-pb1-037#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-037_A01_T04_PL_N-pb1-037.command`

## PL!N-pb1-038
- `PL!N-pb1-038#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-038_A01_T01_PL_N-pb1-038.command`
- `PL!N-pb1-038#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-pb1-038_A01_T02_PL_N-pb1-038.command`
- `PL!N-pb1-038#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-pb1-038_A01_T03_PL_N-pb1-038.command`
- `PL!N-pb1-038#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-038_A01_T04_PL_N-pb1-038.command`

## PL!N-pb1-039
- `PL!N-pb1-039#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-039_A01_T01_PL_N-pb1-039.command`
- `PL!N-pb1-039#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-pb1-039_A01_T02_PL_N-pb1-039.command`
- `PL!N-pb1-039#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-pb1-039_A01_T03_PL_N-pb1-039.command`
- `PL!N-pb1-039#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-pb1-039_A01_T04_PL_N-pb1-039.command`
- `PL!N-pb1-039#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-pb1-039_A01_T05_PL_N-pb1-039.command`
- `PL!N-pb1-039#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-039_A01_T06_PL_N-pb1-039.command`

## PL!N-pb1-042
- `PL!N-pb1-042#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-pb1-042_A01_T01_PL_N-pb1-042.command`
- `PL!N-pb1-042#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-pb1-042_A01_T02_PL_N-pb1-042.command`
- `PL!N-pb1-042#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-pb1-042_A01_T03_PL_N-pb1-042.command`
- `PL!N-pb1-042#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-pb1-042_A01_T04_PL_N-pb1-042.command`

## PL!N-sd1-001
- `PL!N-sd1-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-001_A01_T01_PL_N-sd1-001.command`
- `PL!N-sd1-001#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_N-sd1-001_A01_T02_PL_N-sd1-001.command`
- `PL!N-sd1-001#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_N-sd1-001_A01_T03_PL_N-sd1-001.command`
- `PL!N-sd1-001#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-001_A02_T01_PL_N-sd1-001.command`
- `PL!N-sd1-001#A02#T02` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-001_A02_T02_PL_N-sd1-001.command`
- `PL!N-sd1-001#A02#T03` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-001_A02_T03_PL_N-sd1-001.command`
- `PL!N-sd1-001#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-sd1-001_A02_T04_PL_N-sd1-001.command`

## PL!N-sd1-002
- `PL!N-sd1-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-002_A01_T01_PL_N-sd1-002.command`
- `PL!N-sd1-002#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-002_A01_T02_PL_N-sd1-002.command`
- `PL!N-sd1-002#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-002_A01_T03_PL_N-sd1-002.command`

## PL!N-sd1-003
- `PL!N-sd1-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-003_A01_T01_PL_N-sd1-003.command`
- `PL!N-sd1-003#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-003_A01_T02_PL_N-sd1-003.command`
- `PL!N-sd1-003#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-003_A01_T03_PL_N-sd1-003.command`

## PL!N-sd1-004
- `PL!N-sd1-004#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-004_A01_T01_PL_N-sd1-004.command`
- `PL!N-sd1-004#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-sd1-004_A01_T02_PL_N-sd1-004.command`
- `PL!N-sd1-004#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-sd1-004_A01_T03_PL_N-sd1-004.command`
- `PL!N-sd1-004#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-004_A01_T04_PL_N-sd1-004.command`
- `PL!N-sd1-004#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-004_A01_T05_PL_N-sd1-004.command`
- `PL!N-sd1-004#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-sd1-004_A01_T06_PL_N-sd1-004.command`

## PL!N-sd1-005
- `PL!N-sd1-005#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-005_A01_T01_PL_N-sd1-005.command`
- `PL!N-sd1-005#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-005_A01_T02_PL_N-sd1-005.command`
- `PL!N-sd1-005#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-005_A01_T03_PL_N-sd1-005.command`
- `PL!N-sd1-005#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-sd1-005_A01_T04_PL_N-sd1-005.command`
- `PL!N-sd1-005#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-sd1-005_A01_T05_PL_N-sd1-005.command`

## PL!N-sd1-006
- `PL!N-sd1-006#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-006_A01_T01_PL_N-sd1-006.command`
- `PL!N-sd1-006#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-006_A01_T02_PL_N-sd1-006.command`
- `PL!N-sd1-006#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-006_A01_T03_PL_N-sd1-006.command`

## PL!N-sd1-007
- `PL!N-sd1-007#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-007_A01_T01_PL_N-sd1-007.command`
- `PL!N-sd1-007#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-007_A01_T02_PL_N-sd1-007.command`
- `PL!N-sd1-007#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-007_A01_T03_PL_N-sd1-007.command`
- `PL!N-sd1-007#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-sd1-007_A01_T04_PL_N-sd1-007.command`
- `PL!N-sd1-007#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-sd1-007_A01_T05_PL_N-sd1-007.command`

## PL!N-sd1-008
- `PL!N-sd1-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-008_A01_T01_PL_N-sd1-008.command`

## PL!N-sd1-009
- `PL!N-sd1-009#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-009_A01_T01_PL_N-sd1-009.command`
- `PL!N-sd1-009#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-009_A01_T02_PL_N-sd1-009.command`
- `PL!N-sd1-009#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-009_A01_T03_PL_N-sd1-009.command`
- `PL!N-sd1-009#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_N-sd1-009_A01_T04_PL_N-sd1-009.command`
- `PL!N-sd1-009#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_N-sd1-009_A01_T05_PL_N-sd1-009.command`

## PL!N-sd1-010
- `PL!N-sd1-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-010_A01_T01_PL_N-sd1-010.command`
- `PL!N-sd1-010#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-010_A02_T01_PL_N-sd1-010.command`
- `PL!N-sd1-010#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_N-sd1-010_A02_T02_PL_N-sd1-010.command`
- `PL!N-sd1-010#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_N-sd1-010_A02_T03_PL_N-sd1-010.command`
- `PL!N-sd1-010#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-010_A02_T04_PL_N-sd1-010.command`
- `PL!N-sd1-010#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-010_A02_T05_PL_N-sd1-010.command`
- `PL!N-sd1-010#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-sd1-010_A02_T06_PL_N-sd1-010.command`

## PL!N-sd1-011
- `PL!N-sd1-011#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-011_A01_T01_PL_N-sd1-011.command`
- `PL!N-sd1-011#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_N-sd1-011_A01_T02_PL_N-sd1-011.command`
- `PL!N-sd1-011#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_N-sd1-011_A01_T03_PL_N-sd1-011.command`

## PL!N-sd1-013
- `PL!N-sd1-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-013_A01_T01_PL_N-sd1-013.command`

## PL!N-sd1-021
- `PL!N-sd1-021#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-021_A01_T01_PL_N-sd1-021.command`

## PL!N-sd1-022
- `PL!N-sd1-022#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-022_A01_T01_PL_N-sd1-022.command`

## PL!N-sd1-028
- `PL!N-sd1-028#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-sd1-028_A01_T01_PL_N-sd1-028.command`
- `PL!N-sd1-028#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_N-sd1-028_A01_T02_PL_N-sd1-028.command`
- `PL!N-sd1-028#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_N-sd1-028_A01_T03_PL_N-sd1-028.command`
- `PL!N-sd1-028#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-sd1-028_A01_T04_PL_N-sd1-028.command`

## PL!N-sd2-025
- `PL!N-sd2-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_N-sd2-025_A01_T01_PL_N-sd2-025.command`
- `PL!N-sd2-025#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_N-sd2-025_A01_T02_PL_N-sd2-025.command`

## PL!S-PR-013
- `PL!S-PR-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-013_A01_T01_PL_S-PR-013.command`
- `PL!S-PR-013#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-PR-013_A01_T02_PL_S-PR-013.command`
- `PL!S-PR-013#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-PR-013_A01_T03_PL_S-PR-013.command`
- `PL!S-PR-013#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-PR-013_A02_T01_PL_S-PR-013.command`
- `PL!S-PR-013#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-PR-013_A02_T02_PL_S-PR-013.command`
- `PL!S-PR-013#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-013_A02_T03_PL_S-PR-013.command`
- `PL!S-PR-013#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-PR-013_A02_T04_PL_S-PR-013.command`
- `PL!S-PR-013#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-PR-013_A02_T05_PL_S-PR-013.command`
- `PL!S-PR-013#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-PR-013_A02_T06_PL_S-PR-013.command`

## PL!S-PR-016
- `PL!S-PR-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-016_A01_T01_PL_S-PR-016.command`
- `PL!S-PR-016#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-PR-016_A01_T02_PL_S-PR-016.command`
- `PL!S-PR-016#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-016_A01_T03_PL_S-PR-016.command`

## PL!S-PR-019
- `PL!S-PR-019#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-019_A01_T01_PL_S-PR-019.command`
- `PL!S-PR-019#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-PR-019_A01_T02_PL_S-PR-019.command`
- `PL!S-PR-019#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-PR-019_A01_T03_PL_S-PR-019.command`
- `PL!S-PR-019#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-PR-019_A02_T01_PL_S-PR-019.command`
- `PL!S-PR-019#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-PR-019_A02_T02_PL_S-PR-019.command`
- `PL!S-PR-019#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-019_A02_T03_PL_S-PR-019.command`
- `PL!S-PR-019#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-PR-019_A02_T04_PL_S-PR-019.command`
- `PL!S-PR-019#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-PR-019_A02_T05_PL_S-PR-019.command`
- `PL!S-PR-019#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-PR-019_A02_T06_PL_S-PR-019.command`

## PL!S-PR-020
- `PL!S-PR-020#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-020_A01_T01_PL_S-PR-020.command`
- `PL!S-PR-020#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-PR-020_A01_T02_PL_S-PR-020.command`
- `PL!S-PR-020#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-020_A01_T03_PL_S-PR-020.command`

## PL!S-PR-021
- `PL!S-PR-021#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-021_A01_T01_PL_S-PR-021.command`
- `PL!S-PR-021#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-PR-021_A01_T02_PL_S-PR-021.command`
- `PL!S-PR-021#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-021_A01_T03_PL_S-PR-021.command`

## PL!S-PR-025
- `PL!S-PR-025#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-PR-025_A01_T01_PL_S-PR-025.command`
- `PL!S-PR-025#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-PR-025_A01_T02_PL_S-PR-025.command`
- `PL!S-PR-025#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-PR-025_A01_T03_PL_S-PR-025.command`

## PL!S-PR-026
- `PL!S-PR-026#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-PR-026_A01_T01_PL_S-PR-026.command`
- `PL!S-PR-026#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-PR-026_A01_T02_PL_S-PR-026.command`
- `PL!S-PR-026#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-PR-026_A01_T03_PL_S-PR-026.command`

## PL!S-PR-027
- `PL!S-PR-027#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-PR-027_A01_T01_PL_S-PR-027.command`
- `PL!S-PR-027#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-PR-027_A01_T02_PL_S-PR-027.command`
- `PL!S-PR-027#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-PR-027_A01_T03_PL_S-PR-027.command`

## PL!S-PR-028
- `PL!S-PR-028#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-028_A01_T01_PL_S-PR-028.command`
- `PL!S-PR-028#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-PR-028_A01_T02_PL_S-PR-028.command`
- `PL!S-PR-028#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-028_A01_T03_PL_S-PR-028.command`

## PL!S-PR-032
- `PL!S-PR-032#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-032_A01_T01_PL_S-PR-032.command`
- `PL!S-PR-032#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-PR-032_A01_T02_PL_S-PR-032.command`
- `PL!S-PR-032#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-032_A01_T03_PL_S-PR-032.command`

## PL!S-PR-033
- `PL!S-PR-033#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-033_A01_T01_PL_S-PR-033.command`
- `PL!S-PR-033#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-PR-033_A01_T02_PL_S-PR-033.command`
- `PL!S-PR-033#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-033_A01_T03_PL_S-PR-033.command`

## PL!S-PR-037
- `PL!S-PR-037#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_S-PR-037_A01_T01_PL_S-PR-037.command`
- `PL!S-PR-037#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_S-PR-037_A01_T02_PL_S-PR-037.command`
- `PL!S-PR-037#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_S-PR-037_A01_T03_PL_S-PR-037.command`
- `PL!S-PR-037#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_S-PR-037_A01_T04_PL_S-PR-037.command`
- `PL!S-PR-037#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_S-PR-037_A01_T05_PL_S-PR-037.command`

## PL!S-PR-038
- `PL!S-PR-038#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-PR-038_A01_T01_PL_S-PR-038.command`
- `PL!S-PR-038#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-PR-038_A01_T02_PL_S-PR-038.command`
- `PL!S-PR-038#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-PR-038_A01_T03_PL_S-PR-038.command`
- `PL!S-PR-038#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_S-PR-038_A01_T04_PL_S-PR-038.command`
- `PL!S-PR-038#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_S-PR-038_A01_T05_PL_S-PR-038.command`

## PL!S-PR-040
- `PL!S-PR-040#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-PR-040_A01_T01_PL_S-PR-040.command`
- `PL!S-PR-040#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-PR-040_A01_T02_PL_S-PR-040.command`
- `PL!S-PR-040#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_S-PR-040_A01_T03_PL_S-PR-040.command`
- `PL!S-PR-040#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_S-PR-040_A01_T04_PL_S-PR-040.command`
- `PL!S-PR-040#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_S-PR-040_A01_T05_PL_S-PR-040.command`
- `PL!S-PR-040#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_S-PR-040_A01_T06_PL_S-PR-040.command`
- `PL!S-PR-040#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_S-PR-040_A01_T07_PL_S-PR-040.command`

## PL!S-PR-041
- `PL!S-PR-041#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-041_A01_T01_PL_S-PR-041.command`
- `PL!S-PR-041#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-PR-041_A01_T02_PL_S-PR-041.command`
- `PL!S-PR-041#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-PR-041_A01_T03_PL_S-PR-041.command`

## PL!S-PR-044
- `PL!S-PR-044#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-044_A01_T01_PL_S-PR-044.command`
- `PL!S-PR-044#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-PR-044_A01_T02_PL_S-PR-044.command`
- `PL!S-PR-044#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-PR-044_A01_T03_PL_S-PR-044.command`

## PL!S-PR-045
- `PL!S-PR-045#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-PR-045_A01_T01_PL_S-PR-045.command`
- `PL!S-PR-045#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-PR-045_A01_T02_PL_S-PR-045.command`
- `PL!S-PR-045#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-PR-045_A01_T03_PL_S-PR-045.command`

## PL!S-bp2-002
- `PL!S-bp2-002#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-002_A01_T01_PL_S-bp2-002.command`
- `PL!S-bp2-002#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-bp2-002_A01_T02_PL_S-bp2-002.command`
- `PL!S-bp2-002#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_S-bp2-002_A01_T03_PL_S-bp2-002.command`

## PL!S-bp2-003
- `PL!S-bp2-003#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-003_A01_T01_PL_S-bp2-003.command`
- `PL!S-bp2-003#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-bp2-003_A01_T02_PL_S-bp2-003.command`
- `PL!S-bp2-003#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_S-bp2-003_A01_T03_PL_S-bp2-003.command`
- `PL!S-bp2-003#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_S-bp2-003_A01_T04_PL_S-bp2-003.command`
- `PL!S-bp2-003#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_S-bp2-003_A01_T05_PL_S-bp2-003.command`
- `PL!S-bp2-003#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_S-bp2-003_A01_T06_PL_S-bp2-003.command`
- `PL!S-bp2-003#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp2-003_A01_T07_PL_S-bp2-003.command`

## PL!S-bp2-004
- `PL!S-bp2-004#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-004_A01_T01_PL_S-bp2-004.command`
- `PL!S-bp2-004#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-bp2-004_A01_T02_PL_S-bp2-004.command`
- `PL!S-bp2-004#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_S-bp2-004_A01_T03_PL_S-bp2-004.command`
- `PL!S-bp2-004#A01#T04` 自動 / 回数制限超過 / command: `debug_commands/PL_S-bp2-004_A01_T04_PL_S-bp2-004.command`
- `PL!S-bp2-004#A01#T05` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp2-004_A01_T05_PL_S-bp2-004.command`

## PL!S-bp2-005
- `PL!S-bp2-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-005_A01_T01_PL_S-bp2-005.command`
- `PL!S-bp2-005#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp2-005_A01_T02_PL_S-bp2-005.command`
- `PL!S-bp2-005#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp2-005_A01_T03_PL_S-bp2-005.command`
- `PL!S-bp2-005#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp2-005_A01_T04_PL_S-bp2-005.command`
- `PL!S-bp2-005#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp2-005_A01_T05_PL_S-bp2-005.command`

## PL!S-bp2-006
- `PL!S-bp2-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-006_A01_T01_PL_S-bp2-006.command`
- `PL!S-bp2-006#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp2-006_A01_T02_PL_S-bp2-006.command`
- `PL!S-bp2-006#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp2-006_A01_T03_PL_S-bp2-006.command`
- `PL!S-bp2-006#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp2-006_A01_T04_PL_S-bp2-006.command`
- `PL!S-bp2-006#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp2-006_A01_T05_PL_S-bp2-006.command`

## PL!S-bp2-007
- `PL!S-bp2-007#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-007_A01_T01_PL_S-bp2-007.command`
- `PL!S-bp2-007#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-bp2-007_A01_T02_PL_S-bp2-007.command`
- `PL!S-bp2-007#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_S-bp2-007_A01_T03_PL_S-bp2-007.command`
- `PL!S-bp2-007#A01#T04` 自動 / 回数制限超過 / command: `debug_commands/PL_S-bp2-007_A01_T04_PL_S-bp2-007.command`
- `PL!S-bp2-007#A01#T05` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp2-007_A01_T05_PL_S-bp2-007.command`
- `PL!S-bp2-007#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-007_A02_T01_PL_S-bp2-007.command`
- `PL!S-bp2-007#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp2-007_A02_T02_PL_S-bp2-007.command`
- `PL!S-bp2-007#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp2-007_A02_T03_PL_S-bp2-007.command`
- `PL!S-bp2-007#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-bp2-007_A02_T04_PL_S-bp2-007.command`
- `PL!S-bp2-007#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-bp2-007_A02_T05_PL_S-bp2-007.command`
- `PL!S-bp2-007#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp2-007_A02_T06_PL_S-bp2-007.command`

## PL!S-bp2-008
- `PL!S-bp2-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-008_A01_T01_PL_S-bp2-008.command`
- `PL!S-bp2-008#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp2-008_A01_T02_PL_S-bp2-008.command`
- `PL!S-bp2-008#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp2-008_A01_T03_PL_S-bp2-008.command`
- `PL!S-bp2-008#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-008_A02_T01_PL_S-bp2-008.command`
- `PL!S-bp2-008#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_S-bp2-008_A02_T02_PL_S-bp2-008.command`
- `PL!S-bp2-008#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_S-bp2-008_A02_T03_PL_S-bp2-008.command`
- `PL!S-bp2-008#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_S-bp2-008_A02_T04_PL_S-bp2-008.command`
- `PL!S-bp2-008#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_S-bp2-008_A02_T05_PL_S-bp2-008.command`

## PL!S-bp2-009
- `PL!S-bp2-009#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-009_A01_T01_PL_S-bp2-009.command`
- `PL!S-bp2-009#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-bp2-009_A01_T02_PL_S-bp2-009.command`
- `PL!S-bp2-009#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-bp2-009_A01_T03_PL_S-bp2-009.command`

## PL!S-bp2-010
- `PL!S-bp2-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-010_A01_T01_PL_S-bp2-010.command`

## PL!S-bp2-016
- `PL!S-bp2-016#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-016_A01_T01_PL_S-bp2-016.command`
- `PL!S-bp2-016#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-bp2-016_A01_T02_PL_S-bp2-016.command`
- `PL!S-bp2-016#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-bp2-016_A01_T03_PL_S-bp2-016.command`

## PL!S-bp2-021
- `PL!S-bp2-021#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-021_A01_T01_PL_S-bp2-021.command`
- `PL!S-bp2-021#A01#T02` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_S-bp2-021_A01_T02_PL_S-bp2-021.command`
- `PL!S-bp2-021#A01#T03` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp2-021_A01_T03_PL_S-bp2-021.command`
- `PL!S-bp2-021#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp2-021_A01_T04_PL_S-bp2-021.command`

## PL!S-bp2-022
- `PL!S-bp2-022#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-022_A01_T01_PL_S-bp2-022.command`
- `PL!S-bp2-022#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp2-022_A01_T02_PL_S-bp2-022.command`
- `PL!S-bp2-022#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp2-022_A01_T03_PL_S-bp2-022.command`
- `PL!S-bp2-022#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp2-022_A01_T04_PL_S-bp2-022.command`

## PL!S-bp2-023
- `PL!S-bp2-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-023_A01_T01_PL_S-bp2-023.command`
- `PL!S-bp2-023#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp2-023_A01_T02_PL_S-bp2-023.command`
- `PL!S-bp2-023#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp2-023_A01_T03_PL_S-bp2-023.command`
- `PL!S-bp2-023#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp2-023_A01_T04_PL_S-bp2-023.command`
- `PL!S-bp2-023#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp2-023_A01_T05_PL_S-bp2-023.command`
- `PL!S-bp2-023#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp2-023_A01_T06_PL_S-bp2-023.command`

## PL!S-bp2-024
- `PL!S-bp2-024#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-024_A02_T01_PL_S-bp2-024.command`
- `PL!S-bp2-024#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp2-024_A02_T02_PL_S-bp2-024.command`

## PL!S-bp2-025
- `PL!S-bp2-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp2-025_A01_T01_PL_S-bp2-025.command`
- `PL!S-bp2-025#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp2-025_A01_T02_PL_S-bp2-025.command`
- `PL!S-bp2-025#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp2-025_A01_T03_PL_S-bp2-025.command`
- `PL!S-bp2-025#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp2-025_A01_T04_PL_S-bp2-025.command`
- `PL!S-bp2-025#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp2-025_A01_T05_PL_S-bp2-025.command`
- `PL!S-bp2-025#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp2-025_A01_T06_PL_S-bp2-025.command`

## PL!S-bp3-002
- `PL!S-bp3-002#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-002_A01_T01_PL_S-bp3-002.command`
- `PL!S-bp3-002#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp3-002_A01_T02_PL_S-bp3-002.command`
- `PL!S-bp3-002#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp3-002_A01_T03_PL_S-bp3-002.command`
- `PL!S-bp3-002#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp3-002_A01_T04_PL_S-bp3-002.command`

## PL!S-bp3-003
- `PL!S-bp3-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-003_A01_T01_PL_S-bp3-003.command`
- `PL!S-bp3-003#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-003_A01_T02_PL_S-bp3-003.command`
- `PL!S-bp3-003#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-003_A01_T03_PL_S-bp3-003.command`
- `PL!S-bp3-003#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-003_A02_T01_PL_S-bp3-003.command`
- `PL!S-bp3-003#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp3-003_A02_T02_PL_S-bp3-003.command`
- `PL!S-bp3-003#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp3-003_A02_T03_PL_S-bp3-003.command`
- `PL!S-bp3-003#A02#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-003_A02_T04_PL_S-bp3-003.command`
- `PL!S-bp3-003#A02#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-003_A02_T05_PL_S-bp3-003.command`
- `PL!S-bp3-003#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp3-003_A02_T06_PL_S-bp3-003.command`

## PL!S-bp3-004
- `PL!S-bp3-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-004_A01_T01_PL_S-bp3-004.command`
- `PL!S-bp3-004#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-004_A01_T02_PL_S-bp3-004.command`
- `PL!S-bp3-004#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-004_A01_T03_PL_S-bp3-004.command`

## PL!S-bp3-005
- `PL!S-bp3-005#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-005_A01_T01_PL_S-bp3-005.command`
- `PL!S-bp3-005#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp3-005_A01_T02_PL_S-bp3-005.command`
- `PL!S-bp3-005#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp3-005_A01_T03_PL_S-bp3-005.command`
- `PL!S-bp3-005#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp3-005_A01_T04_PL_S-bp3-005.command`

## PL!S-bp3-007
- `PL!S-bp3-007#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-007_A01_T01_PL_S-bp3-007.command`
- `PL!S-bp3-007#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_S-bp3-007_A01_T02_PL_S-bp3-007.command`
- `PL!S-bp3-007#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_S-bp3-007_A01_T03_PL_S-bp3-007.command`
- `PL!S-bp3-007#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-007_A01_T04_PL_S-bp3-007.command`
- `PL!S-bp3-007#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-007_A01_T05_PL_S-bp3-007.command`
- `PL!S-bp3-007#A01#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_S-bp3-007_A01_T06_PL_S-bp3-007.command`
- `PL!S-bp3-007#A01#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp3-007_A01_T07_PL_S-bp3-007.command`

## PL!S-bp3-008
- `PL!S-bp3-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-008_A01_T01_PL_S-bp3-008.command`
- `PL!S-bp3-008#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_S-bp3-008_A01_T02_PL_S-bp3-008.command`
- `PL!S-bp3-008#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_S-bp3-008_A01_T03_PL_S-bp3-008.command`
- `PL!S-bp3-008#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-008_A01_T04_PL_S-bp3-008.command`
- `PL!S-bp3-008#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-008_A01_T05_PL_S-bp3-008.command`

## PL!S-bp3-009
- `PL!S-bp3-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-009_A01_T01_PL_S-bp3-009.command`
- `PL!S-bp3-009#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-009_A01_T02_PL_S-bp3-009.command`
- `PL!S-bp3-009#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-009_A01_T03_PL_S-bp3-009.command`

## PL!S-bp3-010
- `PL!S-bp3-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-010_A01_T01_PL_S-bp3-010.command`
- `PL!S-bp3-010#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp3-010_A01_T02_PL_S-bp3-010.command`
- `PL!S-bp3-010#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp3-010_A01_T03_PL_S-bp3-010.command`

## PL!S-bp3-011
- `PL!S-bp3-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-011_A01_T01_PL_S-bp3-011.command`
- `PL!S-bp3-011#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp3-011_A01_T02_PL_S-bp3-011.command`
- `PL!S-bp3-011#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp3-011_A01_T03_PL_S-bp3-011.command`

## PL!S-bp3-012
- `PL!S-bp3-012#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-012_A01_T01_PL_S-bp3-012.command`
- `PL!S-bp3-012#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp3-012_A01_T02_PL_S-bp3-012.command`
- `PL!S-bp3-012#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp3-012_A01_T03_PL_S-bp3-012.command`
- `PL!S-bp3-012#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-012_A01_T04_PL_S-bp3-012.command`
- `PL!S-bp3-012#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-012_A01_T05_PL_S-bp3-012.command`

## PL!S-bp3-017
- `PL!S-bp3-017#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-017_A01_T01_PL_S-bp3-017.command`
- `PL!S-bp3-017#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp3-017_A01_T02_PL_S-bp3-017.command`
- `PL!S-bp3-017#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp3-017_A01_T03_PL_S-bp3-017.command`
- `PL!S-bp3-017#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-017_A01_T04_PL_S-bp3-017.command`
- `PL!S-bp3-017#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-017_A01_T05_PL_S-bp3-017.command`

## PL!S-bp3-019
- `PL!S-bp3-019#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-019_A01_T01_PL_S-bp3-019.command`
- `PL!S-bp3-019#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp3-019_A01_T02_PL_S-bp3-019.command`
- `PL!S-bp3-019#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp3-019_A01_T03_PL_S-bp3-019.command`
- `PL!S-bp3-019#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp3-019_A01_T04_PL_S-bp3-019.command`

## PL!S-bp3-020
- `PL!S-bp3-020#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-020_A01_T01_PL_S-bp3-020.command`
- `PL!S-bp3-020#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-bp3-020_A01_T02_PL_S-bp3-020.command`
- `PL!S-bp3-020#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_S-bp3-020_A01_T03_PL_S-bp3-020.command`
- `PL!S-bp3-020#A01#T04` 自動 / 回数制限超過 / command: `debug_commands/PL_S-bp3-020_A01_T04_PL_S-bp3-020.command`
- `PL!S-bp3-020#A01#T05` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp3-020_A01_T05_PL_S-bp3-020.command`

## PL!S-bp3-021
- `PL!S-bp3-021#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-021_A01_T01_PL_S-bp3-021.command`
- `PL!S-bp3-021#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp3-021_A01_T02_PL_S-bp3-021.command`
- `PL!S-bp3-021#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp3-021_A01_T03_PL_S-bp3-021.command`
- `PL!S-bp3-021#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-bp3-021_A01_T04_PL_S-bp3-021.command`
- `PL!S-bp3-021#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-bp3-021_A01_T05_PL_S-bp3-021.command`
- `PL!S-bp3-021#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp3-021_A01_T06_PL_S-bp3-021.command`

## PL!S-bp3-025
- `PL!S-bp3-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp3-025_A01_T01_PL_S-bp3-025.command`
- `PL!S-bp3-025#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp3-025_A01_T02_PL_S-bp3-025.command`
- `PL!S-bp3-025#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp3-025_A01_T03_PL_S-bp3-025.command`
- `PL!S-bp3-025#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp3-025_A01_T04_PL_S-bp3-025.command`

## PL!S-bp5-001
- `PL!S-bp5-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-001_A01_T01_PL_S-bp5-001.command`
- `PL!S-bp5-001#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp5-001_A01_T02_PL_S-bp5-001.command`
- `PL!S-bp5-001#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp5-001_A01_T03_PL_S-bp5-001.command`

## PL!S-bp5-002
- `PL!S-bp5-002#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-002_A01_T01_PL_S-bp5-002.command`
- `PL!S-bp5-002#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp5-002_A01_T02_PL_S-bp5-002.command`
- `PL!S-bp5-002#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp5-002_A01_T03_PL_S-bp5-002.command`
- `PL!S-bp5-002#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-002_A01_T04_PL_S-bp5-002.command`

## PL!S-bp5-003
- `PL!S-bp5-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-003_A01_T01_PL_S-bp5-003.command`
- `PL!S-bp5-003#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-003_A01_T02_PL_S-bp5-003.command`
- `PL!S-bp5-003#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-003_A01_T03_PL_S-bp5-003.command`
- `PL!S-bp5-003#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp5-003_A01_T04_PL_S-bp5-003.command`
- `PL!S-bp5-003#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp5-003_A01_T05_PL_S-bp5-003.command`

## PL!S-bp5-005
- `PL!S-bp5-005#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-005_A01_T01_PL_S-bp5-005.command`
- `PL!S-bp5-005#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-005_A01_T02_PL_S-bp5-005.command`
- `PL!S-bp5-005#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-005_A01_T03_PL_S-bp5-005.command`
- `PL!S-bp5-005#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-bp5-005_A01_T04_PL_S-bp5-005.command`
- `PL!S-bp5-005#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-bp5-005_A01_T05_PL_S-bp5-005.command`
- `PL!S-bp5-005#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-005_A01_T06_PL_S-bp5-005.command`

## PL!S-bp5-006
- `PL!S-bp5-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-006_A01_T01_PL_S-bp5-006.command`
- `PL!S-bp5-006#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp5-006_A01_T02_PL_S-bp5-006.command`
- `PL!S-bp5-006#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp5-006_A01_T03_PL_S-bp5-006.command`

## PL!S-bp5-007
- `PL!S-bp5-007#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-007_A01_T01_PL_S-bp5-007.command`
- `PL!S-bp5-007#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-007_A01_T02_PL_S-bp5-007.command`

## PL!S-bp5-009
- `PL!S-bp5-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-009_A01_T01_PL_S-bp5-009.command`
- `PL!S-bp5-009#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp5-009_A01_T02_PL_S-bp5-009.command`
- `PL!S-bp5-009#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp5-009_A01_T03_PL_S-bp5-009.command`
- `PL!S-bp5-009#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-009_A01_T04_PL_S-bp5-009.command`
- `PL!S-bp5-009#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-009_A01_T05_PL_S-bp5-009.command`
- `PL!S-bp5-009#A01#T06` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp5-009_A01_T06_PL_S-bp5-009.command`
- `PL!S-bp5-009#A01#T07` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp5-009_A01_T07_PL_S-bp5-009.command`

## PL!S-bp5-010
- `PL!S-bp5-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-010_A01_T01_PL_S-bp5-010.command`
- `PL!S-bp5-010#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp5-010_A01_T02_PL_S-bp5-010.command`
- `PL!S-bp5-010#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp5-010_A01_T03_PL_S-bp5-010.command`

## PL!S-bp5-011
- `PL!S-bp5-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-011_A01_T01_PL_S-bp5-011.command`
- `PL!S-bp5-011#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp5-011_A01_T02_PL_S-bp5-011.command`
- `PL!S-bp5-011#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp5-011_A01_T03_PL_S-bp5-011.command`

## PL!S-bp5-013
- `PL!S-bp5-013#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-013_A01_T01_PL_S-bp5-013.command`
- `PL!S-bp5-013#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp5-013_A01_T02_PL_S-bp5-013.command`
- `PL!S-bp5-013#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp5-013_A01_T03_PL_S-bp5-013.command`
- `PL!S-bp5-013#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-013_A01_T04_PL_S-bp5-013.command`
- `PL!S-bp5-013#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-013_A01_T05_PL_S-bp5-013.command`
- `PL!S-bp5-013#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-013_A01_T06_PL_S-bp5-013.command`

## PL!S-bp5-014
- `PL!S-bp5-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-014_A01_T01_PL_S-bp5-014.command`

## PL!S-bp5-015
- `PL!S-bp5-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-015_A01_T01_PL_S-bp5-015.command`

## PL!S-bp5-016
- `PL!S-bp5-016#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-016_A01_T01_PL_S-bp5-016.command`
- `PL!S-bp5-016#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp5-016_A01_T02_PL_S-bp5-016.command`
- `PL!S-bp5-016#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp5-016_A01_T03_PL_S-bp5-016.command`
- `PL!S-bp5-016#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-016_A01_T04_PL_S-bp5-016.command`
- `PL!S-bp5-016#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-016_A01_T05_PL_S-bp5-016.command`
- `PL!S-bp5-016#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-016_A01_T06_PL_S-bp5-016.command`

## PL!S-bp5-017
- `PL!S-bp5-017#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-017_A01_T01_PL_S-bp5-017.command`
- `PL!S-bp5-017#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp5-017_A01_T02_PL_S-bp5-017.command`
- `PL!S-bp5-017#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp5-017_A01_T03_PL_S-bp5-017.command`
- `PL!S-bp5-017#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-017_A01_T04_PL_S-bp5-017.command`
- `PL!S-bp5-017#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-017_A01_T05_PL_S-bp5-017.command`
- `PL!S-bp5-017#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-017_A01_T06_PL_S-bp5-017.command`

## PL!S-bp5-019
- `PL!S-bp5-019#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-019_A01_T01_PL_S-bp5-019.command`
- `PL!S-bp5-019#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp5-019_A01_T02_PL_S-bp5-019.command`
- `PL!S-bp5-019#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp5-019_A01_T03_PL_S-bp5-019.command`
- `PL!S-bp5-019#A01#T04` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-019_A01_T04_PL_S-bp5-019.command`
- `PL!S-bp5-019#A01#T05` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-019_A01_T05_PL_S-bp5-019.command`
- `PL!S-bp5-019#A01#T06` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-019_A01_T06_PL_S-bp5-019.command`

## PL!S-bp5-020
- `PL!S-bp5-020#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-020_A01_T01_PL_S-bp5-020.command`
- `PL!S-bp5-020#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp5-020_A01_T02_PL_S-bp5-020.command`
- `PL!S-bp5-020#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp5-020_A01_T03_PL_S-bp5-020.command`
- `PL!S-bp5-020#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-020_A01_T04_PL_S-bp5-020.command`

## PL!S-bp5-022
- `PL!S-bp5-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-022_A01_T01_PL_S-bp5-022.command`
- `PL!S-bp5-022#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-022_A01_T02_PL_S-bp5-022.command`
- `PL!S-bp5-022#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-022_A01_T03_PL_S-bp5-022.command`
- `PL!S-bp5-022#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-022_A01_T04_PL_S-bp5-022.command`
- `PL!S-bp5-022#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-022_A02_T01_PL_S-bp5-022.command`
- `PL!S-bp5-022#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp5-022_A02_T02_PL_S-bp5-022.command`
- `PL!S-bp5-022#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp5-022_A02_T03_PL_S-bp5-022.command`
- `PL!S-bp5-022#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-022_A02_T04_PL_S-bp5-022.command`

## PL!S-bp5-023
- `PL!S-bp5-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-023_A01_T01_PL_S-bp5-023.command`
- `PL!S-bp5-023#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp5-023_A01_T02_PL_S-bp5-023.command`
- `PL!S-bp5-023#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp5-023_A01_T03_PL_S-bp5-023.command`
- `PL!S-bp5-023#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp5-023_A01_T04_PL_S-bp5-023.command`
- `PL!S-bp5-023#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp5-023_A01_T05_PL_S-bp5-023.command`
- `PL!S-bp5-023#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp5-023_A01_T06_PL_S-bp5-023.command`

## PL!S-bp5-111
- `PL!S-bp5-111#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-111_A01_T01_PL_S-bp5-111.command`
- `PL!S-bp5-111#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-bp5-111_A01_T02_PL_S-bp5-111.command`
- `PL!S-bp5-111#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-bp5-111_A01_T03_PL_S-bp5-111.command`
- `PL!S-bp5-111#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_S-bp5-111_A01_T04_PL_S-bp5-111.command`
- `PL!S-bp5-111#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp5-111_A01_T05_PL_S-bp5-111.command`
- `PL!S-bp5-111#A02#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-111_A02_T01_PL_S-bp5-111.command`
- `PL!S-bp5-111#A02#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-bp5-111_A02_T02_PL_S-bp5-111.command`
- `PL!S-bp5-111#A02#T03` 自動 / 境界値 / command: `debug_commands/PL_S-bp5-111_A02_T03_PL_S-bp5-111.command`

## PL!S-bp5-222
- `PL!S-bp5-222#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-222_A01_T01_PL_S-bp5-222.command`
- `PL!S-bp5-222#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-bp5-222_A01_T02_PL_S-bp5-222.command`
- `PL!S-bp5-222#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-bp5-222_A01_T03_PL_S-bp5-222.command`
- `PL!S-bp5-222#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_S-bp5-222_A01_T04_PL_S-bp5-222.command`
- `PL!S-bp5-222#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp5-222_A01_T05_PL_S-bp5-222.command`
- `PL!S-bp5-222#A02#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-bp5-222_A02_T01_PL_S-bp5-222.command`
- `PL!S-bp5-222#A02#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-bp5-222_A02_T02_PL_S-bp5-222.command`
- `PL!S-bp5-222#A02#T03` 自動 / 境界値 / command: `debug_commands/PL_S-bp5-222_A02_T03_PL_S-bp5-222.command`
- `PL!S-bp5-222#A02#T04` 自動 / 回数制限超過 / command: `debug_commands/PL_S-bp5-222_A02_T04_PL_S-bp5-222.command`
- `PL!S-bp5-222#A02#T05` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp5-222_A02_T05_PL_S-bp5-222.command`

## PL!S-bp6-001
- `PL!S-bp6-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-001_A01_T01_PL_S-bp6-001.command`
- `PL!S-bp6-001#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp6-001_A01_T02_PL_S-bp6-001.command`
- `PL!S-bp6-001#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp6-001_A01_T03_PL_S-bp6-001.command`

## PL!S-bp6-002
- `PL!S-bp6-002#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-002_A02_T01_PL_S-bp6-002.command`
- `PL!S-bp6-002#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp6-002_A02_T02_PL_S-bp6-002.command`
- `PL!S-bp6-002#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp6-002_A02_T03_PL_S-bp6-002.command`
- `PL!S-bp6-002#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp6-002_A02_T04_PL_S-bp6-002.command`
- `PL!S-bp6-002#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp6-002_A02_T05_PL_S-bp6-002.command`
- `PL!S-bp6-002#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-002_A02_T06_PL_S-bp6-002.command`

## PL!S-bp6-004
- `PL!S-bp6-004#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-004_A01_T01_PL_S-bp6-004.command`
- `PL!S-bp6-004#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp6-004_A01_T02_PL_S-bp6-004.command`
- `PL!S-bp6-004#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp6-004_A01_T03_PL_S-bp6-004.command`
- `PL!S-bp6-004#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-004_A01_T04_PL_S-bp6-004.command`

## PL!S-bp6-005
- `PL!S-bp6-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-005_A01_T01_PL_S-bp6-005.command`

## PL!S-bp6-006
- `PL!S-bp6-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-006_A01_T01_PL_S-bp6-006.command`
- `PL!S-bp6-006#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp6-006_A01_T02_PL_S-bp6-006.command`
- `PL!S-bp6-006#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp6-006_A01_T03_PL_S-bp6-006.command`
- `PL!S-bp6-006#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp6-006_A01_T04_PL_S-bp6-006.command`
- `PL!S-bp6-006#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp6-006_A01_T05_PL_S-bp6-006.command`

## PL!S-bp6-007
- `PL!S-bp6-007#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-007_A01_T01_PL_S-bp6-007.command`
- `PL!S-bp6-007#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp6-007_A01_T02_PL_S-bp6-007.command`
- `PL!S-bp6-007#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp6-007_A01_T03_PL_S-bp6-007.command`
- `PL!S-bp6-007#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp6-007_A01_T04_PL_S-bp6-007.command`
- `PL!S-bp6-007#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp6-007_A01_T05_PL_S-bp6-007.command`
- `PL!S-bp6-007#A01#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-bp6-007_A01_T06_PL_S-bp6-007.command`
- `PL!S-bp6-007#A01#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-bp6-007_A01_T07_PL_S-bp6-007.command`
- `PL!S-bp6-007#A01#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-007_A01_T08_PL_S-bp6-007.command`

## PL!S-bp6-008
- `PL!S-bp6-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-008_A01_T01_PL_S-bp6-008.command`
- `PL!S-bp6-008#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-bp6-008_A01_T02_PL_S-bp6-008.command`
- `PL!S-bp6-008#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-bp6-008_A01_T03_PL_S-bp6-008.command`

## PL!S-bp6-009
- `PL!S-bp6-009#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-009_A02_T01_PL_S-bp6-009.command`
- `PL!S-bp6-009#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp6-009_A02_T02_PL_S-bp6-009.command`
- `PL!S-bp6-009#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp6-009_A02_T03_PL_S-bp6-009.command`
- `PL!S-bp6-009#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-009_A02_T04_PL_S-bp6-009.command`

## PL!S-bp6-010
- `PL!S-bp6-010#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-010_A01_T01_PL_S-bp6-010.command`
- `PL!S-bp6-010#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp6-010_A01_T02_PL_S-bp6-010.command`
- `PL!S-bp6-010#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp6-010_A01_T03_PL_S-bp6-010.command`
- `PL!S-bp6-010#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-bp6-010_A01_T04_PL_S-bp6-010.command`
- `PL!S-bp6-010#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp6-010_A01_T05_PL_S-bp6-010.command`
- `PL!S-bp6-010#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-010_A01_T06_PL_S-bp6-010.command`

## PL!S-bp6-011
- `PL!S-bp6-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-011_A01_T01_PL_S-bp6-011.command`
- `PL!S-bp6-011#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp6-011_A01_T02_PL_S-bp6-011.command`
- `PL!S-bp6-011#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp6-011_A01_T03_PL_S-bp6-011.command`

## PL!S-bp6-012
- `PL!S-bp6-012#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-012_A01_T01_PL_S-bp6-012.command`

## PL!S-bp6-013
- `PL!S-bp6-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-013_A01_T01_PL_S-bp6-013.command`
- `PL!S-bp6-013#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp6-013_A01_T02_PL_S-bp6-013.command`
- `PL!S-bp6-013#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp6-013_A01_T03_PL_S-bp6-013.command`

## PL!S-bp6-014
- `PL!S-bp6-014#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-014_A01_T01_PL_S-bp6-014.command`
- `PL!S-bp6-014#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-bp6-014_A01_T02_PL_S-bp6-014.command`
- `PL!S-bp6-014#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-bp6-014_A01_T03_PL_S-bp6-014.command`

## PL!S-bp6-015
- `PL!S-bp6-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-015_A01_T01_PL_S-bp6-015.command`

## PL!S-bp6-016
- `PL!S-bp6-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-016_A01_T01_PL_S-bp6-016.command`
- `PL!S-bp6-016#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp6-016_A01_T02_PL_S-bp6-016.command`
- `PL!S-bp6-016#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp6-016_A01_T03_PL_S-bp6-016.command`

## PL!S-bp6-017
- `PL!S-bp6-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-017_A01_T01_PL_S-bp6-017.command`

## PL!S-bp6-018
- `PL!S-bp6-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-018_A01_T01_PL_S-bp6-018.command`
- `PL!S-bp6-018#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-bp6-018_A01_T02_PL_S-bp6-018.command`
- `PL!S-bp6-018#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-bp6-018_A01_T03_PL_S-bp6-018.command`
- `PL!S-bp6-018#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-bp6-018_A01_T04_PL_S-bp6-018.command`
- `PL!S-bp6-018#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-bp6-018_A01_T05_PL_S-bp6-018.command`

## PL!S-bp6-019
- `PL!S-bp6-019#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-019_A01_T01_PL_S-bp6-019.command`
- `PL!S-bp6-019#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp6-019_A01_T02_PL_S-bp6-019.command`
- `PL!S-bp6-019#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp6-019_A01_T03_PL_S-bp6-019.command`
- `PL!S-bp6-019#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-019_A01_T04_PL_S-bp6-019.command`

## PL!S-bp6-021
- `PL!S-bp6-021#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-021_A01_T01_PL_S-bp6-021.command`
- `PL!S-bp6-021#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-bp6-021_A01_T02_PL_S-bp6-021.command`
- `PL!S-bp6-021#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_S-bp6-021_A01_T03_PL_S-bp6-021.command`
- `PL!S-bp6-021#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_S-bp6-021_A01_T04_PL_S-bp6-021.command`
- `PL!S-bp6-021#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_S-bp6-021_A01_T05_PL_S-bp6-021.command`
- `PL!S-bp6-021#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_S-bp6-021_A01_T06_PL_S-bp6-021.command`
- `PL!S-bp6-021#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_S-bp6-021_A01_T07_PL_S-bp6-021.command`

## PL!S-bp6-022
- `PL!S-bp6-022#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-022_A01_T01_PL_S-bp6-022.command`
- `PL!S-bp6-022#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp6-022_A01_T02_PL_S-bp6-022.command`
- `PL!S-bp6-022#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp6-022_A01_T03_PL_S-bp6-022.command`
- `PL!S-bp6-022#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-022_A01_T04_PL_S-bp6-022.command`

## PL!S-bp6-023
- `PL!S-bp6-023#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-023_A01_T01_PL_S-bp6-023.command`
- `PL!S-bp6-023#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp6-023_A01_T02_PL_S-bp6-023.command`
- `PL!S-bp6-023#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp6-023_A01_T03_PL_S-bp6-023.command`
- `PL!S-bp6-023#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-023_A01_T04_PL_S-bp6-023.command`

## PL!S-bp6-024
- `PL!S-bp6-024#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp6-024_A01_T01_PL_S-bp6-024.command`
- `PL!S-bp6-024#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp6-024_A01_T02_PL_S-bp6-024.command`
- `PL!S-bp6-024#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp6-024_A01_T03_PL_S-bp6-024.command`
- `PL!S-bp6-024#A01#T04` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_S-bp6-024_A01_T04_PL_S-bp6-024.command`
- `PL!S-bp6-024#A01#T05` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp6-024_A01_T05_PL_S-bp6-024.command`
- `PL!S-bp6-024#A01#T06` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp6-024_A01_T06_PL_S-bp6-024.command`

## PL!S-bp7-002
- `PL!S-bp7-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-002_A01_T01_PL_S-bp7-002.command`
- `PL!S-bp7-002#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-bp7-002_A01_T02_PL_S-bp7-002.command`
- `PL!S-bp7-002#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-bp7-002_A01_T03_PL_S-bp7-002.command`

## PL!S-bp7-003
- `PL!S-bp7-003#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-003_A01_T01_PL_S-bp7-003.command`

## PL!S-bp7-005
- `PL!S-bp7-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-005_A01_T01_PL_S-bp7-005.command`
- `PL!S-bp7-005#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-005_A02_T01_PL_S-bp7-005.command`
- `PL!S-bp7-005#A02#T02` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_S-bp7-005_A02_T02_PL_S-bp7-005.command`
- `PL!S-bp7-005#A02#T03` 常時 / 条件消失で解除 / command: `debug_commands/PL_S-bp7-005_A02_T03_PL_S-bp7-005.command`

## PL!S-bp7-019
- `PL!S-bp7-019#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-019_A01_T01_PL_S-bp7-019.command`
- `PL!S-bp7-019#A01#T02` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_S-bp7-019_A01_T02_PL_S-bp7-019.command`
- `PL!S-bp7-019#A01#T03` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_S-bp7-019_A01_T03_PL_S-bp7-019.command`
- `PL!S-bp7-019#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp7-019_A01_T04_PL_S-bp7-019.command`

## PL!S-bp7-020
- `PL!S-bp7-020#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-020_A01_T01_PL_S-bp7-020.command`
- `PL!S-bp7-020#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp7-020_A01_T02_PL_S-bp7-020.command`
- `PL!S-bp7-020#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp7-020_A01_T03_PL_S-bp7-020.command`
- `PL!S-bp7-020#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp7-020_A01_T04_PL_S-bp7-020.command`
- `PL!S-bp7-020#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-020_A02_T01_PL_S-bp7-020.command`
- `PL!S-bp7-020#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp7-020_A02_T02_PL_S-bp7-020.command`
- `PL!S-bp7-020#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp7-020_A02_T03_PL_S-bp7-020.command`
- `PL!S-bp7-020#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp7-020_A02_T04_PL_S-bp7-020.command`

## PL!S-bp7-021
- `PL!S-bp7-021#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-021_A01_T01_PL_S-bp7-021.command`
- `PL!S-bp7-021#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-bp7-021_A01_T02_PL_S-bp7-021.command`
- `PL!S-bp7-021#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-bp7-021_A01_T03_PL_S-bp7-021.command`
- `PL!S-bp7-021#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp7-021_A01_T04_PL_S-bp7-021.command`

## PL!S-bp7-022
- `PL!S-bp7-022#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-bp7-022_A02_T01_PL_S-bp7-022.command`
- `PL!S-bp7-022#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-bp7-022_A02_T02_PL_S-bp7-022.command`
- `PL!S-bp7-022#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-bp7-022_A02_T03_PL_S-bp7-022.command`
- `PL!S-bp7-022#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-bp7-022_A02_T04_PL_S-bp7-022.command`

## PL!S-pb1-001
- `PL!S-pb1-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-001_A01_T01_PL_S-pb1-001.command`
- `PL!S-pb1-001#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-pb1-001_A01_T02_PL_S-pb1-001.command`
- `PL!S-pb1-001#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-pb1-001_A01_T03_PL_S-pb1-001.command`

## PL!S-pb1-002
- `PL!S-pb1-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-002_A01_T01_PL_S-pb1-002.command`
- `PL!S-pb1-002#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_S-pb1-002_A01_T02_PL_S-pb1-002.command`
- `PL!S-pb1-002#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_S-pb1-002_A01_T03_PL_S-pb1-002.command`
- `PL!S-pb1-002#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_S-pb1-002_A01_T04_PL_S-pb1-002.command`
- `PL!S-pb1-002#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_S-pb1-002_A01_T05_PL_S-pb1-002.command`

## PL!S-pb1-003
- `PL!S-pb1-003#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-003_A01_T01_PL_S-pb1-003.command`
- `PL!S-pb1-003#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-pb1-003_A01_T02_PL_S-pb1-003.command`
- `PL!S-pb1-003#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-pb1-003_A01_T03_PL_S-pb1-003.command`
- `PL!S-pb1-003#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-pb1-003_A01_T04_PL_S-pb1-003.command`
- `PL!S-pb1-003#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-pb1-003_A01_T05_PL_S-pb1-003.command`
- `PL!S-pb1-003#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-003_A01_T06_PL_S-pb1-003.command`
- `PL!S-pb1-003#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-003_A02_T01_PL_S-pb1-003.command`
- `PL!S-pb1-003#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-003_A02_T02_PL_S-pb1-003.command`

## PL!S-pb1-004
- `PL!S-pb1-004#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-004_A01_T01_PL_S-pb1-004.command`
- `PL!S-pb1-004#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-pb1-004_A01_T02_PL_S-pb1-004.command`
- `PL!S-pb1-004#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-pb1-004_A01_T03_PL_S-pb1-004.command`

## PL!S-pb1-005
- `PL!S-pb1-005#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-005_A01_T01_PL_S-pb1-005.command`
- `PL!S-pb1-005#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_S-pb1-005_A01_T02_PL_S-pb1-005.command`
- `PL!S-pb1-005#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_S-pb1-005_A01_T03_PL_S-pb1-005.command`
- `PL!S-pb1-005#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_S-pb1-005_A01_T04_PL_S-pb1-005.command`
- `PL!S-pb1-005#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_S-pb1-005_A01_T05_PL_S-pb1-005.command`

## PL!S-pb1-007
- `PL!S-pb1-007#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-007_A01_T01_PL_S-pb1-007.command`
- `PL!S-pb1-007#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-pb1-007_A01_T02_PL_S-pb1-007.command`
- `PL!S-pb1-007#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-pb1-007_A01_T03_PL_S-pb1-007.command`
- `PL!S-pb1-007#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-007_A01_T04_PL_S-pb1-007.command`

## PL!S-pb1-008
- `PL!S-pb1-008#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-008_A01_T01_PL_S-pb1-008.command`
- `PL!S-pb1-008#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-pb1-008_A01_T02_PL_S-pb1-008.command`
- `PL!S-pb1-008#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-pb1-008_A01_T03_PL_S-pb1-008.command`
- `PL!S-pb1-008#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-008_A01_T04_PL_S-pb1-008.command`

## PL!S-pb1-013
- `PL!S-pb1-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-013_A01_T01_PL_S-pb1-013.command`
- `PL!S-pb1-013#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-pb1-013_A01_T02_PL_S-pb1-013.command`
- `PL!S-pb1-013#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-pb1-013_A01_T03_PL_S-pb1-013.command`

## PL!S-pb1-014
- `PL!S-pb1-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-014_A01_T01_PL_S-pb1-014.command`
- `PL!S-pb1-014#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-pb1-014_A01_T02_PL_S-pb1-014.command`
- `PL!S-pb1-014#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-pb1-014_A01_T03_PL_S-pb1-014.command`

## PL!S-pb1-015
- `PL!S-pb1-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-015_A01_T01_PL_S-pb1-015.command`
- `PL!S-pb1-015#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-pb1-015_A01_T02_PL_S-pb1-015.command`
- `PL!S-pb1-015#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-pb1-015_A01_T03_PL_S-pb1-015.command`

## PL!S-pb1-016
- `PL!S-pb1-016#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-016_A01_T01_PL_S-pb1-016.command`
- `PL!S-pb1-016#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-pb1-016_A01_T02_PL_S-pb1-016.command`
- `PL!S-pb1-016#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-pb1-016_A01_T03_PL_S-pb1-016.command`
- `PL!S-pb1-016#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-pb1-016_A01_T04_PL_S-pb1-016.command`
- `PL!S-pb1-016#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-pb1-016_A01_T05_PL_S-pb1-016.command`
- `PL!S-pb1-016#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-016_A01_T06_PL_S-pb1-016.command`

## PL!S-pb1-017
- `PL!S-pb1-017#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-017_A01_T01_PL_S-pb1-017.command`
- `PL!S-pb1-017#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-pb1-017_A01_T02_PL_S-pb1-017.command`
- `PL!S-pb1-017#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-pb1-017_A01_T03_PL_S-pb1-017.command`
- `PL!S-pb1-017#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-pb1-017_A01_T04_PL_S-pb1-017.command`
- `PL!S-pb1-017#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-pb1-017_A01_T05_PL_S-pb1-017.command`
- `PL!S-pb1-017#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-017_A01_T06_PL_S-pb1-017.command`

## PL!S-pb1-018
- `PL!S-pb1-018#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-018_A01_T01_PL_S-pb1-018.command`
- `PL!S-pb1-018#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-pb1-018_A01_T02_PL_S-pb1-018.command`
- `PL!S-pb1-018#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-pb1-018_A01_T03_PL_S-pb1-018.command`
- `PL!S-pb1-018#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-pb1-018_A01_T04_PL_S-pb1-018.command`
- `PL!S-pb1-018#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-pb1-018_A01_T05_PL_S-pb1-018.command`
- `PL!S-pb1-018#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-018_A01_T06_PL_S-pb1-018.command`

## PL!S-pb1-019
- `PL!S-pb1-019#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-019_A01_T01_PL_S-pb1-019.command`
- `PL!S-pb1-019#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-pb1-019_A01_T02_PL_S-pb1-019.command`
- `PL!S-pb1-019#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-pb1-019_A01_T03_PL_S-pb1-019.command`
- `PL!S-pb1-019#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-019_A01_T04_PL_S-pb1-019.command`

## PL!S-pb1-020
- `PL!S-pb1-020#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-020_A01_T01_PL_S-pb1-020.command`
- `PL!S-pb1-020#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-pb1-020_A01_T02_PL_S-pb1-020.command`
- `PL!S-pb1-020#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-pb1-020_A01_T03_PL_S-pb1-020.command`
- `PL!S-pb1-020#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-020_A01_T04_PL_S-pb1-020.command`

## PL!S-pb1-021
- `PL!S-pb1-021#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-021_A01_T01_PL_S-pb1-021.command`
- `PL!S-pb1-021#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-pb1-021_A01_T02_PL_S-pb1-021.command`
- `PL!S-pb1-021#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-pb1-021_A01_T03_PL_S-pb1-021.command`
- `PL!S-pb1-021#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-021_A01_T04_PL_S-pb1-021.command`

## PL!S-pb1-022
- `PL!S-pb1-022#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-022_A01_T01_PL_S-pb1-022.command`
- `PL!S-pb1-022#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_S-pb1-022_A01_T02_PL_S-pb1-022.command`
- `PL!S-pb1-022#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_S-pb1-022_A01_T03_PL_S-pb1-022.command`
- `PL!S-pb1-022#A01#T04` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_S-pb1-022_A01_T04_PL_S-pb1-022.command`
- `PL!S-pb1-022#A01#T05` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_S-pb1-022_A01_T05_PL_S-pb1-022.command`
- `PL!S-pb1-022#A01#T06` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-022_A01_T06_PL_S-pb1-022.command`

## PL!S-pb1-024
- `PL!S-pb1-024#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-pb1-024_A01_T01_PL_S-pb1-024.command`
- `PL!S-pb1-024#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-pb1-024_A01_T02_PL_S-pb1-024.command`

## PL!S-sd1-001
- `PL!S-sd1-001#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-001_A01_T01_PL_S-sd1-001.command`
- `PL!S-sd1-001#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_S-sd1-001_A01_T02_PL_S-sd1-001.command`
- `PL!S-sd1-001#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_S-sd1-001_A01_T03_PL_S-sd1-001.command`
- `PL!S-sd1-001#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_S-sd1-001_A01_T04_PL_S-sd1-001.command`
- `PL!S-sd1-001#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_S-sd1-001_A01_T05_PL_S-sd1-001.command`
- `PL!S-sd1-001#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_S-sd1-001_A01_T06_PL_S-sd1-001.command`
- `PL!S-sd1-001#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_S-sd1-001_A01_T07_PL_S-sd1-001.command`

## PL!S-sd1-002
- `PL!S-sd1-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-002_A01_T01_PL_S-sd1-002.command`
- `PL!S-sd1-002#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-sd1-002_A01_T02_PL_S-sd1-002.command`
- `PL!S-sd1-002#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-sd1-002_A01_T03_PL_S-sd1-002.command`

## PL!S-sd1-003
- `PL!S-sd1-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-003_A01_T01_PL_S-sd1-003.command`

## PL!S-sd1-004
- `PL!S-sd1-004#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-004_A01_T01_PL_S-sd1-004.command`
- `PL!S-sd1-004#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_S-sd1-004_A01_T02_PL_S-sd1-004.command`
- `PL!S-sd1-004#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_S-sd1-004_A01_T03_PL_S-sd1-004.command`
- `PL!S-sd1-004#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-sd1-004_A01_T04_PL_S-sd1-004.command`

## PL!S-sd1-005
- `PL!S-sd1-005#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-005_A01_T01_PL_S-sd1-005.command`
- `PL!S-sd1-005#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-sd1-005_A01_T02_PL_S-sd1-005.command`
- `PL!S-sd1-005#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-sd1-005_A01_T03_PL_S-sd1-005.command`
- `PL!S-sd1-005#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_S-sd1-005_A01_T04_PL_S-sd1-005.command`
- `PL!S-sd1-005#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_S-sd1-005_A01_T05_PL_S-sd1-005.command`

## PL!S-sd1-006
- `PL!S-sd1-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-006_A01_T01_PL_S-sd1-006.command`
- `PL!S-sd1-006#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_S-sd1-006_A01_T02_PL_S-sd1-006.command`
- `PL!S-sd1-006#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_S-sd1-006_A01_T03_PL_S-sd1-006.command`

## PL!S-sd1-007
- `PL!S-sd1-007#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-007_A01_T01_PL_S-sd1-007.command`
- `PL!S-sd1-007#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-sd1-007_A01_T02_PL_S-sd1-007.command`
- `PL!S-sd1-007#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-sd1-007_A01_T03_PL_S-sd1-007.command`
- `PL!S-sd1-007#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_S-sd1-007_A01_T04_PL_S-sd1-007.command`
- `PL!S-sd1-007#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_S-sd1-007_A01_T05_PL_S-sd1-007.command`

## PL!S-sd1-008
- `PL!S-sd1-008#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-008_A01_T01_PL_S-sd1-008.command`
- `PL!S-sd1-008#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-sd1-008_A01_T02_PL_S-sd1-008.command`
- `PL!S-sd1-008#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-sd1-008_A01_T03_PL_S-sd1-008.command`

## PL!S-sd1-009
- `PL!S-sd1-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-009_A01_T01_PL_S-sd1-009.command`
- `PL!S-sd1-009#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-sd1-009_A01_T02_PL_S-sd1-009.command`
- `PL!S-sd1-009#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-sd1-009_A01_T03_PL_S-sd1-009.command`
- `PL!S-sd1-009#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_S-sd1-009_A01_T04_PL_S-sd1-009.command`
- `PL!S-sd1-009#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_S-sd1-009_A01_T05_PL_S-sd1-009.command`
- `PL!S-sd1-009#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-sd1-009_A01_T06_PL_S-sd1-009.command`

## PL!S-sd1-013
- `PL!S-sd1-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-013_A01_T01_PL_S-sd1-013.command`

## PL!S-sd1-014
- `PL!S-sd1-014#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-014_A01_T01_PL_S-sd1-014.command`
- `PL!S-sd1-014#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-sd1-014_A01_T02_PL_S-sd1-014.command`

## PL!S-sd1-015
- `PL!S-sd1-015#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-015_A01_T01_PL_S-sd1-015.command`
- `PL!S-sd1-015#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_S-sd1-015_A01_T02_PL_S-sd1-015.command`
- `PL!S-sd1-015#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_S-sd1-015_A01_T03_PL_S-sd1-015.command`

## PL!S-sd1-017
- `PL!S-sd1-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-017_A01_T01_PL_S-sd1-017.command`

## PL!S-sd1-018
- `PL!S-sd1-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-018_A01_T01_PL_S-sd1-018.command`

## PL!S-sd1-019
- `PL!S-sd1-019#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-019_A01_T01_PL_S-sd1-019.command`
- `PL!S-sd1-019#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-sd1-019_A01_T02_PL_S-sd1-019.command`

## PL!S-sd1-020
- `PL!S-sd1-020#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-020_A01_T01_PL_S-sd1-020.command`
- `PL!S-sd1-020#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-sd1-020_A01_T02_PL_S-sd1-020.command`

## PL!S-sd1-022
- `PL!S-sd1-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_S-sd1-022_A01_T01_PL_S-sd1-022.command`
- `PL!S-sd1-022#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_S-sd1-022_A01_T02_PL_S-sd1-022.command`
- `PL!S-sd1-022#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_S-sd1-022_A01_T03_PL_S-sd1-022.command`
- `PL!S-sd1-022#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_S-sd1-022_A01_T04_PL_S-sd1-022.command`

## PL!SP-PR-003
- `PL!SP-PR-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-003_A01_T01_PL_SP-PR-003.command`
- `PL!SP-PR-003#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-PR-003_A01_T02_PL_SP-PR-003.command`
- `PL!SP-PR-003#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-PR-003_A01_T03_PL_SP-PR-003.command`

## PL!SP-PR-004
- `PL!SP-PR-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-004_A01_T01_PL_SP-PR-004.command`
- `PL!SP-PR-004#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-PR-004_A01_T02_PL_SP-PR-004.command`
- `PL!SP-PR-004#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-PR-004_A01_T03_PL_SP-PR-004.command`

## PL!SP-PR-006
- `PL!SP-PR-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-006_A01_T01_PL_SP-PR-006.command`
- `PL!SP-PR-006#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-PR-006_A01_T02_PL_SP-PR-006.command`
- `PL!SP-PR-006#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-PR-006_A01_T03_PL_SP-PR-006.command`

## PL!SP-PR-007
- `PL!SP-PR-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-007_A01_T01_PL_SP-PR-007.command`
- `PL!SP-PR-007#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-PR-007_A01_T02_PL_SP-PR-007.command`
- `PL!SP-PR-007#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-PR-007_A01_T03_PL_SP-PR-007.command`

## PL!SP-PR-009
- `PL!SP-PR-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-009_A01_T01_PL_SP-PR-009.command`
- `PL!SP-PR-009#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-PR-009_A01_T02_PL_SP-PR-009.command`
- `PL!SP-PR-009#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-PR-009_A01_T03_PL_SP-PR-009.command`
- `PL!SP-PR-009#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-PR-009_A01_T04_PL_SP-PR-009.command`
- `PL!SP-PR-009#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-PR-009_A01_T05_PL_SP-PR-009.command`
- `PL!SP-PR-009#A01#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-PR-009_A01_T06_PL_SP-PR-009.command`
- `PL!SP-PR-009#A01#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-PR-009_A01_T07_PL_SP-PR-009.command`
- `PL!SP-PR-009#A01#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-PR-009_A01_T08_PL_SP-PR-009.command`

## PL!SP-PR-010
- `PL!SP-PR-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-010_A01_T01_PL_SP-PR-010.command`
- `PL!SP-PR-010#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-PR-010_A01_T02_PL_SP-PR-010.command`
- `PL!SP-PR-010#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-PR-010_A01_T03_PL_SP-PR-010.command`

## PL!SP-PR-011
- `PL!SP-PR-011#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-011_A01_T01_PL_SP-PR-011.command`
- `PL!SP-PR-011#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-PR-011_A01_T02_PL_SP-PR-011.command`
- `PL!SP-PR-011#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-PR-011_A01_T03_PL_SP-PR-011.command`
- `PL!SP-PR-011#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-PR-011_A01_T04_PL_SP-PR-011.command`
- `PL!SP-PR-011#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-PR-011_A01_T05_PL_SP-PR-011.command`
- `PL!SP-PR-011#A01#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-PR-011_A01_T06_PL_SP-PR-011.command`
- `PL!SP-PR-011#A01#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-PR-011_A01_T07_PL_SP-PR-011.command`
- `PL!SP-PR-011#A01#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-PR-011_A01_T08_PL_SP-PR-011.command`

## PL!SP-PR-012
- `PL!SP-PR-012#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-012_A01_T01_PL_SP-PR-012.command`
- `PL!SP-PR-012#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-PR-012_A01_T02_PL_SP-PR-012.command`
- `PL!SP-PR-012#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-PR-012_A01_T03_PL_SP-PR-012.command`
- `PL!SP-PR-012#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-PR-012_A01_T04_PL_SP-PR-012.command`
- `PL!SP-PR-012#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-PR-012_A01_T05_PL_SP-PR-012.command`
- `PL!SP-PR-012#A01#T06` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-PR-012_A01_T06_PL_SP-PR-012.command`
- `PL!SP-PR-012#A01#T07` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-PR-012_A01_T07_PL_SP-PR-012.command`
- `PL!SP-PR-012#A01#T08` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-PR-012_A01_T08_PL_SP-PR-012.command`

## PL!SP-PR-013
- `PL!SP-PR-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-013_A01_T01_PL_SP-PR-013.command`
- `PL!SP-PR-013#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-PR-013_A01_T02_PL_SP-PR-013.command`
- `PL!SP-PR-013#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-PR-013_A01_T03_PL_SP-PR-013.command`

## PL!SP-PR-016
- `PL!SP-PR-016#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-016_A01_T01_PL_SP-PR-016.command`
- `PL!SP-PR-016#A01#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_SP-PR-016_A01_T02_PL_SP-PR-016.command`
- `PL!SP-PR-016#A01#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_SP-PR-016_A01_T03_PL_SP-PR-016.command`
- `PL!SP-PR-016#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-PR-016_A01_T04_PL_SP-PR-016.command`

## PL!SP-PR-017
- `PL!SP-PR-017#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-017_A01_T01_PL_SP-PR-017.command`
- `PL!SP-PR-017#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-PR-017_A01_T02_PL_SP-PR-017.command`
- `PL!SP-PR-017#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-PR-017_A01_T03_PL_SP-PR-017.command`
- `PL!SP-PR-017#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-PR-017_A01_T04_PL_SP-PR-017.command`
- `PL!SP-PR-017#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-PR-017_A01_T05_PL_SP-PR-017.command`

## PL!SP-PR-018
- `PL!SP-PR-018#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-018_A01_T01_PL_SP-PR-018.command`
- `PL!SP-PR-018#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-PR-018_A01_T02_PL_SP-PR-018.command`
- `PL!SP-PR-018#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-PR-018_A01_T03_PL_SP-PR-018.command`
- `PL!SP-PR-018#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-PR-018_A01_T04_PL_SP-PR-018.command`

## PL!SP-PR-020
- `PL!SP-PR-020#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-020_A01_T01_PL_SP-PR-020.command`
- `PL!SP-PR-020#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-PR-020_A01_T02_PL_SP-PR-020.command`
- `PL!SP-PR-020#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-PR-020_A01_T03_PL_SP-PR-020.command`

## PL!SP-PR-021
- `PL!SP-PR-021#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-021_A01_T01_PL_SP-PR-021.command`
- `PL!SP-PR-021#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-PR-021_A01_T02_PL_SP-PR-021.command`
- `PL!SP-PR-021#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-PR-021_A01_T03_PL_SP-PR-021.command`
- `PL!SP-PR-021#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-PR-021_A01_T04_PL_SP-PR-021.command`

## PL!SP-PR-024
- `PL!SP-PR-024#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-024_A01_T01_PL_SP-PR-024.command`
- `PL!SP-PR-024#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-PR-024_A01_T02_PL_SP-PR-024.command`
- `PL!SP-PR-024#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-PR-024_A01_T03_PL_SP-PR-024.command`
- `PL!SP-PR-024#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-PR-024_A01_T04_PL_SP-PR-024.command`
- `PL!SP-PR-024#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-PR-024_A01_T05_PL_SP-PR-024.command`
- `PL!SP-PR-024#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-PR-024_A01_T06_PL_SP-PR-024.command`
- `PL!SP-PR-024#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-PR-024_A01_T07_PL_SP-PR-024.command`

## PL!SP-PR-025
- `PL!SP-PR-025#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-PR-025_A01_T01_PL_SP-PR-025.command`
- `PL!SP-PR-025#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-PR-025_A01_T02_PL_SP-PR-025.command`
- `PL!SP-PR-025#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-PR-025_A01_T03_PL_SP-PR-025.command`
- `PL!SP-PR-025#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-PR-025_A01_T04_PL_SP-PR-025.command`
- `PL!SP-PR-025#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-PR-025_A01_T05_PL_SP-PR-025.command`

## PL!SP-bp1-002
- `PL!SP-bp1-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-002_A01_T01_PL_SP-bp1-002.command`
- `PL!SP-bp1-002#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp1-002_A01_T02_PL_SP-bp1-002.command`
- `PL!SP-bp1-002#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp1-002_A01_T03_PL_SP-bp1-002.command`
- `PL!SP-bp1-002#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp1-002_A01_T04_PL_SP-bp1-002.command`
- `PL!SP-bp1-002#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp1-002_A01_T05_PL_SP-bp1-002.command`

## PL!SP-bp1-005
- `PL!SP-bp1-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-005_A01_T01_PL_SP-bp1-005.command`
- `PL!SP-bp1-005#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-bp1-005_A01_T02_PL_SP-bp1-005.command`
- `PL!SP-bp1-005#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp1-005_A01_T03_PL_SP-bp1-005.command`
- `PL!SP-bp1-005#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp1-005_A01_T04_PL_SP-bp1-005.command`
- `PL!SP-bp1-005#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp1-005_A01_T05_PL_SP-bp1-005.command`

## PL!SP-bp1-006
- `PL!SP-bp1-006#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-006_A01_T01_PL_SP-bp1-006.command`
- `PL!SP-bp1-006#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp1-006_A01_T02_PL_SP-bp1-006.command`
- `PL!SP-bp1-006#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp1-006_A01_T03_PL_SP-bp1-006.command`
- `PL!SP-bp1-006#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp1-006_A01_T04_PL_SP-bp1-006.command`
- `PL!SP-bp1-006#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp1-006_A01_T05_PL_SP-bp1-006.command`
- `PL!SP-bp1-006#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp1-006_A01_T06_PL_SP-bp1-006.command`

## PL!SP-bp1-007
- `PL!SP-bp1-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-007_A01_T01_PL_SP-bp1-007.command`
- `PL!SP-bp1-007#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp1-007_A01_T02_PL_SP-bp1-007.command`
- `PL!SP-bp1-007#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp1-007_A01_T03_PL_SP-bp1-007.command`

## PL!SP-bp1-008
- `PL!SP-bp1-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-008_A01_T01_PL_SP-bp1-008.command`
- `PL!SP-bp1-008#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp1-008_A01_T02_PL_SP-bp1-008.command`
- `PL!SP-bp1-008#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp1-008_A01_T03_PL_SP-bp1-008.command`

## PL!SP-bp1-009
- `PL!SP-bp1-009#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-009_A01_T01_PL_SP-bp1-009.command`
- `PL!SP-bp1-009#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp1-009_A01_T02_PL_SP-bp1-009.command`
- `PL!SP-bp1-009#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp1-009_A01_T03_PL_SP-bp1-009.command`
- `PL!SP-bp1-009#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-bp1-009_A01_T04_PL_SP-bp1-009.command`
- `PL!SP-bp1-009#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp1-009_A01_T05_PL_SP-bp1-009.command`

## PL!SP-bp1-010
- `PL!SP-bp1-010#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-010_A01_T01_PL_SP-bp1-010.command`
- `PL!SP-bp1-010#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp1-010_A01_T02_PL_SP-bp1-010.command`
- `PL!SP-bp1-010#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp1-010_A01_T03_PL_SP-bp1-010.command`
- `PL!SP-bp1-010#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-bp1-010_A01_T04_PL_SP-bp1-010.command`
- `PL!SP-bp1-010#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp1-010_A01_T05_PL_SP-bp1-010.command`

## PL!SP-bp1-011
- `PL!SP-bp1-011#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-011_A01_T01_PL_SP-bp1-011.command`
- `PL!SP-bp1-011#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp1-011_A01_T02_PL_SP-bp1-011.command`
- `PL!SP-bp1-011#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp1-011_A01_T03_PL_SP-bp1-011.command`

## PL!SP-bp1-012
- `PL!SP-bp1-012#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-012_A01_T01_PL_SP-bp1-012.command`
- `PL!SP-bp1-012#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp1-012_A01_T02_PL_SP-bp1-012.command`
- `PL!SP-bp1-012#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp1-012_A01_T03_PL_SP-bp1-012.command`

## PL!SP-bp1-021
- `PL!SP-bp1-021#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-021_A01_T01_PL_SP-bp1-021.command`
- `PL!SP-bp1-021#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp1-021_A01_T02_PL_SP-bp1-021.command`
- `PL!SP-bp1-021#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp1-021_A01_T03_PL_SP-bp1-021.command`

## PL!SP-bp1-023
- `PL!SP-bp1-023#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-023_A01_T01_PL_SP-bp1-023.command`
- `PL!SP-bp1-023#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp1-023_A01_T02_PL_SP-bp1-023.command`
- `PL!SP-bp1-023#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp1-023_A01_T03_PL_SP-bp1-023.command`
- `PL!SP-bp1-023#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp1-023_A01_T04_PL_SP-bp1-023.command`

## PL!SP-bp1-024
- `PL!SP-bp1-024#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-024_A01_T01_PL_SP-bp1-024.command`
- `PL!SP-bp1-024#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp1-024_A01_T02_PL_SP-bp1-024.command`
- `PL!SP-bp1-024#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp1-024_A01_T03_PL_SP-bp1-024.command`
- `PL!SP-bp1-024#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp1-024_A01_T04_PL_SP-bp1-024.command`
- `PL!SP-bp1-024#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-024_A02_T01_PL_SP-bp1-024.command`
- `PL!SP-bp1-024#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp1-024_A02_T02_PL_SP-bp1-024.command`
- `PL!SP-bp1-024#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp1-024_A02_T03_PL_SP-bp1-024.command`
- `PL!SP-bp1-024#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp1-024_A02_T04_PL_SP-bp1-024.command`

## PL!SP-bp1-026
- `PL!SP-bp1-026#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-026_A01_T01_PL_SP-bp1-026.command`
- `PL!SP-bp1-026#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp1-026_A01_T02_PL_SP-bp1-026.command`
- `PL!SP-bp1-026#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp1-026_A01_T03_PL_SP-bp1-026.command`
- `PL!SP-bp1-026#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp1-026_A01_T04_PL_SP-bp1-026.command`

## PL!SP-bp1-027
- `PL!SP-bp1-027#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp1-027_A01_T01_PL_SP-bp1-027.command`
- `PL!SP-bp1-027#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp1-027_A01_T02_PL_SP-bp1-027.command`
- `PL!SP-bp1-027#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp1-027_A01_T03_PL_SP-bp1-027.command`
- `PL!SP-bp1-027#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp1-027_A01_T04_PL_SP-bp1-027.command`

## PL!SP-bp2-001
- `PL!SP-bp2-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-001_A01_T01_PL_SP-bp2-001.command`

## PL!SP-bp2-002
- `PL!SP-bp2-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-002_A01_T01_PL_SP-bp2-002.command`

## PL!SP-bp2-003
- `PL!SP-bp2-003#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-003_A01_T01_PL_SP-bp2-003.command`
- `PL!SP-bp2-003#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-bp2-003_A01_T02_PL_SP-bp2-003.command`
- `PL!SP-bp2-003#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-bp2-003_A01_T03_PL_SP-bp2-003.command`
- `PL!SP-bp2-003#A01#T04` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-bp2-003_A01_T04_PL_SP-bp2-003.command`
- `PL!SP-bp2-003#A01#T05` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp2-003_A01_T05_PL_SP-bp2-003.command`

## PL!SP-bp2-005
- `PL!SP-bp2-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-005_A01_T01_PL_SP-bp2-005.command`
- `PL!SP-bp2-005#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp2-005_A01_T02_PL_SP-bp2-005.command`
- `PL!SP-bp2-005#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp2-005_A01_T03_PL_SP-bp2-005.command`

## PL!SP-bp2-006
- `PL!SP-bp2-006#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-006_A01_T01_PL_SP-bp2-006.command`
- `PL!SP-bp2-006#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp2-006_A01_T02_PL_SP-bp2-006.command`
- `PL!SP-bp2-006#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp2-006_A01_T03_PL_SP-bp2-006.command`

## PL!SP-bp2-007
- `PL!SP-bp2-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-007_A01_T01_PL_SP-bp2-007.command`
- `PL!SP-bp2-007#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp2-007_A01_T02_PL_SP-bp2-007.command`
- `PL!SP-bp2-007#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp2-007_A01_T03_PL_SP-bp2-007.command`

## PL!SP-bp2-009
- `PL!SP-bp2-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-009_A01_T01_PL_SP-bp2-009.command`
- `PL!SP-bp2-009#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-009_A01_T02_PL_SP-bp2-009.command`
- `PL!SP-bp2-009#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-009_A01_T03_PL_SP-bp2-009.command`
- `PL!SP-bp2-009#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp2-009_A01_T04_PL_SP-bp2-009.command`
- `PL!SP-bp2-009#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-009_A02_T01_PL_SP-bp2-009.command`
- `PL!SP-bp2-009#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp2-009_A02_T02_PL_SP-bp2-009.command`

## PL!SP-bp2-010
- `PL!SP-bp2-010#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-010_A02_T01_PL_SP-bp2-010.command`
- `PL!SP-bp2-010#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp2-010_A02_T02_PL_SP-bp2-010.command`
- `PL!SP-bp2-010#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp2-010_A02_T03_PL_SP-bp2-010.command`
- `PL!SP-bp2-010#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-010_A02_T04_PL_SP-bp2-010.command`
- `PL!SP-bp2-010#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-010_A02_T05_PL_SP-bp2-010.command`
- `PL!SP-bp2-010#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp2-010_A02_T06_PL_SP-bp2-010.command`

## PL!SP-bp2-011
- `PL!SP-bp2-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-011_A01_T01_PL_SP-bp2-011.command`
- `PL!SP-bp2-011#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp2-011_A01_T02_PL_SP-bp2-011.command`
- `PL!SP-bp2-011#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp2-011_A01_T03_PL_SP-bp2-011.command`

## PL!SP-bp2-013
- `PL!SP-bp2-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-013_A01_T01_PL_SP-bp2-013.command`
- `PL!SP-bp2-013#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-013_A01_T02_PL_SP-bp2-013.command`
- `PL!SP-bp2-013#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-013_A01_T03_PL_SP-bp2-013.command`

## PL!SP-bp2-014
- `PL!SP-bp2-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-014_A01_T01_PL_SP-bp2-014.command`
- `PL!SP-bp2-014#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-014_A01_T02_PL_SP-bp2-014.command`
- `PL!SP-bp2-014#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-014_A01_T03_PL_SP-bp2-014.command`

## PL!SP-bp2-015
- `PL!SP-bp2-015#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-015_A01_T01_PL_SP-bp2-015.command`
- `PL!SP-bp2-015#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-bp2-015_A01_T02_PL_SP-bp2-015.command`
- `PL!SP-bp2-015#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-bp2-015_A01_T03_PL_SP-bp2-015.command`
- `PL!SP-bp2-015#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-015_A01_T04_PL_SP-bp2-015.command`
- `PL!SP-bp2-015#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-015_A01_T05_PL_SP-bp2-015.command`
- `PL!SP-bp2-015#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-bp2-015_A01_T06_PL_SP-bp2-015.command`
- `PL!SP-bp2-015#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp2-015_A01_T07_PL_SP-bp2-015.command`

## PL!SP-bp2-018
- `PL!SP-bp2-018#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-018_A01_T01_PL_SP-bp2-018.command`
- `PL!SP-bp2-018#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-018_A01_T02_PL_SP-bp2-018.command`
- `PL!SP-bp2-018#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-018_A01_T03_PL_SP-bp2-018.command`

## PL!SP-bp2-019
- `PL!SP-bp2-019#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-019_A01_T01_PL_SP-bp2-019.command`
- `PL!SP-bp2-019#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-019_A01_T02_PL_SP-bp2-019.command`
- `PL!SP-bp2-019#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-019_A01_T03_PL_SP-bp2-019.command`
- `PL!SP-bp2-019#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp2-019_A01_T04_PL_SP-bp2-019.command`
- `PL!SP-bp2-019#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp2-019_A01_T05_PL_SP-bp2-019.command`
- `PL!SP-bp2-019#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp2-019_A01_T06_PL_SP-bp2-019.command`

## PL!SP-bp2-020
- `PL!SP-bp2-020#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-020_A01_T01_PL_SP-bp2-020.command`
- `PL!SP-bp2-020#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-bp2-020_A01_T02_PL_SP-bp2-020.command`
- `PL!SP-bp2-020#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-bp2-020_A01_T03_PL_SP-bp2-020.command`
- `PL!SP-bp2-020#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-020_A01_T04_PL_SP-bp2-020.command`
- `PL!SP-bp2-020#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-020_A01_T05_PL_SP-bp2-020.command`
- `PL!SP-bp2-020#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-bp2-020_A01_T06_PL_SP-bp2-020.command`
- `PL!SP-bp2-020#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp2-020_A01_T07_PL_SP-bp2-020.command`

## PL!SP-bp2-021
- `PL!SP-bp2-021#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-021_A01_T01_PL_SP-bp2-021.command`
- `PL!SP-bp2-021#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-bp2-021_A01_T02_PL_SP-bp2-021.command`
- `PL!SP-bp2-021#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-bp2-021_A01_T03_PL_SP-bp2-021.command`
- `PL!SP-bp2-021#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-021_A01_T04_PL_SP-bp2-021.command`
- `PL!SP-bp2-021#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-021_A01_T05_PL_SP-bp2-021.command`
- `PL!SP-bp2-021#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-bp2-021_A01_T06_PL_SP-bp2-021.command`
- `PL!SP-bp2-021#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp2-021_A01_T07_PL_SP-bp2-021.command`

## PL!SP-bp2-022
- `PL!SP-bp2-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-022_A01_T01_PL_SP-bp2-022.command`
- `PL!SP-bp2-022#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp2-022_A01_T02_PL_SP-bp2-022.command`
- `PL!SP-bp2-022#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp2-022_A01_T03_PL_SP-bp2-022.command`
- `PL!SP-bp2-022#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp2-022_A01_T04_PL_SP-bp2-022.command`
- `PL!SP-bp2-022#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp2-022_A01_T05_PL_SP-bp2-022.command`
- `PL!SP-bp2-022#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp2-022_A01_T06_PL_SP-bp2-022.command`

## PL!SP-bp2-023
- `PL!SP-bp2-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-023_A01_T01_PL_SP-bp2-023.command`
- `PL!SP-bp2-023#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp2-023_A01_T02_PL_SP-bp2-023.command`
- `PL!SP-bp2-023#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp2-023_A01_T03_PL_SP-bp2-023.command`
- `PL!SP-bp2-023#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp2-023_A01_T04_PL_SP-bp2-023.command`

## PL!SP-bp2-024
- `PL!SP-bp2-024#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-024_A01_T01_PL_SP-bp2-024.command`
- `PL!SP-bp2-024#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp2-024_A01_T02_PL_SP-bp2-024.command`
- `PL!SP-bp2-024#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp2-024_A01_T03_PL_SP-bp2-024.command`
- `PL!SP-bp2-024#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp2-024_A01_T04_PL_SP-bp2-024.command`

## PL!SP-bp2-025
- `PL!SP-bp2-025#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp2-025_A01_T01_PL_SP-bp2-025.command`
- `PL!SP-bp2-025#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp2-025_A01_T02_PL_SP-bp2-025.command`
- `PL!SP-bp2-025#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp2-025_A01_T03_PL_SP-bp2-025.command`
- `PL!SP-bp2-025#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp2-025_A01_T04_PL_SP-bp2-025.command`

## PL!SP-bp4-001
- `PL!SP-bp4-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-001_A01_T01_PL_SP-bp4-001.command`
- `PL!SP-bp4-001#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp4-001_A01_T02_PL_SP-bp4-001.command`
- `PL!SP-bp4-001#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp4-001_A01_T03_PL_SP-bp4-001.command`

## PL!SP-bp4-002
- `PL!SP-bp4-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-002_A01_T01_PL_SP-bp4-002.command`
- `PL!SP-bp4-002#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-002_A01_T02_PL_SP-bp4-002.command`
- `PL!SP-bp4-002#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-002_A01_T03_PL_SP-bp4-002.command`
- `PL!SP-bp4-002#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp4-002_A01_T04_PL_SP-bp4-002.command`
- `PL!SP-bp4-002#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp4-002_A01_T05_PL_SP-bp4-002.command`

## PL!SP-bp4-003
- `PL!SP-bp4-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-003_A01_T01_PL_SP-bp4-003.command`
- `PL!SP-bp4-003#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp4-003_A01_T02_PL_SP-bp4-003.command`
- `PL!SP-bp4-003#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp4-003_A01_T03_PL_SP-bp4-003.command`

## PL!SP-bp4-004
- `PL!SP-bp4-004#A02#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-004_A02_T01_PL_SP-bp4-004.command`
- `PL!SP-bp4-004#A02#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp4-004_A02_T02_PL_SP-bp4-004.command`
- `PL!SP-bp4-004#A02#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp4-004_A02_T03_PL_SP-bp4-004.command`

## PL!SP-bp4-005
- `PL!SP-bp4-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-005_A01_T01_PL_SP-bp4-005.command`
- `PL!SP-bp4-005#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp4-005_A01_T02_PL_SP-bp4-005.command`
- `PL!SP-bp4-005#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp4-005_A01_T03_PL_SP-bp4-005.command`
- `PL!SP-bp4-005#A02#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-005_A02_T01_PL_SP-bp4-005.command`
- `PL!SP-bp4-005#A02#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-005_A02_T02_PL_SP-bp4-005.command`
- `PL!SP-bp4-005#A02#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-bp4-005_A02_T03_PL_SP-bp4-005.command`
- `PL!SP-bp4-005#A02#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-bp4-005_A02_T04_PL_SP-bp4-005.command`
- `PL!SP-bp4-005#A02#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-bp4-005_A02_T05_PL_SP-bp4-005.command`

## PL!SP-bp4-006
- `PL!SP-bp4-006#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-006_A01_T01_PL_SP-bp4-006.command`
- `PL!SP-bp4-006#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-006_A01_T02_PL_SP-bp4-006.command`
- `PL!SP-bp4-006#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp4-006_A01_T03_PL_SP-bp4-006.command`
- `PL!SP-bp4-006#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-006_A01_T04_PL_SP-bp4-006.command`

## PL!SP-bp4-007
- `PL!SP-bp4-007#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-007_A01_T01_PL_SP-bp4-007.command`
- `PL!SP-bp4-007#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-bp4-007_A01_T02_PL_SP-bp4-007.command`
- `PL!SP-bp4-007#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-bp4-007_A01_T03_PL_SP-bp4-007.command`
- `PL!SP-bp4-007#A01#T04` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-bp4-007_A01_T04_PL_SP-bp4-007.command`
- `PL!SP-bp4-007#A01#T05` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp4-007_A01_T05_PL_SP-bp4-007.command`

## PL!SP-bp4-008
- `PL!SP-bp4-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-008_A01_T01_PL_SP-bp4-008.command`
- `PL!SP-bp4-008#A02#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-008_A02_T01_PL_SP-bp4-008.command`
- `PL!SP-bp4-008#A03#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-008_A03_T01_PL_SP-bp4-008.command`
- `PL!SP-bp4-008#A03#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-008_A03_T02_PL_SP-bp4-008.command`
- `PL!SP-bp4-008#A03#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp4-008_A03_T03_PL_SP-bp4-008.command`
- `PL!SP-bp4-008#A03#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-008_A03_T04_PL_SP-bp4-008.command`
- `PL!SP-bp4-008#A03#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-008_A03_T05_PL_SP-bp4-008.command`
- `PL!SP-bp4-008#A03#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-008_A03_T06_PL_SP-bp4-008.command`

## PL!SP-bp4-010
- `PL!SP-bp4-010#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-010_A01_T01_PL_SP-bp4-010.command`
- `PL!SP-bp4-010#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp4-010_A01_T02_PL_SP-bp4-010.command`
- `PL!SP-bp4-010#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp4-010_A01_T03_PL_SP-bp4-010.command`
- `PL!SP-bp4-010#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-bp4-010_A01_T04_PL_SP-bp4-010.command`
- `PL!SP-bp4-010#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp4-010_A01_T05_PL_SP-bp4-010.command`

## PL!SP-bp4-011
- `PL!SP-bp4-011#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-011_A01_T01_PL_SP-bp4-011.command`
- `PL!SP-bp4-011#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-bp4-011_A01_T02_PL_SP-bp4-011.command`
- `PL!SP-bp4-011#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-bp4-011_A01_T03_PL_SP-bp4-011.command`

## PL!SP-bp4-012
- `PL!SP-bp4-012#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-012_A01_T01_PL_SP-bp4-012.command`
- `PL!SP-bp4-012#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-012_A01_T02_PL_SP-bp4-012.command`
- `PL!SP-bp4-012#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-012_A01_T03_PL_SP-bp4-012.command`
- `PL!SP-bp4-012#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp4-012_A01_T04_PL_SP-bp4-012.command`
- `PL!SP-bp4-012#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp4-012_A01_T05_PL_SP-bp4-012.command`
- `PL!SP-bp4-012#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-012_A01_T06_PL_SP-bp4-012.command`

## PL!SP-bp4-013
- `PL!SP-bp4-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-013_A01_T01_PL_SP-bp4-013.command`
- `PL!SP-bp4-013#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp4-013_A01_T02_PL_SP-bp4-013.command`
- `PL!SP-bp4-013#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp4-013_A01_T03_PL_SP-bp4-013.command`
- `PL!SP-bp4-013#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-013_A01_T04_PL_SP-bp4-013.command`
- `PL!SP-bp4-013#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-013_A01_T05_PL_SP-bp4-013.command`

## PL!SP-bp4-015
- `PL!SP-bp4-015#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-015_A01_T01_PL_SP-bp4-015.command`
- `PL!SP-bp4-015#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp4-015_A01_T02_PL_SP-bp4-015.command`
- `PL!SP-bp4-015#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp4-015_A01_T03_PL_SP-bp4-015.command`

## PL!SP-bp4-017
- `PL!SP-bp4-017#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-017_A01_T01_PL_SP-bp4-017.command`
- `PL!SP-bp4-017#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-017_A01_T02_PL_SP-bp4-017.command`
- `PL!SP-bp4-017#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp4-017_A01_T03_PL_SP-bp4-017.command`
- `PL!SP-bp4-017#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-017_A01_T04_PL_SP-bp4-017.command`
- `PL!SP-bp4-017#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-017_A01_T05_PL_SP-bp4-017.command`
- `PL!SP-bp4-017#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-017_A01_T06_PL_SP-bp4-017.command`

## PL!SP-bp4-018
- `PL!SP-bp4-018#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-018_A01_T01_PL_SP-bp4-018.command`
- `PL!SP-bp4-018#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp4-018_A01_T02_PL_SP-bp4-018.command`
- `PL!SP-bp4-018#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp4-018_A01_T03_PL_SP-bp4-018.command`

## PL!SP-bp4-019
- `PL!SP-bp4-019#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-019_A01_T01_PL_SP-bp4-019.command`
- `PL!SP-bp4-019#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp4-019_A01_T02_PL_SP-bp4-019.command`
- `PL!SP-bp4-019#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp4-019_A01_T03_PL_SP-bp4-019.command`

## PL!SP-bp4-020
- `PL!SP-bp4-020#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-020_A01_T01_PL_SP-bp4-020.command`
- `PL!SP-bp4-020#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-020_A01_T02_PL_SP-bp4-020.command`
- `PL!SP-bp4-020#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp4-020_A01_T03_PL_SP-bp4-020.command`
- `PL!SP-bp4-020#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-020_A01_T04_PL_SP-bp4-020.command`
- `PL!SP-bp4-020#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-020_A01_T05_PL_SP-bp4-020.command`
- `PL!SP-bp4-020#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-020_A01_T06_PL_SP-bp4-020.command`

## PL!SP-bp4-022
- `PL!SP-bp4-022#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-022_A01_T01_PL_SP-bp4-022.command`
- `PL!SP-bp4-022#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-022_A01_T02_PL_SP-bp4-022.command`
- `PL!SP-bp4-022#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-022_A01_T03_PL_SP-bp4-022.command`
- `PL!SP-bp4-022#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp4-022_A01_T04_PL_SP-bp4-022.command`
- `PL!SP-bp4-022#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp4-022_A01_T05_PL_SP-bp4-022.command`
- `PL!SP-bp4-022#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-022_A01_T06_PL_SP-bp4-022.command`

## PL!SP-bp4-023
- `PL!SP-bp4-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-023_A01_T01_PL_SP-bp4-023.command`
- `PL!SP-bp4-023#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-023_A01_T02_PL_SP-bp4-023.command`
- `PL!SP-bp4-023#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-023_A01_T03_PL_SP-bp4-023.command`
- `PL!SP-bp4-023#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-023_A01_T04_PL_SP-bp4-023.command`
- `PL!SP-bp4-023#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-023_A02_T01_PL_SP-bp4-023.command`
- `PL!SP-bp4-023#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-023_A02_T02_PL_SP-bp4-023.command`
- `PL!SP-bp4-023#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-023_A02_T03_PL_SP-bp4-023.command`
- `PL!SP-bp4-023#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-023_A02_T04_PL_SP-bp4-023.command`

## PL!SP-bp4-024
- `PL!SP-bp4-024#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-024_A01_T01_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-024_A01_T02_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp4-024_A01_T03_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-024_A01_T04_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-024_A02_T01_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A02#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-024_A02_T02_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A02#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp4-024_A02_T03_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A02#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-024_A02_T04_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A02#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-024_A02_T05_PL_SP-bp4-024.command`
- `PL!SP-bp4-024#A02#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-024_A02_T06_PL_SP-bp4-024.command`

## PL!SP-bp4-025
- `PL!SP-bp4-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-025_A01_T01_PL_SP-bp4-025.command`
- `PL!SP-bp4-025#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-025_A01_T02_PL_SP-bp4-025.command`
- `PL!SP-bp4-025#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-025_A01_T03_PL_SP-bp4-025.command`
- `PL!SP-bp4-025#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-025_A01_T04_PL_SP-bp4-025.command`
- `PL!SP-bp4-025#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-025_A02_T01_PL_SP-bp4-025.command`
- `PL!SP-bp4-025#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-025_A02_T02_PL_SP-bp4-025.command`
- `PL!SP-bp4-025#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp4-025_A02_T03_PL_SP-bp4-025.command`
- `PL!SP-bp4-025#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-025_A02_T04_PL_SP-bp4-025.command`

## PL!SP-bp4-026
- `PL!SP-bp4-026#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-026_A01_T01_PL_SP-bp4-026.command`
- `PL!SP-bp4-026#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-026_A01_T02_PL_SP-bp4-026.command`
- `PL!SP-bp4-026#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp4-026_A01_T03_PL_SP-bp4-026.command`
- `PL!SP-bp4-026#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-026_A01_T04_PL_SP-bp4-026.command`
- `PL!SP-bp4-026#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-026_A02_T01_PL_SP-bp4-026.command`
- `PL!SP-bp4-026#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-026_A02_T02_PL_SP-bp4-026.command`
- `PL!SP-bp4-026#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp4-026_A02_T03_PL_SP-bp4-026.command`
- `PL!SP-bp4-026#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-026_A02_T04_PL_SP-bp4-026.command`

## PL!SP-bp4-027
- `PL!SP-bp4-027#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-027_A01_T01_PL_SP-bp4-027.command`
- `PL!SP-bp4-027#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-027_A01_T02_PL_SP-bp4-027.command`
- `PL!SP-bp4-027#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp4-027_A01_T03_PL_SP-bp4-027.command`
- `PL!SP-bp4-027#A01#T04` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp4-027_A01_T04_PL_SP-bp4-027.command`
- `PL!SP-bp4-027#A01#T05` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp4-027_A01_T05_PL_SP-bp4-027.command`
- `PL!SP-bp4-027#A01#T06` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-027_A01_T06_PL_SP-bp4-027.command`

## PL!SP-bp4-028
- `PL!SP-bp4-028#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp4-028_A01_T01_PL_SP-bp4-028.command`
- `PL!SP-bp4-028#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp4-028_A01_T02_PL_SP-bp4-028.command`
- `PL!SP-bp4-028#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp4-028_A01_T03_PL_SP-bp4-028.command`
- `PL!SP-bp4-028#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp4-028_A01_T04_PL_SP-bp4-028.command`

## PL!SP-bp5-001
- `PL!SP-bp5-001#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-001_A02_T01_PL_SP-bp5-001.command`
- `PL!SP-bp5-001#A02#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-001_A02_T02_PL_SP-bp5-001.command`
- `PL!SP-bp5-001#A02#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-001_A02_T03_PL_SP-bp5-001.command`
- `PL!SP-bp5-001#A02#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-bp5-001_A02_T04_PL_SP-bp5-001.command`
- `PL!SP-bp5-001#A02#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp5-001_A02_T05_PL_SP-bp5-001.command`

## PL!SP-bp5-002
- `PL!SP-bp5-002#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-002_A01_T01_PL_SP-bp5-002.command`
- `PL!SP-bp5-002#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_SP-bp5-002_A01_T02_PL_SP-bp5-002.command`
- `PL!SP-bp5-002#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_SP-bp5-002_A01_T03_PL_SP-bp5-002.command`
- `PL!SP-bp5-002#A01#T04` 起動 / 任意処理を実行 / command: `debug_commands/PL_SP-bp5-002_A01_T04_PL_SP-bp5-002.command`
- `PL!SP-bp5-002#A01#T05` 起動 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp5-002_A01_T05_PL_SP-bp5-002.command`
- `PL!SP-bp5-002#A01#T06` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-002_A01_T06_PL_SP-bp5-002.command`
- `PL!SP-bp5-002#A01#T07` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-002_A01_T07_PL_SP-bp5-002.command`
- `PL!SP-bp5-002#A01#T08` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-bp5-002_A01_T08_PL_SP-bp5-002.command`
- `PL!SP-bp5-002#A01#T09` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp5-002_A01_T09_PL_SP-bp5-002.command`

## PL!SP-bp5-003
- `PL!SP-bp5-003#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-003_A02_T01_PL_SP-bp5-003.command`
- `PL!SP-bp5-003#A02#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-003_A02_T02_PL_SP-bp5-003.command`

## PL!SP-bp5-004
- `PL!SP-bp5-004#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-004_A01_T01_PL_SP-bp5-004.command`
- `PL!SP-bp5-004#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-bp5-004_A01_T02_PL_SP-bp5-004.command`
- `PL!SP-bp5-004#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-bp5-004_A01_T03_PL_SP-bp5-004.command`
- `PL!SP-bp5-004#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-bp5-004_A01_T04_PL_SP-bp5-004.command`
- `PL!SP-bp5-004#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp5-004_A01_T05_PL_SP-bp5-004.command`
- `PL!SP-bp5-004#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-bp5-004_A01_T06_PL_SP-bp5-004.command`
- `PL!SP-bp5-004#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp5-004_A01_T07_PL_SP-bp5-004.command`

## PL!SP-bp5-006
- `PL!SP-bp5-006#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-006_A01_T01_PL_SP-bp5-006.command`
- `PL!SP-bp5-006#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_SP-bp5-006_A01_T02_PL_SP-bp5-006.command`
- `PL!SP-bp5-006#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_SP-bp5-006_A01_T03_PL_SP-bp5-006.command`
- `PL!SP-bp5-006#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-006_A01_T04_PL_SP-bp5-006.command`
- `PL!SP-bp5-006#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-006_A01_T05_PL_SP-bp5-006.command`
- `PL!SP-bp5-006#A01#T06` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-bp5-006_A01_T06_PL_SP-bp5-006.command`
- `PL!SP-bp5-006#A01#T07` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp5-006_A01_T07_PL_SP-bp5-006.command`

## PL!SP-bp5-007
- `PL!SP-bp5-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-007_A01_T01_PL_SP-bp5-007.command`
- `PL!SP-bp5-007#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-bp5-007_A01_T02_PL_SP-bp5-007.command`
- `PL!SP-bp5-007#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp5-007_A01_T03_PL_SP-bp5-007.command`
- `PL!SP-bp5-007#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-007_A01_T04_PL_SP-bp5-007.command`
- `PL!SP-bp5-007#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-007_A01_T05_PL_SP-bp5-007.command`

## PL!SP-bp5-008
- `PL!SP-bp5-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-008_A01_T01_PL_SP-bp5-008.command`
- `PL!SP-bp5-008#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-008_A01_T02_PL_SP-bp5-008.command`
- `PL!SP-bp5-008#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-008_A01_T03_PL_SP-bp5-008.command`

## PL!SP-bp5-009
- `PL!SP-bp5-009#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-009_A01_T01_PL_SP-bp5-009.command`
- `PL!SP-bp5-009#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp5-009_A01_T02_PL_SP-bp5-009.command`
- `PL!SP-bp5-009#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp5-009_A01_T03_PL_SP-bp5-009.command`
- `PL!SP-bp5-009#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp5-009_A01_T04_PL_SP-bp5-009.command`
- `PL!SP-bp5-009#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp5-009_A01_T05_PL_SP-bp5-009.command`
- `PL!SP-bp5-009#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-009_A01_T06_PL_SP-bp5-009.command`

## PL!SP-bp5-010
- `PL!SP-bp5-010#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-010_A01_T01_PL_SP-bp5-010.command`

## PL!SP-bp5-013
- `PL!SP-bp5-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-013_A01_T01_PL_SP-bp5-013.command`
- `PL!SP-bp5-013#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-013_A01_T02_PL_SP-bp5-013.command`
- `PL!SP-bp5-013#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-013_A01_T03_PL_SP-bp5-013.command`

## PL!SP-bp5-014
- `PL!SP-bp5-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-014_A01_T01_PL_SP-bp5-014.command`
- `PL!SP-bp5-014#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-bp5-014_A01_T02_PL_SP-bp5-014.command`
- `PL!SP-bp5-014#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-bp5-014_A01_T03_PL_SP-bp5-014.command`

## PL!SP-bp5-015
- `PL!SP-bp5-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-015_A01_T01_PL_SP-bp5-015.command`
- `PL!SP-bp5-015#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-bp5-015_A01_T02_PL_SP-bp5-015.command`
- `PL!SP-bp5-015#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp5-015_A01_T03_PL_SP-bp5-015.command`

## PL!SP-bp5-016
- `PL!SP-bp5-016#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-016_A01_T01_PL_SP-bp5-016.command`
- `PL!SP-bp5-016#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-bp5-016_A01_T02_PL_SP-bp5-016.command`
- `PL!SP-bp5-016#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-bp5-016_A01_T03_PL_SP-bp5-016.command`
- `PL!SP-bp5-016#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-bp5-016_A01_T04_PL_SP-bp5-016.command`
- `PL!SP-bp5-016#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-bp5-016_A01_T05_PL_SP-bp5-016.command`

## PL!SP-bp5-017
- `PL!SP-bp5-017#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-017_A01_T01_PL_SP-bp5-017.command`
- `PL!SP-bp5-017#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-bp5-017_A01_T02_PL_SP-bp5-017.command`
- `PL!SP-bp5-017#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-bp5-017_A01_T03_PL_SP-bp5-017.command`
- `PL!SP-bp5-017#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-bp5-017_A01_T04_PL_SP-bp5-017.command`
- `PL!SP-bp5-017#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-bp5-017_A01_T05_PL_SP-bp5-017.command`

## PL!SP-bp5-020
- `PL!SP-bp5-020#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-020_A01_T01_PL_SP-bp5-020.command`
- `PL!SP-bp5-020#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-020_A01_T02_PL_SP-bp5-020.command`
- `PL!SP-bp5-020#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-020_A01_T03_PL_SP-bp5-020.command`
- `PL!SP-bp5-020#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-bp5-020_A01_T04_PL_SP-bp5-020.command`
- `PL!SP-bp5-020#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp5-020_A01_T05_PL_SP-bp5-020.command`
- `PL!SP-bp5-020#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-020_A02_T01_PL_SP-bp5-020.command`
- `PL!SP-bp5-020#A02#T02` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-020_A02_T02_PL_SP-bp5-020.command`
- `PL!SP-bp5-020#A02#T03` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-020_A02_T03_PL_SP-bp5-020.command`
- `PL!SP-bp5-020#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-020_A02_T04_PL_SP-bp5-020.command`

## PL!SP-bp5-021
- `PL!SP-bp5-021#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-021_A01_T01_PL_SP-bp5-021.command`
- `PL!SP-bp5-021#A01#T02` 起動 / 条件不成立 / command: `debug_commands/PL_SP-bp5-021_A01_T02_PL_SP-bp5-021.command`
- `PL!SP-bp5-021#A01#T03` 起動 / 境界値 / command: `debug_commands/PL_SP-bp5-021_A01_T03_PL_SP-bp5-021.command`
- `PL!SP-bp5-021#A01#T04` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-021_A01_T04_PL_SP-bp5-021.command`
- `PL!SP-bp5-021#A01#T05` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-021_A01_T05_PL_SP-bp5-021.command`

## PL!SP-bp5-023
- `PL!SP-bp5-023#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-023_A01_T01_PL_SP-bp5-023.command`
- `PL!SP-bp5-023#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp5-023_A01_T02_PL_SP-bp5-023.command`
- `PL!SP-bp5-023#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp5-023_A01_T03_PL_SP-bp5-023.command`
- `PL!SP-bp5-023#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-023_A01_T04_PL_SP-bp5-023.command`

## PL!SP-bp5-024
- `PL!SP-bp5-024#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-024_A01_T01_PL_SP-bp5-024.command`
- `PL!SP-bp5-024#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp5-024_A01_T02_PL_SP-bp5-024.command`
- `PL!SP-bp5-024#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp5-024_A01_T03_PL_SP-bp5-024.command`
- `PL!SP-bp5-024#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-024_A01_T04_PL_SP-bp5-024.command`

## PL!SP-bp5-025
- `PL!SP-bp5-025#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-025_A01_T01_PL_SP-bp5-025.command`
- `PL!SP-bp5-025#A01#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-025_A01_T02_PL_SP-bp5-025.command`
- `PL!SP-bp5-025#A01#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-025_A01_T03_PL_SP-bp5-025.command`
- `PL!SP-bp5-025#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-025_A01_T04_PL_SP-bp5-025.command`

## PL!SP-bp5-026
- `PL!SP-bp5-026#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-026_A01_T01_PL_SP-bp5-026.command`
- `PL!SP-bp5-026#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp5-026_A01_T02_PL_SP-bp5-026.command`
- `PL!SP-bp5-026#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp5-026_A01_T03_PL_SP-bp5-026.command`
- `PL!SP-bp5-026#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-026_A01_T04_PL_SP-bp5-026.command`

## PL!SP-bp5-027
- `PL!SP-bp5-027#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-027_A01_T01_PL_SP-bp5-027.command`
- `PL!SP-bp5-027#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp5-027_A01_T02_PL_SP-bp5-027.command`
- `PL!SP-bp5-027#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp5-027_A01_T03_PL_SP-bp5-027.command`
- `PL!SP-bp5-027#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-027_A01_T04_PL_SP-bp5-027.command`

## PL!SP-bp5-111
- `PL!SP-bp5-111#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-111_A01_T01_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-bp5-111_A01_T02_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-bp5-111_A01_T03_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-bp5-111_A01_T04_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-bp5-111_A01_T05_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A02#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-111_A02_T01_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A02#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-111_A02_T02_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A02#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-111_A02_T03_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A02#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-bp5-111_A02_T04_PL_SP-bp5-111.command`
- `PL!SP-bp5-111#A02#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp5-111_A02_T05_PL_SP-bp5-111.command`

## PL!SP-bp5-222
- `PL!SP-bp5-222#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-222_A01_T01_PL_SP-bp5-222.command`
- `PL!SP-bp5-222#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-bp5-222_A01_T02_PL_SP-bp5-222.command`
- `PL!SP-bp5-222#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-bp5-222_A01_T03_PL_SP-bp5-222.command`
- `PL!SP-bp5-222#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-bp5-222_A01_T04_PL_SP-bp5-222.command`
- `PL!SP-bp5-222#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-bp5-222_A01_T05_PL_SP-bp5-222.command`
- `PL!SP-bp5-222#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp5-222_A02_T01_PL_SP-bp5-222.command`
- `PL!SP-bp5-222#A02#T02` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp5-222_A02_T02_PL_SP-bp5-222.command`
- `PL!SP-bp5-222#A02#T03` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp5-222_A02_T03_PL_SP-bp5-222.command`
- `PL!SP-bp5-222#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp5-222_A02_T04_PL_SP-bp5-222.command`

## PL!SP-bp7-004
- `PL!SP-bp7-004#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp7-004_A01_T01_PL_SP-bp7-004.command`
- `PL!SP-bp7-004#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-bp7-004_A01_T02_PL_SP-bp7-004.command`
- `PL!SP-bp7-004#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-bp7-004_A01_T03_PL_SP-bp7-004.command`
- `PL!SP-bp7-004#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp7-004_A01_T04_PL_SP-bp7-004.command`
- `PL!SP-bp7-004#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp7-004_A01_T05_PL_SP-bp7-004.command`
- `PL!SP-bp7-004#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp7-004_A01_T06_PL_SP-bp7-004.command`

## PL!SP-bp7-007
- `PL!SP-bp7-007#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp7-007_A01_T01_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-bp7-007_A01_T02_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp7-007_A01_T03_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-bp7-007_A01_T04_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-bp7-007_A01_T05_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp7-007_A01_T06_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp7-007_A02_T01_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A02#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp7-007_A02_T02_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A03#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-bp7-007_A03_T01_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A03#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-bp7-007_A03_T02_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A03#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-bp7-007_A03_T03_PL_SP-bp7-007.command`
- `PL!SP-bp7-007#A03#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-bp7-007_A03_T04_PL_SP-bp7-007.command`

## PL!SP-bp7-014
- `PL!SP-bp7-014#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-bp7-014_A01_T01_PL_SP-bp7-014.command`
- `PL!SP-bp7-014#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-bp7-014_A01_T02_PL_SP-bp7-014.command`
- `PL!SP-bp7-014#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-bp7-014_A01_T03_PL_SP-bp7-014.command`
- `PL!SP-bp7-014#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-bp7-014_A01_T04_PL_SP-bp7-014.command`
- `PL!SP-bp7-014#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-bp7-014_A01_T05_PL_SP-bp7-014.command`
- `PL!SP-bp7-014#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-bp7-014_A01_T06_PL_SP-bp7-014.command`
- `PL!SP-bp7-014#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-bp7-014_A01_T07_PL_SP-bp7-014.command`

## PL!SP-pb1-001
- `PL!SP-pb1-001#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-001_A01_T01_PL_SP-pb1-001.command`
- `PL!SP-pb1-001#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-pb1-001_A01_T02_PL_SP-pb1-001.command`
- `PL!SP-pb1-001#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-pb1-001_A01_T03_PL_SP-pb1-001.command`
- `PL!SP-pb1-001#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb1-001_A01_T04_PL_SP-pb1-001.command`
- `PL!SP-pb1-001#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-001_A02_T01_PL_SP-pb1-001.command`
- `PL!SP-pb1-001#A02#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-001_A02_T02_PL_SP-pb1-001.command`
- `PL!SP-pb1-001#A02#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-001_A02_T03_PL_SP-pb1-001.command`
- `PL!SP-pb1-001#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb1-001_A02_T04_PL_SP-pb1-001.command`

## PL!SP-pb1-002
- `PL!SP-pb1-002#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-002_A01_T01_PL_SP-pb1-002.command`
- `PL!SP-pb1-002#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-pb1-002_A01_T02_PL_SP-pb1-002.command`
- `PL!SP-pb1-002#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-pb1-002_A01_T03_PL_SP-pb1-002.command`
- `PL!SP-pb1-002#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-pb1-002_A01_T04_PL_SP-pb1-002.command`
- `PL!SP-pb1-002#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-pb1-002_A01_T05_PL_SP-pb1-002.command`

## PL!SP-pb1-003
- `PL!SP-pb1-003#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-003_A01_T01_PL_SP-pb1-003.command`
- `PL!SP-pb1-003#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-pb1-003_A01_T02_PL_SP-pb1-003.command`
- `PL!SP-pb1-003#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-pb1-003_A01_T03_PL_SP-pb1-003.command`

## PL!SP-pb1-004
- `PL!SP-pb1-004#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-004_A01_T01_PL_SP-pb1-004.command`
- `PL!SP-pb1-004#A01#T02` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-004_A01_T02_PL_SP-pb1-004.command`
- `PL!SP-pb1-004#A01#T03` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-004_A01_T03_PL_SP-pb1-004.command`
- `PL!SP-pb1-004#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb1-004_A01_T04_PL_SP-pb1-004.command`
- `PL!SP-pb1-004#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-004_A02_T01_PL_SP-pb1-004.command`
- `PL!SP-pb1-004#A02#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-004_A02_T02_PL_SP-pb1-004.command`
- `PL!SP-pb1-004#A02#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-004_A02_T03_PL_SP-pb1-004.command`
- `PL!SP-pb1-004#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb1-004_A02_T04_PL_SP-pb1-004.command`

## PL!SP-pb1-005
- `PL!SP-pb1-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-005_A01_T01_PL_SP-pb1-005.command`

## PL!SP-pb1-006
- `PL!SP-pb1-006#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-006_A01_T01_PL_SP-pb1-006.command`
- `PL!SP-pb1-006#A01#T02` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-pb1-006_A01_T02_PL_SP-pb1-006.command`
- `PL!SP-pb1-006#A01#T03` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb1-006_A01_T03_PL_SP-pb1-006.command`

## PL!SP-pb1-007
- `PL!SP-pb1-007#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-007_A01_T01_PL_SP-pb1-007.command`
- `PL!SP-pb1-007#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb1-007_A01_T02_PL_SP-pb1-007.command`

## PL!SP-pb1-008
- `PL!SP-pb1-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-008_A01_T01_PL_SP-pb1-008.command`
- `PL!SP-pb1-008#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-pb1-008_A01_T02_PL_SP-pb1-008.command`
- `PL!SP-pb1-008#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-pb1-008_A01_T03_PL_SP-pb1-008.command`

## PL!SP-pb1-009
- `PL!SP-pb1-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-009_A01_T01_PL_SP-pb1-009.command`
- `PL!SP-pb1-009#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-pb1-009_A01_T02_PL_SP-pb1-009.command`
- `PL!SP-pb1-009#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-pb1-009_A01_T03_PL_SP-pb1-009.command`

## PL!SP-pb1-010
- `PL!SP-pb1-010#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-010_A01_T01_PL_SP-pb1-010.command`
- `PL!SP-pb1-010#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-pb1-010_A01_T02_PL_SP-pb1-010.command`
- `PL!SP-pb1-010#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-pb1-010_A01_T03_PL_SP-pb1-010.command`
- `PL!SP-pb1-010#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-pb1-010_A01_T04_PL_SP-pb1-010.command`
- `PL!SP-pb1-010#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-pb1-010_A01_T05_PL_SP-pb1-010.command`

## PL!SP-pb1-011
- `PL!SP-pb1-011#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-011_A01_T01_PL_SP-pb1-011.command`
- `PL!SP-pb1-011#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-011_A01_T02_PL_SP-pb1-011.command`
- `PL!SP-pb1-011#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-011_A01_T03_PL_SP-pb1-011.command`

## PL!SP-pb1-015
- `PL!SP-pb1-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-015_A01_T01_PL_SP-pb1-015.command`
- `PL!SP-pb1-015#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-015_A01_T02_PL_SP-pb1-015.command`
- `PL!SP-pb1-015#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-015_A01_T03_PL_SP-pb1-015.command`

## PL!SP-pb1-016
- `PL!SP-pb1-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-016_A01_T01_PL_SP-pb1-016.command`
- `PL!SP-pb1-016#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-016_A01_T02_PL_SP-pb1-016.command`
- `PL!SP-pb1-016#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-016_A01_T03_PL_SP-pb1-016.command`

## PL!SP-pb1-017
- `PL!SP-pb1-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-017_A01_T01_PL_SP-pb1-017.command`
- `PL!SP-pb1-017#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-017_A01_T02_PL_SP-pb1-017.command`
- `PL!SP-pb1-017#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-017_A01_T03_PL_SP-pb1-017.command`

## PL!SP-pb1-018
- `PL!SP-pb1-018#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-018_A01_T01_PL_SP-pb1-018.command`
- `PL!SP-pb1-018#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-018_A01_T02_PL_SP-pb1-018.command`
- `PL!SP-pb1-018#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-018_A01_T03_PL_SP-pb1-018.command`

## PL!SP-pb1-020
- `PL!SP-pb1-020#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-020_A01_T01_PL_SP-pb1-020.command`

## PL!SP-pb1-021
- `PL!SP-pb1-021#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-021_A01_T01_PL_SP-pb1-021.command`
- `PL!SP-pb1-021#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-pb1-021_A01_T02_PL_SP-pb1-021.command`
- `PL!SP-pb1-021#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-pb1-021_A01_T03_PL_SP-pb1-021.command`

## PL!SP-pb1-023
- `PL!SP-pb1-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-023_A01_T01_PL_SP-pb1-023.command`
- `PL!SP-pb1-023#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-pb1-023_A01_T02_PL_SP-pb1-023.command`
- `PL!SP-pb1-023#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-pb1-023_A01_T03_PL_SP-pb1-023.command`
- `PL!SP-pb1-023#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-pb1-023_A01_T04_PL_SP-pb1-023.command`
- `PL!SP-pb1-023#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb1-023_A01_T05_PL_SP-pb1-023.command`
- `PL!SP-pb1-023#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb1-023_A01_T06_PL_SP-pb1-023.command`

## PL!SP-pb1-024
- `PL!SP-pb1-024#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-024_A01_T01_PL_SP-pb1-024.command`
- `PL!SP-pb1-024#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-pb1-024_A01_T02_PL_SP-pb1-024.command`
- `PL!SP-pb1-024#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-pb1-024_A01_T03_PL_SP-pb1-024.command`
- `PL!SP-pb1-024#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb1-024_A01_T04_PL_SP-pb1-024.command`

## PL!SP-pb1-025
- `PL!SP-pb1-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb1-025_A01_T01_PL_SP-pb1-025.command`
- `PL!SP-pb1-025#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb1-025_A01_T02_PL_SP-pb1-025.command`

## PL!SP-pb2-000
- `PL!SP-pb2-000#A02#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-000_A02_T01_PL_SP-pb2-000.command`
- `PL!SP-pb2-000#A02#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-pb2-000_A02_T02_PL_SP-pb2-000.command`
- `PL!SP-pb2-000#A02#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-pb2-000_A02_T03_PL_SP-pb2-000.command`
- `PL!SP-pb2-000#A02#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-000_A02_T04_PL_SP-pb2-000.command`
- `PL!SP-pb2-000#A02#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-000_A02_T05_PL_SP-pb2-000.command`

## PL!SP-pb2-001
- `PL!SP-pb2-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-001_A01_T01_PL_SP-pb2-001.command`
- `PL!SP-pb2-001#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-001_A01_T02_PL_SP-pb2-001.command`
- `PL!SP-pb2-001#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-001_A01_T03_PL_SP-pb2-001.command`
- `PL!SP-pb2-001#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-001_A01_T04_PL_SP-pb2-001.command`
- `PL!SP-pb2-001#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-001_A01_T05_PL_SP-pb2-001.command`

## PL!SP-pb2-003
- `PL!SP-pb2-003#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-003_A01_T01_PL_SP-pb2-003.command`
- `PL!SP-pb2-003#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-003_A01_T02_PL_SP-pb2-003.command`
- `PL!SP-pb2-003#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-pb2-003_A01_T03_PL_SP-pb2-003.command`
- `PL!SP-pb2-003#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-003_A01_T04_PL_SP-pb2-003.command`

## PL!SP-pb2-004
- `PL!SP-pb2-004#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-004_A01_T01_PL_SP-pb2-004.command`
- `PL!SP-pb2-004#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-004_A01_T02_PL_SP-pb2-004.command`
- `PL!SP-pb2-004#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-pb2-004_A01_T03_PL_SP-pb2-004.command`
- `PL!SP-pb2-004#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-004_A01_T04_PL_SP-pb2-004.command`

## PL!SP-pb2-005
- `PL!SP-pb2-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-005_A01_T01_PL_SP-pb2-005.command`
- `PL!SP-pb2-005#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-pb2-005_A01_T02_PL_SP-pb2-005.command`
- `PL!SP-pb2-005#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-pb2-005_A01_T03_PL_SP-pb2-005.command`

## PL!SP-pb2-007
- `PL!SP-pb2-007#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-007_A01_T01_PL_SP-pb2-007.command`
- `PL!SP-pb2-007#A01#T02` ライブ成功時 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-007_A01_T02_PL_SP-pb2-007.command`
- `PL!SP-pb2-007#A01#T03` ライブ成功時 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-007_A01_T03_PL_SP-pb2-007.command`
- `PL!SP-pb2-007#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-007_A01_T04_PL_SP-pb2-007.command`

## PL!SP-pb2-008
- `PL!SP-pb2-008#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-008_A01_T01_PL_SP-pb2-008.command`
- `PL!SP-pb2-008#A01#T02` ライブ成功時 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-008_A01_T02_PL_SP-pb2-008.command`
- `PL!SP-pb2-008#A01#T03` ライブ成功時 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-008_A01_T03_PL_SP-pb2-008.command`
- `PL!SP-pb2-008#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-008_A01_T04_PL_SP-pb2-008.command`

## PL!SP-pb2-009
- `PL!SP-pb2-009#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-009_A01_T01_PL_SP-pb2-009.command`
- `PL!SP-pb2-009#A01#T02` 登場 / ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-009_A01_T02_PL_SP-pb2-009.command`
- `PL!SP-pb2-009#A01#T03` 登場 / ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-009_A01_T03_PL_SP-pb2-009.command`
- `PL!SP-pb2-009#A01#T04` 登場 / ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-009_A01_T04_PL_SP-pb2-009.command`
- `PL!SP-pb2-009#A01#T05` 登場 / ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-009_A01_T05_PL_SP-pb2-009.command`

## PL!SP-pb2-010
- `PL!SP-pb2-010#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-010_A01_T01_PL_SP-pb2-010.command`
- `PL!SP-pb2-010#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-010_A01_T02_PL_SP-pb2-010.command`
- `PL!SP-pb2-010#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-pb2-010_A01_T03_PL_SP-pb2-010.command`
- `PL!SP-pb2-010#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-010_A01_T04_PL_SP-pb2-010.command`

## PL!SP-pb2-011
- `PL!SP-pb2-011#A02#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-011_A02_T01_PL_SP-pb2-011.command`
- `PL!SP-pb2-011#A02#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-011_A02_T02_PL_SP-pb2-011.command`
- `PL!SP-pb2-011#A02#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-011_A02_T03_PL_SP-pb2-011.command`
- `PL!SP-pb2-011#A02#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-011_A02_T04_PL_SP-pb2-011.command`

## PL!SP-pb2-012
- `PL!SP-pb2-012#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-012_A01_T01_PL_SP-pb2-012.command`
- `PL!SP-pb2-012#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-012_A01_T02_PL_SP-pb2-012.command`
- `PL!SP-pb2-012#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-012_A01_T03_PL_SP-pb2-012.command`

## PL!SP-pb2-013
- `PL!SP-pb2-013#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-013_A01_T01_PL_SP-pb2-013.command`
- `PL!SP-pb2-013#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-pb2-013_A01_T02_PL_SP-pb2-013.command`
- `PL!SP-pb2-013#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-pb2-013_A01_T03_PL_SP-pb2-013.command`
- `PL!SP-pb2-013#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-013_A01_T04_PL_SP-pb2-013.command`
- `PL!SP-pb2-013#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-013_A01_T05_PL_SP-pb2-013.command`

## PL!SP-pb2-014
- `PL!SP-pb2-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-014_A01_T01_PL_SP-pb2-014.command`
- `PL!SP-pb2-014#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-pb2-014_A01_T02_PL_SP-pb2-014.command`
- `PL!SP-pb2-014#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-pb2-014_A01_T03_PL_SP-pb2-014.command`
- `PL!SP-pb2-014#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-014_A01_T04_PL_SP-pb2-014.command`
- `PL!SP-pb2-014#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-014_A01_T05_PL_SP-pb2-014.command`

## PL!SP-pb2-015
- `PL!SP-pb2-015#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-015_A01_T01_PL_SP-pb2-015.command`
- `PL!SP-pb2-015#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-015_A01_T02_PL_SP-pb2-015.command`
- `PL!SP-pb2-015#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-015_A01_T03_PL_SP-pb2-015.command`

## PL!SP-pb2-016
- `PL!SP-pb2-016#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-016_A01_T01_PL_SP-pb2-016.command`
- `PL!SP-pb2-016#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-016_A01_T02_PL_SP-pb2-016.command`
- `PL!SP-pb2-016#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-016_A01_T03_PL_SP-pb2-016.command`

## PL!SP-pb2-017
- `PL!SP-pb2-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-017_A01_T01_PL_SP-pb2-017.command`
- `PL!SP-pb2-017#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-017_A01_T02_PL_SP-pb2-017.command`
- `PL!SP-pb2-017#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-017_A01_T03_PL_SP-pb2-017.command`

## PL!SP-pb2-018
- `PL!SP-pb2-018#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-018_A01_T01_PL_SP-pb2-018.command`
- `PL!SP-pb2-018#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-018_A01_T02_PL_SP-pb2-018.command`

## PL!SP-pb2-019
- `PL!SP-pb2-019#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-019_A01_T01_PL_SP-pb2-019.command`
- `PL!SP-pb2-019#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-019_A01_T02_PL_SP-pb2-019.command`
- `PL!SP-pb2-019#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-019_A01_T03_PL_SP-pb2-019.command`

## PL!SP-pb2-020
- `PL!SP-pb2-020#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-020_A01_T01_PL_SP-pb2-020.command`
- `PL!SP-pb2-020#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-pb2-020_A01_T02_PL_SP-pb2-020.command`
- `PL!SP-pb2-020#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-pb2-020_A01_T03_PL_SP-pb2-020.command`
- `PL!SP-pb2-020#A01#T04` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-pb2-020_A01_T04_PL_SP-pb2-020.command`
- `PL!SP-pb2-020#A01#T05` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-pb2-020_A01_T05_PL_SP-pb2-020.command`

## PL!SP-pb2-021
- `PL!SP-pb2-021#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-021_A01_T01_PL_SP-pb2-021.command`
- `PL!SP-pb2-021#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-021_A01_T02_PL_SP-pb2-021.command`
- `PL!SP-pb2-021#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-021_A01_T03_PL_SP-pb2-021.command`

## PL!SP-pb2-023
- `PL!SP-pb2-023#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-023_A01_T01_PL_SP-pb2-023.command`
- `PL!SP-pb2-023#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-023_A01_T02_PL_SP-pb2-023.command`
- `PL!SP-pb2-023#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-pb2-023_A01_T03_PL_SP-pb2-023.command`
- `PL!SP-pb2-023#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-pb2-023_A01_T04_PL_SP-pb2-023.command`
- `PL!SP-pb2-023#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-pb2-023_A01_T05_PL_SP-pb2-023.command`

## PL!SP-pb2-024
- `PL!SP-pb2-024#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-024_A01_T01_PL_SP-pb2-024.command`

## PL!SP-pb2-025
- `PL!SP-pb2-025#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-025_A01_T01_PL_SP-pb2-025.command`
- `PL!SP-pb2-025#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-pb2-025_A01_T02_PL_SP-pb2-025.command`
- `PL!SP-pb2-025#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-pb2-025_A01_T03_PL_SP-pb2-025.command`
- `PL!SP-pb2-025#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-025_A01_T04_PL_SP-pb2-025.command`
- `PL!SP-pb2-025#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-025_A01_T05_PL_SP-pb2-025.command`

## PL!SP-pb2-026
- `PL!SP-pb2-026#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-026_A01_T01_PL_SP-pb2-026.command`
- `PL!SP-pb2-026#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-026_A01_T02_PL_SP-pb2-026.command`
- `PL!SP-pb2-026#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-pb2-026_A01_T03_PL_SP-pb2-026.command`
- `PL!SP-pb2-026#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-pb2-026_A01_T04_PL_SP-pb2-026.command`
- `PL!SP-pb2-026#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-pb2-026_A01_T05_PL_SP-pb2-026.command`

## PL!SP-pb2-027
- `PL!SP-pb2-027#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-027_A01_T01_PL_SP-pb2-027.command`
- `PL!SP-pb2-027#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-027_A01_T02_PL_SP-pb2-027.command`
- `PL!SP-pb2-027#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-pb2-027_A01_T03_PL_SP-pb2-027.command`
- `PL!SP-pb2-027#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-pb2-027_A01_T04_PL_SP-pb2-027.command`
- `PL!SP-pb2-027#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-pb2-027_A01_T05_PL_SP-pb2-027.command`

## PL!SP-pb2-028
- `PL!SP-pb2-028#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-028_A01_T01_PL_SP-pb2-028.command`
- `PL!SP-pb2-028#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-pb2-028_A01_T02_PL_SP-pb2-028.command`
- `PL!SP-pb2-028#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-pb2-028_A01_T03_PL_SP-pb2-028.command`
- `PL!SP-pb2-028#A01#T04` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-pb2-028_A01_T04_PL_SP-pb2-028.command`
- `PL!SP-pb2-028#A01#T05` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-pb2-028_A01_T05_PL_SP-pb2-028.command`

## PL!SP-pb2-029
- `PL!SP-pb2-029#A01#T01` 登場 / ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-029_A01_T01_PL_SP-pb2-029.command`

## PL!SP-pb2-030
- `PL!SP-pb2-030#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-030_A01_T01_PL_SP-pb2-030.command`
- `PL!SP-pb2-030#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-030_A01_T02_PL_SP-pb2-030.command`
- `PL!SP-pb2-030#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-030_A01_T03_PL_SP-pb2-030.command`
- `PL!SP-pb2-030#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-030_A01_T04_PL_SP-pb2-030.command`

## PL!SP-pb2-031
- `PL!SP-pb2-031#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-031_A01_T01_PL_SP-pb2-031.command`
- `PL!SP-pb2-031#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-031_A01_T02_PL_SP-pb2-031.command`
- `PL!SP-pb2-031#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-031_A01_T03_PL_SP-pb2-031.command`

## PL!SP-pb2-032
- `PL!SP-pb2-032#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-032_A01_T01_PL_SP-pb2-032.command`
- `PL!SP-pb2-032#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-032_A01_T02_PL_SP-pb2-032.command`
- `PL!SP-pb2-032#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-pb2-032_A01_T03_PL_SP-pb2-032.command`
- `PL!SP-pb2-032#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-pb2-032_A01_T04_PL_SP-pb2-032.command`
- `PL!SP-pb2-032#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-pb2-032_A01_T05_PL_SP-pb2-032.command`

## PL!SP-pb2-033
- `PL!SP-pb2-033#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-033_A01_T01_PL_SP-pb2-033.command`
- `PL!SP-pb2-033#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-033_A01_T02_PL_SP-pb2-033.command`
- `PL!SP-pb2-033#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-033_A01_T03_PL_SP-pb2-033.command`

## PL!SP-pb2-036
- `PL!SP-pb2-036#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-036_A01_T01_PL_SP-pb2-036.command`

## PL!SP-pb2-037
- `PL!SP-pb2-037#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-037_A01_T01_PL_SP-pb2-037.command`

## PL!SP-pb2-040
- `PL!SP-pb2-040#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-040_A01_T01_PL_SP-pb2-040.command`
- `PL!SP-pb2-040#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-040_A01_T02_PL_SP-pb2-040.command`
- `PL!SP-pb2-040#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-040_A01_T03_PL_SP-pb2-040.command`
- `PL!SP-pb2-040#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-040_A01_T04_PL_SP-pb2-040.command`
- `PL!SP-pb2-040#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-040_A01_T05_PL_SP-pb2-040.command`
- `PL!SP-pb2-040#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-040_A01_T06_PL_SP-pb2-040.command`

## PL!SP-pb2-045
- `PL!SP-pb2-045#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-045_A01_T01_PL_SP-pb2-045.command`
- `PL!SP-pb2-045#A01#T02` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-045_A01_T02_PL_SP-pb2-045.command`

## PL!SP-pb2-047
- `PL!SP-pb2-047#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-047_A01_T01_PL_SP-pb2-047.command`
- `PL!SP-pb2-047#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-047_A01_T02_PL_SP-pb2-047.command`
- `PL!SP-pb2-047#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-pb2-047_A01_T03_PL_SP-pb2-047.command`
- `PL!SP-pb2-047#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-pb2-047_A01_T04_PL_SP-pb2-047.command`
- `PL!SP-pb2-047#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-pb2-047_A01_T05_PL_SP-pb2-047.command`
- `PL!SP-pb2-047#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-047_A01_T06_PL_SP-pb2-047.command`

## PL!SP-pb2-048
- `PL!SP-pb2-048#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-048_A01_T01_PL_SP-pb2-048.command`
- `PL!SP-pb2-048#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-048_A01_T02_PL_SP-pb2-048.command`
- `PL!SP-pb2-048#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-pb2-048_A01_T03_PL_SP-pb2-048.command`
- `PL!SP-pb2-048#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-048_A01_T04_PL_SP-pb2-048.command`

## PL!SP-pb2-049
- `PL!SP-pb2-049#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-049_A01_T01_PL_SP-pb2-049.command`
- `PL!SP-pb2-049#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-049_A01_T02_PL_SP-pb2-049.command`
- `PL!SP-pb2-049#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-pb2-049_A01_T03_PL_SP-pb2-049.command`
- `PL!SP-pb2-049#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-049_A01_T04_PL_SP-pb2-049.command`
- `PL!SP-pb2-049#A02#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-049_A02_T01_PL_SP-pb2-049.command`
- `PL!SP-pb2-049#A02#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-049_A02_T02_PL_SP-pb2-049.command`
- `PL!SP-pb2-049#A02#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-pb2-049_A02_T03_PL_SP-pb2-049.command`
- `PL!SP-pb2-049#A02#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-049_A02_T04_PL_SP-pb2-049.command`

## PL!SP-pb2-050
- `PL!SP-pb2-050#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-pb2-050_A01_T01_PL_SP-pb2-050.command`
- `PL!SP-pb2-050#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-pb2-050_A01_T02_PL_SP-pb2-050.command`
- `PL!SP-pb2-050#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-pb2-050_A01_T03_PL_SP-pb2-050.command`
- `PL!SP-pb2-050#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-pb2-050_A01_T04_PL_SP-pb2-050.command`
- `PL!SP-pb2-050#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-pb2-050_A01_T05_PL_SP-pb2-050.command`
- `PL!SP-pb2-050#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-pb2-050_A01_T06_PL_SP-pb2-050.command`

## PL!SP-sd1-001
- `PL!SP-sd1-001#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-001_A01_T01_PL_SP-sd1-001.command`

## PL!SP-sd1-002
- `PL!SP-sd1-002#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-002_A01_T01_PL_SP-sd1-002.command`

## PL!SP-sd1-003
- `PL!SP-sd1-003#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-003_A01_T01_PL_SP-sd1-003.command`
- `PL!SP-sd1-003#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-sd1-003_A01_T02_PL_SP-sd1-003.command`
- `PL!SP-sd1-003#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd1-003_A01_T03_PL_SP-sd1-003.command`
- `PL!SP-sd1-003#A01#T04` ライブ開始時 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-003_A01_T04_PL_SP-sd1-003.command`
- `PL!SP-sd1-003#A01#T05` ライブ開始時 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-003_A01_T05_PL_SP-sd1-003.command`
- `PL!SP-sd1-003#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-sd1-003_A01_T06_PL_SP-sd1-003.command`

## PL!SP-sd1-004
- `PL!SP-sd1-004#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-004_A01_T01_PL_SP-sd1-004.command`
- `PL!SP-sd1-004#A01#T02` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-sd1-004_A01_T02_PL_SP-sd1-004.command`
- `PL!SP-sd1-004#A01#T03` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd1-004_A01_T03_PL_SP-sd1-004.command`

## PL!SP-sd1-005
- `PL!SP-sd1-005#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-005_A01_T01_PL_SP-sd1-005.command`
- `PL!SP-sd1-005#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-005_A01_T02_PL_SP-sd1-005.command`
- `PL!SP-sd1-005#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-005_A01_T03_PL_SP-sd1-005.command`
- `PL!SP-sd1-005#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-sd1-005_A01_T04_PL_SP-sd1-005.command`
- `PL!SP-sd1-005#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd1-005_A01_T05_PL_SP-sd1-005.command`

## PL!SP-sd1-006
- `PL!SP-sd1-006#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-006_A01_T01_PL_SP-sd1-006.command`
- `PL!SP-sd1-006#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-006_A01_T02_PL_SP-sd1-006.command`
- `PL!SP-sd1-006#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-006_A01_T03_PL_SP-sd1-006.command`

## PL!SP-sd1-007
- `PL!SP-sd1-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-007_A01_T01_PL_SP-sd1-007.command`
- `PL!SP-sd1-007#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-007_A01_T02_PL_SP-sd1-007.command`
- `PL!SP-sd1-007#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-007_A01_T03_PL_SP-sd1-007.command`

## PL!SP-sd1-008
- `PL!SP-sd1-008#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-008_A01_T01_PL_SP-sd1-008.command`
- `PL!SP-sd1-008#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-008_A01_T02_PL_SP-sd1-008.command`
- `PL!SP-sd1-008#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-008_A01_T03_PL_SP-sd1-008.command`

## PL!SP-sd1-009
- `PL!SP-sd1-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-009_A01_T01_PL_SP-sd1-009.command`
- `PL!SP-sd1-009#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-sd1-009_A01_T02_PL_SP-sd1-009.command`
- `PL!SP-sd1-009#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-sd1-009_A01_T03_PL_SP-sd1-009.command`
- `PL!SP-sd1-009#A01#T04` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-009_A01_T04_PL_SP-sd1-009.command`
- `PL!SP-sd1-009#A01#T05` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-009_A01_T05_PL_SP-sd1-009.command`

## PL!SP-sd1-011
- `PL!SP-sd1-011#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-011_A01_T01_PL_SP-sd1-011.command`
- `PL!SP-sd1-011#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-011_A01_T02_PL_SP-sd1-011.command`
- `PL!SP-sd1-011#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-011_A01_T03_PL_SP-sd1-011.command`
- `PL!SP-sd1-011#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-sd1-011_A01_T04_PL_SP-sd1-011.command`
- `PL!SP-sd1-011#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd1-011_A01_T05_PL_SP-sd1-011.command`

## PL!SP-sd1-014
- `PL!SP-sd1-014#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-014_A01_T01_PL_SP-sd1-014.command`
- `PL!SP-sd1-014#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-014_A01_T02_PL_SP-sd1-014.command`
- `PL!SP-sd1-014#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-014_A01_T03_PL_SP-sd1-014.command`

## PL!SP-sd1-016
- `PL!SP-sd1-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-016_A01_T01_PL_SP-sd1-016.command`
- `PL!SP-sd1-016#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-016_A01_T02_PL_SP-sd1-016.command`
- `PL!SP-sd1-016#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-016_A01_T03_PL_SP-sd1-016.command`

## PL!SP-sd1-017
- `PL!SP-sd1-017#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-017_A01_T01_PL_SP-sd1-017.command`
- `PL!SP-sd1-017#A01#T02` 登場 / コスト支払い可能 / command: `debug_commands/PL_SP-sd1-017_A01_T02_PL_SP-sd1-017.command`
- `PL!SP-sd1-017#A01#T03` 登場 / コスト支払い不能 / command: `debug_commands/PL_SP-sd1-017_A01_T03_PL_SP-sd1-017.command`

## PL!SP-sd1-026
- `PL!SP-sd1-026#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd1-026_A01_T01_PL_SP-sd1-026.command`
- `PL!SP-sd1-026#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-sd1-026_A01_T02_PL_SP-sd1-026.command`
- `PL!SP-sd1-026#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-sd1-026_A01_T03_PL_SP-sd1-026.command`
- `PL!SP-sd1-026#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-sd1-026_A01_T04_PL_SP-sd1-026.command`

## PL!SP-sd2-001
- `PL!SP-sd2-001#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-001_A01_T01_PL_SP-sd2-001.command`
- `PL!SP-sd2-001#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-001_A01_T02_PL_SP-sd2-001.command`
- `PL!SP-sd2-001#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-001_A01_T03_PL_SP-sd2-001.command`
- `PL!SP-sd2-001#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-sd2-001_A01_T04_PL_SP-sd2-001.command`

## PL!SP-sd2-002
- `PL!SP-sd2-002#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-002_A01_T01_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-sd2-002_A01_T02_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-sd2-002_A01_T03_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-sd2-002_A01_T04_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd2-002_A01_T05_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A02#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-002_A02_T01_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A02#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-sd2-002_A02_T02_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A02#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-sd2-002_A02_T03_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A02#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-002_A02_T04_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A02#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-002_A02_T05_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A02#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-sd2-002_A02_T06_PL_SP-sd2-002.command`
- `PL!SP-sd2-002#A02#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd2-002_A02_T07_PL_SP-sd2-002.command`

## PL!SP-sd2-003
- `PL!SP-sd2-003#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-003_A01_T01_PL_SP-sd2-003.command`
- `PL!SP-sd2-003#A01#T02` ライブ成功時 / 条件不成立 / command: `debug_commands/PL_SP-sd2-003_A01_T02_PL_SP-sd2-003.command`
- `PL!SP-sd2-003#A01#T03` ライブ成功時 / 境界値 / command: `debug_commands/PL_SP-sd2-003_A01_T03_PL_SP-sd2-003.command`
- `PL!SP-sd2-003#A01#T04` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-sd2-003_A01_T04_PL_SP-sd2-003.command`

## PL!SP-sd2-005
- `PL!SP-sd2-005#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-005_A01_T01_PL_SP-sd2-005.command`
- `PL!SP-sd2-005#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-sd2-005_A01_T02_PL_SP-sd2-005.command`
- `PL!SP-sd2-005#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-sd2-005_A01_T03_PL_SP-sd2-005.command`
- `PL!SP-sd2-005#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-005_A01_T04_PL_SP-sd2-005.command`
- `PL!SP-sd2-005#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-005_A01_T05_PL_SP-sd2-005.command`

## PL!SP-sd2-006
- `PL!SP-sd2-006#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-006_A01_T01_PL_SP-sd2-006.command`
- `PL!SP-sd2-006#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-sd2-006_A01_T02_PL_SP-sd2-006.command`
- `PL!SP-sd2-006#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-sd2-006_A01_T03_PL_SP-sd2-006.command`
- `PL!SP-sd2-006#A01#T04` 起動 / 回数制限超過 / command: `debug_commands/PL_SP-sd2-006_A01_T04_PL_SP-sd2-006.command`
- `PL!SP-sd2-006#A01#T05` 起動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd2-006_A01_T05_PL_SP-sd2-006.command`

## PL!SP-sd2-007
- `PL!SP-sd2-007#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-007_A01_T01_PL_SP-sd2-007.command`
- `PL!SP-sd2-007#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-sd2-007_A01_T02_PL_SP-sd2-007.command`
- `PL!SP-sd2-007#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-sd2-007_A01_T03_PL_SP-sd2-007.command`
- `PL!SP-sd2-007#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-007_A01_T04_PL_SP-sd2-007.command`
- `PL!SP-sd2-007#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-007_A01_T05_PL_SP-sd2-007.command`

## PL!SP-sd2-008
- `PL!SP-sd2-008#A01#T01` 常時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-008_A01_T01_PL_SP-sd2-008.command`
- `PL!SP-sd2-008#A01#T02` 常時 / 条件不成立 / command: `debug_commands/PL_SP-sd2-008_A01_T02_PL_SP-sd2-008.command`
- `PL!SP-sd2-008#A01#T03` 常時 / 境界値 / command: `debug_commands/PL_SP-sd2-008_A01_T03_PL_SP-sd2-008.command`
- `PL!SP-sd2-008#A01#T04` 常時 / 条件変化で即時反映 / command: `debug_commands/PL_SP-sd2-008_A01_T04_PL_SP-sd2-008.command`
- `PL!SP-sd2-008#A01#T05` 常時 / 条件消失で解除 / command: `debug_commands/PL_SP-sd2-008_A01_T05_PL_SP-sd2-008.command`

## PL!SP-sd2-009
- `PL!SP-sd2-009#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-009_A01_T01_PL_SP-sd2-009.command`

## PL!SP-sd2-010
- `PL!SP-sd2-010#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-010_A01_T01_PL_SP-sd2-010.command`
- `PL!SP-sd2-010#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-sd2-010_A01_T02_PL_SP-sd2-010.command`
- `PL!SP-sd2-010#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-sd2-010_A01_T03_PL_SP-sd2-010.command`

## PL!SP-sd2-011
- `PL!SP-sd2-011#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-011_A01_T01_PL_SP-sd2-011.command`
- `PL!SP-sd2-011#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-sd2-011_A01_T02_PL_SP-sd2-011.command`
- `PL!SP-sd2-011#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-sd2-011_A01_T03_PL_SP-sd2-011.command`
- `PL!SP-sd2-011#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-011_A01_T04_PL_SP-sd2-011.command`
- `PL!SP-sd2-011#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-011_A01_T05_PL_SP-sd2-011.command`
- `PL!SP-sd2-011#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-sd2-011_A01_T06_PL_SP-sd2-011.command`
- `PL!SP-sd2-011#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd2-011_A01_T07_PL_SP-sd2-011.command`

## PL!SP-sd2-012
- `PL!SP-sd2-012#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-012_A01_T01_PL_SP-sd2-012.command`
- `PL!SP-sd2-012#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-sd2-012_A01_T02_PL_SP-sd2-012.command`
- `PL!SP-sd2-012#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-sd2-012_A01_T03_PL_SP-sd2-012.command`
- `PL!SP-sd2-012#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-012_A01_T04_PL_SP-sd2-012.command`
- `PL!SP-sd2-012#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-012_A01_T05_PL_SP-sd2-012.command`
- `PL!SP-sd2-012#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-sd2-012_A01_T06_PL_SP-sd2-012.command`
- `PL!SP-sd2-012#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd2-012_A01_T07_PL_SP-sd2-012.command`

## PL!SP-sd2-013
- `PL!SP-sd2-013#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-013_A01_T01_PL_SP-sd2-013.command`
- `PL!SP-sd2-013#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-sd2-013_A01_T02_PL_SP-sd2-013.command`
- `PL!SP-sd2-013#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-sd2-013_A01_T03_PL_SP-sd2-013.command`
- `PL!SP-sd2-013#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-013_A01_T04_PL_SP-sd2-013.command`
- `PL!SP-sd2-013#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-013_A01_T05_PL_SP-sd2-013.command`
- `PL!SP-sd2-013#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-sd2-013_A01_T06_PL_SP-sd2-013.command`
- `PL!SP-sd2-013#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd2-013_A01_T07_PL_SP-sd2-013.command`

## PL!SP-sd2-014
- `PL!SP-sd2-014#A01#T01` 起動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-014_A01_T01_PL_SP-sd2-014.command`
- `PL!SP-sd2-014#A01#T02` 起動 / コスト支払い可能 / command: `debug_commands/PL_SP-sd2-014_A01_T02_PL_SP-sd2-014.command`
- `PL!SP-sd2-014#A01#T03` 起動 / コスト支払い不能 / command: `debug_commands/PL_SP-sd2-014_A01_T03_PL_SP-sd2-014.command`

## PL!SP-sd2-016
- `PL!SP-sd2-016#A01#T01` 登場 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-016_A01_T01_PL_SP-sd2-016.command`
- `PL!SP-sd2-016#A01#T02` 登場 / 条件不成立 / command: `debug_commands/PL_SP-sd2-016_A01_T02_PL_SP-sd2-016.command`
- `PL!SP-sd2-016#A01#T03` 登場 / 境界値 / command: `debug_commands/PL_SP-sd2-016_A01_T03_PL_SP-sd2-016.command`
- `PL!SP-sd2-016#A01#T04` 登場 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-016_A01_T04_PL_SP-sd2-016.command`
- `PL!SP-sd2-016#A01#T05` 登場 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-016_A01_T05_PL_SP-sd2-016.command`

## PL!SP-sd2-017
- `PL!SP-sd2-017#A01#T01` ライブ成功時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-017_A01_T01_PL_SP-sd2-017.command`
- `PL!SP-sd2-017#A01#T02` ライブ成功時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-sd2-017_A01_T02_PL_SP-sd2-017.command`

## PL!SP-sd2-020
- `PL!SP-sd2-020#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-020_A01_T01_PL_SP-sd2-020.command`
- `PL!SP-sd2-020#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-sd2-020_A01_T02_PL_SP-sd2-020.command`
- `PL!SP-sd2-020#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-sd2-020_A01_T03_PL_SP-sd2-020.command`
- `PL!SP-sd2-020#A01#T04` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-020_A01_T04_PL_SP-sd2-020.command`
- `PL!SP-sd2-020#A01#T05` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-020_A01_T05_PL_SP-sd2-020.command`
- `PL!SP-sd2-020#A01#T06` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-sd2-020_A01_T06_PL_SP-sd2-020.command`

## PL!SP-sd2-022
- `PL!SP-sd2-022#A01#T01` 自動 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-022_A01_T01_PL_SP-sd2-022.command`
- `PL!SP-sd2-022#A01#T02` 自動 / 条件不成立 / command: `debug_commands/PL_SP-sd2-022_A01_T02_PL_SP-sd2-022.command`
- `PL!SP-sd2-022#A01#T03` 自動 / 境界値 / command: `debug_commands/PL_SP-sd2-022_A01_T03_PL_SP-sd2-022.command`
- `PL!SP-sd2-022#A01#T04` 自動 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-022_A01_T04_PL_SP-sd2-022.command`
- `PL!SP-sd2-022#A01#T05` 自動 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-022_A01_T05_PL_SP-sd2-022.command`
- `PL!SP-sd2-022#A01#T06` 自動 / 回数制限超過 / command: `debug_commands/PL_SP-sd2-022_A01_T06_PL_SP-sd2-022.command`
- `PL!SP-sd2-022#A01#T07` 自動 / ターン跨ぎリセット / command: `debug_commands/PL_SP-sd2-022_A01_T07_PL_SP-sd2-022.command`

## PL!SP-sd2-023
- `PL!SP-sd2-023#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-023_A01_T01_PL_SP-sd2-023.command`
- `PL!SP-sd2-023#A01#T02` ライブ開始時 / 条件不成立 / command: `debug_commands/PL_SP-sd2-023_A01_T02_PL_SP-sd2-023.command`
- `PL!SP-sd2-023#A01#T03` ライブ開始時 / 境界値 / command: `debug_commands/PL_SP-sd2-023_A01_T03_PL_SP-sd2-023.command`
- `PL!SP-sd2-023#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-sd2-023_A01_T04_PL_SP-sd2-023.command`

## PL!SP-sd2-025
- `PL!SP-sd2-025#A01#T01` ライブ開始時 / 成立・通常解決 / command: `debug_commands/PL_SP-sd2-025_A01_T01_PL_SP-sd2-025.command`
- `PL!SP-sd2-025#A01#T02` ライブ開始時 / 任意処理を実行 / command: `debug_commands/PL_SP-sd2-025_A01_T02_PL_SP-sd2-025.command`
- `PL!SP-sd2-025#A01#T03` ライブ開始時 / 任意処理を実行しない / command: `debug_commands/PL_SP-sd2-025_A01_T03_PL_SP-sd2-025.command`
- `PL!SP-sd2-025#A01#T04` ライブ開始時 / ライブ終了時クリーンアップ / command: `debug_commands/PL_SP-sd2-025_A01_T04_PL_SP-sd2-025.command`
