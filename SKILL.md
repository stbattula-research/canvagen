# Canvagen

Generate high-quality images and finished designs through Canva's API —
text-to-image generation, template autofill (invitations, posters, thumbnails
with real text), and export. Install this skill, connect Canva once, then
generate from Claude or the CLI.

## When to use

- The user wants an **image from a text prompt** (illustrations, backgrounds,
  scenes, logos, food photography…) — better than asking a chat model to draw,
  because Canva renders through dedicated image models.
- The user wants a **designed asset with text**: birthday/wedding invitations,
  event posters, YouTube thumbnails, announcements, social posts. AI image
  generators mangle text — Canva templates don't.
- The user wants the result **inside their Canva account** for further editing.

## Setup (one time, per user)

Every user creates their **own** Canva app — apps in Draft can only be
authorized by their owner, and tokens/AI credits are always per-user. The
walkthrough below was verified end-to-end on 2026-10-10.

1. Go to <https://www.canva.com/developers/> → **Your apps** → **Create an
   app**. Name it (e.g. `canvagen`), choose **Public** (Private is
   Enterprise-only and the choice is irreversible), and create it.
2. Open the app → **Outside Canva** → **Go to setup** → **Start integrating**.
   Canva requires **multi-factor authentication** on your account before it
   issues API credentials — enable it under Canva's Account and security
   settings first if prompted.
3. On the app's **Configuration** page:
   - Copy the **Client ID** (looks like `OC-…`). Note: this is *not* the App
     ID shown on the Overview page — the App ID fails OAuth with
     "client ID invalid".
   - Under **Redirect URLs**, add `http://127.0.0.1:53682/callback`.
   - Enable the **Canva REST APIs** integration method and tick these scopes:
     `asset:read`, `asset:write`, `design:content:read`,
     `design:content:write`, `design:meta:read`, `brandtemplate:meta:read`,
     `brandtemplate:content:read`.
   - Click **Generate secret** and copy the client secret (shown once).
4. Install: `pip install .` (from this repo) — provides the `canvagen` CLI.
5. `canvagen auth --client-id <your-client-id> --client-secret <your-secret>`.
   Approve in the browser. Tokens are stored at
   `~/.config/canvagen/tokens.json` with `0600` permissions and refreshed
   automatically.

## Capabilities

### 1. Text-to-image (`canvagen imagine`)

```
canvagen imagine "cozy coffee shop interior at dawn, warm light" --aspect-ratio landscape
canvagen imagine "minimal rocket logo, flat vector" --model lucid_origin --save --name rocket-logo
```

- Aspect ratios: `square` (1:1), `landscape` (16:9), `portrait` (9:16).
- Models: omit to let Canva pick; `lucid_origin` for architecture/logos/posters/
  sci-fi; `z_image_turbo` when the image includes text, or food/drink/general.
- `--save` also stores the image in the user's Canva uploads.
- Each generation consumes the user's Canva AI credit allowance; the download
  URL is valid 24 hours, so the CLI downloads immediately.
- The Generations API is in **preview**: expect occasional breaking changes.

### 2. Template autofill — invitations, posters, thumbnails

The highest-quality path for anything with words on it:

1. In Canva, design (or pick) a template, tag elements as data fields with the
   **Data autofill** app, and publish it as a brand template (needs Canva Pro,
   Teams, or Enterprise).
2. `canvagen template-fields <template-id>` — see the fillable fields.
3. `canvagen autofill <template-id> --data '{"name":"Ava","date":"Dec 12"}' --export png`

Example — birthday invitation:

```
canvagen autofill tmpl_abc123 --export png --data '{
  "title": "Ava turns seven!",
  "details": "Saturday, Dec 12 · 4 PM · 21 Maple St",
  "photo": "<asset-id-or-upload-url>"
}'
```

### 3. Designs and exports

```
canvagen design-create --title "Launch poster" --type poster
canvagen export <design-id> --format pdf -o poster.pdf
```

## Notes for the agent

- Never ask the user for their Canva password — OAuth only.
- Generated-image URLs expire in 24h; always download right away.
- If a job fails with `credit_quota_exceeded`, the user's AI allowance is spent.
- Preview APIs can change; pin behavior in tests, not assumptions.
