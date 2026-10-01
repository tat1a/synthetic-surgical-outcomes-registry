# Technical validation report — 2026-10-01

**Scope:** a synthetic registry software demonstration. The report describes executable checks and generated outputs, not clinical validation, research results or regulatory qualification.

## Reproduction

From the repository root, with Python 3.10+ and no external packages:

```bash
python -m src.build
python -m unittest discover -s tests -v
```

The build generated three SQLite states and aggregate reports; all **8 automated tests passed** locally. CI rebuilds and tests on Python 3.10 and 3.12; a remote CI run remains to be observed after publication. The default seed is `20261001` and generator version is the repository's committed source. The fixed pseudo-audit timestamp is intentional for reproducibility.

## Results and reconciliation

| Check | Expected | Observed | Assessment |
| --- | ---: | ---: | --- |
| Participants | 300, 100/module | 300, 100/module | Pass |
| Scheduled visits | 4/participant | 1,200 | Pass |
| Completed visits | Descriptive only | 1,012/1,200 (84.3%) | Reported |
| AE rows / serious flags | Descriptive only | 52 / 5 | Reported |
| Clean critical rule hits | 0 | 0 | Pass |
| Controlled root errors detected | 18/18 | 18/18 | Pass for this challenge |
| Challenge rule hits | Root and cascades | 30 | Challenge blocked |
| Reconciled open queries / residual issues | 0 / 0 | 0 / 0 | Pass |
| Simulated audit rows | Corrections plus query closures | 48 | Pass |
| Empty registry lock | Fail | Fail | Pass negative test |

The 30 rule hits are **18 intentionally injected root errors plus 12 due-date effects** from three altered index dates. The validator does not read `data/injected_errors.csv` or the clean reference. The resolution script does read them, so the reconciled result is a controlled known-truth exercise, not independent source verification. Clean and reconciled states pass the implemented technical lock gate; the challenge fails. Tests also cover invalid calendar dates, missing procedure, an open critical query on otherwise clean data, row-level seed reproducibility, foreign keys, and aggregate export reconciliation.

## What is and is not validated

The tests support reproducible execution of the documented software rules at this revision. They do not measure clinical validity, real-world rule sensitivity, absence of all undiscovered data errors, privacy certification, validated electronic signatures, or production EDC compliance. The invented score, AE vocabulary, timing, and cohort balance cannot support inference. No expert reviewer sign-off is claimed. The methods review and remaining real-study decisions are documented in `internal_review_2026-10-01.md` and `reviewer_packet.md`.
