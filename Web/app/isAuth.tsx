"use client";
import {useAppSelector} from "@/store";
import {useEffect} from "react";
import {redirect} from "next/navigation";


export default function isAuth(Component: any) {
    return function IsAuth(props: any) {

        const isLogin = useAppSelector(
            state => state.auth.authState.isLogin
        )
        
        useEffect(() => {
            if (!isLogin) {
                return redirect("/login");
            }
        }, [isLogin]);


        if (!isLogin) {
            return null;
        }

        return <Component {...props} />;
    };
}