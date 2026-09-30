# mainome-norns

A single-file, mobile-friendly catalog of [monome norns](https://monome.org/norns/) scripts
that you can browse from any phone, tablet, or computer on the same network as your norns —
and install patches straight to the device with one tap.

**Live page:** https://wildseyed.github.io/mainome-norns/norns-catalog.html
(see the note on https below before installing from the hosted copy)

## Raison d'être

The norns ecosystem lives on GitHub, but discovering scripts has traditionally meant
hanging around a single forum — one that has recently decided that works developed with
LLM assistance are unwelcome, requiring disclosure on submission and deleting posts that
comply. That policy doesn't just gatekeep a toolset; it hides good work from the people
who would enjoy it.

This project routes around the gate entirely:

- **Discovery without permission.** The catalog is built on
  [nornslist](https://github.com/seajaysec/nornslist), which finds norns scripts across
  *all* of public GitHub — tagged or not, forum-member or not, currently ~1,240 scripts
  and refreshed every 3 hours by a GitHub Actions workflow in that repo (nothing to
  run or host on your side).
- **AI-assisted work gets top billing, not a scarlet letter.** Scripts whose authors
  disclose LLM assistance are marked with a ✦ badge and boosted to the top of the default
  view. The methods are transparent (see below), and the curator list is plain text anyone
  can edit.
- **Zero infrastructure.** One HTML file. No server, no build step, no dependencies.
  Download it, AirDrop it, host it on your norns itself — it works the same everywhere.

If you love the device and want the most out of it, the catalog is yours.

## Features

- **Responsive card grid** — packs as many columns as the screen allows; cards expand
  to full width for details, links, and install controls.
- **Search & filters** — full-text search across name/author/description/tags/engine;
  capability chips for **grid**, **arc**, **crow**, **midi**; sorts by hidden-gem score,
  stars, recency, or name.
- **Works offline** — the full catalog snapshot is embedded in the file. When online,
  it silently refreshes itself from nornslist's live feed (CORS-enabled raw URL).
- **One-tap install to norns** — sends `POST /api/v1/project/install?url=<repo>` to
  maiden's HTTP API (the same call maiden's own `;install` makes), then **verifies** the
  result through the matron REPL websocket on port 5555. No login anywhere.
- **Host this page on norns** — uploads the catalog file to `~/dust/data/` on your
  device, so it can be opened same-origin at
  `http://<norns>/api/v1/dust/data/norns-catalog.html` with full install feedback.
- **✦ AI-assisted visibility**, via three transparent mechanisms:
  1. a **curator list** baked into the file (`AI_SCRIPTS` / `AI_AUTHORS`);
  2. a **keyword heuristic** over script metadata (`vibecoded`, `ChatGPT`, `Claude`,
     `Copilot`, `AI-assisted`, …);
  3. a **lazy README scan** — expanding a card checks the repo's README for disclosure
     and upgrades the badge live.

## Usage

### Browse

Open `norns-catalog.html` in any browser. That's the whole install.

| Where you open it | Browsing | Direct install |
|---|---|---|
| `file://` (downloaded copy) | ✓ | ✓ |
| `http://` on your LAN | ✓ | ✓ |
| `http://<norns>/api/v1/dust/data/norns-catalog.html` (hosted on norns) | ✓ | ✓ with full feedback |
| `https://` (e.g. GitHub Pages) | ✓ | ✗ — browsers block LAN calls from https pages |

### Install a script to your norns

1. Tap ⚙, enter your norns address (`norns.local` or its IP), **save**, optionally **test**.
2. Expand a script card, tap **⇣ install to norns**.
3. Watch the on-card log: the install POST is fired, then confirmed via the matron REPL.
4. Restart the norns (`SYSTEM > RESTART`) if the script needs it.

Fallback: the **copy cmd** button puts `;install <repo>` on your clipboard for pasting
into the maiden REPL.

### Host the catalog on your norns

⚙ → **⇪ host this page on norns**. The page base64-chunks itself through the matron REPL
into `~/dust/data/norns-catalog.html`. Share the resulting URL with any device on your
network — same-origin with maiden means installs get real JSON responses instead of the
verification step.

Finding the hosted copy later: the URL is always
`http://<norns>/api/v1/dust/data/norns-catalog.html` (maiden's server serves files out of
`~/dust/`; the exact link is shown in the settings panel right after upload). Note that
nothing is added to maiden's own web UI — its frontend only lists `dust/code` projects and
has no way to register links, so bookmark the URL or write it down.

### Curate the ✦ list

Edit the `CURATION` block near the top of the `<script>` in `norns-catalog.html`:

```js
const AI_SCRIPTS = [
  "rync/magnetar",       // "author/repo", lowercase
];
const AI_AUTHORS = [
  "wildseyed",           // every repo by these authors
];
```

The list travels with the file — anyone you share it with sees the same flags.

Want your own repos auto-detected everywhere, no curation needed? Put a disclosure in the
repo's GitHub description **and** README — e.g. *"built with Claude"* or *"AI-assisted
development"*. nornslist re-scrapes GitHub every 3 hours, so the description propagates
to every copy of the catalog on its own.

## Refreshing the embedded snapshot

Rarely needed (the page self-updates from the live feed), but to bake in fresh data:

```bash
python build_catalog.py                 # downloads the latest feed
python build_catalog.py catalog.json    # or inject a local copy
```

The script swaps only the data between the `SNAPSHOT:BEGIN/END` markers — your curation
block and any other edits are preserved.

## How install works (the technical bits)

- maiden's `;install` REPL command is **not** a matron feature — maiden's web frontend
  intercepts it and calls `POST /api/v1/project/install?url=<repo>` on its own HTTP API
  ([source](https://github.com/monome/maiden/blob/main/web/src/model/repl-actions.js)).
  This page calls the same endpoint. It performs a git clone into `~/dust/code/`, which
  is exactly what maiden's project manager does.
- maiden sends no CORS headers, so a cross-origin page can *send* the POST but not *read*
  the response. Verification therefore happens over the matron REPL websocket
  (`ws://<host>:5555`, subprotocol `bus.sp.nanomsg.org`, exposed by
  [ws-wrapper](https://github.com/monome/norns/blob/main/ws-wrapper/src/main.c)):
  a one-line Lua `os.execute("test -d …")` confirms the project landed.
- No authentication is involved in any of these paths; the threat model is "your LAN",
  same as maiden itself.

## Data & credit

Catalog data: [seajaysec/nornslist](https://github.com/seajaysec/nornslist) — public
GitHub discovery of norns scripts, refreshed every 3 hours. README text and images are not
mirrored; links go to the authors' own repos.

Built for the norns community — all of it.
