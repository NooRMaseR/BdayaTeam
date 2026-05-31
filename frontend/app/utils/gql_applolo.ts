/* eslint-disable @typescript-eslint/no-explicit-any */
'use server';

import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";
import { cookies } from "next/headers";
import { gql } from "graphql-tag";
import type { SettingsSiteImageQuery } from "../generated/graphql";
import { GET_SITE_IMAGE_SETTINGS } from "./graphql_helpers";

export async function getAuthCookies() {
    const cookieStore = await cookies();
    const access_token = cookieStore.get("access_token")?.value;
    const refresh_token = cookieStore.get("refresh_token")?.value;
    const csrfToken = cookieStore.get("csrftoken")?.value;
    const locale = cookieStore.get("NEXT_LOCALE")?.value;

    return {
        token: access_token,
        refresh: refresh_token,
        csrf: csrfToken,
        locale
    }
}

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
            uri: `${process.env.NEXT_API_URL}/api/graphql/`,
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
        return {
            data: {} as T,
            error: error,
            success: false
        };
    }
}
export async function fetchSiteImage() {
    return await serverGraphQL<SettingsSiteImageQuery>(GET_SITE_IMAGE_SETTINGS);
}
