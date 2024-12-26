# Это просто пример, как можно хранить статистику
stats = {
    'user': [],
    'mod': []
}

def get_stats(stat_type):
    return stats.get(stat_type, [])

def add_user_stat(user_data):
    stats['user'].append(user_data)

def add_mod_stat(mod_data):
    stats['mod'].append(mod_data)