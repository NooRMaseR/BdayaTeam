"use server";

import axios, { AxiosRequestConfig } from "axios";
import { cookies } from "next/headers";

type ApiResponse<T> = {
    success: boolean,
    data?: T,
    error?: any,
    status: number,
};

function parseCookie(cookie: string) {
    const splited = cookie.split(";").map((value) => value.trim());
    const [nameVal, ...attributes] = splited;
    const [name, ...valueParts] = nameVal.split('=');
    const value = valueParts.join('=');

    if (!name || !value) return null;

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

export default async function serverApi<T>(method: "GET" | "POST" | "PUT" | "DELETE" = "GET", url: string, data: any = null): Promise<ApiResponse<T>> {
    const cookies_data = await cookies();
    const authToken = cookies_data.get("auth_token");
    const csrfToken = cookies_data.get("csrftoken");
    
    const config: AxiosRequestConfig = {
        method: method,
        baseURL: `http://127.0.0.1:8000${url}`,
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken ? csrfToken.value : "",
            Authorization: authToken ? `Token ${authToken.value}` : "",
            Cookie: [
                authToken ? `${authToken.name}=${authToken.value}` : "",
                csrfToken ? `${csrfToken.name}=${csrfToken.value}` : ""
            ].filter(Boolean).join("; "),
        },
        withCredentials: true,
        data: data
    };

    try {
        const response = await axios<T>(config);
        const rawCookies: string[] = typeof response.headers?.getSetCookie === 'function' ? response.headers.getSetCookie() : [];

        if (rawCookies.length > 0) {
            rawCookies.forEach((cookieStr: string) => {
                const parsedCookie = parseCookie(cookieStr);

                if (parsedCookie) {
                    cookies_data.set(parsedCookie);
                }
            });
        }
        return {
            success: true,
            status: response.status,
            data: response.data
        };
    } catch (error: any) {
        console.error("Server API Error:", error?.response?.data || error.message);
        return {
            success: false,
            status: error?.response?.status,
            error: error?.response?.data
        };
    };
}
