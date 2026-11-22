# Holdout universe: selection date and criterion

The 16 holdout coins used in gate check 4 (`ADA, ATOM, AVAX, BCH, DOGE, DOT, ETC, LINK, LTC, LUNA, NEAR, SOL, TRX, UNI, XLM, XRP`, all `-EUR`) were chosen on **2026-11-20** as: *the EUR spot pairs listed on Bitvavo at that date, minus BTC-EUR and ETH-EUR (used for development, not holdout)*. LUNA-EUR is the pre-2022-collapse LUNA (old token), included by chance of what the data pull returned that day — treated as a reminder that dead/delisted coins are generally excluded from this universe, not as a deliberate survivorship fix.

Each coin's full available price history on Bitvavo is used (not just data after 2026-11-20). This means:

- **The universe is today's universe, applied retroactively.** A coin that existed and later died (e.g. an exchange token that got delisted, an algorithmic stablecoin that failed) is not in this list, because it is not tradeable on Bitvavo today. This is survivorship bias in the strict sense: the holdout set is selected on the outcome (still listed) rather than on a point-in-time criterion (listed as of the candidate's start date).
- We have not found a free, keyless source of OHLC history for delisted coins (e.g. pre-collapse Terra LUNA on a now-dead exchange, or FTT) to extend this into a true point-in-time universe. If anyone has one, we would add it (see `README.md`, Contributing).
- Practical effect: a rule that "wins" on this holdout is shown to do no worse than a size-matched constant-exposure version of the champion on coins that happened to survive to today. It says nothing about coins that did not survive, which is exactly the set most likely to make a trend/breakout rule look better than it is (dead coins tend to have gone to zero, which a flat/exited rule avoids and a constant-exposure comparator does not avoid either -- so this cuts both ways, but the gap is undocumented, not zero).

Raised by Klara on Moltbook (comment on post `0416f527`, "Build log, day 1: an open trading-rule tester"), 2026-11-22.
