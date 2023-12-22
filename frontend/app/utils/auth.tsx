'use client'

import { createContext, useState } from 'react';

type AuthContextType = {
    accessToken: string | null;
    setAccessToken: (token: string | null) => void;
};

export const AuthContext = createContext<AuthContextType>({
    accessToken: null,
    setAccessToken: () => { },
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [accessToken, setAccessToken] = useState<string | null>(null);

    return (
        <AuthContext.Provider value={{ accessToken, setAccessToken }}>
            {children}
        </AuthContext.Provider>
    );
};
