
from database import criar_conexao

try:
    conexao = criar_conexao()
    print("Conexão realizada com sucesso!")

    conexao.close()

except Exception as erro:
    print("Não foi possível conectar:")
    print(repr(erro))
