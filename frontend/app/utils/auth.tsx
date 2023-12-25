'use client'

import { createContext, useState } from 'react';
import { Props } from '@/app/interfaces/iprops.interface';

type AuthContextType = {
    accessToken: string | null;
    setAccessToken: (token: string | null) => void;
};

export const AuthContext = createContext<AuthContextType>({
    accessToken: null,
    setAccessToken: () => { },
});

export const AuthProvider = ({ children }: Props) => {
    const [accessToken, setAccessToken] = useState<string | null>(null);

    return (
        <AuthContext.Provider value={{ accessToken, setAccessToken }}>
            {children}
        </AuthContext.Provider>
    );
};
