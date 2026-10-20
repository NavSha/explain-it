# Replies and shares move your post on X. Likes barely do.

Record of the explain-it page `index.html` (same folder). Read from the open-source code at github.com/xai-org/x-algorithm, commit 17c96bf, 14 Oct 2026. Also the demo for Instagram reel 065.

**The answer:** X guesses what each person will do with your post, then adds up those guesses. A reply, quote or shared link counts many times more than a like. A mute or report counts hard against you. Small accounts get a test slot in the first 2 hours.

**Assumptions:** code defaults = live values (X says a scheduled job syncs them); weights multiply predicted probabilities, not counts; some spam rules and prompts are not public; X runs tests on part of its users.

## 1. How does X decide what to show?
Collect → remove (older than 48 h, already seen, muted) → score (Σ weight × P(action)) → adjust (author diversity, out-of-network 0.75, new-author boost) → safety check → feed.

## 2. Which actions count most?
Positive: share via copy link 20 · reply 5 · quote 5 · share via DM 5 · follow 4 · share 2 · repost 1 · like 0.66 · click 0.3 · open link 0.2 · dwell 0.05 · video open 0.02 · video view 0.
Negative: report −234 · mute −58.8 · not interested −52.272 · block −31.2 · not dwelled −0.02.
Source: `home-mixer/params/param.rs`, `xai-value-model/scoring.rs`.

## 3. Is there a boost for small accounts?
Yes. Original posts (not replies or reposts), under 2 hours old, under 200 home views, from accounts with ≤ 50,000 followers can be lifted to about position 15–16 in a feed. Picked by Thompson sampling on like rate (likes / home views), prior Beta(0.75, 49.25) ≈ 1.5%. Viewers are bucketed into test groups. Source: `home-mixer/scorers/author_cold_start.rs`.
**Decision 1 (suggested):** post when the audience is online and stay 2 hours to reply.

## 4. Do my replies reach new people?
Rarely. `OONRetweetReplyFilter` drops replies from accounts the viewer doesn't follow; `SelfReplyChainFilter` keeps a reply only if the viewer follows the account it's aimed at. So a reply shows in For You only to people who follow both you and the other person. Mutual-follow boost: reply weight 5 → 20 for original posts from authors the viewer mutually follows (set to 15 on 24 Jul 2026, `docs/BIDIRECTIONAL_BOOST_CHANGE.md`).
**Decision 2 (suggested):** reply to builders your size who may follow back.

## 5. What happens if I post a lot?
Author diversity: multiplier = (1 − 0.25) × 0.5ⁿ + 0.25 → 100%, 63%, 44%, 34%, floor 25%. Out-of-network posts × 0.75. Source: `vm-ranker/params.rs`.
**Decision 3 (suggested):** 1–2 strong original posts a day, spread out.

## 6. Which popular tips does the code not support?
- Links: no penalty found; open-link weight 0.2.
- Premium: no multiplier in the scoring code (may be a model input).
- Video: video-view weight 0; videos under 10 s don't count as video views.
- "1 report = 468 likes": X says wrong (weights × probabilities; reports > 1,000× rarer).

## What we still do not know
Live values for test groups; the model's full inputs; hidden spam rules.

## Next steps
Answer the 3 decisions. Try for two weeks: fewer, stronger posts; stay 2 hours after each; reply to builders your size. Compare views and new followers with the two weeks before. Check x.com/i/jf/under_the_hood for labels.
