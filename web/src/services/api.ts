const API_BASE = import.meta.env.PROD
    ? "https://api.pulse.kwako.nl"
    : "http://localhost:3001";
export async function apiFetch(path: string, opts: RequestInit = {}) {
    // Start with any headers passed in opts
    const headers = new Headers(opts.headers || {});

    // Add Authorization header with Bearer token if available
    const accessToken = localStorage.getItem("access_token");
    if (accessToken) {
        headers.set("Authorization", `Bearer ${accessToken}`);
    }

    // If body is an object (and not FormData), JSON stringify it
    if (
        opts.body &&
        typeof opts.body === "object" &&
        !(opts.body instanceof FormData)
    ) {
        headers.set("Content-Type", "application/json");
        opts.body = JSON.stringify(opts.body);
    }

    // Merge opts with headers and credentials
    const fetchOptions: RequestInit = {
        ...opts, // keep all other opts (method, body, etc.)
        headers, // override headers with our normalized Headers object
        credentials: "include", // always include cookies
    };

    const normalized = path.startsWith("/") ? path : `/${path}`;
    const url = `${API_BASE}${normalized}`;

    const res = await fetch(url, fetchOptions);
    return res;
}

export default { apiFetch };
