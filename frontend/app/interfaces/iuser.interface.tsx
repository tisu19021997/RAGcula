export interface IUser {
    username: string;
    password: string;
}

export interface IUserSignin extends IUser {
    email: string;
}

export interface IUserWithEmailAndPassword {
    email: string;
    password: string;
}