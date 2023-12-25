"use client"

import { Fragment, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/auth/provider";
import LoginForm from "@/app/components/login-form";


const Home = () => {
    const router = useRouter();
    const { user } = useAuth();

    useEffect(() => {
        // If already logged in, go home bitch.
        if (user.uid) {
            router.push('/');
        }
    }, [user])

    return (
        <Fragment>
            <main className="m-0 bg-gradient-to-br from-primary-color to-blue-400 px-4">
                {user.uid == null ? <LoginForm /> : null}
            </main>
        </Fragment>
    )
}

export default Home;