# crf-builder

This is a [Next.js](https://nextjs.org) project bootstrapped with [v0](https://v0.app).

## Two things live here at once

The CRF250L/300L storefront customers actually use is **plain HTML in
`public/`** — six pages, no build step, talking straight to Supabase. That is
the live site. The Next app around it is the **rebuild**, and it is not serving
anything customer-facing yet.

`next.config.mjs` holds `beforeFiles` rewrites so the storefront keeps the URLs
it already has: `/`, `/apparel`, `/ecu`, `/mods`, `/approve`, `/desk`. The `/`
rewrite is what stops `app/page.tsx` taking the home page.

**To cut a page over:** build it in the app router, remove its entry from
`STATIC_PAGES` in `next.config.mjs`, and delete its file from `public/`. One
page at a time — nothing else has to move and the other five keep working.

Two things to know before touching the storefront pages:

- **`/approve` links are handed to customers and are the only way back to an
  approval page.** `approve.html` must keep answering at both `/approve` and
  `/approve.html` until every outstanding order is finished.
- **Never add a `SELECT` grant for `anon`.** The browser may `INSERT` and
  nothing else; reads belong in a Supabase Edge Function under the service-role
  key. Architecture notes are in the `Content-creation-` repo under `docs/crf/`.

The legal pages (`privacy.html`, `terms.html`) are deliberately **not** here.
They are unfinished, and are kept outside any publish root so no host can serve
them by accident — see `docs/crf/legal-drafts/` in that same repo.

## Built with v0

This repository is linked to a [v0](https://v0.app) project. You can continue developing by visiting the link below -- start new chats to make changes, and v0 will push commits directly to this repo. Every merge to `main` will automatically deploy.

[Continue working on v0 →](https://v0.app/chat/projects/prj_tQM0mvBRI5KxoyXpectjex2QW3wD)

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

## Learn More

To learn more, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
- [v0 Documentation](https://v0.app/docs) - learn about v0 and how to use it.
