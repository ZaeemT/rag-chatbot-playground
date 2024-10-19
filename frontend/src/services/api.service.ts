import axios, { AxiosInstance, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { constants } from '../utils/constants';

// Setting up the Axios instance
const axiosService: AxiosInstance = axios.create({
  baseURL: constants.BASE_URL,
  timeout: 60 * 1000, 
});

// Response interceptor for handling errors
axiosService.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    console.error('API Response Error:', error);
    if (error.response && error.response.data) {
      return Promise.reject(error.response.data);
    }
    return Promise.reject(error);
  }
);

export { axiosService };

// Another instance without base URL for dynamic requests
const api: AxiosInstance = axios.create({
  timeout: 60 * 1000, 
});

// Request interceptor 
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    config.headers.set('Content-Type', 'application/json');
    config.headers.set('Access-Control-Allow-Origin', '*');  

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

export { api };
