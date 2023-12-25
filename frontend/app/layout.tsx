import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthContextProvider } from "@/app/auth/provider";
import { Props } from "@/app/interfaces/iprops.interface";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TalkingResume",
};

export default function RootLayout({ children }: Props) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthContextProvider>{children}</AuthContextProvider>
      </body>
    </html>
  );
}
