
def extract_command_parts(command: str, expected_parts: int) -> list[str] | None:
    """
    Divide o comando em partes e valida o formato.

    Args:
        command (str): O comando completo enviado pelo cliente.
        expected_parts (int): O número esperado de partes no comando.

    Returns:
        list[str] | None: Uma lista com as partes do comando ou None se o formato for inválido.
        :param command:
        :param expected_parts:
        :return:
    """
    parts = command.split(' ', expected_parts - 1)
    if len(parts) != expected_parts or not all(part.strip() for part in parts):
        return None
    return parts
