import ProtectedRoute from "@/app/components/protected-route";
import LoginForm from "@/app/components/login-form";

export default function Home() {
    return (
        <>
            <main className="m-0 bg-gradient-to-br from-primary-color to-blue-400 px-4">
                <ProtectedRoute>
                    <LoginForm />
                </ProtectedRoute>
            </main>
        </>
    )
}