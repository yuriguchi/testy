import { MeProvider } from "processes"
import { Navigate, Outlet, useLocation } from "react-router-dom"

import { getCsrfCookie } from "../api"

export const RequireAuth = () => {
  const token = getCsrfCookie()
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return (
    <MeProvider>
      <Outlet />
    </MeProvider>
  )
}
