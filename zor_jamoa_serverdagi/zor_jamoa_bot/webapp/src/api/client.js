import axios from "axios";

const tg = window.Telegram?.WebApp;

const client = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

// Har bir so'rovga X-Init-Data header qo'shish
client.interceptors.request.use((config) => {
  const initData = tg?.initData ?? "";
  if (initData) {
    config.headers["X-Init-Data"] = initData;
  }
  return config;
});

export default client;
