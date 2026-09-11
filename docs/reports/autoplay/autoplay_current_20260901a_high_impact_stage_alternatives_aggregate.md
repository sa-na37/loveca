# Loveca Autoplay Multi-Seed Summary

複数seedで同じデッキを回し、平均・最小・最大・ばらつきをまとめた確認表です。
単一seedの偏りを見るのではなく、主に `combined_cumulative_mean` と `cumulative_mean` を見ます。

| Deck | Seeds | Recommended | T2 stage mean | T3 stage mean | T3 recovery mean | T3 combined mean | T4 stage mean | T4 recovery mean |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 果林 | 901,902 | 2-2 -> 2-4-2 -> 2-10-2 | 0.9333 | 0.7416 | 0.7416 | 0.0083 | 0.4167 | 0.4167 |
| 真黄ちゃん | 901,902 | 4 -> 9 -> 15単騎 | 0.8583 | 0.5917 | 0.5917 | 0.0 | 0.0 | 0.0 |
| EN | 901,902 | 4 -> 9 -> 15単騎 | 0.8917 | 0.7083 | 0.7083 | 0.0834 | 0.3834 | 0.3834 |
| けつ空手 | 901,902 | dynamic energy-activate 2-2 -> 4-2-2 -> 9-4-2 -> 17-9-2 -> 17-13-2 | 0.8583 | 0.3167 | 0.3584 | 0.0083 | 0.0 | 0.0 |

## Miss Examples

- 果林: T2 missing 4 4 (0.0667) / missing 4 3 (0.05) / T3 missing 10 18 (0.3) / missing 10 13 (0.2167)
- 真黄ちゃん: T2 missing 9 11 (0.1833) / missing 9 6 (0.1) / T3 missing 15 25 (0.4167) / missing 15 24 (0.4)
- EN: T2 missing 9 7 (0.1167) / missing 9 6 (0.1) / T3 missing 15 19 (0.3167) / missing 15 16 (0.2667)
- けつ空手: T2 missing 4 2 (0.0333) / missing 2 7 (0.1167) / T3 missing 9 37 (0.6167) / missing 9 36 (0.6)
