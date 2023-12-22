'use client'

import React, { useState, useContext } from 'react';
import { useMutation } from '@tanstack/react-query'
import { useRouter } from 'next/navigation';
import { setCookie } from 'cookies-next';
import { isAxiosError } from 'axios';
import { AxiosRequestConfig, AxiosRequestHeaders } from "axios";
import { axInstance, login } from '@/app/utils/api';
import { IUser } from '@/app/interfaces/iuser.interface';
import { AuthContext } from '@/app/utils/auth';

// Don't ask me, this is from stackoverflow.
interface AdaptAxiosRequestConfig extends AxiosRequestConfig {
    headers: AxiosRequestHeaders
}

// TODO: another UI for already logged-in dudes.
const Form = () => {
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [errorMessage, setErrorMessage] = useState<string>('');

    // Context for JWT authentication.
    const { setAccessToken } = useContext(AuthContext);
    // For programmatically page navigation.
    const router = useRouter();

    const mutation = useMutation({
        mutationFn: (userInfo: IUser) => login(userInfo),
    });

    const onSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        mutation.mutate(
            { username, password },
            {
                onSuccess: (response) => {
                    const accessToken = response.data.access_token;
                    // Save token in context and cookie.
                    setAccessToken(accessToken);
                    setCookie("accessToken", accessToken, {
                        path: '/',
                        maxAge: 1440 * 60, // number of seconds in a day
                    })
                    // Modify the axios instance header to include the token afterwards.
                    axInstance.interceptors.request.use(
                        (config): AdaptAxiosRequestConfig => {
                            config.headers.Authorization = `Bearer ${accessToken}`
                            return config;
                        })

                    // Let's go home.
                    router.push('/');
                },
                onError: (err) => {
                    if (isAxiosError(err)) {
                        setErrorMessage(err.response?.data.detail);
                    }
                }
            }
        );
    };

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
                        onSubmit={onSubmit}
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
                                    onChange={(e) => setUsername(e.target.value)}
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
                                    required
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>

                        <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm text-red-500 text-sm">
                            {mutation.isError && <p>😔 {errorMessage}</p>}
                        </div>

                        <div>
                            <button
                                type="submit"
                                className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                            >
                                Login
                            </button>
                        </div>
                    </form>

                    <p className="mt-10 text-center text-sm text-gray-500">
                        Not a member?{' '}
                        <a href="/signup" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
                            Create new account
                        </a>
                    </p>
                </div>

            </div>
        </>
    )
}
export default Form;