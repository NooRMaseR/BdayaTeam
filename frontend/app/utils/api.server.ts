import type { paths } from "@/app/generated/api_types";
import { fetchWithCookies } from "./api_utils";
import createClient from "openapi-fetch";

export const API = createClient<paths>({
    baseUrl: process.env.NEXT_PUBLIC_API_URL,
    fetch: fetchWithCookies,
});

