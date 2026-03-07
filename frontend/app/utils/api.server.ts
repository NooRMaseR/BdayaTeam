import { refreshToken } from "./api.client";
import { fetchWithCookies } from "./api_utils";
import type { paths } from "@/app/generated/api_types";
import createClient, { type Middleware } from "openapi-fetch";

const API = createClient<paths>({
    baseUrl: process.env.NEXT_PUBLIC_API_URL,
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