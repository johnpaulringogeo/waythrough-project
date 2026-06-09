/**
 * Cloudflare Pages middleware — runs on every request.
 *
 * Purpose: 301 redirect the www. subdomain to the apex (canonical) domain.
 * This CANNOT be done in _redirects, because Cloudflare Pages _redirects
 * only matches URL paths, never hostnames. Without this, www.waythroughproject.com
 * serves a full duplicate of the site (Google: "Alternate page with proper
 * canonical tag" x146) and old www slugs 404.
 *
 * Defensive: any error falls through to normal handling so the site never breaks.
 * Path-level redirects remain in _redirects and still apply via next().
 */
export async function onRequest(context) {
  try {
    const url = new URL(context.request.url);
    if (url.hostname === "www.waythroughproject.com") {
      url.hostname = "waythroughproject.com";
      return Response.redirect(url.toString(), 301);
    }
  } catch (_e) {
    // fall through
  }
  return context.next();
}
