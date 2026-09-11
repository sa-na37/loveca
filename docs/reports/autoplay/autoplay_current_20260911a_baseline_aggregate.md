# Loveca Autoplay Multi-Seed Summary

複数seedで同じデッキを回し、平均・最小・最大・ばらつきをまとめた確認表です。
単一seedの偏りを見るのではなく、主に `combined_cumulative_mean` と `cumulative_mean` を見ます。

| Deck | Seeds | Recommended | T2 stage mean | T3 stage mean | T3 recovery mean | T3 combined mean | T4 stage mean | T4 recovery mean |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 果林 | 901,902 | 2-2 -> 2-4-2 -> 2-10-2 | 0.95 | 0.75 | 0.75 | 0.0125 | 0.4562 | 0.4562 |
| 真黄ちゃん | 901,902 | 4 -> 9 -> 15単騎 | 0.8562 | 0.5688 | 0.5688 | 0.0 | 0.0 | 0.0 |
| EN | 901,902 | 4 -> 9 -> 15単騎 | 0.875 | 0.675 | 0.675 | 0.0813 | 0.375 | 0.375 |
| けつ空手 | 901,902 | dynamic energy-activate 2-2 -> 4-2-2 -> 9-4-2 -> 17-9-2 -> 17-13-2 | 0.8688 | 0.3125 | 0.3438 | 0.0125 | 0.0 | 0.0 |

## Miss Examples

- 果林: T2 missing 4 4 (0.05) / missing 4 3 (0.0375) / T3 missing 10 22 (0.275) / missing 10 18 (0.225)
- 真黄ちゃん: T2 missing 9 14 (0.175) / missing 9 9 (0.1125) / T3 missing 15 36 (0.45) / missing 15 33 (0.4125)
- EN: T2 missing 9 10 (0.125) / missing 9 10 (0.125) / T3 missing 15 28 (0.35) / missing 15 24 (0.3)
- けつ空手: T2 missing 4 2 (0.025) / missing 2 8 (0.1) / T3 missing 9 52 (0.65) / missing 9 47 (0.5875)
