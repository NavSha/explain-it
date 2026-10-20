# X For You Algorithm: Comprehensive Analysis and Key Takeaways

## Overview

The X (formerly Twitter) For You feed algorithm has been open-sourced by xAI in the `xai-org/x-algorithm` repository. This document provides a comprehensive breakdown of how the algorithm works, the key components involved, and actionable insights for creators looking to grow their reach on the platform.

## Architecture Overview

The system is composed of several interconnected services and pipelines:

- **Home Mixer**: The core service responsible for building the For You feed
  - Implements the Post Pipeline (PhoenixCandidatePipeline)
  - Implements the Blending Pipeline (ForYouCandidatePipeline)
  - Handles query hydration, candidate sourcing, hydration, filtering, scoring, and selection
  - Calls side effects after the response is sent
- **Candidate Pipeline**: The framework Home Mixer is built on
  - Defines stage types: source, hydrator, filter, scorer, selector, side effect
  - Runs stages in parallel where possible
- **Thunder**: In-memory store of recent posts from followed accounts (in-network)
- **Phoenix**: Retrieval and ranking model
  - Retrieval: embeds viewer and posts as vectors, returns nearest posts
  - Ranking: transformer that predicts probabilities of user actions
  - Written in JAX with a Rust serving layer
  - Uses hash-based embeddings
  - Candidate isolation during inference
- **SimClusters**: Clusters accounts and posts by engagement patterns for out-of-network discovery
- **Popular Posts Source**: Shared list of popular recent posts
- **Phoenix RankAll / RankAll Strato**: Maintains and updates the retrieval index
- **VM Ranker**: Reranking service using a determinantal point process (DPP) over embeddings
- **Visibility Filtering**: Determines ALLOW / NOTICE / INTERSTITIAL / DROP per post and viewer
- **Content Understanding**: grox, media-model-proxy, clip, agatha, bdsm, user-cred-v2, adult-content, pnsfwmedia
- **Labeling Rules**: scarecrow, botmaker, botmaker-rules, abuse-enforcement-service, abuse-ledger-service, safety-label-user-agg
- **Under the Hood**: Transparency tool showing labels applied to your account

## Request Path

1. **Query Hydration**
   - User action sequence (recent engagements)
   - Following list
   - Blocks and mutes
   - Muted keywords
   - Posts already seen and served
   - Followed topics
2. **Candidate Sources** (queried in parallel)
   - In-network: Thunder
   - Out-of-network: Phoenix retrieval, SimClusters, Popular posts
3. **Candidate Hydration**
   - Post text and media
   - Author details and account labels
   - Quoted post
   - Language
   - Engagement counts
   - Subscription status
4. **Pre-Scoring Filters**
   - DropDuplicatesFilter
   - CoreDataHydrationFilter
   - AgeFilter (posts older than 48 hours)
   - SelfTweetFilter
   - OONRetweetReplyFilter
   - OONNsfwSimclustersFilter
   - RetweetDeduplicationFilter
   - IneligibleSubscriptionFilter
   - PreviouslySeenPostsFilter
   - PreviouslySeenPostsBackupFilter
   - PreviouslyServedPostsFilter
   - MutedKeywordFilter
   - AuthorSocialgraphFilter
   - Brazil2026ElectionFilter
   - VideoFilter
   - TopicIdsFilter
   - NewUserMinEngagementFilter
   - InventoryHoldoutFilter
   - FavHoldoutFilter
5. **Scoring**
   - PhoenixScorer: probability for each action
   - RankingScorer: weighted sum, author diversity decay, out-of-network discount, new-author boost
   - VMRanker: calls reranking service
6. **Selection**: TopKScoreSelector sorts and keeps top K
7. **Post-Selection Filters**
   - VFCandidateHydrator
   - VFFilter
   - AncillaryVFFilter
   - DedupConversationFilter

## Scoring Formula

Final Score = Σ (weight_i × P(action_i))

### Positive Actions and Weights

- Favorite (like): 0.66
- Reply: 5.0
- Bidirectional follow reply weight boost: 15.0
- Bidirectional follow dwell weight boost: 0.0
- Retweet (repost): 1.0
- Photo expand: 0.05
- Video open: 0.02
- Click: 0.3
- Open link: 0.2
- Profile click: 0.0
- Video quality view (VQV): 0.0
- Share: 2.0
- Share via DM: 5.0
- Share via copy link: 20.0
- Dwell: 0.05
- Quote: 5.0
- Quoted click: 0.05
- Quoted VQV: 0.0
- Follow author: 4.0
- Post unexplored: 0.015
- React with video: 0.0
- Continuous dwell time: 0.006
- Continuous click dwell time: 0.4

### Negative Actions and Weights

- Not interested: -52.272
- Block author: -31.2
- Mute author: -58.8
- Report: -234.0
- Not dwelled: -0.02

### Important Note on Weights

- Weights multiply predicted probabilities, not raw engagement counts
- It is incorrect to say "1 report cancels out 468 likes"
- The baseline probability of a report is more than 1000x lower than a like
- Recommendations are personalized
- Engagement must happen on a post served in Home Timeline to count

## Adjustments

- **Author Diversity**
  - Enabled: true
  - Decay: 0.5
  - Floor: 0.25
  - Formula: (1 - floor) × decay^n + floor
- **Out-of-Network Discount**
  - OON weight factor: 0.75
  - Topic OON weight factor: 0.5
  - New user OON weight factor: 0.00001
  - OON rescore for in-network replies/retweets: true
- **New-Author / Cold-Start Boost**
  - Cold start impression threshold: 200
  - Cold start slot min: 15
  - Cold start slot max: 16
  - Cold start follower cap: 50,000
  - Cold start max post age: 7,200 seconds
  - Low impressions max position ratio: 0.97
  - Viewer cold start enabled: true
  - Thompson sampling enabled: true
  - Beta alpha0: 0.75
  - Beta beta0: 49.25
  - TS top K: 2

## Bidirectional Follow Boost History

- July 10, 2026: A/B test with values 5, 10, 15, 20
- July 13, 2026: Value of 20 rolled out to many users
- July 24, 2026: Value set to 15 after feedback (e.g. World Cup discussion)
- Dwell weight boost tested but not shipped

## Other Notable Parameters

- Minimum video duration: 10,000 ms
- Max posts to cache: 750
- Who to Follow module enabled
- Video carousel enabled with fatigue and position settings
- NewUserMinEngagementFilter max account age: 1,800 seconds

## Self-Reply Chain Filter

- Replies are kept only if the effective directed-at user is followed by the viewer
- Applies when the post is a reply with ancestor users

## Things Not Found in the Code

- No explicit link penalty
- No explicit Premium multiplier in the scoring code
- Some botmaker rules and Grox prompts are not published

## Key Takeaways for Creators

1. Focus on replies, quotes, and shares rather than likes
2. Build mutual follows
3. The first 2 hours after posting are important for small accounts
4. Spread posts out to avoid author diversity decay
5. Original posts matter more than replies for out-of-network reach
6. Avoid content that gets muted, reported, or marked not interested
7. Check the Under the Hood tool for labels on your account
8. Posts older than 48 hours are filtered out
9. Video is not specially weighted at the moment
10. Links are not penalized but have a low weight

## Conclusion

The open-sourcing of the X algorithm provides unprecedented transparency into how content is ranked and distributed. By understanding these mechanics, creators can make more informed decisions about their content strategy. However, it is important to remember that the algorithm is constantly evolving through experiments, and the weights reflect predicted probabilities rather than raw counts.
