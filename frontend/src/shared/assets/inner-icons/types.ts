import { AntdIconProps } from "@ant-design/icons/lib/components/AntdIcon"
import { ForwardRefExoticComponent, RefAttributes } from "react"

type Icon =
  | React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  | ForwardRefExoticComponent<AntdIconProps & RefAttributes<HTMLSpanElement>>

export interface IconsPackType {
  ArchiveIcon: Icon
  ArrowIcon: Icon
  ArrowLeftIcon: Icon
  BackIcon: Icon
  BookmarkFillIcon: Icon
  BookmarkIcon: Icon
  CloseIcon: Icon
  CollapseIcon: Icon
  ColumnViewIcon: Icon
  ContextMenuIcon: Icon
  DashboardIcon: Icon
  DotsIcon: Icon
  ExpandIcon: Icon
  FilterIcon: Icon
  FilterPlusIcon: Icon
  InfoIcon: Icon
  LogoutIcon: Icon
  ResetIcon: Icon
  SaveIcon: Icon
  SorterIcon: Icon
  TableIcon: Icon
  TestPlansIcon: Icon
  TestSuitesIcon: Icon
  UserGroupsIcon: Icon
  UserIcon: Icon
}
