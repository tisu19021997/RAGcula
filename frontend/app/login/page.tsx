// import Form from "@/app/login/form";
// import { ProvidesTheQueryClient } from '@/app/utils/query-client';

// export default function Home() {
//     return (
//         <ProvidesTheQueryClient>
//             <main className="flex min-h-screen flex-col items-center gap-10 p-24 background-gradient">
//                 <Form />
//             </main>
//         </ProvidesTheQueryClient>
//     );
// }

import LoginForm from "@/app/components/login-form";

export default function Home() {
    return (
        <>
            <main className="m-0 bg-gradient-to-br from-primary-color to-blue-400 px-4">
                <LoginForm />
            </main>
        </>
    )
}