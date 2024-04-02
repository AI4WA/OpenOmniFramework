import {createSlice} from "@reduxjs/toolkit";
import type {PayloadAction} from "@reduxjs/toolkit";

export interface IAuthState {
    authState: {
        username?: string,
        userId?: number,
        firstName?: string,
        lastName?: string,
        orgName?: string,
        orgId?: number,
        orgType?: string,
        isLogin: boolean
    };
}

export interface LLMJwtPayload {
    username?: string;
    user_id?: number;
    first_name?: string;
    last_name?: string;
    org_name?: string;
    org_id?: number;

}

// Define a type for the payload that matches the structure of authState
export type AuthStatePayload = {
    username?: string;
    userId?: number;
    firstName?: string;
    lastName?: string;
    orgName?: string;
    orgId?: number;
    orgType?: string;
    isLogin: boolean;
};

const initialState: IAuthState = {
    authState: {
        username: "",
        userId: -1,
        firstName: "",
        lastName: "",
        orgName: "",
        orgId: -1,
        orgType: "",
        isLogin: false

    }
};

export const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setAuthState: (state, action: PayloadAction<AuthStatePayload>) => {
            state.authState = {...state.authState, ...action.payload};
        },
        logout: (state) => {
            state.authState = {
                username: "",
                userId: -1,
                firstName: "",
                lastName: "",
                orgName: "",
                orgId: -1,
                orgType: "",
                isLogin: false
            };
        }
    },
});
export const {setAuthState, logout} = authSlice.actions;
export const authReducer = authSlice.reducer;