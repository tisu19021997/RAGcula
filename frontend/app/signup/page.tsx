import Form from "@/app/signup/form";
import { ProvidesTheQueryClient } from '@/app/utils/query-client';

export default function Home() {
    return (
        <ProvidesTheQueryClient>
            <main className="flex min-h-screen flex-col items-center gap-10 p-24 background-gradient">
                <Form />
            </main>
        </ProvidesTheQueryClient>
    );
}