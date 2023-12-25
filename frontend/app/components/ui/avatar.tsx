'use client'

import { Fragment } from 'react'
import { IUser } from '@/app/interfaces/iuser.interface';
import Link from 'next/link';

const Avatar = (user: IUser) => {
    return user.email
        ? <Fragment>
            <span className="absolute -inset-1.5" />
            <span className="sr-only">Open user menu</span>

            <span className="text-gray-300 text-sm pr-2">
                👋 {user.email!.split("@")[0]}
            </span>
        </Fragment>
        : <Fragment>
            <span className="absolute -inset-1.5" />
            <span className="sr-only">Open user menu</span>
            <Link href="login">Login</Link>

        </Fragment>
}

export default Avatar;