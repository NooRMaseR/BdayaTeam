'use server';

import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";
import { cookies } from "next/headers";
import { gql } from "graphql-tag";

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
    const auth_token = cookieStore.get("auth_token")?.value;

    const headers = new Headers(options?.headers);
    if (!headers.get("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    if (auth_token) {
        headers.set("Authorization", `Token ${auth_token}`);
    }

    const response = await fetch(url, {
        ...options,
        headers,
        credentials: "include",
    });


    const setCookieHeader = response.headers.getSetCookie();
    if (setCookieHeader && setCookieHeader.length > 0) {
        setCookieHeader.forEach((cookieStr) => {
            const parsed = parseCookie(cookieStr);
            if (parsed) {
                cookieStore.set(parsed.name, parsed.value, parsed);
            }
        });
    }

    return response;
};

export async function serverGraphQL<T>(query: string, variables: Record<string, any> = {}, mutate: boolean = false): Promise<T> {
    const cookieStore = await cookies();
    const authToken = cookieStore.get("auth_token");
    const csrfToken = cookieStore.get("csrftoken");

    const ap = new ApolloClient({
        link: new HttpLink({
            uri: "http://localhost/graphql/",
            headers: {
                "Content-Type": "application/json",
                Authorization: authToken ? `Token ${authToken.value}` : "",
                "X-CSRFToken": csrfToken?.value || ""
            },
            credentials: "include"
        }),
        cache: new InMemoryCache(),
    });

    const newQuery = gql`${query}`;

    const { data, error } = mutate ? await ap.mutate({ mutation: newQuery, variables }) : await ap.query({ query: newQuery, variables });

    if (error) {
        console.error(error);
        throw new Error(error.message);
    }
    return data as T;

}