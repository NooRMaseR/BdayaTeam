"use client";

import Button from "@mui/material/Button";
import { useEffect, useReducer } from "react";
import { subscribeToPush } from "@/app/utils/notifications"; 

type NotificationState = {
  isSupported: boolean;
  isSubscribed: boolean;
  isLoading: boolean;
};

const initialState: NotificationState = {
  isSupported: false,
  isSubscribed: false,
  isLoading: false,
};

type Action = 
    { type: 'SET_SUPPORTED'; payload: boolean }
  | { type: 'SET_SUBSCRIBED'; payload: boolean }
  | { type: 'SET_LOADING'; payload: boolean };

function reducer(state: NotificationState, action: Action): NotificationState {
  switch (action.type) {
    case 'SET_SUPPORTED':
      return { ...state, isSupported: action.payload };
    case 'SET_SUBSCRIBED':
      return { ...state, isSubscribed: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    default:
      return state;
  }
}

export default function AskNotificationButton() {
    const [state, dispatch] = useReducer(reducer, initialState);
    
    useEffect(() => {
        async function checkSubscriptionState() {
            if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
                dispatch({ type: "SET_LOADING", payload: false });
                return;
            }
            
            dispatch({ type: "SET_SUPPORTED", payload: true });
            
            if (Notification.permission === "granted") {
                try {
                    // Check if we ACTUALLY have a subscription key generated
                    const registration = await navigator.serviceWorker.ready;
                    const existingSubscription = await registration.pushManager.getSubscription();
                    
                    if (existingSubscription) {
                        dispatch({ type: "SET_SUBSCRIBED", payload: true });
                    } else {
                        // ORPHANED STATE: Allowed, but the API request failed previously!
                        console.warn("Permission granted, but no subscription found. User needs to resync.");
                        dispatch({ type: "SET_SUBSCRIBED", payload: false });
                    }
                } catch (err) {
                    console.error("Error checking subscription state", err);
                    dispatch({ type: "SET_SUBSCRIBED", payload: false });
                }
            } else {
                dispatch({ type: "SET_SUBSCRIBED", payload: false });
            }
            dispatch({ type: "SET_LOADING", payload: false });
        }

        checkSubscriptionState();
    }, []);

    const handleSubscribe = async () => {
        dispatch({ type: "SET_LOADING", payload: true });
        try {
            await subscribeToPush();
            dispatch({ type: "SET_SUBSCRIBED", payload: true });
        } catch (error) {
            console.error("Failed to subscribe:", error);
            alert("Could not enable notifications. Please check your browser settings.");
        } finally {
            dispatch({ type: "SET_LOADING", payload: false });
        }
    };

    if (!state.isSupported) {
        return null;
    }

    if (state.isSubscribed) {
        return null;
    }

    return (
        <Button
            onClick={handleSubscribe} 
            loading={state.isLoading}
            variant="contained"
        >
            {state.isLoading ? "Checking..." : Notification.permission === "granted" ? "Repair Notifications" : "Enable Notifications"}
        </Button>
    );
}