import type { MetadataRoute } from 'next';
import { NextResponse } from 'next/server';
import { fetchTracks } from '../utils/api.server';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const role = searchParams.get('role');
    const track = searchParams.get('track');

    const baseManifest: MetadataRoute.Manifest = {
        name: 'Team Bdaya',
        short_name: 'Bdaya',
        description: 'A Place where you can build skills and get courses for free',
        start_url: '/',
        display: 'standalone',
        theme_color: "#193cb8",
        background_color: "#292929",
        icons: [
            {
                src: '/favicon-96x96.png',
                sizes: '96x96',
                type: 'image/png',
            },
            {
                src: "/web-app-manifest-192x192.png",
                sizes: "192x192",
                type: "image/png",
                purpose: "any"
            },
            {
                src: "/web-app-manifest-512x512.png",
                sizes: "512x512",
                type: "image/png",
                purpose: "any"
            }
        ],
        screenshots: [
            {
                src: "/screenshot-mobile.jpeg",
                sizes: "540x1200",
                type: "image/jpeg",
                form_factor: "narrow"
            },
            {
                src: "/screenshot-mobile-light.jpeg",
                sizes: "540x1200",
                type: "image/jpeg",
                form_factor: "narrow"
            },
            {
                src: "/Screenshot-dark.png",
                sizes: "931x1019",
                type: "image/png",
                form_factor: "wide"
            },
            {
                src: "/Screenshot-light.png",
                sizes: "931x1019",
                type: "image/png",
                form_factor: "wide"
            },
        ],
        shortcuts: []
    };

    switch (role) {
        case "organizer":
            baseManifest.shortcuts?.push(
                {
                    name: 'Organizer Home',
                    short_name: 'Home',
                    description: 'Home Page for Organizers',
                    url: '/organizer',
                },
                {
                    name: 'Site Settings',
                    short_name: 'Settings',
                    description: 'View and edit Site Settings',
                    url: '/organizer/settings',
                }
            );
            const {response, data} = await fetchTracks();
            if (response.status === 200) {
                data?.forEach(track => baseManifest.shortcuts?.push(
                    {
                        name: `${track.name} Members`,
                        short_name: track.name,
                        description: `manage ${track.name} members`,
                        url: `/organizer/${track.name}/members`,
                    }
                ))
            }
            break;
        
        case "technical":
            baseManifest.shortcuts?.push(
                {
                    name: 'Tasks',
                    short_name: 'Tasks',
                    url: `/technical/${track}/tasks`,
                },
                {
                    name: 'Members',
                    short_name: 'Members',
                    url: `/technical/${track}/members`,
                },
                {
                    name: 'Members Attendances',
                    short_name: 'Attendances',
                    url: `/technical/${track}/members-attendances`,
                },
            );
            break;

        case "member":
            baseManifest.shortcuts?.push(
                {
                    name: 'Waiting Tasks',
                    short_name: 'Tasks',
                    url: `/member/${track}/tasks`,
                },
                {
                    name: 'Profile',
                    short_name: 'Profile',
                    url: `/profile/${track}`,
                }
            );
        
        default:
            baseManifest.shortcuts?.push(
                {
                    name: "Login",
                    short_name: "Login",
                    url: "/login"
                },
                {
                    name: "Register",
                    short_name: "Register",
                    url: "/register"
                },
            )
            break;
    }
    return NextResponse.json(baseManifest);
}