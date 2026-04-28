# Contributing

## Branch Strategy

`main` is the only long-lived branch. Work must happen in short-lived scoped branches, such as `agentops/<plan-id>/<provider-or-scope>` or `governance/<scope>`, and pull requests must target `main`.

After a pull request is approved and merged, or explicitly closed by a human, the temporary branch must be deleted locally and remotely. The repository is configured to delete merged PR branches automatically.

## Commit Messages

Use Conventional Commits without strict enforcement for now:

```text
docs: update AgentOps governance rules
ci: add repository guard check
test: validate provider specs
feat: add aegis provider spec
fix: correct bluestone parser mapping
chore: remove dependabot config
```

Scopes are optional and useful when they clarify ownership:

```text
docs(governance): define PR evidence checklist
test(specs): add provider spec validation
feat(adapter): add aegis row parser
```

Prefer small commits that explain one intent. Include tests or evidence in the pull request body rather than overloading the commit message.
