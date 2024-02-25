import type {Metadata} from "next";
import {Inter} from "next/font/google";
import "./css/globals.css";
import Head from 'next/head';


const inter = Inter({subsets: ["latin"]});

export const metadata: Metadata = {
    title: "LLM Assistant",
    description: "Enjoy big data time",
};

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
        <Head>
            {/* Standard favicon */}
            <link rel="icon" href="/assets/favicon.ico"/>

            {/* For example, adding a 32x32 .png favicon */}
            <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png"/>

            {/* Apple Touch Icon */}
            <link rel="apple-touch-icon" sizes="76x76" href="/assets/apple-touch-icon.png"/>

            {/* Web App Manifest */}
            <link rel="manifest" href="/assets/site.webmanifest"/>
        </Head>
        <body className={inter.className}>{children}</body>
        </html>
    );
}
