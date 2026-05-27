import { api } from "./client";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export async function login(
  email: string,
  password: string,
): Promise<TokenPair> {
  const res = await api.post<TokenPair>("/auth/login", { email, password });
  return res.data;
}

export async function register(email: string, password: string) {
  const res = await api.post("/auth/register", { email, password });
  return res.data;
}
