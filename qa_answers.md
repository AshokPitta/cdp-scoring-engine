# QA Response — Company 5

## Why did Company 5 score 0/4 on Climate Change?

Company 5 submitted two rows under the Climate Change theme, both with valid dates after 2023-01-01, which means they correctly entered the scored route (Route A). However, both rows scored 0 out of a possible 4 points. Here is why.

Route A for Climate Change has two scoring conditions:

**Condition 1 — 3 points**
The second lorem ipsum statement must appear in the free-text answer (c1), AND the list of numbers (c3) must contain more than 3 elements.

**Condition 2 — 1 point**
The third lorem ipsum statement must appear in the free-text answer (c1), AND the list of numbers (c3) must contain at least one even number.

Looking at Company 5's actual submissions:

- **Row 1:** c1 contains the first and second statements but is missing the third statement ("sed do eiusmod tempor"). c3 is `[1, 2, 3]`, which has only 3 elements — the criterion requires *more than* 3, so 3 does not qualify. Condition 1 fails because c3 has exactly 3 elements (not more than 3). Condition 2 fails because the third statement is absent from c1.

- **Row 2:** c1 again contains the first and second statements but not the third. c3 is `[4, 5]`, which has only 2 elements. Both conditions fail for the same reasons.

In short: neither row included the third lorem ipsum statement, and neither row's number list was long enough to trigger the 3-point condition.

## Is the criterion producing the right outcome here?

This is worth raising with the methodology team. Company 5 did engage meaningfully — they submitted two rows with valid dates and relevant statements. Their score of 0 feels disproportionate for two reasons:

1. **The 3-point condition is strict on list length.** A company submitting `[1, 2, 3]` (3 elements) scores the same as a company submitting nothing, despite being one element short of the threshold. It may be worth clarifying whether the intent was "more than 3" or "3 or more".

2. **Partial credit is not available on Condition 1.** A company that includes the second statement but falls just short on list length receives 0 rather than any partial recognition. Given that Condition 2 awards 1 point independently, the asymmetry between the two conditions (3 points vs 1 point) means a single missed threshold has an outsized impact on the final score.

I would suggest reviewing whether the list-length threshold of "more than 3" was intentional, and whether partial credit for statement presence alone should be considered.
