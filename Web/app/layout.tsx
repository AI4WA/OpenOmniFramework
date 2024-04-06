'use client'
import React, {useEffect} from "react";
import {useRouter, usePathname} from "next/navigation"; // Import useRouter
import {Inter} from "next/font/google";
import "./globals.css";
import {refreshAccessToken} from "@/cloud/apiClient"
import dynamic from "next/dynamic";
import {setAuthState, logout, LLMJwtPayload} from "@/store/authSlices";
import {store} from "@/store";
import apolloClient from "@/cloud/graphqlClient"
import {jwtDecode} from 'jwt-decode';
import {ApolloProvider} from '@apollo/client';
import {PUBLIC_URLS} from "@/utils/constants";
import {ThemeProvider} from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from '@/theme';

const ReduxProvider = dynamic(() => import("@/store/redux-provider"), {
    ssr: false
});


const inter = Inter({subsets: ["latin"]});


export default function RootLayout({children,}: Readonly<{ children: React.ReactNode; }>) {
    const router = useRouter(); // Use the useRouter hook
    const pathname = usePathname()

    // do auth stuff, check access token here, if not, redirect to log in, otherwise to /
    useEffect(() => {
        const accessToken = localStorage.getItem("access")
        const refreshToken = localStorage.getItem("refresh")
        if (!accessToken || !refreshToken) {
            store.dispatch(
                logout()
            )
            // TODO: control the not isAuth page should stay there
            if (!PUBLIC_URLS.includes(pathname)) {
                router.push('/login')
            }
            localStorage.removeItem("access")
            localStorage.removeItem("refresh")
        } else {
            // set redux
            const decodedToken = jwtDecode<LLMJwtPayload>(accessToken)
            store.dispatch(
                setAuthState(
                    {
                        username: decodedToken?.username,
                        userId: decodedToken?.user_id,
                        firstName: decodedToken?.first_name,
                        lastName: decodedToken?.last_name,
                        orgName: decodedToken?.org_name,
                        orgId: decodedToken?.org_id,
                        isLogin: true
                    }
                )
            )
            if (pathname === '/login') {
                router.push('/dashboard')
            }
        }
    }, [router, pathname]);

    // do auth stuff here, refresh token
    useEffect(() => {
        // if this page is a login page, then do not do this
        // if it has the access token, then we should do this unless it is in /login page
        const access = localStorage.getItem("access")

        if (access && pathname !== "/login") {
            // Set up the interval
            const intervalId = setInterval(async () => {
                const result = await refreshAccessToken(); // Call your API fetching function here
                if (result === null) {
                    router.push("/login")
                }
            }, 60000); // 5000ms = 5 seconds

            // Clear the interval when the component unmounts
            return () => clearInterval(intervalId);
        }
    }, [pathname, router]);

    return (
        <html lang="en">
        <head>
            <title>WA Data & LLM Platform</title>
            <meta name="description" content="WA Data & LLM Platform"/>
            {/* Standard favicon */}
            <link rel="icon" href="/assets/favicon.ico"/>
            {/* For example, adding a 32x32 .png favicon */}
            <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32x32.png"/>

            {/* Apple Touch Icon */}
            <link rel="apple-touch-icon" sizes="76x76" href="/assets/apple-touch-icon.png"/>

        </head>
        <body className={inter.className}>
        <ThemeProvider theme={theme}>
            {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
            <CssBaseline/>
            <ApolloProvider client={apolloClient}>
                <ReduxProvider>
                    {children}
                </ReduxProvider>
            </ApolloProvider>
        </ThemeProvider>
        </body>
        </html>
    );
}
