/**
 * Base interface for User data containing common properties between
 * sign-in and existing users.
 */
export interface IUser {
    uid?: string | null; // Optional for existing users, required for sign-in.
    email: string | null;
    password?: string | null;
}