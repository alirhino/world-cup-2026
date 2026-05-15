# Iran at the 2026 FIFA World Cup — Fan Dashboard

A self-contained dashboard tracking IR Iran's Group G path through the 2026 World Cup, with Monte Carlo simulation of every route to the Round of 16.

**Live site:** https://USERNAME.github.io/world-cup-2026/

## What's inside

- `index.html` — the dashboard. Single self-contained file (~78 KB) with all simulation results inlined. Loads only Chart.js from a CDN.
- `code/compute_paths.py` — Monte Carlo simulation. 80,000 runs. Models every group-stage match with FIFA's Elo-style formula (divisor 600), resolves Iran's R32 opponent via FIFA's Annex C 495-row 3rd-place mapping (embedded in the script), computes joint path probabilities.
- `code/build_dashboard.py` — reads `data/iran_r16_paths.json` and produces `index.html`.
- `code/test_dashboard.py` — headless-browser regression test (Playwright) — verifies every tab renders, the finish-position chart paints, paths expand, filters work.
- `data/teams_fifa_ranking_april2026.json` — FIFA April 2026 ranking points for all 48 WC teams (group, rank, pts).
- `data/iran_group_stage_schedule.json` — Iran's 3 group matches with venues, dates, kickoff times.
- `data/knockout_bracket_structure.json` — every R32 + R16 match (#73–96) with venue, date, and which group/Annex-C cell feeds it.
- `data/iran_r16_paths.json` — computed output: 24 paths, each with a qualification chain decomposition.

## Refreshing the simulation

```bash
python3 code/compute_paths.py      # rerun Monte Carlo (~20s)
python3 code/build_dashboard.py    # rebuild index.html
python3 code/test_dashboard.py     # headless test (optional)
```

## Headline numbers (as of April 2026 FIFA rankings)

| Iran's group finish | Probability |
| --- | --- |
| 1st (Group G winner) | 23.9% |
| 2nd (Group G runner-up) | 40.4% |
| 3rd / 4th (out) | 35.7% |

Iran reaches the R16 via top-2 finish: **34.2%**.

## Data sources

- FIFA April 2026 rankings via football-ranking.com mirror of inside.fifa.com
- Match schedule: FIFA official + Yahoo Sports + Al Jazeera cross-check
- Bracket structure: FIFA 2026 Competition Regulations (Annex C) via Wikipedia 2026 FIFA World Cup knockout stage article

Built by [Ali Alavi](https://github.com/) with Claude.
