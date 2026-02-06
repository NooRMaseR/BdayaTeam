import { ReactNode } from "react";

export default function BodyM({ children }: { children: ReactNode }) {
    return (
        <main className='mt-20'>
            {children}
        </main>
    )
}
