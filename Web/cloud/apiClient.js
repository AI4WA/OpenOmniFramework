'use client';
import axios from 'axios';

const BASEURL = process.env.NEXT_PUBLIC_API_DOMIAN;

const apiClient = axios.create({
    baseURL: BASEURL
});

const getAccessToken = async () => {
    // Implement your logic to get the access token from storage (e.g., localStorage or cookies)

    return localStorage.getItem('access');
};

const getRefreshToken = async () => {
    // Implement your logic to get the refresh token from storage

    return localStorage.getItem('refresh');
};


const refreshAccessToken = async () => {
    try {
        const refreshToken = await getRefreshToken();
        // Call your refresh token API endpoint with the refresh token
        const response = await axios.post(`${BASEURL}/authenticate/api/token/refresh/`, {
            refresh: refreshToken,
        }, {
            headers: {
                'Authorization': `Bearer ${await getRefreshToken()}`,
            },
        });

        if (response.status !== 200) {
            // redirect it to /login
            localStorage.removeItem("access")
            localStorage.removeItem("refresh")
            return null
        } else {
            // Save the new access token and refresh token to storage
            localStorage.setItem('access', response.data?.access);
            localStorage.setItem('refresh', response.data?.refresh);
            return response.data.access;
        }

    } catch (error) {
        localStorage.removeItem("access")
        localStorage.removeItem("refresh")
        // Handle refresh token error (e.g., log out the user or redirect to the login page)
        console.error('Failed to refresh access token:', error);
        return null
    }
};

apiClient.interceptors.request.use(
    async (config) => {
        const access = await getAccessToken();
        if (access) {
            config.headers.Authorization = `Bearer ${access}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const newAccessToken = await refreshAccessToken();
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return apiClient(originalRequest);
        }
        return Promise.reject(error);
    }
);

export default apiClient;
export {
    refreshAccessToken
}