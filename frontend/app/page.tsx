import Header from "@/app/components/header";
import NavBar from "@/app/components/ui/navbar";
import ChatSection from "@/app/components/chat-section";
import ProtectedRoute from "./components/protected-route";

export default function Home() {
  return (
    <ProtectedRoute>
      <main>
        <NavBar />
        <div className="flex min-h-screen flex-col items-center gap-10 p-24 background-gradient">
          {/* <Header /> */}
          <ChatSection />
        </div>
      </main>
    </ProtectedRoute>
  );
}
