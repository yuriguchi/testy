interface NotificationSetting {
  action_code: number
  verbose_name: string
  message: string
  enabled: boolean
}

interface NotificationWSMessage {
  count: number
}

interface NotificationData {
  id: number
  unread: boolean
  actor: string
  message: {
    template: string
    placeholder_text: string
    placeholder_link: string
  }
  timeago: string
}

interface GetNotificationQuery {
  unread?: boolean
  v?: number
}

interface MarkAsMutation {
  unread: boolean
  notifications: number[]
}
