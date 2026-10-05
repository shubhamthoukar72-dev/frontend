import { API_URL } from "./api";

const CURRENT_USER_KEY = "jobai_current_user";
const ACCESS_TOKEN_KEY = "access_token";
const REMEMBER_ME_KEY = "jobai_remember_me";
const REMEMBERED_EMAIL_KEY = "jobai_remembered_email";

export async function signIn(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Unable to sign in. Please try again.");
  }

  if (!data.access_token || !data.user?.id || !data.user?.role) {
    throw new Error("The sign-in response was incomplete. Please try again.");
  }

  return data;
}

export function saveAuthSession(data, email, rememberMe) {
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(data.user));

  if (rememberMe) {
    localStorage.setItem(REMEMBER_ME_KEY, "true");
    localStorage.setItem(REMEMBERED_EMAIL_KEY, email);
  } else {
    localStorage.removeItem(REMEMBER_ME_KEY);
    localStorage.removeItem(REMEMBERED_EMAIL_KEY);
  }

  window.dispatchEvent(new Event("jobai-auth-change"));
}
