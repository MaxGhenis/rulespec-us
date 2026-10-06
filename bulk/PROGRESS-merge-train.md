# Merge train status

- Train PR #763 (`bulk-encode-merge-train`): 132 modules, one sync (520 declared) + one reverse-index.
- Local gate battery GREEN before push: guard-generated pass, validate 132/132, proof-validate (incl money-atoms) pass. File-set verified == union of carried originals (no drops).
- Excluded (open, branches retained): #638 az/43-1011, #739 md/gtg/10-716 (money-atom ratchet); #629 wv/11-21-21, #632 wv/11-21-23 (sibling rule-name collision).
- 131 carried source PRs CLOSED referencing #763; branches retained (no deletion until #763 merges).
- Auto-merge armed; up-to-date with main (5e78c160). Blocked only on org Actions runner availability. Merges autonomously on green.
- On merge: reconcile worklist ledger pr-open -> merged-via-train.
