---
name: categorize
description: Use on the transaction sweep cron, when the owner asks about uncategorized transactions, or when new transactions land in the books. Finds transactions sitting in Uncategorized or Ask My Accountant, matches them against learned rules, proposes categorizations with confidence and reasoning, and posts only what the owner approves.
version: 1.0.0
author: Vindex Consulting
license: MIT
metadata:
  hermes:
    tags: [categorization, quickbooks, xero, uncategorized, bookkeeping]
    related_skills: [rules-engine, daily-close, receipt-intake]
---

# Categorizing transactions

Find what is uncategorized, decide what you actually know, and be honest about
the rest.

## Check your tools before you start

You reach the books through whatever onboarding wired into this profile — an MCP
server, or a documented API using a key in `.env`. Look at what you actually
have.

**No accounting tools on this profile → stop and run `onboarding`.** Do not fall
back to a CLI you happen to find on the shell. A tool nobody granted you is a
tool pointed at an account nobody chose, and with two companies connected that is
how one company's expenses land in another's ledger.

Tool names below are the common Composio slugs. If onboarding wired something
else, use its equivalent — the operation is what matters, not the spelling.

## Step 1 — Find the work

**QuickBooks.** Query transactions posted to the catch-all accounts:

```bash
composio execute "QUICKBOOKS_QUERY_ENTITIES" -d '{"query":"SELECT * FROM Purchase WHERE TxnDate >= '\''2026-08-01'\'' MAXRESULTS 200"}'
```

Then filter to lines whose `AccountBasedExpenseLineDetail.AccountRef` points at
Uncategorized Expense, Uncategorized Income, Uncategorized Asset, or Ask My
Accountant — look their IDs up in `brain/chart-of-accounts.md`.

Also check `Deposit` and `Transfer` entities; uncategorized income hides there.

**Xero.** `XERO_LIST_BANK_TRANSACTIONS` and filter for unreconciled or
uncategorized lines.

**A note on what you cannot see.** QuickBooks' "For Review" tab is a staging
area with no API. If `bank_feed_mode` is `manual_accept` and the queue looks
empty, that does not mean there is nothing to do — it may mean nothing has been
accepted into the books yet. Say that rather than reporting "all clear," which
would be misleading.

## Step 2 — Match against rules

For each transaction, read `brain/rules.md` and try to match on vendor name,
then on description keywords, then on amount pattern.

Assign an honest confidence:

| Confidence | When | What you do |
|---|---|---|
| **high** | Owner-confirmed rule, exact vendor match | Propose it. Auto-post only if `autonomy: auto` |
| **medium** | Rule matches but something differs — unusual amount, vendor variant | Propose with the discrepancy called out |
| **low** | Weak signal — general merchant, partial match | Propose as a question, not an answer |
| **none** | No rule, unrecognizable vendor | Ask. Do not guess |

**Always drop to "ask" regardless of rule match when:**
- The amount exceeds `large_txn_threshold` in `brain/config.md`
- The vendor is a general merchant (Amazon, Costco, Walmart, Target)
- It looks personal on a business account
- It could be a fixed asset rather than an expense — that is a real accounting
  distinction with tax consequences, and it is not yours to make
- Anything about it touches deductibility

That last group is the reason Penny is trustworthy. Confidently miscategorizing
a $6,000 equipment purchase as an expense is exactly the kind of error that
costs the owner real money at tax time.

## Step 3 — Propose

Never post silently. Present:

```
14 uncategorized · 9 I'm confident about · 5 need you

CONFIDENT — say the word and I'll post these
  1. Home Depot          $340.18  Aug 18  → Job Materials
     rule: Home Depot → Job Materials (34/34, you confirmed)
  2. Verizon Wireless    $198.00  Aug 18  → Utilities
     rule: Verizon → Utilities (12/12, you confirmed)
  ...

NEED YOU
 10. AMZN Mktp US        $487.22  Aug 19
     Amazon goes lots of places in your books — what was this?
 11. TX Equipment Co     $6,240.00  Aug 17
     Over your $1,000 threshold, and this size often belongs on the balance
     sheet as an asset rather than an expense. Worth asking your accountant.
```

Each proposal shows the rule that produced it. A proposal without a stated
reason is a guess wearing a suit.

## Step 4 — Post what was approved

**QuickBooks.** Update the transaction's line to the correct `AccountRef`:

```bash
composio execute "QUICKBOOKS_EXECUTE_BATCH_OPERATION" -d '{...}'
```

QuickBooks updates are **full-object updates** — read the current object, change
only the account reference, and send it back with its current `SyncToken`.
A stale `SyncToken` fails the write, which is QuickBooks protecting you from
overwriting a concurrent change. If you get that error, re-read and retry once,
then report it.

If `track_by` in `brain/config.md` is `customer` or `class`, set that reference
too. Dropping it silently breaks the owner's job-costing reports.

**Xero.** `XERO_CREATE_BANK_TRANSACTION` or the update equivalent.

**Verify every write.** Re-query the transaction and confirm the account
actually changed. Report the count you verified, not the count you attempted —
those are different numbers and only one of them is true.

## Step 5 — Learn

Every owner answer becomes a rule. Hand it to `rules-engine`:
- A correction to something you proposed → a rule with `source: owner`, which
  outranks anything you inferred
- An answer about an unknown vendor → a new rule, if it is likely to recur
- A one-off ("that was a gift, not a supply") → a note, **not** a rule

Knowing which of those you are looking at is the difference between learning and
overfitting. When unsure, ask: *"Is that always the case for them, or just this
one?"*

**Completion criterion:** every approved categorization is posted and verified
in the books, every owner answer is either a rule or a note, and the counts you
reported match what actually changed.
