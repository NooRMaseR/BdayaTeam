import type { paths } from "@/app/generated/api_types";
import { fetchWithCookies } from "./api_utils";
import { BASE_API_URL } from "./api.client";
import createClient from "openapi-fetch";

export const API = createClient<paths>({
    baseUrl: BASE_API_URL,
    fetch: fetchWithCookies,
});

