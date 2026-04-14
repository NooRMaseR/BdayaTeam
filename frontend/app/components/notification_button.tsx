"use client";

import Button from "@mui/material/Button";
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
                return;
            }

            setIsSupported(true);

            if (Notification.permission === "granted") {
                try {
                    // Check if we ACTUALLY have a subscription key generated
                    const registration = await navigator.serviceWorker.ready;
                    const existingSubscription = await registration.pushManager.getSubscription();

                    if (existingSubscription) {
                        setIsSubscribed(true);
                    } else {
                        // ORPHANED STATE: Allowed, but the API request failed previously!
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
        <Button
            onClick={handleSubscribe} 
            loading={isLoading}
            variant="contained"
        >
            {isLoading ? "Checking..." : Notification.permission === "granted" ? "Repair Notifications" : "Enable Notifications"}
        </Button>
    );
}