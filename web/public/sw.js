self.addEventListener('push', (event) => {
  const payload = event.data?.json() ?? { title: 'SideQuest', body: 'New quest awaiting!' }
  event.waitUntil(
    self.registration.showNotification(payload.title, {
      body: payload.body,
      data: payload.data,
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification.data?.url || '/'
  event.waitUntil(clients.openWindow(url))
})
