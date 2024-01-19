"use client";

import NextLink from "next/link";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useAuth } from "@/app/auth/provider";
import { IUser } from "@/app/interfaces/iuser.interface";
import InlineError from "@/app/components/ui/inline-error";

const LoginForm = () => {
    const [data, setData] = useState<IUser>({
        email: "",
        password: ""
    });
    const [errorMsg, setErrorMsg] = useState<string | null>("")
    const { user, logIn } = useAuth();
    const router = useRouter();

    useEffect(() => {
        // If already logged in, go home bitch.
        if (user.uid) {
            router.back();
        }
    }, [user])


    const handleLogin = async (e: any) => {
        e.preventDefault();
        try {
            await logIn(data.email!, data.password!);
            // router.push('/');
            router.back();
        } catch (error: any) {
            setErrorMsg('😪 Invalid credentials. Please double-check and retry.');
        }
    };

    const { ...allData } = data;
    const canSubmit = [...Object.values(allData)].every(Boolean);

    return (
        <>
            <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
                <div className="sm:mx-auto sm:w-full sm:max-w-lg sm:min-w-full">
                    <img
                        className="mx-auto h-10 w-auto"
                        src="https://tailwindui.com/img/logos/mark.svg?color=indigo&shade=600"
                        alt="Your Company"
                    />
                    <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                        Login to your account
                    </h2>
                </div>

                <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                    <form
                        className="space-y-6"
                        onSubmit={handleLogin}
                    >

                        <div>
                            <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
                                Email
                            </label>
                            <div className="mt-2">
                                <input
                                    id="email"
                                    name="email"
                                    type="text"
                                    required
                                    onChange={(e: any) => {
                                        setData({
                                            ...data,
                                            email: e.target.value
                                        });
                                    }}
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium leading-6 text-gray-900">
                                Password
                            </label>
                            <div className="mt-2">
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="current-password"
                                    pattern=".{8,}"
                                    required
                                    onChange={(e: any) => {
                                        setData({
                                            ...data,
                                            password: e.target.value
                                        });
                                    }}
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                            {errorMsg ? <InlineError message={errorMsg} /> : null}
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={!canSubmit}
                                className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                            >
                                Login
                            </button>
                        </div>
                    </form>

                    <p className="mt-10 text-center text-sm text-gray-500">
                        Not a member?{' '}
                        <NextLink
                            href="/signup"
                            className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500"
                        >
                            Create new account
                        </NextLink>
                    </p>
                </div>

            </div>
        </>
    )
}

export default LoginForm;