import React from 'react';
import TechnicalWebSocket from './socket_component';

export default async function TechnicalLayout({children, params}: {children: React.ReactNode, params: Promise<{track: string}>}) {
    const { track } = await params;
    return (
        <>
            <TechnicalWebSocket track={track} />
            {children}
        </>
    );
}
