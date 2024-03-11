import axios from "axios";

const axInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API,
  timeout: 1000,
});

export default axInstance;
