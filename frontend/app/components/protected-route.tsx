"use client"

import { useAuth } from "@/app/auth/provider";
import { useRouter, usePathname } from "next/navigation";
import React, { useEffect } from "react";

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const router = useRouter();
    const pathname = usePathname();
    const { user } = useAuth();

    useEffect(() => {
        if (!user.uid) {
            router.push('/login');
        }
    }, [pathname, user]);
    return <div>{user ? children : null}</div>;
};

export default ProtectedRoute;