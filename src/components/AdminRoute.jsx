import { Navigate, Outlet } from "react-router-dom";

function getStoredUser() {
  const rawUser = localStorage.getItem("jobai_current_user");

  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch {
    return null;
  }
}

function AdminRoute() {
  const token = localStorage.getItem("access_token");
  const currentUser = getStoredUser();

  if (!token || !currentUser) {
    return <Navigate to="/admin/login" replace />;
  }

  if (currentUser.role !== "admin") {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

export default AdminRoute;
