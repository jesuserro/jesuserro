# AGENTS.md

Operational and normative instructions for agents working in this repository.

## Repository scope

Canonical repository:

```text
/home/jesus/proyectos/jesuserro
https://github.com/jesuserro/jesuserro
```

Do not confuse this repository with `jesuserro.com`. That is a different project and stays out of scope.

## Git workflow

This repository uses **PR-gated Trunk-Based Development**.

`main` is the only permanent branch.

All changes flow through ephemeral branches and a Pull Request:

```text
main
  ↑
Pull Request
  ↑
feat/* | fix/* | chore/*
```

Rules:

- never develop directly on `main`;
- one short branch per logical change;
- allowed branch prefixes:

  - `feat/*`
  - `fix/*`
  - `chore/*`
- PRs always target `main`;
- squash merge by default;
- delete the branch after the merge;
- do not create permanent branches such as `dev`, `develop`, `staging` or equivalents;
- keep PRs small;
- do not accumulate multiple independent pieces of work on one branch.

## CV source of truth

The CV content lives in:

```text
cv/master/jesus_erro_cv_master.yaml
```

This is the single file to edit when CV content must change.

The files under:

```text
cv/generated/*.yaml
```

are derived artifacts. They must not be edited manually. They are produced by:

```text
scripts/build_cv_variants.py
```

Canonical render:

```bash
./render.sh
```

`render.sh`:

1. decrypts the required variables via SOPS;
2. generates the variants;
3. runs RenderCV;
4. produces the output artifacts.

Do not change this architecture without explicit approval.

## Secrets

- `.env.enc` may be versioned.
- `.env` in plaintext must never be versioned.
- Never show decrypted secrets in agent reports.
- Never copy secrets into logs.
- Never modify or reveal private `age` keys.
- Respect the existing SOPS + age infrastructure.

## CV factual policy

**CV content must remain evidence-based.**

Rules:

- do not invent experience;
- do not turn uncertain memories into facts;
- do not attribute specific technologies without evidence;
- do not increase the duration, responsibility or scope of any experience;
- do not turn one-off exposure into expertise;
- allowed:

  - improve wording;
  - reorganize;
  - summarize;
  - adapt relevance;
  - select content per variant;
- when factual uncertainty exists, preserve it explicitly.

General example:

```text
A short operational exposure must not be rewritten as
long-term administration or specialist expertise.
```

## Use of agents

Deterministic or operational tasks may be delegated to Big Pickle:

- Git operations;
- variant generation;
- mechanical synchronization;
- validations;
- renders;
- repetitive changes;
- checks on derived files.

For professional writing:

- always respect known facts;
- never infer experience that has not been declared.

## Local validation

This repository intentionally has no CI/CD for now. Do not add GitHub Actions workflows unless a future decision requires them.

Use fast local validation instead.

For purely documentary changes:

```bash
git diff --check
```

For changes to scripts:

```bash
bash -n render.sh
python3 -m py_compile scripts/build_cv_variants.py
```

For CV / RenderCV changes:

```bash
./render.sh
```

plus visual review of the affected PDF.

The model is:

```text
PR gate + fast local validation
```
