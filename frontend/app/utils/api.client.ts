import createClient, { type Middleware } from "openapi-fetch";
import type { paths } from "@/app/generated/api_types";
import { getAuthCookies } from "./api_utils";

export const API = createClient<paths>({
    baseUrl: process.env.NEXT_PUBLIC_API_URL,
    credentials: "include"
});

const middleware: Middleware = {
    onRequest: async (options) => {
        const { token, csrf } = await getAuthCookies();
        options.request.headers.set("Authorization", `Token ${token}`);
        options.request.headers.set("X-CSRFToken", csrf || '');
    },
}

// eslint-disable-next-line react-hooks/rules-of-hooks
API.use(middleware);