from channels.generic.websocket import AsyncJsonWebsocketConsumer

class LoanUpdateConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')

        if not user or user.is_anonymous:
            await self.close(code=4001)
            return

        self.user_group_name = f'user_{user.id}'
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        # branch users get branch group too, if available
        home_branch = getattr(getattr(user, 'profile', None), 'home_branch', None)
        if home_branch:
            self.branch_group_name = f'branch_{home_branch.id}'
            await self.channel_layer.group_add(self.branch_group_name, self.channel_name)
        else:
            self.branch_group_name = None

        # global admins can listen on a global group
        if user.is_staff or getattr(user, 'is_head_office', False):
            self.admin_group_name = 'loans_admins'
            await self.channel_layer.group_add(self.admin_group_name, self.channel_name)
        else:
            self.admin_group_name = None

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        if getattr(self, 'branch_group_name', None):
            await self.channel_layer.group_discard(self.branch_group_name, self.channel_name)
        if getattr(self, 'admin_group_name', None):
            await self.channel_layer.group_discard(self.admin_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # No direct client commands are needed yet; keep real-time channel as a push-only channel.
        await self.send_json({'detail': 'WebSocket connection active'})

    async def loan_update(self, event):
        await self.send_json({
            'type': event.get('type', 'loan_update'),
            'event': event.get('event'),
            'payload': event.get('payload'),
        })
