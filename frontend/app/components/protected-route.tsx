"use client"

import { useRouter, usePathname } from "next/navigation";
import React, { useEffect, useState } from "react";
import { useAuth } from "@/app/auth/provider";
import { Props } from "@/app/interfaces/iprops.interface";

const ProtectedRoute = ({ children }: Props) => {
    const { user } = useAuth();
    const [loading, setLoading] = useState<Boolean>(false);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (!user.uid) {
            router.push('/login');
        } else {
            setLoading(false);
        }
    }, [user, pathname]);

    // TODO: Implement loading state.
    return loading ? <div></div> : <>{children}</>;
};

export default ProtectedRoute;