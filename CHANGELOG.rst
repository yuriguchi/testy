Version 2.0.5
--------------
*Status: General availability*

Release Overview:

The use of attributes.

Now, attributes can be created not only for test cases and test results but also for test suites and test plans.
Create/Edit pages for Test Plans and Suites reflect the changes above.

*Released: 30-01-2025*

- Added custom attributes for Test Plans and Test Suites (TMS-1022)


**Bug fixes**:

- Fixed a bug where changing Test Result is not available from root (TMS-1353)
- Drawer is pined by default (TMS-1390)
- Fixed a destructuring of MeContext (TMS-1396)
- "Clone" button is inactive when copying Test Result (TMS-1398)
- Custom Attributes is missing when copying Test Result (TMS-1399)
- Fixed incorrect sorting of Custom Attributes (TMS-1403)
- Project cards are duplicated when switching the archive filter (TMS-1410)
- "Show Archived" checkbox in the filter cannot be unchecked (TMS-1423)
- "Unassigned" filter does not work (TMS-1425)
- Fixed bug when editing a Test Result, an optional Custom Attribute becomes required (TMS-1439)

Version 2.0.4
--------------
*Status: General availability*


Release Overview:
Versions 2.0, 2.0.1, 2.0.2 and 2.0.3 are internal releases which we used to stabilize TestY after the major change
we made (for both front and backend sides), 2.0.4 incorporates the whole set of features from previous 2.x releases with
various bug fixes and this is the most stable production version we have.
The key difference between the 2.x and 1.3.x versions is a redesign of Test Plans & Results and Test Suites & Cases tabs.
For now, there are two ways of how plans/tests and suites/cases can be represented (tree and flat views) and the end user can choose the way he/she likes.

Taking into account this change we eliminated the need of the Child Plans/Suites panes, because for now child items are visually incorporated to the parent one.
We also reworked navigation within the application, so now the user can simply go to any place in the structure of Plans/Suites using sidebar.
Another major change we made is the redesign of filters. The filter is now available on the both Test Plans & Results and Test Suites & Cases tabs.
The filter works in both views (table and tree), it incorporates search bar and allows user to filter the data on a combination of various independent conditions (meaning the filter is not hierarchical).
Also, it is possible to save/edit/remove filters or share filtered representation to the coworker with just copying URL.

Sorting functionality available within a separate menu right next to the filter button.
In addition to the above within this release significant work has been done to preserve the application's state for users and address performance issues.

Also, we’ve added localization and users now have a fully Russian-translated interface.
For backward compatibility we preserved API v1, so if you used it for scripting you can still use it, but all new functions would be available in API v2.

Additional details for Filters
==============================

Test Plans & Results

- **Search bar** by **Name** and **ID**: If the filter is opened without transitioning to a specific plan, it will search tests across all plans.
- **Test Plan**: Plan selector useful for searching by child plans or all plans, when the filter is opened without transitioning to a specific plan.
- **Test Suites**: Suite selector returning the previous behavior; selecting a parent suite will select all its children.
- **Status**: Multi-select **OR** filter, works similarly to filtering in statistics.
- **Assignee**: Multi-select filter.
- **Label**: Filtering by labels, functionality preserved from the previous implementation.
- **Test Plan Start At**: Date range filter, allows selection of specific plans by their start date.
- **Test Plan Created At**: Date range filter, by the actual creation date of the plan.
- **Test Created At**: Date range filter, by the date the test was added to the plan.
- **Show Archived**: Shows archived tests. This will be removed after the rework of archiving.

Test Suites & Cases

- **Search bar** by **Name** and **ID**: If the filter is opened without transitioning to a specific suite, the search will cover the entire project.
- **Test Suites**: Suite selector, similar to the Test Plans filter.
- **Label**: Filtering test cases by labels, works the same way as it did for plans.
- **Test Suite Created At**: Date range filter, by the creation date of the suite.
- **Test Case Created At**: Date range filter, by the creation date of the case.
- **Show Archived**: Shows archived test cases and suites. This will be removed after the rework of archiving.

Important notes

- **Show full tree** toggle: When selecting a plan or suite selector, this toggle displays all suites/plans, regardless of where the filter is opened (e.g., if the filter is opened within a specific suite/plan, the selector will show all suites/plans of the project).
- Filters can be saved, edited, and deleted. You can create an unlimited number of filters.
- Saved filters are available within the project.
- On the **Test Plans** tab, all filter segments except for the label filter **do not affect statistics** in the current implementation

*Released: 28-12-2024*

