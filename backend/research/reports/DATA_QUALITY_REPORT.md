# Data quality report

Generated: 2026-08-28T05:10:22.829428+00:00
Git: `8f439439a32f6ae9111ffeb5da367f7c7b4eb1d2`

## Blocking (must fix before training)

- tamil_language_code_absent_from_manifest

`can_train`: **False**

## Warnings

- none

## Checks run

| Check | Result |
|-------|--------|
| Required metadata fields | 0 / 0 ok |
| Duplicate clip ids | see blocking |
| Speaker split leakage | see blocking |
| Clean/compressed pair split leakage | see blocking |
| Tamil in manifest labels | False |
| Tamil audio bytes verified | False |
| Missing audio files for `uri` | 0 |
| Orphan speaker_id | 0 |
| Split counts | {'train': 0, 'val': 0, 'test': 0} |

Training is **stopped** until a curated, speaker-disjoint corpus with on-disk audio exists.
