import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { GetLogIn } from './api_types_helper';

export type UserAuth = {
    isLoading: boolean,
    isAuthed: boolean,
    user: GetLogIn | null
}

const initialState: UserAuth = {
    isLoading: true,
    isAuthed: false,
    user: null
} 

const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setCredentials: (state, action: PayloadAction<UserAuth>) => {
            state.isLoading = action.payload.isLoading;
            state.isAuthed = action.payload.isAuthed;
            state.user = action.payload.user;
        },
        logout: (state) => {
            state.isLoading = false;
            state.isAuthed = false;
            state.user = null;
        }
    }
});

export const { setCredentials, logout } = authSlice.actions;
export const authReducer = authSlice.reducer;

