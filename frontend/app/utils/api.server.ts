import createClient, { type Middleware } from "openapi-fetch";
import type { paths } from "@/app/generated/api_types";
import { getAuthCookies } from "./gql_applolo";
import { refreshToken } from "./api.client";
import { cookies } from "next/headers";

function parseCookie(cookie: string) {
    const splited = cookie.split(";").map((value) => value.trim());
    const [nameVal, ...attributes] = splited;
    const [name, ...valueParts] = nameVal.split('=');
    const value = valueParts.join('=');

    if (!name || !value) return null;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cookieOptions: any = {
        name: name,
        value: value,
        path: '/',
    };
    attributes.forEach(attr => {
        const lowerAttr = attr.toLowerCase();

        if (lowerAttr === 'httponly') {
            cookieOptions.httpOnly = true;
        } else if (lowerAttr === 'secure') {
            cookieOptions.secure = true;
        } else if (lowerAttr.startsWith('samesite=')) {
            const sameSiteVal = attr.split('=')[1].toLowerCase();
            if (['lax', 'strict', 'none'].includes(sameSiteVal)) {
                cookieOptions.sameSite = sameSiteVal as 'lax' | 'strict' | 'none';
            }
        } else if (lowerAttr.startsWith('max-age=')) {
            cookieOptions.maxAge = parseInt(attr.split('=')[1]);
        } else if (lowerAttr.startsWith('expires=')) {
            const dateStr = attr.split('=')[1];
            cookieOptions.expires = new Date(dateStr).getTime();
        } else if (lowerAttr.startsWith('path=')) {
            cookieOptions.path = attr.split('=')[1];
        }
    });
    return cookieOptions;
}

async function fetchWithCookies(url: string | URL | Request, options?: RequestInit): Promise<Response> {
    const cookieStore = await cookies();
    const { token, csrf, locale } = await getAuthCookies();

    const headers = new Headers(options?.headers);
    if (!headers.get("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    const cookieString = cookieStore.getAll().map(c => `${c.name}=${c.value}`).join('; ');
    if (cookieString) {
        headers.set("Cookie", cookieString);
    }

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    if (csrf) {
        headers.set("X-CSRFToken", csrf);
    }

    if (locale) {
        headers.set("Accept-Language", locale);
    }

    const response = await fetch(url, {
        ...options,
        headers,
        credentials: "include",
    });

    const setCookieHeaders = response.headers.getSetCookie();
    if (setCookieHeaders && setCookieHeaders.length > 0) {
        setCookieHeaders.forEach((cookieStr) => {
            const parsed = parseCookie(cookieStr);
            if (parsed) {
                try {
                    cookieStore.set(parsed.name, parsed.value, parsed);
                } catch { }
            }
        });
    }

    return response;
};

const API = createClient<paths>({
    baseUrl: process.env.NEXT_API_URL,
    fetch: fetchWithCookies,
});

const middleware: Middleware = {
    onResponse: refreshToken
}

// eslint-disable-next-line react-hooks/rules-of-hooks
API.use(middleware);


export async function fetchTracks() {
    return await API.GET('/api/tracks/', { next: { revalidate: 300, tags: ['tracks'] } });
}

export default API;