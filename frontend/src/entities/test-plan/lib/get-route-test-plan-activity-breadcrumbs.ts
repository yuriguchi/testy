export const getRouteTestPlanActivityBreadCrumbs = (
  breadcrumbs: BreadCrumbsActivityResult,
  routes: BreadCrumbsActivityResult[] = []
): BreadCrumbsActivityResult[] => {
  if (breadcrumbs.parent === null) {
    routes.push(breadcrumbs)
  } else {
    routes = [breadcrumbs, ...getRouteTestPlanActivityBreadCrumbs(breadcrumbs.parent, routes)]
  }

  return routes
}
