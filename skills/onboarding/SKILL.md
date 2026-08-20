---
name: onboarding
description: Use when Penny is first installed, when brain/chart-of-accounts.md is missing, or when the owner says "onboard", "set me up", or "you don't know my books yet". Connects the accounting system, reads the chart of accounts, mines transaction history for vendor patterns, proposes starter categorization rules, and sets up receipt intake.
version: 1.0.0
author: Vindex Consulting
license: MIT
metadata:
  hermes:
    tags: [onboarding, setup, chart-of-accounts, quickbooks, xero, rules]
    related_skills: [categorize, rules-engine, receipt-intake]
---

# Onboarding Penny

Penny cannot categorize into a chart of accounts she has not read. This skill is
how she learns one, and how she arrives already knowing most of the answers.

**Output is a set of files in `brain/`.** If you finish and
`brain/chart-of-accounts.md` does not exist, onboarding did not happen.

## Resolve your accounts first

Every `{{ACCOUNT:<toolkit>}}` below is a placeholder. Read `brain/accounts.md`
and substitute the `word_id` recorded there.

If `brain/accounts.md` is missing, or the toolkit you need has no entry, **stop
and run `onboarding`.** Never substitute a default and never guess. An unpinned
call lands in whichever account the platform happens to pick — which may belong
to an entirely different company.


## Precondition — is anyone actually there?

Before anything else, confirm you are in a session where the owner can answer.

If this is a cron run, a one-shot (`-z`), a scheduled job, or any context where
your questions cannot reach a human, **stop now**. Write nothing. Bind nothing.
Report: *"Onboarding needs an interactive session — run `<agent> chat` and say
'onboard me'."*

Every step below depends on a real answer from a real person. Proceeding without
one produces a binding that looks confirmed and is not, which is worse than no
binding at all.

## Step 1 — Decide, together, what you are allowed to touch

You arrive with no accounts. This step is where the owner grants you exactly one
set of books, and it is the only step that can create the failure where you post
one company's expenses into another's ledger. Do not rush it and do not offer to
"just figure it out."

Ask in this order. One or two questions at a time.

### 1a. Which system?

QuickBooks Online or Xero? If they use something else, say plainly that you
support these two today rather than pretending otherwise.

### 1b. How do they want to connect it?

Lay out both honestly and let them pick:

- **Composio (recommended).** `composio link quickbooks`. Managed OAuth, nothing
  pasted anywhere, revocable from one place.
- **Direct API credentials.** Their own Intuit or Xero developer app, keys in
  `.env`. More control, meaningfully more work — say so rather than
  under-selling the effort.

### 1c. Which account, specifically?

**Never assume there is only one.** Owners routinely have a second company
connected — their own business and a client's, an old file and a live one.

```bash
composio connections list --toolkit quickbooks
```

Show them every result, with alias and status. Then ask which one you should
work in, and offer the third option explicitly:

> I can see two QuickBooks companies on your Composio account. Which should I
> work in — or would you rather connect a different one first?

If they want a fresh connection, stop and let them run `composio link` before
you continue. Waiting is correct; guessing is not.

**Never pick the first result. Never assume the alias that matches their company
name is the right file.** An alias is a label somebody typed once.

### 1d. Verify from the source

The alias is a label. `CompanyName` is the truth. Read it back:

```bash
composio execute "QUICKBOOKS_QUERY_ENTITIES" --account <chosen_word_id> \
  -d '{"query":"SELECT * FROM CompanyInfo"}'
```

Then say it out loud and wait for a yes:

> I'm working in **Your Company, LLC**, books opened March 2019. Correct?

If the name is not what they expected, **stop.** A surprise here means the wrong
account, and everything downstream would be wrong with it.

### 1e. Write the binding

Create `brain/accounts.md`. This file is what turns you from inert into
operational, and it is the only place your account bindings live:

```markdown
# Account bindings
Written by onboarding. Every skill resolves {{ACCOUNT:...}} from here.

- toolkit: quickbooks
  word_id: quickbooks_example-handle
  verified_as: "Your Company, LLC"
  method: composio
  owner_said: "yes, that's the right one"   # their literal words
  confirmed_at: 2026-08-20
```


### The confirmation cannot be fabricated

`owner_said` holds the owner's **actual words**, quoted. If you cannot quote
something a human really typed in this session, the binding is **not confirmed**
and you may not write the file. Do not fill the field from inference, do not
paraphrase silence into agreement, and never write a confirmation date for a
confirmation that did not happen.

Every downstream skill trusts this field. A fabricated confirmation is not a
tidy-looking record — it is an agent operating on an account nobody approved.

`brain/` is yours, not the distribution's — `hermes profile update` never
touches it, so an update can never silently unwire or re-point you.

**Completion criterion:** `brain/accounts.md` exists, and the owner has
confirmed out loud the company name you read back from the books themselves.
Until both are true you are still inert and must not read or write anything else.

## Step 2 — Read the chart of accounts

```bash
composio execute "QUICKBOOKS_QUERY_ACCOUNT" --account {{ACCOUNT:quickbooks}} \
  -d '{"query":"SELECT * FROM Account MAXRESULTS 500"}'
```
Xero: `XERO_LIST_ACCOUNTS`.

