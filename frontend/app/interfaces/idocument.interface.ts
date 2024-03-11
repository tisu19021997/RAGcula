/**
 * Base interface for uploaded document.
 */
export interface IDocumentGet {
    id?: string | null; // Optional for existing users, required for sign-in.
    display_name: string;
    path: string;
    is_active: boolean;
    description: string;
    question: string;
    user_id: string;
    llamaindex_ref_doc_ids: string;
}