import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ChakraProvider } from '@chakra-ui/react';
import { AntdRegistry } from '@ant-design/nextjs-registry';
import { AuthContextProvider } from "@/app/auth/provider";
import { Props } from "@/app/interfaces/iprops.interface";
import NavBar from "./components/ui/navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TalkingResume",
};

export default function RootLayout({ children }: Props) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AntdRegistry>
          <ChakraProvider>
            <AuthContextProvider>
              {/* <NavBar /> */}
              {children}
            </AuthContextProvider>
          </ChakraProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}
