import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ChakraProvider } from "@chakra-ui/react";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import { Props } from "@/app/interfaces/iprops.interface";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "RAGcula",
};

export default function RootLayout({ children }: Props) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AntdRegistry>
          <ChakraProvider>{children}</ChakraProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}
