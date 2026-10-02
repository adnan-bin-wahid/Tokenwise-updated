# Contributing to TokenWise

Thank you for your interest in contributing.

## Development Principles

- Keep changes focused and minimal.
- Prefer clear UX over complex options.
- Do not commit large binary model files.
- Include a short rationale in PR descriptions.

## Local Workflow

1. Fork and clone the repository.
2. Create a feature branch:

```bash
git checkout -b feat/short-description
```

3. Make your changes.
4. Run basic checks relevant to your change.
5. Commit with clear messages.
6. Open a pull request.

## Pull Request Checklist

- [ ] Change is scoped to one clear goal
- [ ] README/docs updated if behavior changed
- [ ] No secrets, tokens, or local env files included
- [ ] No large binaries added

## Commit Message Style

Use concise prefixes when possible:

- `feat:` new functionality
- `fix:` bug fix
- `docs:` documentation-only changes
- `refactor:` code restructuring without behavior change
- `chore:` maintenance changes

Example:

```text
feat: add command to prune selected editor text
```
