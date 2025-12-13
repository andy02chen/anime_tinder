import { type JSX } from "react";
import { Navigate } from "react-router-dom";
import Loader from "./Loader";

interface ProtectedRouteProps {
  user: any;
  loading: boolean;
  children: JSX.Element;
}

export default function ProtectedRoute({ user, loading, children }: ProtectedRouteProps) {
  if (loading) return <Loader />;        // show loader while session/user is loading
  if (!user) return <Navigate to="/" replace />; // redirect if not logged in
  return children;                        // render the route content
}
