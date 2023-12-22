"use client";

import NextLink from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { useAuth } from "@/app/auth/provider";
import { IUserWithEmailAndPassword } from "@/app/interfaces/iuser.interface";

const LoginForm = () => {
    const [data, setData] = useState<IUserWithEmailAndPassword>({
        email: "",
        password: ""
    });
    const { user, logIn } = useAuth();
    const router = useRouter();

    useEffect(() => {
        console.log('Logged in as', user.email);
        // If already logged in, go home bitch.
        if (user.uid) {
            router.push('/');
            return
        }
    }, [user])


    const handleLogin = async (e: any) => {
        e.preventDefault();
        try {
            await logIn(data.email, data.password);
            router.push('/');
        } catch (error: any) {
            // TODO: handle this error.
            console.log(error.message);
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
                            <label htmlFor="username" className="block text-sm font-medium leading-6 text-gray-900">
                                Username
                            </label>
                            <div className="mt-2">
                                <input
                                    id="username"
                                    name="username"
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