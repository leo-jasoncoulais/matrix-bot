from bot.registry import Group

delete = Group("delete", description="Gestion des suppressions", admin_only=True)

from . import room
from . import message
from . import empty
