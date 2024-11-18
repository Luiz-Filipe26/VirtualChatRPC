import rpyc
from rpyc.utils.helpers import BgServingThread

SERVER_IP = 'localhost'
SERVER_PORT = 18861

# Conectando ao servidor RPC
proxy = rpyc.connect(SERVER_IP, SERVER_PORT, config={'allow_public_attrs': True})

# Ativando o BgServingThread para processar callbacks
bg_thread = BgServingThread(proxy)


def menu():
    print("\nEscolha uma opção:")
    print("1. Entrar na sala")
    print("2. Sair da sala")
    print("3. Enviar mensagem para todos")
    print("4. Listar mensagens recebidas")
    print("5. Enviar mensagem para um usuário específico")
    print("6. Listar usuários na sala")
    print("7. Sair")


def new_message_callback(sender_name, message):
    print(f"\nNova mensagem de {sender_name}: {message}")


def entrar_na_sala(user_name):
    response = proxy.root.entrar_na_sala(user_name)
    print(f"{user_name} entrou na sala.")


def sair_da_sala(user_name):
    proxy.root.sair_da_sala(user_name)
    print(f"{user_name} saiu da sala.")


def enviar_mensagem(user_name):
    message = input("Digite sua mensagem: ")
    response = proxy.root.enviar_mensagem(user_name, message)
    if response == "sender_not_in_room_error":
        print("Erro: Você não está na sala.")
    else:
        print("Mensagem enviada para todos os usuários na sala.")


def listar_mensagens(user_name):
    messages = proxy.root.listar_mensagens(user_name)
    if messages:
        print("\nMensagens recebidas:")
        for msg in messages:
            print(f"- {msg}")
    else:
        print("Nenhuma mensagem recebida ainda.")


def enviar_mensagem_usuario(user_name):
    recipient_name = input("Digite o nome do destinatário: ")
    message = input("Digite sua mensagem: ")
    response = proxy.root.enviar_mensagem_usuario(user_name, recipient_name, message)
    if response == "sender_not_in_room_error":
        print("Erro: Você não está na sala.")
    elif response == "recipient_not_in_room_error":
        print(f"Erro: O usuário {recipient_name} não está na sala.")
    elif response == "same_user_error":
        print("Erro: Você não pode enviar uma mensagem para si mesmo.")
    else:
        print(f"Mensagem enviada para {recipient_name}.")


def listar_usuarios():
    users = proxy.root.listar_usuarios()
    print("\nUsuários na sala:")
    for user in users:
        print(f"- {user}")


if __name__ == "__main__":
    # Solicita o nome do usuário ao iniciar o programa
    user_name = input("Digite seu nome de usuário: ")

    # Tenta ingressar no sistema com o nome escolhido
    response = proxy.root.ingressar_no_sistema(user_name, new_message_callback)
    if response == "user_already_exists":
        print("Erro: O nome de usuário já existe. Tente outro.")
        exit(1)

    print(f"Usuário {user_name} ingressou com sucesso. Agora você pode interagir com a sala.")

    try:
        while True:
            menu()
            option = input("Escolha uma opção: ")

            if option == "1":
                entrar_na_sala(user_name)

            elif option == "2":
                sair_da_sala(user_name)

            elif option == "3":
                enviar_mensagem(user_name)

            elif option == "4":
                listar_mensagens(user_name)

            elif option == "5":
                enviar_mensagem_usuario(user_name)

            elif option == "6":
                listar_usuarios()

            elif option == "7":
                print("Saindo...")
                break

            else:
                print("Opção inválida, tente novamente.")

    finally:
        # Finaliza o BgServingThread corretamente
        bg_thread.stop()
        proxy.close()
