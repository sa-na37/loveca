# Loveca Autoplay Multi-Seed Summary

複数seedで同じデッキを回し、平均・最小・最大・ばらつきをまとめた確認表です。
単一seedの偏りを見るのではなく、主に `combined_cumulative_mean` と `cumulative_mean` を見ます。

| Deck | Seeds | Recommended | T2 stage mean | T3 stage mean | T3 combined mean | T4 stage mean |
|---|---:|---|---:|---:|---:|---:|
| 5軸ミラステ | 401,502,603 | 2-2 -> 2-5-2 -> 2-11-2 | 0.8056 | 0.5195 | 0.0167 | 0.2805 |
| 10軸ミラステ | 401,502,603 | 2-2 -> 2-4-2 -> 2-10-2 | 0.8278 | 0.6889 | 0.025 | 0.2222 |
| 君ここ | 401,502,603 | 2-2 -> 7-2 -> 13-2 | 0.8639 | 0.7083 | 0.0 | 0.5889 |

## Miss Examples

- 5軸ミラステ: T2 missing 2 13 (0.1083) / missing 2 16 (0.1333) / missing 2 13 (0.1083) / T3 missing 11 56 (0.4667) / missing 11 45 (0.375) / missing 11 42 (0.35)
- 10軸ミラステ: T2 missing 2 15 (0.125) / missing 2 14 (0.1167) / missing 2 18 (0.15) / T3 missing 10 20 (0.1667) / missing 10 31 (0.2583) / missing 10 22 (0.1833)
- 君ここ: T2 missing 7 11 (0.0917) / missing 7 11 (0.0917) / missing 7 11 (0.0917) / T3 missing 13 30 (0.25) / missing 13 32 (0.2667) / missing 13 28 (0.2333)
