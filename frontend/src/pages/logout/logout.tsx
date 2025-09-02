import { useEffect } from "react"
import { useNavigate } from "react-router-dom"

import { useLogoutMutation } from "entities/auth/api"

import { ContainerLoader } from "shared/ui"

export const LogoutPage = () => {
  const navigate = useNavigate()
  const [logoutRequest] = useLogoutMutation()

  useEffect(() => {
    logoutRequest()
      .unwrap()
      .then(() => {
        navigate("/login")
      })
  }, [])

  return <ContainerLoader />
}
