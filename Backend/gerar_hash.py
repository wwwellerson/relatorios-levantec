# Arquivo: backend/gerar_hash.py
from passlib.context import CryptContext

# Usa a mesma configuração do nosso arquivo auth.py
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

senha_para_criptografar = "senha123"

hash_gerado = pwd_context.hash(senha_para_criptografar)

print("\n--- HASH ARGON2 GERADO ---")
print(f"Para a senha: {senha_para_criptografar}")
print(f"O hash é: {hash_gerado}")
print("--- Copie a linha de hash abaixo e cole no seu usuarios.csv ---\n")