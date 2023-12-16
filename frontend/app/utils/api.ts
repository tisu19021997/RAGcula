import axios from 'axios'
import { IUserLogin } from '@/app/interfaces/iuser.interface'

export const axInstance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API,
    timeout: 1000,
})

export const createUser = async (body: IUserLogin) => {
    const response = await axInstance.post('/users', body);
    console.log(response.data);
    return response.data
}
