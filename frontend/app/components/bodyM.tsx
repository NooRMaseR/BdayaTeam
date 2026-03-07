import { ReactNode } from "react";

export default function BodyM({ children }: { children: ReactNode }) {
    return (
        <main className='my-20'>
            {children}
        </main>
    )
}
