/* eslint-disable @typescript-eslint/no-explicit-any */
'use server';

import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";
import type { SettingsSiteImageQuery } from "../generated/graphql";
import { SetContextLink } from "@apollo/client/link/context";
import { GET_SITE_IMAGE_SETTINGS } from "./graphql_helpers";
import { cookies } from "next/headers";
import { gql } from "graphql-tag";

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

const httpLink = new HttpLink({ uri: `${process.env.NEXT_API_URL}/api/graphql/` });

const authLink = new SetContextLink(async (prevContext) => {
    const { token, csrf } = await getAuthCookies();

    return {
        headers: {
            ...prevContext.headers,
            Authorization: token ? `Bearer ${token}` : "",
            "X-CSRFToken": csrf || ""
        }
    };
});

const client = new ApolloClient({
    link: authLink.concat(httpLink),
    cache: new InMemoryCache(),
});

export async function serverGraphQL<T>(query: string, variables: Record<string, any> = {}, mutate: boolean = false): Promise<GraphResponse<T>> {

    const wrappedQuery = gql`${query}`;

    try {
        const { data } = mutate
            ? await client.mutate({ mutation: wrappedQuery, variables })
            : await client.query({ query: wrappedQuery, variables });
        
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
