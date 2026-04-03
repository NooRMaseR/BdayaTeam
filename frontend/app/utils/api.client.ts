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

export function formatTime(totalSeconds: number){
    const minutes = Math.floor(totalSeconds / 60);
    const hours = Math.floor((totalSeconds / 60) / 60);

    if (hours >= 1) return { duration: hours, unit: "hour" };
    else if (minutes >= 1) return { duration: minutes, unit: "minutes" };
    return { duration: Math.floor(totalSeconds % 60), unit: "seconds" };
};

export default API;