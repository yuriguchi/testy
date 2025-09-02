import { Layout } from "antd"
import { ResultStatusType } from "antd/es/result"
import { useEffect } from "react"
import { Outlet, useLocation } from "react-router-dom"
import { FooterView as Footer, SystemMessages } from "widgets"

import { useAppDispatch, useAppSelector } from "app/hooks"
import { handleError, selectAppError } from "app/slice"

import { ErrorPage } from "pages/error-page/error-page"

import { BtnToTop } from "shared/ui"

import { Sidebar } from "./sidebar/sidebar"

const { Content } = Layout

export const Main = () => {
  const dispatch = useAppDispatch()
  const { pathname } = useLocation()
  const appError = useAppSelector(selectAppError)

  useEffect(() => {
    dispatch(handleError(null))
  }, [pathname])

  const HAS_TREE =
    pathname.includes("projects") && (pathname.includes("suites") || pathname.includes("plans"))

  return (
    <Layout
      style={{ display: "flex", flexDirection: "row", minHeight: "100vh", maxWidth: "100vw" }}
    >
      <Sidebar />
      <Layout>
        <SystemMessages />
        <Content style={{ minHeight: "100vh", zIndex: 1 }}>
          {appError ? (
            <ErrorPage code={appError.code as ResultStatusType} message={appError.message} />
          ) : (
            <Outlet />
          )}
        </Content>
        {!HAS_TREE && <Footer />}
      </Layout>
      <BtnToTop />
    </Layout>
  )
}
