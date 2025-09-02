import { Flex } from "antd"

import { Skeleton } from "shared/ui"

export const TestPlanHeaderSkeleton = () => {
  return (
    <Flex vertical>
      <Skeleton width="30%" height={28} style={{ marginBottom: 4 }} />
      <Flex gap={96} style={{ marginBottom: 12 }}>
        <Flex gap={16}>
          <Skeleton width={100} height={16} />
          <Skeleton width={100} height={16} />
        </Flex>
        <Flex gap={16}>
          <Skeleton width={100} height={16} />
          <Skeleton width={100} height={16} />
        </Flex>
      </Flex>
      <Flex gap={8} wrap style={{ marginBottom: 8 }}>
        <Skeleton width={200} height={32} />
        <Skeleton width={85} height={32} />
        <Skeleton width={85} height={32} />
        <Skeleton width={85} height={32} />
        <Skeleton width={100} height={32} />
      </Flex>
    </Flex>
  )
}
