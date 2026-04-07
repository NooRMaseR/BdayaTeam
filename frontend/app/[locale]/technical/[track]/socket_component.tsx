'use client';

import useWebSocket from 'react-use-websocket';
import { toast } from 'sonner';

export default function TechnicalWebSocket({track}: {track: string}) {
    useWebSocket(`${process.env.NEXT_PUBLIC_WEBSOCKET_URL}/technical/notify/${track}/`, {
        shouldReconnect: () => true,
        reconnectAttempts: 10,
        reconnectInterval: 3000,
        onMessage(event) {
            const payload = JSON.parse(event.data);
            toast.info(payload.message);
        },
    });

    return null;
}
