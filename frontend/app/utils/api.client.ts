import createClient, { type MiddlewareCallbackParams, type Middleware } from "openapi-fetch";
import type { paths } from "@/app/generated/api_types";
import { getAuthCookies } from "./api_utils";
import type { UserAuth } from "./store";

const API = createClient<paths>({
    baseUrl: process.env.NEXT_PUBLIC_API_URL,
    credentials: "include"
});

export async function refreshToken(options: MiddlewareCallbackParams & {
    response: Response;
}) {
    if (options.response.status === 401) {
        if (options.request.url.includes("/api/token/refresh/")) {
            return options.response;
        };

        const { refresh, csrf } = await getAuthCookies();
        const refreshRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/token/refresh/`, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf ?? ''
            },
            body: JSON.stringify({ refresh }),
        });

        if (refreshRes.ok) {
            options.request.headers.delete("Authorization");
            const newCookies = refreshRes.headers.getSetCookie();
            let cookies = options.request.headers.get("Cookie") || "";
            let newAccessToken: string | null = null;

            newCookies.forEach(cookie => {
                const [keyValue] = cookie.split(';');
                const [key, value] = keyValue.split('=');

                if (key.trim() === 'access_token') {
                    newAccessToken = value.trim();
                }

                // 2. Safely replace the old token in the string, or append it
                const regex = new RegExp(`(?:^|;\\s*)${key}=[^;]*`);
                if (regex.test(cookies)) {
                    cookies = cookies.replace(regex, `; ${key}=${value}`);
                } else {
                    cookies += (cookies ? `; ` : "") + `${key}=${value}`;
                }
            });

            // Clean up any leading semicolons that might have formed
            cookies = cookies.replace(/^;\s*/, '');
            const retryRequest = new Request(options.request, {
                ...options,
                headers: options.request.headers
            });

            if (cookies) {
                retryRequest.headers.set("Cookie", cookies);
            }

            if (newAccessToken) {
                retryRequest.headers.set("Authorization", `Bearer ${newAccessToken}`);
            }

            return await fetch(retryRequest);
        }
    }
    return options.response;
}


const middleware: Middleware = {
    onResponse: refreshToken,
    onRequest: async (options) => {
        const { csrf } = await getAuthCookies();

        if (csrf)
            options.request.headers.set("X-CSRFToken", csrf);
        return options.request;
    },
}

// eslint-disable-next-line react-hooks/rules-of-hooks
API.use(middleware);


export function getHomeUrl(user: UserAuth['user']): string {
    return user?.role === "member" || user?.role === 'technical' ? `/${user?.role}/${user?.track?.name}` : `/${user?.role}`;
}

export function formatTime(totalSeconds: number) {
    const minutes = Math.floor(totalSeconds / 60);
    const hours = Math.floor((totalSeconds / 60) / 60);

    if (hours >= 1) return { duration: hours, unit: "hour" };
    else if (minutes >= 1) return { duration: minutes, unit: "minutes" };
    return { duration: Math.floor(totalSeconds % 60), unit: "seconds" };
};

export default API;