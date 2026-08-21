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

Already running Hermes? Paste the install prompt into the session you have open
and it handles this for you. She installs as her **own profile**, alongside
whatever you already run — nothing you have is modified.

Then one thing before you talk to her: give the profile a model. Hermes profiles
carry their own credentials and do **not** inherit yours, which is exactly why no
API key ever ships inside a distribution. Skip this and you get a confusing
"No inference provider configured" error.

```bash
hermes -p penny setup --portal   # authenticate this profile
hermes -p penny model            # confirm or change the model
```

Now onboard her:

```bash
penny chat
```

Say **"onboard me"**.

> Requires Hermes >= 0.20.0 and git.

---

## She arrives with no access to anything

This is the part worth understanding before you start.

A freshly installed Penny can reach **nothing** — no QuickBooks, no Xero, no
bank data. `hermes -p penny mcp list` comes back empty. That is not a broken
install: Hermes scopes tools per profile, so whatever you already connected to
your main agent is **not** connected to her.

**Onboarding is where you hand over the keys**, one at a time, the way you would
with a new hire. She will ask what you use, how you want to connect it, and then
wire it to her profile — and she reads the company name back to you from the
books themselves before she touches anything.

Until that is done she cannot act on the wrong account, because she cannot act
at all.

---

## What onboarding will connect

| Need | Options she'll offer | Required? |
|---|---|---|
| Your books | Composio (recommended), your own Intuit/Xero API credentials, or an MCP server you already run | **Yes** |
| Receipt photos | Telegram gateway, or a forwarding inbox | No |

**New to Composio?** She'll walk you through signing up. It handles OAuth so
nothing gets pasted anywhere and access is revocable from one dashboard. The
direct-credential route works too — it means creating a developer app at Intuit
or Xero, which is real work, and she'll say so rather than talking you into it.

---

### Turn on her schedule

Cron jobs ship with the package but are **not** started automatically — Hermes
will not schedule someone else's jobs behind your back. Once you are happy after
onboarding:

```bash
hermes -p penny cron list      # see what she would run
hermes -p penny cron tick      # activate the schedule
```

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
| `access.md` | What you connected her to, and the words you confirmed it with |
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

Your `brain/`, memories, sessions, `.env`, receipts, ledger database — **and the
tools you connected her to** — are never touched. Updates change how she works,
never what she can reach.

---

Built on [Hermes Agent](https://hermes-agent.nousresearch.com) by Nous Research.
