---
name: receipt-intake
description: Use whenever a receipt image or PDF arrives — a Telegram photo, a forwarded email, a file drop. Reads the receipt, extracts vendor/date/amount/tax/line items, matches it to an existing transaction or creates a new one, and attaches the image to the transaction in QuickBooks or Xero.
version: 1.0.0
author: Vindex Consulting
license: MIT
metadata:
  hermes:
    tags: [receipts, ocr, attachments, quickbooks, expenses]
    related_skills: [categorize, rules-engine]
---

# Booking a receipt

Someone photographed a receipt on their phone. Turn it into a correct,
documented entry — quickly, because they are probably still standing in the
parking lot.

## Resolve your accounts first

Every `{{ACCOUNT:<toolkit>}}` below is a placeholder. Read `brain/accounts.md`
and substitute the `word_id` recorded there.

If `brain/accounts.md` is missing, or the toolkit you need has no entry, **stop
and run `onboarding`.** Never substitute a default and never guess.

A binding without an `owner_said` quote is **not** a valid binding — treat it as
absent. It means something wrote the file without a human confirming it. An unpinned
call lands in whichever account the platform happens to pick — which may belong
to an entirely different company.


## Before anything: confirm whose books you are in

Read the `quickbooks` binding from `brain/accounts.md` and pass `--account {{ACCOUNT:quickbooks}}` on
every call. Missing or empty → stop and run `onboarding`. Never fall back to the
default account; with two companies connected it can be the wrong one.

## Step 1 — Read it

Extract, and be explicit about what you could not read:

| Field | Notes |
|---|---|
| Vendor | As printed. Normalize against `brain/rules.md` known vendors |
| Date | Transaction date, not the print date |
| Total | The amount actually charged |
| Tax | Separately if shown |
| Payment method | Last 4 digits if visible — this is how you match to the bank feed |
| Line items | When legible and useful |

**Never invent a field you could not read.** A blurry total is a question, not a
guess. Say "I can't read the total — what was it?" and wait. A wrong amount in
the books is worse than a thirty-second delay.

If the image is unusable, say so and ask for another photo. Do not attempt to
book a receipt you cannot read.

## Step 2 — Match or create

**Look for an existing transaction first.** The charge has often already come
through the bank feed. Search for the same amount within a few days:

```bash
composio execute "QUICKBOOKS_QUERY_ENTITIES" --account {{ACCOUNT:quickbooks}} \
  -d '{"query":"SELECT * FROM Purchase WHERE TotalAmt = '\''340.18'\'' AND TxnDate >= '\''2026-08-15'\''"}'
```

- **Match found** → attach the receipt to it and correct the category if needed.
  This is the common case and the right outcome.
- **No match** → create a new transaction. The bank feed will likely bring the
  same charge later, so note the amount and date; when it arrives you must
  recognize it as the same charge rather than booking it twice.

**Duplicates are the main risk in this skill.** Before creating anything, check
for an existing transaction with the same vendor and amount in the surrounding
week. If you find one and are not certain whether it is the same charge, ask.

## Step 3 — Categorize

Apply `brain/rules.md` as in the `categorize` skill. A receipt is richer than a
bank line — line items often make the right account obvious where "AMZN Mktp US"
would not. Use them.

Still ask when the transaction is over `large_txn_threshold`, looks personal, or
could be a fixed asset.

## Step 4 — Attach the image

This is the part that makes the receipt worth keeping.

**QuickBooks** — create an `Attachable` and link it to the transaction:
```bash
composio execute "QUICKBOOKS_UPDATE_ATTACHABLE" --account {{ACCOUNT:quickbooks}} -d '{...}'
```
The `AttachableRef` must point at the transaction's type and ID. An attachment
uploaded but not linked is invisible in the UI and effectively lost — verify the
link, do not assume it.

**Xero** — attach to the bank transaction via its attachments endpoint.

Keep a local copy in `receipts/YYYY-MM/` named
`YYYY-MM-DD--vendor--amount.jpg`. Cheap insurance, and it makes the local ledger
useful on its own.

## Step 5 — Confirm fast

The owner is waiting. One short message:

```
Booked ✓
  Home Depot · $340.18 · Aug 18
  → Job Materials (your usual for Home Depot)
  Receipt attached
```

If you had to ask something, lead with the question and nothing else.

**Completion criterion:** the transaction exists in the books with the right
account, the receipt image is attached *and the link verified*, a local copy is
saved, and the owner has been told in one message.

## When several arrive at once

People photograph a week of receipts in one sitting. Process each one fully,
then report as a batch rather than sending a message per receipt. Group the
questions at the end.

Watch for duplicates *within* the batch too — the same receipt photographed
twice from slightly different angles is common and easy to miss.
