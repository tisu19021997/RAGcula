/**
 * Base interface for uploaded document.
 */
export interface IDocumentGet {
    id?: string | null; // Optional for existing users, required for sign-in.
    s3_path: string;
    s3_url?: string;
    is_active: boolean;
    description: string;
    question: string;
    user_id: string;
}