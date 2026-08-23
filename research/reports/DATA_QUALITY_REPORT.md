# Data quality report

Generated: 2026-08-15T13:42:50.130172+00:00
Git: `2d49ac0af9bfb4800996e43feea3f321a10725c2`

## Blocking (must fix before training)

- audio_bytes_missing_for_n=6

`can_train`: **False**

## Warnings

- speaker_id_missing_n=1
- no_validation_split_rows
- no_test_split_rows
- checksum_missing_n=5

## Checks run

| Check | Result |
|-------|--------|
| Required metadata fields | 6 / 6 ok |
| Duplicate clip ids | see blocking |
| Speaker split leakage | see blocking |
| Clean/compressed pair split leakage | see blocking |
| Tamil in manifest labels | True |
| Tamil audio bytes verified | False |
| Missing audio files for `uri` | 6 |
| Orphan speaker_id | 1 |
| Split counts | {'train': 6, 'val': 0, 'test': 0} |

Training is **stopped** until a curated, speaker-disjoint corpus with on-disk audio exists.
