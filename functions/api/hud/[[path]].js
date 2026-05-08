/**
 * Cloudflare Pages Function — HUD API Proxy
 *
 * Proxies requests to the HUD User API (huduser.gov) to avoid CORS issues.
 * The API token is kept server-side so it's not exposed to clients.
 *
 * URL mapping:
 *   /api/hud/fmr/listStates       → https://www.huduser.gov/hudapi/public/fmr/listStates
 *   /api/hud/fmr/listCounties/CA  → https://www.huduser.gov/hudapi/public/fmr/listCounties/CA
 *   /api/hud/fmr/data/...         → https://www.huduser.gov/hudapi/public/fmr/data/...
 *   /api/hud/il/data/...          → https://www.huduser.gov/hudapi/public/il/data/...
 *   etc.
 */

const HUD_API_BASE = 'https://www.huduser.gov/hudapi/public';
const HUD_API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI2IiwianRpIjoiZDVkMDJjM2M5NDUyNzFkNjEzNjI5ZTk3NGRhMGEwODNjYmE1MWY3YmRlMDgzYTVjNzkwMzA2MDk5NTAyZTI1YWJjMWM5ZjdiNzU0MDU3NDMiLCJpYXQiOjE3NzQ4OTg5NTIuNTM1Mzk2LCJuYmYiOjE3NzQ4OTg5NTIuNTM1Mzk4LCJleHAiOjIwOTA1MTgxNTIuNTMxMjk3LCJzdWIiOiIxMjQxNjgiLCJzY29wZXMiOltdfQ.iUSBmLhvDlf7F6TWZ4341RAkd_T1OWnKH3cAdN7efBY5CB1X2yNbBDS3w34_uTgMUK2JJ_ieupojw-Z3to8W_A';

// CORS headers for browser requests
const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
};

export async function onRequest(context) {
    // Handle CORS preflight
    if (context.request.method === 'OPTIONS') {
        return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    // Only allow GET requests
    if (context.request.method !== 'GET') {
        return new Response(JSON.stringify({ error: 'Method not allowed' }), {
            status: 405,
            headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        });
    }

    // Extract the API path from the catch-all route parameter
    const pathSegments = context.params.path;
    const apiPath = '/' + (Array.isArray(pathSegments) ? pathSegments.join('/') : pathSegments);

    // Only allow /fmr/ and /il/ endpoints (prevent abuse)
    if (!apiPath.startsWith('/fmr/') && !apiPath.startsWith('/il/')) {
        return new Response(JSON.stringify({ error: 'Only /fmr/ and /il/ endpoints are supported' }), {
            status: 400,
            headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        });
    }

    try {
        const hudResponse = await fetch(HUD_API_BASE + apiPath, {
            headers: {
                'Authorization': 'Bearer ' + HUD_API_TOKEN,
                'User-Agent': 'WaythroughProject/1.0',
            },
        });

        const data = await hudResponse.text();

        return new Response(data, {
            status: hudResponse.status,
            headers: {
                ...CORS_HEADERS,
                'Content-Type': hudResponse.headers.get('Content-Type') || 'application/json',
                'Cache-Control': 'public, max-age=86400', // Cache for 24 hours
            },
        });
    } catch (err) {
        return new Response(JSON.stringify({ error: 'Failed to reach HUD API', details: err.message }), {
            status: 502,
            headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        });
    }
}
