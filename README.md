# slym-pipeline-demo

A demo of [slym](https://github.com/p-phi/slym) running in GitHub Actions.

Comment `/ai-review` on a pull request, and a workflow pipes the diff into a
local bundle and posts the result as a comment. End to end, it takes about
20 seconds.

## The workflow

`.github/workflows/simple-review.yml`:

```yaml
name: Weary Senior Engineer Review

permissions:
  issues: write
  pull-requests: write

on:
  issue_comment:
    types: [created]

jobs:
  review:
    if: |
      github.event.issue.pull_request &&
      startsWith(github.event.comment.body, '/ai-review') &&
      contains(fromJson('["p-phi"]'), github.event.comment.user.login)

    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - run: curl -fsSL https://raw.githubusercontent.com/p-phi/slym/main/install.sh | bash

      - name: Get PR Diff
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr diff ${{ github.event.issue.number }} > pr_diff.txt

      - name: Run the Weary Review
        env:
          SLYM_ENDPOINT: ${{ secrets.OPENAI_ENDPOINT }}
          SLYM_MODEL: ${{ vars.OPEN_AI_MODEL }}
          SLYM_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          cat pr_diff.txt \
            | slym .slym/bundles/weary-reviewer --run "Review with attitude" \
            | slym-show --last > review.md

      - name: Post Review Comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 👴 Weary Senior Engineer Says:\n\n${review}`
            });
```

The trigger is gated on three things: it's a PR comment, the comment starts
with `/ai-review`, and the author is on the allowlist. Nothing runs on push.

## The bundle

```
.slym/bundles/weary-reviewer/
  SKILL.md
```

One file. The persona and the review policy are prose, committed to the repo.
Changing the reviewer means editing `SKILL.md` and opening a PR — the same
review process as any other change.

This bundle declares no tools, so the agent only reads the diff and responds.
Adding `schemas/` and `tools/` would let it run commands against the checkout.

## The step

```bash
cat pr_diff.txt \
  | slym .slym/bundles/weary-reviewer --run "Review with attitude" \
  | slym-show --last > review.md
```

`gh pr diff` is the context. `slym` runs the loop and emits the trace.
`slym-show --last` takes the final assistant message. The redirect writes the
file the next step reads.

To reproduce a run locally, set the same three environment variables and run
that pipeline against a diff.

## Running it yourself

Fork, then set:

- `OPENAI_ENDPOINT` (secret) — any OpenAI-compatible chat-completions URL
- `OPENAI_API_KEY` (secret)
- `OPEN_AI_MODEL` (variable)

Edit the allowlist in the `if:` condition to your own username. Open a PR,
comment `/ai-review`.

## Notes

The workflow installs slym with `curl | bash`. Pin it to a tag or commit if
you're running this anywhere that matters.

`permissions` is scoped to `issues: write` and `pull-requests: write`. The job
reads the diff and posts a comment; it doesn't push, and it doesn't need
contents access.

## License

MIT.
