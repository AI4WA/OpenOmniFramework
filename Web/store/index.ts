import {combineReducers, configureStore} from "@reduxjs/toolkit";
import {useDispatch, TypedUseSelectorHook, useSelector} from "react-redux";

import {authReducer} from "@/store/authSlices";


const rootReducer = combineReducers({
    auth: authReducer,
});

export const store = configureStore({
    reducer: rootReducer,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({serializableCheck: false}),
    devTools: process.env.NODE_ENV !== "production", // Enable Redux DevTools only in non-production environments

});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;