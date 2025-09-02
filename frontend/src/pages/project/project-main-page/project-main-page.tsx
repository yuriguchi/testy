import { TreebarProvider } from "processes"
import { Outlet } from "react-router-dom"
import { FooterView as Footer } from "widgets"

import { Treebar } from "widgets/[ui]/treebar/treebar"

import styles from "./project-main-page.module.css"

export const ProjectMainPage = () => {
  return (
    <TreebarProvider>
      <div className={styles.wrapper}>
        <Treebar />
        <div className={styles.containerContent}>
          <div className={styles.wrapperContent}>
            <Outlet />
          </div>
          <Footer />
        </div>
        <div id="portal-root" />
      </div>
    </TreebarProvider>
  )
}
