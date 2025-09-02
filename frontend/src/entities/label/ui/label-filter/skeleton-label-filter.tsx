import { Skeleton } from "shared/ui"

export const SkeletonLabelFilter = () => {
  return (
    <ul style={{ display: "flex", flexWrap: "wrap", gap: 8, margin: 0 }}>
      <Skeleton width={42} height={22} style={{ borderRadius: "100px" }} />
      <Skeleton width={46} height={22} style={{ borderRadius: "100px" }} />
      <Skeleton width={70} height={22} style={{ borderRadius: "100px" }} />
      <Skeleton width={64} height={22} style={{ borderRadius: "100px" }} />
      <Skeleton width={56} height={22} style={{ borderRadius: "100px" }} />
    </ul>
  )
}