- Implement visual separation between Test Case and results (TMS-190)
- Move child plans under the parent plan (TMS-215)
- Add grouping of tests by suites on the Test Plan page (TMS-297)
- Display tests in the parent Test Plan (TMS-449)
- Manage the test list in a Test Plan with nested Test Plans (TMS-513)
- Merge child suites and tests in the parent suite (Test Suites & Cases view) (TMS-590)
- Remove excessive empty space around "Test Cases" (TMS-594)
- Add date/time and pre-filled attributes to test results (TMS-679)
- Add a "Back" button to allow navigation to the higher level (TMS-704)
- Implement a table view for the dashboard in addition to the current one (TMS-805)
- Redesign statistics (TMS-819)
- Slow request on api/v1/projects/ (TMS-1049)
- Missing archive icon for tests in "Activity" (TMS-1177)
- Add "archived/non-archived" status to activity (TMS-1182)
- Add label-based filtering during Test Plan creation (TMS-1129)
- Add "Start date" and "Created At" columns to the Tests table (TMS-1130)
- Pagination does not persist between pages (TMS-1148)
- Enable filtering by Test Suites in the Test Cases table (TMS-1195)
- Add tooltips to buttons (TMS-1185)
- Search does not work on the Test Suites & Cases tab (TMS-119)
- Search by Test ID does not work (TMS-243)
- Enable label-based filtering at any level (TMS-435)
- Please improve label management (TMS-506)
- Add label search functionality in Test Suites & Cases (TMS-730)
- Search for test cases on the Test Suites & Cases page (TMS-1089)
- Filter test cases by labels (TMS-1232)
- Improved database performance for histogram endpoint (TMS-1382)
- Locked test plan custom attributes (TMS-1377)



**Bug fixes**:

- URL conditions reset when opening a test from Test Plans (TMS-1083)
- Attribute deletion is not blocked (TMS-1115)
- Multiple attributes per test result (TMS-1117)
- Number of comments on test results is always 0 (TMS-1119)
- Sorting by suite/assignee in the test list is very slow (TMS-1120)
- Incorrect case count when creating Test Plan with label filtering (TMS-1121)
- Archived test cases not marked in the list (TMS-1122)
- Lost Russian translation in "Copy Test Plan" (TMS-1123)
- Trim text in labels (TMS-1124)
- Deleting a test case leads to a 404 error (TMS-1125)
- "Load more" button does not disappear after clicking in the test list (TMS-1127)
- Rename "Parameters" to "Parent plan" in Edit Test Plan (TMS-1128)
- Error opening test case (TMS-1131)
- Unable to edit a result with a deleted status (TMS-1132)
- Unable to update test case (TMS-1133)
- No translations for the "Action" column in the Activity page (TMS-1137)
- Label block disappears (TMS-1138)
- Non-project user can be assigned to a test (TMS-1139)
- Test Plan attribute is missing during creation/editing (TMS-1140)
- Dollar sign appears on a button (TMS-1141)
- Test cases with steps are missing in the Test Plan list (TMS-1142)
- Deleting a custom status removes test results (TMS-1143)
- Editing an archived Test Plan causes a 403 error (TMS-1144)
- "Archive" button is available for archived Test Plans (TMS-1145)
- Infinite spinner when filtering cases by any label (TMS-1146)
- Align archive icon for cases in Test Plan creation window (TMS-1147)
- Copying an archived test case (TMS-1149)
- Copying an archived plan into a regular plan (TMS-1150)
- Tests fail during migration (TMS-1152)
- [Dashboard][Table view] Private projects show "Request Access" icon instead of navigation (TMS-1155)
- Unable to update custom attributes in project settings (TMS-1156)
- Restoring archived project causes a 403 error (TMS-1158)
- Project settings issue (TMS-1159)
- Test result status not updated (TMS-1160)
- Copying parameterized Test Plans results in parameter loss (TMS-1165)
- Moving tests returns a 500 error (TMS-1167)
- Editing archived results: statuses fail to load (TMS-1176)
- Date Picker: missing Russian translation (TMS-1178)
- Test Plan: tree sorting is case-sensitive (TMS-1179)
- Test Plan section cannot be expanded after being collapsed (TMS-1180)
- Browser resizing overlaps charts (TMS-1181)
- Deleting a test case causes a 404 error (TMS-1184)
- Missing notification button near profile in the header (TMS-1187)
- Archived projects are not marked (TMS-1188)
- Archiving a project still allows Test Plan archiving (TMS-1192)
- Missing parent check when copying Test Plans (TMS-1197)
- Results remain visible on UI after copying Test Plans (TMS-1198)
- Breadcrumbs missing while navigating Test Plan tree (TMS-1199)
- Sidebar tree does not expand automatically (TMS-1201)
- Notifications incorrectly state that a suite is copied instead of a Test Plan (TMS-1202)
- Search does not work on the Test Suites & Cases tab (TMS-119)
- Search by Test ID does not work (TMS-243)
- Enable label-based filtering at any level (TMS-435)
- Please improve label management (TMS-506)
- Add label search functionality in Test Suites & Cases (TMS-730)
- Search for test cases on the Test Suites & Cases page (TMS-1089)
- Filter test cases by labels (TMS-1232)
- Fixed NaN in navigation for test plan from root (TMS-1367)
- Undefined appears in url when navigating to test suites from root (TMS-1366)
- URL parameters are being reset when page is up (TMS-1364)
- Deprecated parent test suite in modal window after navigating tree (TMS-1360)
- Deprecated parent test plan in modal window after navigating tree (TMS-1361)
- Error when creating nested suite in modal window of creation (TMS-1356)
- Duplicated assignee filter (TMS-1370)
- Submit dialog appears if data was not changed in edit (TMS-1116)
- Show archived filter being reset (TMS-1276)
- Archive button is available for archived test case in version display (TMS-1154)
- Show archived checkbox missing in tests table (TMS-1285)


