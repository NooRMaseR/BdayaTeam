import type { GetAllSettingsQuery } from "@/app/generated/graphql";
import { GET_ALL_SETTINGS } from "@/app/utils/graphql_helpers";
import { serverGraphQL } from "@/app/utils/api_utils";
import SettingsClient from "./client_page";

export default async function SettingsPage() {
    const res = await serverGraphQL<GetAllSettingsQuery>(GET_ALL_SETTINGS);
    if (res.success) {
        const settings = {
            is_register_enabled: res.data.allSettings?.isRegisterEnabled,
            organizer_can_edit: res.data.allSettings?.organizerCanEdit,
            site_image: res.data.allSettings?.siteImage,
            hero_image: res.data.allSettings?.heroImage,
        };
        return <SettingsClient recivedSettings={settings} />
    }
}
