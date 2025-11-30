import { useEffect } from "react";
import { toast, ToastContainer } from "react-toastify";

export default function Login() {
  const params = new URLSearchParams(location.search);
  const error = params.get("error");

  useEffect(() => {
    if (error) {
      const messages: Record<string, string> = {
        cancelled: "You cancelled the MAL login.",
        missing_params: "Something went wrong. Try logging in again.",
        invalid_state: "Invalid session, please retry.",
      };

      toast.error(messages[error] || "Login failed.");
    }
  }, [error]);

  return (
    <ToastContainer aria-label={undefined} />
  )
}