Version 1.3.4
--------------
*Status: General availability*

*Released: 07-10-2024*

- Bumped versions of dependencies (TMS-1102)
- Added functionality to delete results based on specific attributes (TMS-1091)
- Added ability to search by key in plan attributes (TMS-1065)
- Updated Swagger documentation (TMS-970)
- Added default status configuration to project settings (TMS-1070)
- Added ordering and naming functionality to content types (TMS-1086)
- Improved handling of broken images (TMS-616)
- Introduced basic authentication(TMS-1075)
- Added filtering by date range in histograms (TMS-1062)


**Bug fixes**:

- Fixed errors related to filtering by unavailable fields (TMS-1085)
- Returned default ordering to test plans (TMS-1088)
- Fixed sorting issues when the string attribute is a number (TMS-1093)
- Fixed issues with doubled test executions (TMS-1077)


Version 1.3.3
--------------
*Status: General availability*

*Released: 11-09-2024*

- Implemented the ability to create custom statuses at the project level (TMS-545, TMS-678, TMS-733)
- Added a backend for working with custom attributes at the Test Plan level (TMS-1034, TMS-1035)
- Reworked Bulk Assignment test system
- Reworked Attachment image system
- Implemented a mechanism for notifying users about events in the system, with the ability to customize notifications (TMS-955)
- Implemented ability to transfer tests from one Test Plan to another within a project while preserving the results (TMS-907)
- Reworked mechanism for working with loading large amounts of data, fixed issues that caused tables lock
- Reworked compose file and dockerfile for backend for faster deploy
- Updated environment variables

**Bug fixes**:

- [QA]: sorting by name in plans (TMS-956)
- 404 on 2nd page with label filter (TMS-958)
- Table filter resets when creating Test-Case (TMS-959)
- Invalid object passed in permissions (TMS-960)
- White screen when entering the main page (TMS-961)
- Does not find test plan when selecting test transfer (TMS-962)
- Error 404 after filtering Test-Suite on page > 1 (TMS-967)
- Filtering by labels in donut stopped working (TMS-977)
- Restoring labels does not work when restoring (TMS-981)
- Cannot transfer child test suite within one project from one parent suite to another (TMS-984)
- Unexpected Application Error s.map is not a function (TMS-990)
- 404 when deleting an archived test case (TMS-995)
- Bulk assigning large chunk of tests is slow (TMS-999)
- Out of postgres memory (TMS-1002)
- Unable to add test cases to an existing test plan (TMS-1003)
- When reassigning test cases for a specific component, all test cases from the test plan are reassigned (TMS-1004)
- When copying a test suite that contains tests with steps, the steps are not copied (TMS-1009)
- Problems with cache validation in custom attributes (TMS-1026)
- Files do not work between different containers (TMS-1027)
- Test suite is not reset when searching pagination (TMS-1028)
- Bug in migrations when adding a new field (TMS-1031)
- 504 When filtering by labels (TMS-1037)
- 403 for new status creation in Private project (TMS-1046)


Version 1.3.2
--------------
*Status: General availability*

*Released: 12-08-2024*

