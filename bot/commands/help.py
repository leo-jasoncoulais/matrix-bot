from bot.registry import command, commands, command_descriptions, Group, PREFIX
from bot.utils import send


@command("help", description="Afficher la liste des commandes disponibles")
async def cmd_help(room, event, args):
    lines = [f"Commandes disponibles ({PREFIX}help pour cette aide) :", ""]

    for name in sorted(commands.keys()):
        handler = commands[name]
        desc = command_descriptions.get(name, "")
        if isinstance(handler, Group):
            sub_names = " | ".join(sorted(handler._subcommands.keys()))
            line = f"  {name} <sous-commande>"
            if desc:
                line += f"  — {desc}"
            lines.append(line)
            for sub_name in sorted(handler._subcommands.keys()):
                sub_desc = handler._subcommands[sub_name]["description"]
                sub_line = f"    {sub_name}"
                if sub_desc:
                    sub_line += f"  — {sub_desc}"
                lines.append(sub_line)
        else:
            line = f"  {name}"
            if desc:
                line += f"  — {desc}"
            lines.append(line)

    await send(room.room_id, "\n".join(lines))