Write **`brain/chart-of-accounts.md`**: every active account with its ID, name,
type, subtype, and description. Group by type — Income, COGS, Expense, Asset,
Liability, Equity.

The account **ID** is not decoration. Every posting references it, and names are
ambiguous where IDs are not. Record both.

Note specially, because they are where your work lands:
- **Uncategorized Expense / Income / Asset** — the default landing spots
- **Ask My Accountant** — where genuinely unclear items go

**Completion criterion:** you can name the account ID for any account the owner
mentions by name.

## Step 3 — Understand the bank feed, and set it up properly

This step is what makes Penny work, so do not rush it.

**How QuickBooks actually works:** the "For Review" tab is a *staging area*. Items
sitting there are not yet transactions and the API cannot see them. Once
accepted — by a person, or automatically by a **bank rule** — they become real
transactions the API can read, categorize, and correct.

So tell the owner plainly:

> I can see and fix any transaction that has landed in your books. I can't see
> the "For Review" tab — no API can. The fix is a catch-all bank rule that
> auto-adds anything unmatched into Uncategorized Expense. Then everything flows
> into the books automatically and I clean it up from there, which is exactly
> what a bookkeeper does anyway.

Offer both options and let them pick:

**Option A — catch-all rule (recommended).** Walk them through it in the QBO UI:
Banking → Rules → New rule → all transactions → auto-add to Uncategorized
Expense. From then on Penny sees everything and categorizes continuously.

**Option B — they accept transactions themselves.** They click through For
Review as usual; Penny cleans up whatever lands in Uncategorized. Less
automatic, still useful. Say honestly that they will keep doing the clicking.

Xero users: `XERO_LIST_BANK_TRANSACTIONS` exposes bank transactions directly, so
this is simpler — note which mode applies and move on.

Record the choice in `brain/config.md`.

## Step 4 — Mine history for rules

This is the step that makes Penny useful on day one instead of week three.

Pull the last 12 months of transactions:
```bash
composio execute "QUICKBOOKS_GET_TRANSACTION_LIST_REPORT" --account {{ACCOUNT:quickbooks}} -d '{...}'
```

Group by vendor. For each vendor, find where its transactions were actually
categorized. Any vendor with **three or more** transactions that went to the
**same account every time** is a rule the owner already follows — you are
reading their existing practice, not inventing policy.

Propose these as starter rules, showing the evidence:

```
Vendor              → Account                  Seen   Confidence
Home Depot          → Job Materials (Id 61)     34/34   high
Verizon Wireless    → Utilities (Id 22)         12/12   high
Shell / Chevron     → Car & Truck (Id 55)       28/31   medium — 3 went to Travel
Amazon              → (mixed: 9 accounts)         —     none — will ask each time
```

Be explicit about what you will **not** rule on. Amazon, Costco, Walmart and
similar general merchants legitimately span many accounts. Inventing a rule for
them is exactly the wrong instinct; say you will ask each time and why.

Ask the owner to confirm, correct, or drop each proposed rule. Their corrections
are worth more than your inference — write those in as `source: owner`, which
outranks everything you derived yourself.

Write the confirmed set to **`brain/rules.md`** using the format in the
`rules-engine` skill.

**Completion criterion:** every proposed rule has been confirmed, corrected, or
dropped by the owner — none are left in an assumed state.

## Step 5 — Business context

A short interview. Do not make it long; the history in Step 4 already told you
most of it.

- What does the business do, and what are its main expense categories?
- Which vendors are you most often unsure about?
- Anything with special treatment — owner draws, personal charges on a business
  card, reimbursements, mileage?
- Do you track by customer/job or by class/location? (Changes whether postings
  need a customer or class reference — get this right now, not later.)
- Who is your accountant, and what do they want to see at month end?

Write **`brain/business.md`**.

## Step 6 — Receipt intake

Two paths; set up whichever they want, or both.

**Telegram (fastest, best experience):** they photograph a receipt on their
phone, send it to Penny, and it is booked with the image attached in under a
minute. Walk them through connecting the Telegram gateway.

**Email forwarding:** set `PENNY_RECEIPT_EMAIL` to an address she watches and
they forward receipts to it. No new app, works from anywhere.

## Step 7 — Operating rules

Write **`brain/config.md`**:

```yaml
accounting_system: quickbooks   # quickbooks | xero
autonomy: approve               # approve | auto
confidence_threshold: high      # min confidence to auto-post when autonomy: auto
bank_feed_mode: catch_all_rule  # catch_all_rule | manual_accept | xero_direct
daily_close_time: "17:30"
timezone: "America/Chicago"
track_by: none                  # none | customer | class | both
receipt_intake: [telegram]      # telegram | email
large_txn_threshold: 1000       # always ask above this, regardless of rules
```

## Step 8 — Prove it, then hand back

Do not end with a summary. End with evidence:

1. Query the current uncategorized transactions.
2. Categorize the three clearest ones using the rules you just built, and show
   your reasoning for each.
3. Show one you genuinely cannot call, and ask about it — demonstrating that
   asking is normal, not an error.
4. Say what you will do at 5:30pm today without being asked.

**Completion criterion:** the owner has seen a real categorization of a real
transaction from their real books, with the rule that produced it.
