'use client'
// pages/login.js
import React, {useState, useEffect} from 'react';
import apiClient from '@/api/apiClient';
import {useAppSelector} from "@/store";
import {setAuthState, LLMJwtPayload} from "@/store/authSlices";
import {jwtDecode} from 'jwt-decode';
import {store} from "@/store";
import {useRouter} from 'next/navigation';


interface LoginFormData {
    username: string;
    password: string;
}


const LoginPage = () => {

    const [formData, setFormData] = useState<LoginFormData>({
        username: '',
        password: '',
    });

    const router = useRouter()

    const isLogin = useAppSelector((state) => state.auth.authState?.isLogin);

    useEffect(() => {
        if (isLogin) {
            router.push("/chat")
        }
    }, [isLogin, router]);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        // Here, you can add your logic to authenticate the user,
        // For example, you can send a request to your backend API
        try {
            const response = await apiClient.post('/authenticate/api/token/', formData);
            // if the request is successful, you can redirect the user to another page
            // otherwise you can show an error message
            if (response.status === 200) {
                // Redirect the user to another page
                // decode jwt token
                const decodedToken = jwtDecode<LLMJwtPayload>(response.data.access)
                localStorage.setItem(
                    "access", response.data.access)
                localStorage.setItem(
                    "refresh", response.data.refresh
                )
                // dispatch the action to update the auth.authSate
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
                router.push('/chat');
            } else {
                // Show an error message
                alert('Invalid credentials');
            }
        } catch (error) {
            localStorage.removeItem("access")
            localStorage.removeItem("refresh")
            console.error('Error:', error);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const {name, value} = e.target;
        setFormData((prevFormData) => ({...prevFormData, [name]: value}));
    };

    return (
        <div className="flex justify-center items-center h-screen">
            <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 flex flex-col">
                <div className="mb-4">
                    <h1 className="text-2xl font-bold">Login</h1>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label
                            className="block text-gray-700 font-bold mb-2"
                            htmlFor="email"
                        >
                            Email
                        </label>
                        <input
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            id="email"
                            type="email"
                            name="username"
                            placeholder="Enter your email"
                            value={formData.username}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <div className="mb-6">
                        <label
                            className="block text-gray-700 font-bold mb-2"
                            htmlFor="password"
                        >
                            Password
                        </label>
                        <input
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                            id="password"
                            type="password"
                            name="password"
                            placeholder="Enter your password"
                            value={formData.password}
                            onChange={handleInputChange}
                            required
                        />
                    </div>
                    <div className="flex items-center justify-between">
                        <button
                            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                            type="submit"
                        >
                            Login
                        </button>
                        {/*<a*/}
                        {/*    className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800"*/}
                        {/*    href="#"*/}
                        {/*>*/}
                        {/*    Forgot Password?*/}
                        {/*</a>*/}
                    </div>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;