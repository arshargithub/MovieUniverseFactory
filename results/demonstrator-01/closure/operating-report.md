# DEMONSTRATOR-01 operating report

Lifecycle closure and qualification colour are independent.

| Episode | Lifecycle / disposition | Calendar s | Excluded input s | Net s | Coverage |
|---|---|---:|---:|---:|---:|
| stage-a | CLOSED / YELLOW | 110969.19716405869 | UNKNOWN | UNKNOWN | 0.9989040982151269 |

stage-a uncertainty: clock_discontinuity, unexplained_gap.

| documentary-closure | CLOSED / YELLOW | 120.6073272228241 | UNKNOWN | UNKNOWN | 0.9999923615802551 |

documentary-closure uncertainty: unexplained_gap.


Engineering usage: **UNKNOWN**. Exact attributable tokens: UNKNOWN.
Observed token categories (may be partial): {'input_tokens': None, 'cached_input_tokens': None, 'cache_write_input_tokens': None, 'output_tokens': None, 'reasoning_output_tokens': None, 'total_tokens': None}.
Cached and reasoning tokens are subsets, not additions to the total.

Factory API evidence: {'additional_api_usd': 0.51397, 'additional_limit_usd': 10, 'remaining_additional_usd': 9.48603, 'campaign_cumulative_usd': 3.736270001, 'effective_campaign_ceiling_usd': 13.222300001, 'calls': [{'record': 'world-response.json', 'reservation_id': '96df861d-4165-4790-ace1-6575471d0b87', 'model': 'gpt-5.6-sol', 'effort': 'medium', 'cost_usd': 0.20471, 'reasoning_cost_usd': 0.06896, 'input_cost_usd': 0.00471, 'output_cost_usd': 0.2, 'error': 'response_invalid:response_not_completed', 'usage': {'input_tokens': 942, 'cached_input_tokens': 0, 'output_tokens': 10000, 'reasoning_tokens': 3448, 'total_tokens': 10942, 'usage_certainty': 'known'}}, {'record': 'world-retry-response.json', 'reservation_id': '2fdc57c9-6a26-44d9-81c6-e01ac04fcf61', 'model': 'gpt-5.6-sol', 'effort': 'medium', 'cost_usd': 0.265935, 'reasoning_cost_usd': 0.09854, 'input_cost_usd': 0.004955, 'output_cost_usd': 0.26098, 'error': None, 'usage': {'input_tokens': 991, 'cached_input_tokens': 0, 'output_tokens': 13049, 'reasoning_tokens': 4927, 'total_tokens': 14040, 'usage_certainty': 'known'}}, {'record': 'visual-review.json', 'reservation_id': 'f2958b2e-e291-42f7-8d05-a6529649d8a0', 'model': 'gpt-5.6-sol', 'effort': 'medium', 'cost_usd': 0.043325, 'reasoning_cost_usd': 0.02002, 'input_cost_usd': 0.012905, 'output_cost_usd': 0.03042, 'error': None, 'usage': {'input_tokens': 2581, 'cached_input_tokens': 0, 'output_tokens': 1521, 'reasoning_tokens': 1001, 'total_tokens': 4102, 'usage_certainty': 'known'}}], 'purchases_paid_media_cloud_usd': 0, 'subscription_token_usage': None, 'subscription_marginal_cost': None, 'human_review_seconds': None, 'accounting': 'conservative calculated estimate, not provider invoice; reasoning is included in output cost and never added twice'}.
Subscription charges are shared fixed overhead; engineering dollar allocation and API-equivalent cost are UNKNOWN.

Outcome denominators: {'closed_experiments': 1, 'closed_episodes': 2, 'technically_successful_outputs': 2, 'director_accepted_outputs': 1}.
Consumption per outcome: {'closed_experiments': {'net_seconds': None, 'engineering_tokens': None}, 'closed_episodes': {'net_seconds': None, 'engineering_tokens': None}, 'technically_successful_outputs': {'net_seconds': None, 'engineering_tokens': None}, 'director_accepted_outputs': {'net_seconds': None, 'engineering_tokens': None}}.

See JSON for job sums/unions, phases, work intervals and coverage. Job sums are process-seconds, not CPU core-seconds.
Account quota is a separate capacity measure; percentages are not per-experiment tokens.
