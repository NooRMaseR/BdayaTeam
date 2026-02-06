import createClient, { type MiddlewareCallbackParams, type Middleware } from "openapi-fetch";
import type { paths } from "@/app/generated/api_types";
import { getAuthCookies } from "./api_utils";

export const API = createClient<paths>({
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

        const { refresh } = await getAuthCookies();
        const refreshRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/token/refresh/`, {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ refresh: refresh })
        });

        if (refreshRes.ok) {
            options.request.headers.delete("Authorization");
            const data = await refreshRes.json();
            options.request.headers.set("Authorization", `Bearer ${data.access}`);
            const retryRequest = new Request(options.request, {
                ...options,
                headers: options.request.headers
            });

            return await fetch(retryRequest);
        }
    }
    return options.response;
}


const middleware: Middleware = {
    onResponse: refreshToken,
    onRequest: async (options) => {
        const { token } = await getAuthCookies();
        options.request.headers.set("Authorization", `Bearer ${token}`);
    },
}

// eslint-disable-next-line react-hooks/rules-of-hooks
API.use(middleware);