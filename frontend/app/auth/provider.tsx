"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import {
    UserCredential,
    createUserWithEmailAndPassword,
    onAuthStateChanged,
    signInWithEmailAndPassword,
    signOut,
} from 'firebase/auth'
import axInstance from '@/app/api/config';
import { auth } from '@/app/auth/config';
import { Props } from '@/app/interfaces/iprops.interface';
import { IUser } from '@/app/interfaces/iuser.interface';

type AuthContextType = {
    user: IUser;
    loading: Boolean;
    signUp: (email: string, password: string) => Promise<UserCredential>;
    logIn: (email: string, password: string) => Promise<UserCredential>;
    logOut: () => Promise<void>;
}

// Create auth context. Then make auth context available across the app.
export const AuthContext = createContext<AuthContextType>({
    user: {
        email: null,
        uid: null,
    },
    loading: true,
    signUp: (email: string, password: string) => createUserWithEmailAndPassword(auth, email, password),
    logIn: (email: string, password: string) => signInWithEmailAndPassword(auth, email, password),
    logOut: async () => { }
});
export const useAuth = () => useContext(AuthContext);
// Create auth context provider.
export const AuthContextProvider = ({ children }: Props) => {
    const [user, setUser] = useState<IUser>({ email: null, uid: null });
    const [loading, setLoading] = useState<Boolean>(true);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (curUser) => {
            if (curUser) {
                const token = await curUser.getIdToken();
                setUser({
                    email: curUser.email,
                    uid: curUser.uid,
                    token: token,
                });
                // Include the token in HTTP headers.
                axInstance.interceptors.request.use(
                    (config) => {
                        config.headers['Authorization'] = `Bearer ${token}`;
                        return config;
                    },
                    (error) => {
                        return Promise.reject(error)
                    },
                )

            } else {
                setUser({
                    email: null,
                    uid: null,
                    token: null,
                });
            }
        });
        setLoading(false);
        return () => unsubscribe();
    }, []);

    const signUp = (email: string, password: string) => {
        return createUserWithEmailAndPassword(auth, email, password);
    };

    const logIn = async (email: string, password: string) => {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        // const token = await userCredential.user.getIdToken();
        // console.log(`This is cred ${token}`);
        return userCredential;
    }

    const logOut = async () => {
        setUser({ email: null, uid: null });
        return await signOut(auth);
    };

    return (
        <AuthContext.Provider value={{ user, loading, signUp, logIn, logOut }}>
            {loading ? null : children}
        </AuthContext.Provider>
    )
}
