export const userConfig: UserConfig = {
  ui: {
    is_open_sidebar: true,
    drawer_size_test_case_details: 500,
    drawer_size_test_result_details: 500,
    graph_base_type: "pie",
    graph_base_bar_type: "by_time",
    graph_base_bar_attribute_input: "",
    test_plan: {},
    test_plan_estimate_everywhere_period: "minutes",
  },
  projects: {
    is_only_favorite: false,
    is_show_archived: false,
    favorite: [],
  },
  test_plans: {
    is_show_archived: false,
    is_cases_filter_open: false,
    filters: {},
  },
  test_suites: {
    filters: {},
  },
  test_cases: {
    is_show_archived: false,
  },
}
