# portfolio-wiki-dimas

Dimas' portfolio as a wiki, built with [Astro](https://astro.build) + [Starlight](https://starlight.astro.build).

## Development

```powershell
npm install
npm run dev      # http://localhost:4321/portfolio-wiki-dimas/
npm run build    # output in dist/
npm run preview
```

## Adding content

- Regular pages: a new `.md` file in `src/content/docs/`.
- Projects: a new `.md` file in `src/content/docs/projects/`, then link it from `projects/index.md`.
- Notes: a new file in `src/content/docs/notes/`.
- Sidebar order: `sidebar` in `astro.config.mjs`.

## Deploy

Every push to `main` runs `.github/workflows/deploy.yml`. One-time setup on GitHub: **Settings → Pages → Source = GitHub Actions**.

The site is published at <https://wiki.dimasreza.my.id/> (see `CNAME`), so it lives at the domain root: internal links are root-relative (`/about/`, `/projects/`) and must not repeat the repo name.
