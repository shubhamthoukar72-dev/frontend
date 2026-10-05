import { Navigate, Outlet } from "react-router-dom";

const CURRENT_USER_KEY = "jobai_current_user";
const ACCESS_TOKEN_KEY = "access_token";

function getStoredUser() {
  const rawUser = localStorage.getItem(CURRENT_USER_KEY);

  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch {
    return null;
  }
}

function ProtectedRoute() {
  const currentUser = getStoredUser();
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);

  if (!currentUser || !token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export default ProtectedRoute;