#!/usr/bin/env python3
"""Script para executar SQL no Supabase"""
import os
import sys

try:
    import psycopg2
except ImportError:
    print("Instalando psycopg2...")
    os.system("pip install psycopg2-binary --quiet")
    import psycopg2

# Configurações do banco
DB_HOST = "db.safet1ps.supabase.co"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8"

def main():
    print("🔗 Conectando ao Supabase...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode="require"
        )
        print("✅ Conexão estabelecida!\n")
        
        # Ler o arquivo SQL
        sql_file = "CREATE_TABLES_SUPABASE.sql"
        print(f"📄 Lendo script: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Executar o script
        cursor = conn.cursor()
        print("⏳ Executando script SQL...\n")
        
        # Dividir o script em statements individuais (separados por ";")
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            try:
                cursor.execute(statement)
                print(f"✅ Statement {i}/{len(statements)}: OK")
            except psycopg2.Error as e:
                if "already exists" in str(e) or "CONFLICT" in str(e):
                    print(f"⚠️  Statement {i}/{len(statements)}: Já existe (ignorado)")
                else:
                    print(f"❌ Statement {i}/{len(statements)}: ERRO")
                    print(f"   {e}")
        
        # Confirmar as transações
        conn.commit()
        cursor.close()
        print("\n🎉 Script executado com sucesso!\n")
        
        # Verificar as tabelas criadas
        print("📊 Verificando tabelas criadas...\n")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        
        tables = cursor.fetchall()
        print(f"Total de tabelas: {len(tables)}\n")
        
        for table_name, in tables:
            print(f"  ✅ {table_name}")
        
        cursor.close()
        conn.close()
        
        print("\n✨ Tudo pronto! Seu banco está configurado para a API.")
        return 0
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        print("\nVerifique:")
        print("  - Host correto: db.safet1ps.supabase.co")
        print("  - Credenciais do banco")
        print("  - Conexão com internet")
        return 1
    
    except FileNotFoundError:
        print(f"❌ Arquivo {sql_file} não encontrado!")
        return 1
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
