import type { paths } from "@/app/generated/api_types";
import createClient from "openapi-fetch";

export const API = createClient<paths>({
    baseUrl: "http://localhost",
    credentials: "include"
});