- In the first approximation, mass operations with tests have been implemented, namely: transfer of tests, assessment (TMS-700, TMS-907)
- The functionality of custom attributes has been improved. Custom attributes can be applied to specific result statuses within a project (TMS-857)
- Implemented adding user settings to URL (TMS-858)
- Added the ability to change passwords for external users (TMS-886)
- Implemented a mechanism for notifying users about events in the system, with the ability to customize notifications (TMS-955)
- Implemented the ability to transfer tests from one Test Plan to another within a project while preserving the results (TMS-907)
- Added the ability to clone a test result (TMS-885)
- Optimized Test-Suites search when creating/editing a Test Plan (TMS-851)
- Transition to Python 3.11 and Django 4.2.13

**Bug fixes**:

- When switching to a child plan, the list of labels and the condition should be reset (TMS-831)
- Ordering does not work in the Test-Suites table (TMS-846)
- [Test Plan] Clicking on Test name redirects to Test-Suites (TMS-847)
- Navigation doesn't work on various conditions (TMS-848)
- "Not the latest version" warning appears on any close of the test-case (TMS-849)
- Cannot access the frontend raised in Docker (TMS-853)
- Error processing the GET parameter parent_id in TestPlanViewSet (treeview) (TMS-854)
- Incorrect pagination when filtering by name (TMS-855)
- When setting the SKIPPED and RETEST status, it requires filling in the fields (TMS-856)
- Soft deleting parameter not allowing to create another one. (TMS-882)
- Incorrect error output for mandatory attributes in test result (TMS-884)
- Backend responds with incorrect set of Steps (TMS-894)
- Pagination inside the test plan doesn't work 
- Number of DB connections exceeded (TMS-942)
- RecursionError when copying a test plan to itself or a test plan to a child test plan (TMS-946)
- Not all suites are displayed in the Suite field search when editing TC (TMS-954)


Version 1.3.1
--------------
*Status: General availability*

*Released: 05-06-2024*

- Added custom attributes and their project based configuration (TMS-666)

  - Valid targets for custom attributes are: Test-Case, Test-Result, Test-Suite

- Test-Case creation is now in separate window (TMS-670)
- Test result edit time is now configurable per project (TMS-742):

  - Test-Result is editable in time gap
  - Test-Result is forever editable
  - Test-Result is not editable

- Added role based access per project (TMS-712)
- Added Test-Plan copying

  - Plan can only be copied to project of its source
  - Test assignee can be copied or dropped

- Test-Suite copying destination suite select is more readable now (TMS-728)
- Test-Copying copying destination suite select is more readable now (TMS-748)
- Contact email added (TMS-766)
- Added filtering tests by labels in Test-Plan creation window (TMS-706)
- Test-Suite filter in Test-Plan table view improved (TMS-731)
- The behavior of the filter by labels on the Test-Plans tab has been changed.
- Now the filter is applied to the table view of tests (TMS-788).

**Bug fixes**:

