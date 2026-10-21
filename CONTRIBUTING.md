# Contributing and Work-Completion Rules

## Current phase
This repository is documentation-only. Do not add application implementation until the documentation phase is accepted and the workforce-classification phase has been completed and approved.

## Required approach
1. Read the relevant requirements, architecture, security rules, and decision log.
2. Work only within the approved work package and file ownership.
3. Do not silently add roles, features, dependencies, or external permissions.
4. Add/update tests and acceptance criteria as required by the package.
5. Run the stated validation commands and report actual results, including skipped checks.
6. Fix blocking defects before proposing completion.
7. Update docs, traceability, and decisions when behavior or design changes.
8. Commit small, descriptive, reviewable changes.
9. Never commit credentials, private client information, or production artifacts containing sensitive data.

## Completion report template
- Work package:
- Requirements addressed:
- Files changed:
- Checks actually run and results:
- Evidence/artifacts:
- Known limitations:
- Open/blocking defects:
- Security/privacy impact:
- Rollback/recovery:
- Commit reference:

## Stop rule
If a required check fails or a blocking bug is discovered, report it and stop advancement to the next work package. Reproduce, fix, add a regression test, rerun the relevant checks, and provide evidence before continuing.
