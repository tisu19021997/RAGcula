// import Form from "@/app/signup/form";
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

import SignUpForm from "@/app/components/signup-form";

export default function signup() {
    return (
        <>
            <main className="m-0 min-h-screen bg-gradient-to-br from-primary-color to-blue-400 px-4">
                <SignUpForm />
            </main>
        </>
    )
}
