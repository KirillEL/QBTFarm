from ..config import CONFIG


def update_config(config):
    config['FLAG_FORMAT'] = input("Введите новый формат флага: ")
    config['SYSTEM_URL'] = input("Введите новый URL системы: ")
    config['SYSTEM_TOKEN'] = input("Введите новый токен системы: ")

    new_pattern = input("Введите новый паттерн для '10.0.{}.1': ")
    count_teams = int(input("Введите кол-во комманд: "))
    config['TEAMS'] = {'Team #{}'.format(i): new_pattern.format(i) for i in range(1, count_teams)}

    if __name__ == '__main__':
        update_config(CONFIG)
