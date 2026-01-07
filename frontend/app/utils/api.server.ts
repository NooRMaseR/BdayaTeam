import type { paths } from "@/app/generated/api_types";
import { fetchWithCookies } from "./api_utils";
import createClient from "openapi-fetch";

export const API = createClient<paths>({
    baseUrl: "http://localhost",
    fetch: fetchWithCookies,
});

