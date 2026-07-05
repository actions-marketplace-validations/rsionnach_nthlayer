# Contributing to NthLayer

Thank you for considering contributing to NthLayer! We're in active v1.5
development and seeking feedback from the SRE/DevOps community.

This repository (`nthlayer`) is the **project front door + ecosystem hub**: it
hosts the GitHub Action, the PyPI meta-package, ecosystem-wide documentation,
integration-test infrastructure, demo materials, and the architectural design
corpus. **It contains no application code** — implementation lives in the
per-tier component repos. If your change is Python source, it belongs in one
of those repos, each of which has its own `CONTRIBUTING.md`:

| Looking to change… | Contribute in… |
|---|---|
| Generator (specs → artifacts) | [`nthlayer-generate`](https://github.com/rsionnach/nthlayer-generate) |
| Shared library / models / LLM wrapper | [`nthlayer-common`](https://github.com/rsionnach/nthlayer-common) |
| HTTP API, verdict store, cases | [`nthlayer-core`](https://github.com/rsionnach/nthlayer-core) |
| observe / measure / correlate / respond / learn (Tier 2 worker modules) | [`nthlayer-workers`](https://github.com/rsionnach/nthlayer-workers) |
| Operator TUI | [`nthlayer-bench`](https://github.com/rsionnach/nthlayer-bench) |
| The OpenSRM spec itself | [`opensrm`](https://github.com/rsionnach/opensrm) |

## Ways to Contribute Here

### 1. Try It Out and Share Feedback

The most valuable contribution right now is **using NthLayer on a real
service** and telling us what works and what doesn't:

- [Open a Discussion](https://github.com/rsionnach/nthlayer/discussions)
- [Report bugs](https://github.com/rsionnach/nthlayer/issues/new?labels=bug)
- [Request features](https://github.com/rsionnach/nthlayer/issues/new?labels=enhancement)

### 2. Documentation

Most changes here are docs. The corpus lives under `docs/`
(`docs/specs/`, `docs/roadmap/`, `docs/superpowers/`), plus `README.md`,
`CHANGELOG.md`, and the MkDocs site source in `docs-site/` / `mkdocs.yml`.
Fix typos, clarify explanations, and add examples.

### 3. Demo & Integration-Test Infrastructure

- `demo/` — the runnable cascading-failure scenario (`demo.sh`).
- `test/` — cross-repo integration harness
  (`test/integration-three-tier.sh`); see `docs/integration-testing.md`.

These are Bash. CI (`.github/workflows/ci.yml`) runs `bash -n` syntax checks
across `demo/` and `test/` shell scripts — keep them parseable.

### 4. The GitHub Action & Meta-Package

- `action.yml` delegates to `nthlayer-generate` at a **pinned tag** (never
  `main`) — keep that pin intact.
- `meta-package/` is the dependency-only source of `pip install nthlayer`.

## Development Setup

There is no venv or build for the front door itself. To work on docs/demo:

```bash
git clone https://github.com/rsionnach/nthlayer.git
cd nthlayer

# Validate shell scripts the way CI does
bash -n demo/*.sh test/*.sh

# Preview the docs site (optional)
uv run --with mkdocs-material mkdocs serve
```

To run the actual tools, install or work in the component repos (e.g.
`uv run --directory ../nthlayer-generate ...`).

## Pull Request Process

1. Fork the repository and create a feature branch off `main`.
2. Make your change.
3. For shell changes, confirm `bash -n` passes.
4. Commit using Conventional Commits (see below).
5. Push to your fork and open a PR against `main`.

## Development Guidelines

### Commit Messages

```
<type>: <description>

<optional body>
```

For the meta-package changelog: `feat` / `fix` / `deps` / `docs` surface;
`chore` / `test` / `ci` / `build` / `style` / `refactor` are hidden.

### Tag Namespaces (do not cross them)

- `v0.1.0a*` — legacy generator releases (historical).
- `meta-v*` — PyPI meta-package releases (triggers `release.yml`).
- Sub-package `v*` tags live in their own repos.

## Finding Something to Work On

Browse [open issues](https://github.com/rsionnach/nthlayer/issues) and look for
`good-first-issue` / `help-wanted` labels. Maintainers track detailed work in
**Beads**, a Dolt-backed board in the `opensrm` repo
(`cd ../opensrm && bd ready --json`) — you don't need it to contribute.

## Code of Conduct

Be respectful and constructive — we're all here to build better reliability
tooling.

## Questions?

- [GitHub Issues](https://github.com/rsionnach/nthlayer/issues) — bugs and features.
- [GitHub Discussions](https://github.com/rsionnach/nthlayer/discussions) — general questions.

## License

By contributing, you agree that your contributions will be licensed under
this repository's license (see `LICENSE`).

---

**Thank you for helping make NthLayer better!**
