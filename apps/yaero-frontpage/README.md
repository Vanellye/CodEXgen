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

Create a Vercel project connected to `Vanellye/CodEXgen`, with root directory `apps/yaero-frontpage`, framework Vite, and build command `npm run build`. The app is intended for a preview deployment first.

## Runway Dev integration

The serverless endpoint `/api/runway-image` uses the documented Runway Dev `POST /v1/text_to_image` endpoint and `gen4_image` model. Add `RUNWAYML_API_SECRET` as an encrypted Vercel environment variable for Preview and/or Production. Never put this key in browser code, a public repository, or a client-side environment variable.

Runway Dev API credentials and API credits are separate from the Runway web-app workspace and its credits. Generation is an explicit user-triggered action and can consume API credits. The endpoint returns a task ID; this initial integration does not poll or download the generated asset.

## Safety boundaries

- No source code is uploaded to Runway.
- Only the creative brief is sent to Runway.
- No credentials are exposed to the browser.
- No source code is rewritten or executed.
- CI checks remain enabled; failed checks block promotion.
