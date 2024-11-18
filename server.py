import rpyc
from rpyc.utils.server import ThreadedServer
from enum import Enum

# Enum para mensagens de retorno
class ResponseMessages(Enum):
    USER_ALREADY_EXISTS = "user_already_exists"
    SENDER_NOT_IN_ROOM_ERROR = "sender_not_in_room_error"
    RECIPIENT_NOT_IN_ROOM_ERROR = "recipient_not_in_room_error"
    SAME_USER_ERROR = "same_user_error"
    MESSAGES_SENT = "messages_sent"

# Armazenamento de dados dos usuários
user_name_to_info = {}
users_in_room = set()

class ChatService(rpyc.Service):
    def exposed_ingressar_no_sistema(self, user_name, new_message_callback):
        if user_name in user_name_to_info:
            return ResponseMessages.USER_ALREADY_EXISTS
        user_name_to_info[user_name] = {'new_message_callback': new_message_callback, 'messages': []}
        print(f"Usuário '{user_name}' ingressou no sistema.")
        return user_name

    def exposed_entrar_na_sala(self, user_name):
        users_in_room.add(user_name)
        print(f"Usuário '{user_name}' entrou na sala.")
        return

    def exposed_sair_da_sala(self, user_name):
        users_in_room.remove(user_name)
        print(f"Usuário '{user_name}' saiu da sala.")
        return

    def exposed_enviar_mensagem(self, sender_name, message):
        if sender_name not in users_in_room:
            return ResponseMessages.SENDER_NOT_IN_ROOM_ERROR
        print(f"Usuário '{sender_name}' enviou uma mensagem para todos.")
        for recipient_name in users_in_room.copy():
            if recipient_name != sender_name:  # Evita enviar mensagem para si mesmo
                user_info = user_name_to_info[recipient_name]
                # Armazena a mensagem no destinatário
                user_info['messages'].append(f"{sender_name}: {message}")
                msg_callback = user_info['new_message_callback']
                msg_callback(sender_name, message)
        return ResponseMessages.MESSAGES_SENT

    def exposed_listar_mensagens(self, user_name):
        user_info = user_name_to_info.get(user_name)
        if user_info is None:
            return []
        print(f"Mensagens listadas para o usuário '{user_name}'.")
        return user_info.get('messages', [])

    def exposed_enviar_mensagem_usuario(self, sender_name, recipient_name, message):
        if sender_name not in users_in_room:
            return ResponseMessages.SENDER_NOT_IN_ROOM_ERROR
        if recipient_name not in users_in_room:
            return ResponseMessages.RECIPIENT_NOT_IN_ROOM_ERROR
        if sender_name == recipient_name:  # Verifica se o destinatário é o próprio remetente
            return ResponseMessages.SAME_USER_ERROR

        print(f"Usuário '{sender_name}' enviou uma mensagem para '{recipient_name}'.")
        # Armazena a mensagem no destinatário
        user_info = user_name_to_info[recipient_name]
        user_info['messages'].append(f"{sender_name}: {message}")
        msg_callback = user_info['new_message_callback']
        msg_callback(sender_name, message)
        return ResponseMessages.MESSAGES_SENT

    def exposed_listar_usuarios(self):
        print("Lista de usuários solicitada.")
        return list(users_in_room)

# Inicia o servidor
print("Servidor iniciado e aguardando conexões...")
threadedServer = ThreadedServer(ChatService, port=18861)
threadedServer.start()
