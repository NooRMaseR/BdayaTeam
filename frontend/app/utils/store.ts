import { configureStore } from '@reduxjs/toolkit';
import {authReducer} from './states';

export const makeStore = () => {
  return configureStore({
    reducer: {
      auth: authReducer
    },
  });
};

// Types for TypeScript
export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];