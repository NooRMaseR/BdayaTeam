"use client";

import { useState, useEffect } from "react";
import { subscribeToPush } from "@/app/utils/notifications"; 

export default function AskNotificationButton() {
    const [isSupported, setIsSupported] = useState(false);
    const [isSubscribed, setIsSubscribed] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        async function checkSubscriptionState() {
            if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
                setIsLoading(false);
                return; // Not supported
            }

            setIsSupported(true);

            // 1. Check if the browser allows notifications
            if (Notification.permission === "granted") {
                try {
                    // 2. THE FIX: Check if we ACTUALLY have a subscription key generated
                    const registration = await navigator.serviceWorker.ready;
                    const existingSubscription = await registration.pushManager.getSubscription();

                    if (existingSubscription) {
                        // Perfect state: Allowed AND keys exist
                        setIsSubscribed(true);
                    } else {
                        // ORPHANED STATE: Allowed, but the API request failed previously!
                        // We keep isSubscribed as false so the button stays visible.
                        console.warn("Permission granted, but no subscription found. User needs to resync.");
                        setIsSubscribed(false);
                    }
                } catch (err) {
                    console.error("Error checking subscription state", err);
                    setIsSubscribed(false);
                }
            } else {
                setIsSubscribed(false);
            }
            setIsLoading(false);
        }

        checkSubscriptionState();
    }, []);

    const handleSubscribe = async () => {
        setIsLoading(true);
        try {
            await subscribeToPush();
            setIsSubscribed(true);
        } catch (error) {
            console.error("Failed to subscribe:", error);
            alert("Could not enable notifications. Please check your browser settings.");
        } finally {
            setIsLoading(false);
        }
    };

    if (!isSupported) {
        return null;
    }

    if (isSubscribed) {
        return null;
    }

    return (
        <button 
            onClick={handleSubscribe} 
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
            {isLoading ? "Checking..." : Notification.permission === "granted" ? "Repair Notifications" : "Enable Notifications"}
        </button>
    );
}