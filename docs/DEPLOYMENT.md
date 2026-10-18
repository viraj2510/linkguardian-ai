# Deploy LinkGuardian on Vercel Hobby

The repository contains two services. Deploy both from the same GitHub repository as two Vercel projects. Deploying only the frontend leaves scanning unavailable.

## Current production deployment

- Website: [linkguardian-ai-pi.vercel.app](https://linkguardian-ai-pi.vercel.app)
- API health: [linkguardian-api.vercel.app/health](https://linkguardian-api.vercel.app/health)
- API documentation: [linkguardian-api.vercel.app/docs](https://linkguardian-api.vercel.app/docs)
- Repository: [viraj2510/linkguardian-ai](https://github.com/viraj2510/linkguardian-ai)
- Vercel team: `viraj-gundewars-projects`, Hobby plan.

The initial deployment was published from each service directory using Vercel CLI. The API URL and allowed frontend origins are saved in the production environment. GitHub automatic deployment integration is a separate optional account permission.

## 1. Publish the repository

Commit the source, lockfile, documentation, and bundled model. Exclude `.env.local`, `.vercel`, logs, caches, and dependencies using `.gitignore`. Never commit account tokens. Push to the repository owned by the intended GitHub account.

## 2. Deploy the API first

Import the repository into Vercel and select the free Hobby team. Use a project name such as `linkguardian-api` and set **Root Directory** to `backend`. Vercel detects FastAPI through `index.py`; `.python-version` selects Python 3.12. Keep the build settings at their framework defaults. The pinned requirements install the model's Python dependencies.

Deploy, then open `https://<api-domain>/health`. Require HTTP 200 and `"model_available": true` before calling this an AI deployment. `/docs` provides interactive API documentation. A degraded health response means the API is reachable but the model could not load.

## 3. Deploy the frontend

Import the same repository as another project, such as `linkguardian`, with **Root Directory** set to `frontend` and framework **Next.js**. Add `NEXT_PUBLIC_API_URL=https://<api-domain>` to the production environment before building. Use the API origin without a trailing path. Deploy using the default install and build commands.

## 4. Allow the frontend origin

In the API project's production environment, set `CORS_ORIGINS=https://<frontend-domain>` and redeploy the API. Use the exact HTTPS frontend origin, without a trailing slash. Multiple origins may be comma-separated. Preview deployments need their own explicitly allowed origins; production settings do not automatically allow every preview URL.

## 5. Verify the public website

- Confirm the frontend shows **AI engine connected**.
- Scan `google.com`: expect a normalized URL and a low-risk result when DNS succeeds.
- Use **Suspicious pattern**: expect a high-risk result.
- Submit `javascript:alert(1)`: expect a validation message.
- Check recent results, support navigation, FAQ, and mobile layouts.
- Check browser console and network requests for failures and CORS errors.
- Run `BROWSER_TEST_URL=https://<frontend-domain> npm run test:browser` in a POSIX shell, or set `$env:BROWSER_TEST_URL` first in PowerShell. The browser script uses Microsoft Edge by default.

## Free-plan constraints

Hobby is intended for eligible personal, non-commercial projects. Stay within the current free quotas; do not enable paid add-ons or upgrade the team. Python functions have bundle-size and runtime limits, and model imports can add cold-start latency. This repository's deployment does not train the model at startup or require a paid AI API key. Check current limits in [Vercel's documentation](https://vercel.com/docs/limits) before relying on capacity.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Engine unavailable | API health endpoint, public API access, `NEXT_PUBLIC_API_URL`, API deployment logs |
| CORS error | Exact frontend origin in API `CORS_ORIGINS`; redeploy API after changes |
| Frontend still calls localhost | Set the public API variable and rebuild the frontend |
| Limited analysis available | Bundled `app/rf_model.joblib`, compatible dependency versions, function logs |
| Model bundle too large | Exclude training data and caches; retain the saved model and inference dependencies |
| DNS unverified | Resolver availability/timeouts; the app deliberately reports uncertainty |
| 401 on API requests | Vercel deployment protection must permit access to this public scanner API |

Do not retrain inside a serverless request: filesystem writes are ephemeral and training is too expensive for this flow. Train locally, evaluate, commit the replacement artifact, and redeploy.
