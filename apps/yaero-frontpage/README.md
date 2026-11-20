# Ŷæṛö Frontpage

A Vite frontpage and safe lexical workbench. It previews symbolic atoms and balanced scopes only; it does not compile, evaluate, or execute pasted source.

## Local development

```sh
npm install
npm run dev
npm test
npm run build
```

## Vercel

A Vercel project named `yaero-frontpage` exists. Its current READY preview deployment was built from the feature branch snapshot:
`https://yaero-frontpage-264x4yb6w-tkoester0126-5442.vercel.app`

The project is not Git-connected yet. Vercel requires a GitHub Login Connection before it can link `Vanellye/CodEXgen` for automatic branch deployments. After that connection is added, set the project root directory to `apps/yaero-frontpage`, framework to Vite, and build command to `npm run build`. The current preview has no alias or custom domain and is not a production release.

## Runway Dev integration

The serverless endpoint `/api/runway-image` uses the documented Runway Dev `POST /v1/text_to_image` endpoint and `gen4_image` model. Add `RUNWAYML_API_SECRET` as an encrypted Vercel environment variable for Preview and/or Production. Never put this key in browser code, a public repository, or a client-side environment variable.

Runway Dev API credentials and API credits are separate from the Runway web-app workspace and its credits. Generation is an explicit user-triggered action and can consume API credits. The endpoint returns a task ID; this initial integration does not poll or download the generated asset.

## Safety boundaries

- No source code is uploaded to Runway.
- Only the creative brief is sent to Runway.
- No credentials are exposed to the browser.
- No source code is rewritten or executed.
- CI checks remain enabled; failed checks block promotion.
