const getAllTestCases = (node: InfoNode) => {
  const result: string[] = []
  if (node.test_cases) {
    for (const item of node.test_cases) {
      result.push(String(item.id))
    }
  }

  if (node.children) {
    for (const nodeObj of node.children) {
      if (nodeObj.key.startsWith("TS")) {
        result.push(...getAllTestCases(nodeObj as InfoNode))
      }
    }
  }

  return result
}

export const getTestCaseChangeResult = (
  checked: CheckboxChecked,
  info: TreeCheckboxInfo,
  testCasesWatch: string[]
) => {
  const setTestCasesWatch = new Set(testCasesWatch)
  const isSuiteClick = info.node.key.startsWith("TS")
  const checkedFiltered = (checked as string[]).filter((item) => !item.startsWith("TS"))
  const newTestCase = isSuiteClick ? getAllTestCases(info.node) : checkedFiltered

  if (!info.checked || info.node.halfChecked) {
    if (isSuiteClick) {
      newTestCase.forEach((item) => setTestCasesWatch.delete(item))
    } else {
      setTestCasesWatch.delete(info.node.key)
    }
  } else {
    newTestCase.forEach((item) => setTestCasesWatch.add(item))
  }

  return Array.from(setTestCasesWatch)
}
