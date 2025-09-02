import type { DragEndEvent, SensorDescriptor, SensorOptions } from "@dnd-kit/core"
import { DndContext, MouseSensor, useSensor, useSensors } from "@dnd-kit/core"
import { restrictToVerticalAxis } from "@dnd-kit/modifiers"
import {
  SortableContext,
  arrayMove,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import { Space, Table } from "antd"
import { ColumnsType } from "antd/es/table"
import { useGetStatusesQuery } from "entities/status/api"
import { getStatusTypeTextByNumber } from "entities/status/lib"
import { useContext, useEffect, useState } from "react"

import { DeleteStatusButton, EditStatusButton, SetDefaultStatusButton } from "features/status"

import { ProjectContext } from "pages/project"

import { SYSTEM_TYPE } from "shared/config/status-types"
import { Status } from "shared/ui"

interface RowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  "data-row-key": string
}

const Row = (props: RowProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: props["data-row-key"],
  })

  const style: React.CSSProperties = {
    ...props.style,
    transform: CSS.Translate.toString(transform),
    transition,
    cursor: "move",
    ...(isDragging ? { position: "relative", zIndex: 9999 } : {}),
  }

  return <tr {...props} ref={setNodeRef} style={style} {...attributes} {...listeners} />
}

interface Props {
  onChangeOrder: (statuses: Status[]) => void
}

export const StatusesTable = ({ onChangeOrder }: Props) => {
  const [isDisabled, setIsDisabled] = useState(false)
  const { project } = useContext(ProjectContext)!
  const { data, isFetching } = useGetStatusesQuery({ project: project.id })

  const statuses =
    data?.map((status) => ({
      key: status.id,
      ...status,
    })) ?? []

  const [dataSource, setDataSource] = useState(statuses)

  useEffect(() => {
    setDataSource(statuses)
  }, [data])

  useEffect(() => {
    const rawDataIds = data?.map((status) => status.id) ?? []
    const statusesIds = dataSource.map((status) => status.id)
    const isEqualOrder = rawDataIds.every((id, index) => id === statusesIds[index])
    if (!isEqualOrder) {
      onChangeOrder(dataSource)
    }
  }, [dataSource])

  const columns: ColumnsType<Status> = [
    {
      title: "Id",
      dataIndex: "id",
      key: "id",
      width: "70px",
    },
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (text, record) => {
        return <Status id={record.id} name={text as string} color={record.color} />
      },
    },
    {
      title: "Type",
      dataIndex: "type",
      key: "type",
      render: (_, record) => getStatusTypeTextByNumber(record.type),
    },
    {
      title: "Default",
      dataIndex: "default",
      key: "default",
      render: (_, record) => {
        return <SetDefaultStatusButton record={record} />
      },
    },
    {
      title: "Actions",
      key: "action",
      width: 100,
      render: (_, record) => {
        if (record.type === SYSTEM_TYPE) {
          return null
        }
        return (
          <Space>
            <EditStatusButton record={record} onDisableTable={setIsDisabled} />
            <DeleteStatusButton record={record} />
          </Space>
        )
      },
    },
  ]

  const sensors: SensorDescriptor<SensorOptions>[] = useSensors(
    useSensor(MouseSensor, {
      activationConstraint: {
        distance: 1,
      },
    })
  )

  const onDragEnd = ({ active, over }: DragEndEvent) => {
    if (active?.id !== over?.id) {
      setDataSource((prev) => {
        const activeIndex = prev.findIndex((i) => i.key === active.id)
        const overIndex = prev.findIndex((i) => i.key === over?.id)
        return arrayMove(prev, activeIndex, overIndex)
      })
    }
  }

  return (
    <DndContext sensors={sensors} modifiers={[restrictToVerticalAxis]} onDragEnd={onDragEnd}>
      <SortableContext
        items={dataSource.map((i) => i.key)}
        strategy={verticalListSortingStrategy}
        disabled={isDisabled}
      >
        <Table
          components={{
            body: {
              row: Row,
            },
          }}
          loading={isFetching}
          dataSource={dataSource}
          columns={columns}
          rowKey="id"
          style={{ marginTop: 12 }}
          id="administration-projects-statuses"
          rowClassName="administration-projects-statuses-row"
          pagination={false}
        />
      </SortableContext>
    </DndContext>
  )
}
