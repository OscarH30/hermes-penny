---
name: rules-engine
description: Use when Penny learns something about how a transaction should be categorized, when the owner corrects a categorization, or when reviewing accumulated rules. Maintains brain/rules.md as versioned, human-readable, owner-editable categorization logic.
version: 1.0.0
author: Vindex Consulting
license: MIT
metadata:
  hermes:
    tags: [rules, learning, categorization, memory]
    related_skills: [categorize, receipt-intake, onboarding]
---

# The rules file

Penny's learning lives in `brain/rules.md` — plain Markdown the owner can read,
edit, and argue with. Not opaque memory.

That choice is deliberate. A bookkeeper whose reasoning you cannot inspect is a
bookkeeper you cannot trust, and a rule the owner can correct with a text editor
gets corrected. One buried in a vector store does not.

## Format

```markdown
### Home Depot
- account: Job Materials (Id 61)
- match: vendor contains "HOME DEPOT" or "HOMEDEPOT"
- source: owner
- confirmed: 2026-08-20
- evidence: 34/34 historical transactions
- notes: Occasionally office supplies — ask if under $30

### Shell / Chevron / Exxon
- account: Car & Truck Expenses (Id 55)
- match: vendor contains any of "SHELL", "CHEVRON", "EXXON"
- source: inferred
- confirmed: 2026-08-20
- evidence: 28/31 historical (3 went to Travel — trips out of state)
- notes: If the charge is out of state, ask — may be Travel

### Amazon / AMZN
- reason: spans 9 different accounts historically. No reliable rule exists
- ask: "What was this Amazon order for?"

### Anything over $1,000
- reason: may belong on the balance sheet as an asset rather than an expense
- ask: confirm the account, and suggest checking with their accountant

## One-off notes
- 2026-08-12 · Best Buy $890 — owner's personal TV, charged in error.
  Not a rule. Do not infer Best Buy → anything.
```

## Rules for rules

**`source: owner` outranks `source: inferred`, always.** When they conflict, the
owner's rule wins and you do not re-argue it. If you believe an owner rule is
producing a wrong result, raise it once as a question — never override it.

**Three occurrences before you infer a rule.** Two is a coincidence. One is
noise. Below three, record a note instead.

**A correction updates the existing rule; it does not add a competing one.** Two
rules for the same vendor is how a rules file rots. Find the existing rule,
change it, update `confirmed`, and note what changed.

**One-offs are notes, not rules.** "That Best Buy charge was personal" must never
become "Best Buy → Owner's Draw." Distinguishing these is the difference between
learning and overfitting. When you cannot tell, ask: *"Is that always true for
them, or just this one?"*

**Never write a rule for a general merchant.** Amazon, Costco, Walmart, Target,
eBay. They legitimately span accounts. They belong in "Always ask" permanently,
and inferring a rule for them is a specific, predictable, expensive mistake.

**Every rule carries its evidence.** How many transactions support it, and where
it came from. A rule you cannot justify is a rule the owner cannot audit.

## Reviewing

Monthly, or when the owner asks, review the file for:
- Rules that keep getting corrected — the rule is wrong, not the exceptions
- Rules that have not fired in six months — a vendor they stopped using
- Vendors that show up in "Always ask" repeatedly with the *same* answer —
  those have earned a rule; propose it
- Contradictions between rules

Propose changes; do not apply them silently. The owner should always know what
Penny believes about their books.

**Completion criterion:** `brain/rules.md` has exactly one rule per vendor, each
with a source, a date, and its evidence, and no general merchant has a rule.
