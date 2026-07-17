# Partial Branch Analysis

- audit_id: `PL!S-bp3-001#A01`
- cardnumber: `PL!S-bp3-001`
- trigger: `BODY`
- effect: `メンバー1人をウェイトにする：ライブ終了時まで、これによってウェイト状態になったメンバーは、「<常時>ライブの合計スコアを+1する。」を得る。 / (この能力はセンターエリアに登場している場合のみ起動できる。)`

Conclusion: `PARTIAL_CONFIRMED`. The current static/running route evidence does not show a complete cost branch for choosing a member to wait and attaching a live-end temporary score bonus to that selected member. Implement as a generic BODY activated family, not a card-specific route.
