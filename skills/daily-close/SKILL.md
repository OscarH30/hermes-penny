---
name: daily-close
description: Use on the end-of-day cron or when the owner asks for a daily summary. Reports what came through the books today, what Penny categorized, batches every open question into one message, and flags anomalies worth a look.
version: 1.0.0
author: Vindex Consulting
license: MIT
metadata:
  hermes:
    tags: [daily-summary, close, reporting, anomalies]
    related_skills: [categorize, rules-engine]
---

# End of day

One message, once a day. Everything the owner needs, nothing they don't.

## What goes in it

**1. The questions, first.** If anything needs the owner, it leads. They will
read the first four lines and maybe not the rest — put what needs them at the
top, always.

**2. What came through.** Count and total of transactions that hit the books
today, money in and money out.

**3. What you handled.** How many you categorized and posted, briefly. Not a
line-by-line — they can look if they want.

**4. Anything odd.** Only if genuinely odd. See below.

**5. What is still open.** Uncategorized count carrying to tomorrow.

## Shape

```
Wednesday, Aug 20

NEED YOU — 3 things
  1. AMZN Mktp US · $487.22 · Aug 19
     What was this one for?
  2. TX Equipment Co · $6,240.00 · Aug 17
     Big one. Might belong on the balance sheet as an asset rather than an
     expense — worth a quick word with your accountant.
  3. Blue Ridge Supply · $212.40 · Aug 19
     First time I've seen them. Where does this go?

TODAY
  11 transactions · $3,847.22 out · $12,400.00 in
  Categorized and posted: 8
  Receipts booked: 2 (Home Depot, Shell)

HEADS UP
  Adobe charged $52.99 — you mentioned cancelling this in July.

OPEN
  3 uncategorized carrying to tomorrow
```

Answer any of the questions in plain language and Penny handles the rest.

## Anomalies worth flagging

Flag once, plainly, without accusation. The owner decides what it means.

- **Possible duplicate** — same vendor, same amount, within a few days
- **Well outside normal range** — a vendor's charge far above its usual
- **A subscription that should have stopped** — they mentioned cancelling it
- **Personal-looking charge on a business account**
- **New vendor with a large first transaction**
- **Round numbers in unusual places** — sometimes a manual entry error

**Say it once.** If the owner does not act on a flag, do not raise it again
tomorrow and the day after. Note it and let it go. A summary that nags stops
being read, and then the flags that matter get missed too.

## Quiet days

If nothing came through and nothing needs them:

```
Wednesday, Aug 20
Nothing new in the books today. Nothing needs you.
```

That is a complete report. Never pad it, never manufacture an observation to
seem useful, never restate yesterday's work as if it were today's.

## Weekly and monthly

**Fridays**, add a short week view: total in and out, the largest expenses, how
many transactions needed a question versus were handled automatically. That last
ratio is the honest measure of whether Penny is actually learning — if it is not
improving, say so.

**Month end**, offer rather than assume: an uncategorized sweep, receipts
missing on transactions over the threshold, a rules review, and a note of
anything their accountant should look at. Ask before running it — month end has
their own rhythm and you should fit it, not override it.

**Completion criterion:** one message sent, questions at the top, every number
in it verified against the books rather than estimated.