- Incorrect sorting by result attribute is incorrect (TMS-719) 
- Cannot create a label if there was already a label with the same name (TMS-734)
- Cannot update comment in Test result if test or project changed (TMS-736)
- Incorrect suite path in tests (TMS-741)
- Problem with displaying data with markdown in the Expected field (TMS-759)
- (Activity) Incorrect time for result in Activity table (TMS-762)
- It's possible to edit archived test-result (TMS-763)
- It's possible to add new result to archived test (TMS-764)
- Via API you can create a test result with the status UNTESTED (TMS-772)
- Filtering is not working for suites if there are sub suites in the project (TMS-731)
- Delete preview for testcases/testsuites pickling error (TMS-771)
- Redirecting to 404 after using of search with pagination on TestSuites/Cases (TMS-773)
- Archived test cases are imported to test plan (TMS-774)
- HTTP 404 during search and navigation in Test Suites & Cases (TMS-776)
- When updating the result with steps, an error occurred (TMS-777)
- Unable to load allure report (TMS-778)
- 504 Gateway Time-out when creating testplans in bulk (TMS-782)
- Error when using parent query parameter with search on tree structures (TMS-783)
- Labels on TestPlan view are broken (TMS-785)
- Incorrect behavior of "not the latest version" warning on cancel of Test-Case edit (TMS-786)
- 400 on Test-Plans when filtering by Test-Suites (TMS-796)
- Extra confirmation to close the test (TMS-798) 
- After editing a test, the test version is not displayed correctly (TMS-800)
- External User must not see statistics for projects on the Dashboard (TMS-804)
- no way to enter test results (TMS-815)
- bash lines formatting for already written tests (TMS-816)
- Formatting as code (```) in markddown fields broke in already written tests (TMS-820)
- When saving the result, it requires filling in an NOT mandatory attribute (TMS-826)
- When refreshing the test case editing page, it redirects to information about it (TMS-827)
- It's possible to delete required custom attribute on case/result edit screen (TMS-828)
- Error when Restore version test case (TMS-830)
- When creating a case, we have a disable button (TMS-833) 
- Performance issues with cases search when labels are applied (TMS-834) 
- Page layout breaks after test-case editing (TMS-836) 
- 404 when loading pagination (TMS-839) 

Version 1.2.15
--------------
*Status: General availability*

*Released: 11-04-2024*

- Added estimates to tests (TMS-745)
- Fixed duplicate test case history record that caused 500

Version 1.2.14
--------------
*Status: General availability*

*Released: 15-03-2024*

- Generalized import policy to start all imports from *testy*
- Changed plugin system to use pluggy to simplify plugin development
- Made testy installable for more convenient plugin development
- Remade all existing plugins to work with new plugin system
- Added production configuration based on Nginx

Version 1.2.13
--------------
*Status: General Availability*

*Released: 22-11-2023*

- Added `estimate` column for the suite table (TMS-558)
- Added the system statistics (TMS-420, TMS-591)
- Project server pagination (TMS-364)
- Added filter by assignee field for test list (TMS-423)
- Suites table optimization
- Add the ability to add attachments only for comment

Version 1.2.12
--------------
*Status: Internal*

*Released: 20-11-2023*

- Added the ability to update a test case without version (TMS-570)
- Added restore of test case from any version (TMS-585)
- Added link to comment for test result (TMS-563)
- Child test plan creation disabled for archived plan (TMS-578)
- Added direct link to the test result (TMS-510)
- Added `remember me` flag for authorization (TMS-351)
- Frontend build optimization
- Test case search optimization
- Added markdown support for test plan description

Version 1.2.11
--------------
*Status: Internal*

*Released: 03-11-2023*

- Added test case archiving (TMS-498)
- Storing `estimate` option for test plan (TMS-560)
- Added labels for test plan histogram (TMS-548)
- Drawer optimization

Version 1.2.10
--------------
*Status: Internal*

*Released: 25-10-2023*

- Added sorting by name for test case table (TMS-507)
- Added clickable links for markdown (TMS-529)
- Added negative lables for test plan (TMS-526)
- Added comments, tests and history for test case

Version 1.2.9
-------------
*Status: Internal*

*Released: 17-10-2023*

- Added test plan statistics by `estimate` field (TMS-524)
- User list server pagination (TMS-357)
- Added avatar column

Version 1.2.8
-------------
*Status: General Availability*

*Released: 11-10-2023*

- Added project icon (TMS-501)
- Added test case copying (TMS-522)
- Store date for every histogram (TMS-528)
- Added test suite copying (TMS-496)
- Test case search optimization
- Fixed history error for TestRail migration

Version 1.2.7
-------------
*Status: Internal*

*Released: 22-09-2023*

- Server pagination and test suite search (TMS-484)
- Added comments for test case and test result (TMS-482)
- Added user activity statistics

Version 1.2.6
-------------
*Status: Internal*

*Released: 19-09-2023*

- Added histogram for test plan (TMS-476)
- Added `Assing to me` button (TMS-489)
- System messages (TMS-492)
- Added `Under construction` page (TMS-493)
- Added test plan copying via CLI (TMS-485)
- Plugins removed from core
- Added user avatars for test and result

Version 1.2.5
-------------
*Status: Internal*

*Released: 07-09-2023*

- Server sorting for test cases (TMS-429)
- Test plan server pagination (TMS-394)
- Added drawer (TMS-179)
- Fixed list for markdown (TMS-430)
- Fixed slow authentication (TMS-463)
- Removed `Untested` status from test case steps

Version 1.2.4
-------------
*Status: Internal*

*Released: 03-08-2023*

- Added avatar for user profile (TMS-355)
- Removed `Untested` status for test case (TMS-427)

Version 1.2.3
-------------
*Status: Internal*

*Released: 28-07-2023*

- Added execution percent of root test plans (TMS-344)


Version 1.2.2
-------------
*Status: Internal*

*Released: 20-07-2023*

- Added safe models removing and test plan archiving (TMS-233)
- Added link to object for popup message (TMS-396)
- Added `assigned to` field for test (TMS-365)

Version 0.1.0 - 1.1.0
---------------------
*Internal releases under active development, 2022-2023*
