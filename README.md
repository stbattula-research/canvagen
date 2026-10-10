# canvagen

**Generate images and finished designs through Canva — as a Claude skill or a CLI.**

Chat models are mediocre at making images, and terrible at putting *words* on
them. Canvagen bridges that gap: it drives Canva's API so you (or your Claude
agent) can

- **imagine** — text-to-image generation (illustrations, logos, scenes, food…)
- **autofill** — fill a Canva brand template with your data to produce
  invitations, posters, YouTube thumbnails, announcements — with pixel-perfect
  real text, not AI-mangled lettering
- **export** — download finished designs as PNG/JPG/PDF, or keep them in your
  Canva account for further editing

## Quick start

```bash
pip install .
canvagen auth --client-id <id-from-canva-developers>   # one-time browser approval
canvagen imagine "a fox reading a newspaper, watercolor" --aspect-ratio landscape
canvagen autofill <template-id> --data '{"title":"Ava turns 7!"}' --export png
```

Full setup (creating the Canva integration, required scopes, redirect URL) is
in [SKILL.md](SKILL.md).

## Install as a Claude skill

Copy this repo's `SKILL.md` (plus the `canvagen/` package) into your skills
directory, e.g. `~/.claude/skills/canvagen/`, then `pip install <repo>`.
Claude will pick it up automatically when you ask for images or designs.

## Repo layout

| Path | What |
|---|---|
| `SKILL.md` | The Claude skill definition |
| `canvagen/auth.py` | OAuth PKCE flow + `0600` token store |
| `canvagen/generate.py` | Text-to-image (preview Generations API) |
| `canvagen/designs.py` | Create / autofill / export / asset upload |
| `canvagen/cli.py` | The `canvagen` CLI |
| `tests/` | Unit tests (no network) |
| `examples/` | Walkthroughs: invitation, thumbnail |

## Honest limits

- The image-generation endpoint is a **preview API** — it works, but Canva may
  change it without notice.
- Generations consume your Canva AI credit allowance; image URLs expire in 24h.
- Template autofill needs Canva Pro/Teams/Enterprise on the acting account.
- This repo is not affiliated with Canva.

## License

MIT.
