import axios from 'axios'
import { IUser } from '@/app/interfaces/iuser.interface'
import axInstance from '@/app/api/config';

export const createUser = async (userInfo: IUser) => {
    const response = await axInstance.post('/users', userInfo);
    return response.data
}

export const login = async (userInfo: IUser) => {
    const response = await axInstance.post(
        '/users/token',
        userInfo,
        {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        }
    );
    return response;
}
