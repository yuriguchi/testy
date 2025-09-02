import { Skeleton } from "shared/ui"

import styles from "./styles.module.css"

interface Props {
  count?: number
}

export const ProjectCardsSkeleton = ({ count = 6 }: Props) => {
  return Array(count)
    .fill(null)
    .map((_, i) => {
      return (
        <div className={styles.cardWrapper} key={i}>
          <div className={styles.cardContainer}>
            <div className={styles.nameBlock}>
              <Skeleton shape="circle" width={32} height={32} style={{ marginRight: 12 }} />
              <Skeleton width="50%" height={32} />
            </div>
            <Skeleton
              width={32}
              height={32}
              style={{ marginLeft: "auto" }}
              className={styles.bookmark}
            />
            <div className={styles.data}>
              {Array(4)
                .fill(null)
                .map((__, innerIndex) => (
                  <div className={styles.statItem} key={innerIndex}>
                    <Skeleton width={48} height={30} />
                    <Skeleton width="80%" height={22} />
                  </div>
                ))}
            </div>
          </div>
          <ul className={styles.btnsBlock}>
            {Array(3)
              .fill(null)
              .map((__, innerIndex) => (
                <Skeleton width="20%" height={24} key={innerIndex} />
              ))}
          </ul>
        </div>
      )
    })
}
