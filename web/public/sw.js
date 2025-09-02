self.addEventListener('push', event => {
  const data = event.data?.json?.() || { title: 'SideQuest', body: 'New quest!' };
  event.waitUntil(self.registration.showNotification(data.title, { body: data.body }));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(clients.openWindow('/'));
});
