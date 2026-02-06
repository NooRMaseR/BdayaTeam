/* eslint-disable @typescript-eslint/no-explicit-any */
'use server';

import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";
import { cookies } from "next/headers";
import { gql } from "graphql-tag";


export async function getAuthCookies() {
    const cookieStore = await cookies();
    const access_token = cookieStore.get("access_token")?.value;
    const refresh_token = cookieStore.get("refresh_token")?.value;
    const csrfToken = cookieStore.get("csrftoken")?.value;

    return {
        "token": access_token,
        "refresh": refresh_token,
        "csrf": csrfToken
    }
}

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

export const fetchWithCookies: typeof fetch = async (url, options) => {
    const cookieStore = await cookies();
    const { token, csrf } = await getAuthCookies();

    const headers = new Headers(options?.headers);
    if (!headers.get("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    if (csrf) {
        headers.set("X-CSRFToken", csrf);
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
                cookieStore.set(parsed.name, parsed.value, parsed);
            }
        });
    }

    return response;
};

type GraphResponse<T> = {
    data: T;
    error?: any;
    success: boolean;
}

export async function serverGraphQL<T>(query: string, variables: Record<string, any> = {}, mutate: boolean = false, useForm: boolean = false): Promise<GraphResponse<T>> {
    const { token, csrf } = await getAuthCookies();

    const headers: HeadersInit = {
        Authorization: token ? `Bearer ${token}` : "",
        "X-CSRFToken": csrf || ""
    };

    if (!useForm) {
        headers["Content-Type"] = "application/json";
    }

    const ap = new ApolloClient({
        link: new HttpLink({
            uri: `${process.env.NEXT_PUBLIC_API_URL}/api/graphql/`,
            headers: headers,
            credentials: "include"
        }),
        cache: new InMemoryCache(),
    });

    const wrappedQuery = gql`${query}`;

    try {
        const { data } = mutate
            ? await ap.mutate({ mutation: wrappedQuery, variables })
            : await ap.query({ query: wrappedQuery, variables });

        return {
            data: data as T,
            success: true
        };
    } catch (error) {
        // console.error("GraphQL Error:", error);
        return {
            data: {} as T,
            error: error,
            success: false
        };
    }
}
