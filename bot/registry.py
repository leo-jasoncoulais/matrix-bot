"""
Registre central des commandes du bot.

Deux façons de déclarer des commandes :

1. Commande simple :

    from bot.registry import command

    @command("ping", description="Verifier que le bot est en ligne")
    async def cmd_ping(room, event, args):
        ...

2. Groupe de sous-commandes :

    from bot.registry import Group

    delete = Group("delete", description="Gestion des suppressions")

    @delete.command("room", description="Supprimer une room")
    async def cmd_delete_room(room, event, args):
        ...

Le préfixe est ajouté automatiquement par le registry.
"""

PREFIX = "!" # NE PAS MODIFIER

commands = {}
command_descriptions = {}


def command(name, description=""):
    """Décorateur : enregistre une fonction comme handler pour PREFIX+name."""
    full = f"{PREFIX}{name}"
    print(f"Enregistrement de la commande {full}...")
    def decorator(func):
        commands[full] = func
        if description:
            command_descriptions[full] = description
        return func
    return decorator


class Group:
    def __init__(self, name, description="", admin_only=False):
        self.name = name
        self.full_name = f"{PREFIX}{name}"
        self.description = description
        self.admin_only = admin_only
        self._subcommands = {}
        commands[self.full_name] = self
        if description:
            command_descriptions[self.full_name] = description
        print(f"Enregistrement du groupe {self.full_name}...")

    def command(self, subcommand_name, description=""):
        def decorator(func):
            self._subcommands[subcommand_name] = {
                "handler": func,
                "description": description,
            }
            print(f"  Sous-commande {self.full_name} {subcommand_name}...")
            return func
        return decorator

    async def execute(self, subcommand, room, event, args):
        if self.admin_only:
            from bot.admin import is_server_admin
            if not is_server_admin(event.sender):
                return
        entry = self._subcommands.get(subcommand)
        if entry:
            await entry["handler"](room, event, args)
        else:
            await self.show_help(room)

    async def show_help(self, room):
        from bot.utils import send
        lines = [f"{self.full_name} <sous-commande> ..."]
        if self.description:
            lines.append(self.description)
        lines.append("")
        for name, entry in sorted(self._subcommands.items()):
            desc = entry["description"]
            lines.append(f"  {name}    {desc}" if desc else f"  {name}")
        await send(room.room_id, "\n".join(lines))


async def dispatch(command_name, room, event, args):
    handler = commands.get(command_name)
    if handler is None:
        return
    if isinstance(handler, Group):
        if args:
            await handler.execute(args[0], room, event, args[1:])
        else:
            await handler.show_help(room)
    else:
        await handler(room, event, args)
