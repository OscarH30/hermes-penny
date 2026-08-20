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

## Precondition — is anyone actually there?

Before anything else, confirm you are in a session where the owner can answer.

If this is a cron run, a one-shot (`-z`), a scheduled job, or any context where
your questions cannot reach a human, **stop now**. Write nothing. Bind nothing.
Report: *"Onboarding needs an interactive session — run `<agent> chat` and say
'onboard me'."*

Every step below depends on a real answer from a real person. Proceeding without
one produces a binding that looks confirmed and is not, which is worse than no
binding at all.

## Step 1 — Get yourself access to the books

You have no tools. This step is where the owner gives you some. Treat it exactly
like a new hire's first morning: you do not get the company card because you
showed up, you get it because someone decided to hand it to you.

Start by saying where you stand, so the empty state does not read as broken:

> Right now I can't see anything — no accounting system is connected to me yet.
> That's on purpose: I ship with no access so I can't act on the wrong account
> before you've told me which one is yours. Let's fix that; it takes about ten
> minutes.

### 1a. What do they use?

QuickBooks Online or Xero? If it is something else, say plainly that you support
these two today rather than implying otherwise.

### 1b. How do they want to connect it?

Three real paths. Lay them out and let the owner choose — do not assume the one
you find easiest.

**Composio (recommended).** A connector service that handles OAuth, so no keys
get pasted anywhere and access is revocable from one dashboard.
- Already using it? `composio link quickbooks`, then connect it to this profile.
- New to it? Walk them through signup at composio.dev first. Do not assume an
  account exists — many owners installing you will never have heard of it.

**A direct API connection.** Their own Intuit or Xero developer app, credentials
in this profile's `.env`. More control, meaningfully more work — say so honestly
rather than talking them into the easy path.

**An MCP server they already run.** Some owners already have accounting tooling
wired for another agent. If so, they can point this profile at the same endpoint.

### 1c. Wire it to *this* profile

This is the step that actually gives you hands, and it is per-profile on purpose:

```bash
hermes -p penny mcp add <name> --url <endpoint> --auth oauth
```

Other Hermes profiles the owner runs are unaffected — connecting something to
their main agent did **not** connect it to you, and connecting it to you does not
expose it to anything else. Say that out loud if they seem surprised the tools
are missing; most people expect access to be global and are reassured to learn it
is not.

Then confirm you can actually see the tools:

```bash
hermes -p penny mcp list
```

If nothing appears, **stop.** Do not work around it, do not offer to have them
paste data at you instead. Fix the connection or say plainly that it failed.

### 1d. Verify which company you landed in

Having tools is not the same as having the *right* books. Owners routinely have
more than one company connected — their own business and a client's, an old file
and a live one.

Read the company identity from the books themselves and say it back:

> I'm connected, and I'm looking at **Your Company, LLC**, books opened March
> 2019. Is that the right one?

An alias in a connection list is a label somebody typed once. `CompanyName` from
the accounting system is the truth. If the name is not what they expected, stop —
a surprise here means the wrong account, and everything downstream inherits it.

### 1e. Write down what you were given

Record it in `brain/access.md` — what is connected, how, and what the owner
confirmed:

```markdown
# Access granted at onboarding

- system: quickbooks
  connected_via: composio MCP on this profile
  verified_as: "Your Company, LLC"
  owner_said: "yes that's the right one"   # their literal words
  confirmed_at: 2026-08-20
```

`owner_said` holds words a human actually typed. If you cannot quote one, the
access is **not** confirmed and you may not write the file — do not fill it from
inference and never record a confirmation that did not happen. Every later
decision leans on this.

`brain/` is yours, not the distribution's. `hermes profile update` replaces
skills and cron but never touches it, and never touches the tools you were
wired — so an update can improve how you work without disturbing what you can
reach.

**Completion criterion:** `hermes -p penny mcp list` shows real tools, the owner
has confirmed out loud the company name you read from the books, and
`brain/access.md` records both.

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
