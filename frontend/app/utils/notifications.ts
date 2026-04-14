import API from "./api.client";

function urlBase64ToUint8Array(base64String: string) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

export async function subscribeToPush() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn("Push notifications are not supported by your browser.");
        return;
    };

    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
        throw new Error("Notification permission was denied.");
    }

    const registration = await navigator.serviceWorker.getRegistration();
    if (!registration) {
        throw new Error("No Service Worker found. Are you running in dev mode?");
    }

    const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY!)
    });

    const subJSON = subscription.toJSON();

    if (subJSON.endpoint && subJSON.keys) {
        await API.POST("/api/notifications/subscribe/", {
            body: {
                endpoint: subJSON.endpoint,
                auth: subJSON.keys.auth,
                p256dh: subJSON.keys.p256dh
            }
        });
    }
}