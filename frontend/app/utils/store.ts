import { configureStore } from '@reduxjs/toolkit';
import {authReducer, settingsReducer} from './states';

export const makeStore = () => {
  return configureStore({
    reducer: {
      auth: authReducer,
      settings: settingsReducer,
    },
  });
};

// Types for TypeScript
export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];