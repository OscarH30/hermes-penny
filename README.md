# Penny — bookkeeper

Penny learns your chart of accounts, categorizes what lands in your books,
books receipts from a photo, and asks about anything she isn't sure of.

She proposes; **you approve; then she posts.** That is the default and she does
not drift out of it.

---

## Install

```bash
hermes profile install github.com/OscarH30/hermes-penny --alias
```

**Then three one-time steps.** Do them in order — the first two are what make
the agent able to think at all, and skipping them produces a confusing
"No inference provider configured" error.

```bash
# 1. Authenticate this profile with a model provider.
#    Each Hermes profile carries its own credentials — that is deliberate,
#    and it is why no API key ever ships inside a distribution.
hermes -p penny setup --portal

# 2. Confirm the model. The package defaults to Nous Portal; if you are on
#    Anthropic, OpenAI, or anything else, pick it here.
hermes -p penny model

# 3. Connect your books.
cp ~/.hermes/profiles/penny/.env.EXAMPLE ~/.hermes/profiles/penny/.env
composio link quickbooks        # or: composio link xero
```

Then:

```bash
penny chat
```

Say **"onboard me"** and she takes it from there.

> Requires Hermes >= 0.20.0 and git.

### Turn on her schedule

Cron jobs ship with the package but are **not** started automatically — Hermes
will not schedule someone else's jobs behind your back. Review and activate:

```bash
hermes -p penny cron list      # see what she would run
hermes -p penny cron tick      # activate the schedule
```

---

## What she needs connected

| Need | Recommended | Alternative | Required? |
|---|---|---|---|
| Your books | `composio link quickbooks` or `xero` | `QBO_*` / `XERO_*` credentials | **Yes** |
| Receipt photos | Telegram gateway | `PENNY_RECEIPT_EMAIL` forwarding | No |

Composio is genuinely easier here. The direct route means creating a developer
app at Intuit or Xero.

---

## How she sees your transactions

Worth understanding, because it shapes the setup:

QuickBooks' **"For Review" tab is a staging area**. Items sitting there aren't
transactions yet, and no API can see them — not Penny's, not anyone's. Once a
transaction is *accepted* into the books, it becomes fully visible, and Penny
can read, categorize, and correct it.

So onboarding offers you two modes:

**Catch-all bank rule (recommended).** One rule in QuickBooks auto-adds anything
unmatched into Uncategorized Expense. Everything then flows into the books
automatically and Penny cleans it up continuously — which is exactly what a
bookkeeper does anyway. Onboarding walks you through creating it.

**You accept transactions yourself.** You click through For Review as usual;
Penny categorizes whatever lands in Uncategorized. Less automatic, still useful.

**Xero** exposes bank transactions directly, so this is simpler there.

---

## What she does on her own

| When | What |
|---|---|
| Every 3 hours | Sweeps for uncategorized transactions, proposes categorizations |
| Weekdays 5:30pm | One end-of-day summary — questions first, then what came through |
| Whenever you send a receipt | Reads it, books it, attaches the image, confirms |

---

## Skills

| Skill | What it does |
|---|---|
| `onboarding` | Connects your books, reads the chart of accounts, mines 12 months of history for rules |
| `categorize` | Finds uncategorized transactions, proposes with confidence and reasoning |
| `receipt-intake` | Photo → transaction → receipt attached, in under a minute |
| `rules-engine` | Maintains what she has learned, as readable Markdown you can edit |
| `daily-close` | The one end-of-day message |

---

## She arrives already knowing your vendors

Onboarding reads **12 months of your transaction history** and finds the vendors
you always categorize the same way. Home Depot went to Job Materials 34 times
out of 34 — that is a rule, and it is *your* rule, not one she invented.

She proposes them all with the evidence, you confirm or correct, and she starts
work already knowing most of the answers.

She will also tell you which vendors she refuses to make a rule for. Amazon,
Costco, Walmart legitimately span many accounts — inventing a rule for them is
exactly how books get quietly wrong, so she asks every time instead.

---

## Her brain

Onboarding writes these into `~/.hermes/profiles/penny/brain/`. Plain Markdown —
open them, edit them, argue with them.

| File | What's in it |
|---|---|
| `chart-of-accounts.md` | Every account with its ID, type, and description |
| `rules.md` | What she's learned, with the evidence behind each rule |
| `business.md` | What you do and how you want things treated |
| `config.md` | Autonomy, thresholds, close time, receipt intake |

Her reasoning is readable on purpose. A bookkeeper whose logic you cannot
inspect is a bookkeeper you cannot check.

`brain/` never leaves your machine.

---

## What she will not do

- Post anything before you approve it (unless you explicitly set `autonomy: auto`)
- Guess at an account she is unsure about — she asks instead
- Delete a transaction or overwrite history
- Pay, transfer, refund, or move money in any way
- Give tax or deductibility advice

**Penny is not a CPA and this is not tax advice.** She categorizes, documents,
and organizes. Decisions about deductibility, tax positions, and what counts as
a business expense belong to you and your accountant. Review her work before you
rely on it.

---

## Updating

```bash
hermes profile update penny
```

Your `brain/`, memories, sessions, `.env`, receipts, and ledger database are
never touched.

---

Built on [Hermes Agent](https://hermes-agent.nousresearch.com) by Nous Research.
