import { apiFetch } from "./api";

interface TokenResponse {
    refresh_token: string;
    access_token: string;
}

interface ValidateResponse {
    active: boolean;
    payload: {
        sub: string;
        exp: number;
    };
}

/**
 * Save tokens to HTTP-only cookies
 * Note: These should be set by the server via Set-Cookie headers
 * This function stores them in document.cookie for client-side reference if needed
 */
function saveTokensToStorage(tokens: TokenResponse) {
    // Store tokens - the server should handle HTTP-only cookies via Set-Cookie headers
    // This is for client-side reference
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
}

export async function login(email: string, password: string): Promise<void> {
    const res = await apiFetch("/auth/login", {
        method: "POST",
        body: { email, password } as any,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error?.detail?.[0]?.msg || "Login failed");
    }

    const data = (await res.json()) as TokenResponse;

    // Validate we received both tokens
    if (!data.access_token || !data.refresh_token) {
        throw new Error("Login failed: missing tokens in response");
    }

    // Save tokens (server should set HTTP-only cookies via Set-Cookie headers)
    saveTokensToStorage(data);
}

export async function register(email: string, password: string) {
    return await apiFetch("/auth/register", {
        method: "POST",
        body: { email, password } as any,
    });
}

export async function logout() {
    return await apiFetch("/auth/logout", {
        method: "POST",
    });
}

export async function isAuthenticated(): Promise<boolean> {
    try {
        const res = await apiFetch("/auth/validate", { method: "GET" });

        if (!res.ok) {
            return false;
        }

        const data = (await res.json()) as ValidateResponse;
        return data.active === true;
    } catch (err) {
        return false;
    }
}

export default { login, register, logout, isAuthenticated };
