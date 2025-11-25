import random
import json

def generate_test_data(num_containers=3, mass_range=(1.0, 5.0), max_stones_per_container=5):
    """
    Генерирует тестовые данные: контейнеры и камни в каратах
    Камни генерируются так, чтобы их сумма попадала в диапазон контейнера
    
    Args:
        num_containers (int): количество контейнеров
        mass_range (tuple): диапазон масс контейнеров в каратах (мин, макс)
        max_stones_per_container (int): максимальное количество камней в контейнере
    """
    
    print("💎 Генератор тестовых данных для сортировки бриллиантов")
    print("=" * 55)
    
    # Генерируем контейнеры
    containers = generate_containers(num_containers, mass_range)
    
    # Генерируем камни для каждого контейнера
    all_stones = []
    container_stones = {}
    
    for container in containers:
        stones = generate_stones_for_container(container, max_stones_per_container)
        container_stones[container['id']] = stones
        all_stones.extend(stones)
    
    # Перемешиваем все камни
    random.shuffle(all_stones)
    
    # Выводим результаты
    print_results(containers, container_stones, all_stones)
    
    # Сохраняем в файл (опционально)
    save_to_file(containers, all_stones, container_stones)
    
    return containers, all_stones, container_stones

def generate_containers(num_containers, mass_range):
    """Генерирует контейнеры со случайными целевыми массами в каратах"""
    containers = []
    min_mass, max_mass = mass_range
    
    for i in range(num_containers):
        # Случайная целевая масса в заданном диапазоне
        target_mass = round(random.uniform(min_mass, max_mass), 2)
        
        # Погрешность фиксированная - 0.01 карата
        tolerance = 0.01
        
        container = {
            'id': i + 1,
            'name': f'Контейнер {i + 1}',
            'target_mass': target_mass,
            'tolerance': tolerance,
            'min_mass': round(target_mass - tolerance, 2),
            'max_mass': round(target_mass + tolerance, 2)
        }
        containers.append(container)
    
    return containers

def generate_stones_for_container(container, max_stones):
    """Генерирует камни для конкретного контейнера"""
    stones = []
    target_mass = container['target_mass']
    tolerance = container['tolerance']
    
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    color_names = {
        'red': 'Красный', 'blue': 'Синий', 'green': 'Зеленый',
        'yellow': 'Желтый', 'purple': 'Фиолетовый', 'orange': 'Оранжевый'
    }
    
    # Случайное количество камней в контейнере (от 2 до max_stones)
    num_stones = random.randint(2, max_stones)
    
    # Оставшаяся масса для распределения
    remaining_mass = target_mass
    
    for i in range(num_stones):
        if i == num_stones - 1:  # Последний камень
            # Последний камень добирает оставшуюся массу
            mass = round(remaining_mass, 2)
        else:
            # Случайная масса, но оставляем достаточно для остальных камней
            max_possible = remaining_mass - (num_stones - i - 1) * 0.01  # Минимум 0.01 на каждый оставшийся камень
            min_possible = 0.01
            if max_possible < min_possible:
                mass = min_possible
            else:
                mass = round(random.uniform(min_possible, max_possible), 2)
        
        # Добавляем небольшую случайность к массе в пределах погрешности
        if i < num_stones - 1:  # Не для последнего камня
            variation = random.uniform(-tolerance/2, tolerance/2)
            mass = round(mass + variation, 2)
            mass = max(0.01, mass)  # Минимальная масса 0.01 карата
        
        remaining_mass -= mass
        remaining_mass = max(0, remaining_mass)  # Не может быть отрицательной
        
        color = colors[len(stones) % len(colors)]
        
        stone = {
            'number': len(stones) + 1,  # Временный номер, будет пересчитан позже
            'mass': mass,
            'color': color,
            'color_display': color_names[color],
            'target_container': container['id']
        }
        stones.append(stone)
    
    # Проверяем, что сумма масс попадает в диапазон контейнера
    total_mass = sum(stone['mass'] for stone in stones)
    
    # Корректируем если нужно
    if not (container['min_mass'] <= total_mass <= container['max_mass']):
        # Немного корректируем последний камень
        adjustment = container['target_mass'] - total_mass
        stones[-1]['mass'] = round(stones[-1]['mass'] + adjustment, 2)
        total_mass = sum(stone['mass'] for stone in stones)
    
    return stones

def print_results(containers, container_stones, all_stones):
    """Выводит сгенерированные данные в консоль"""
    
    print("\n📦 СГЕНЕРИРОВАННЫЕ КОНТЕЙНЕРЫ:")
    print("-" * 45)
    for container in containers:
        stones = container_stones[container['id']]
        total_stones_mass = sum(stone['mass'] for stone in stones)
        
        print(f"🏷️  {container['name']}")
        print(f"   Целевая масса: {container['target_mass']:.2f} карат")
        print(f"   Погрешность: ±{container['tolerance']:.2f} карат")
        print(f"   Диапазон: {container['min_mass']:.2f} - {container['max_mass']:.2f} карат")
        print(f"   Камней: {len(stones)} шт.")
        print(f"   Фактическая масса камней: {total_stones_mass:.2f} карат")
        
        # Проверка попадания в диапазон
        if container['min_mass'] <= total_stones_mass <= container['max_mass']:
            print("   ✅ Масса камней попадает в диапазон контейнера")
        else:
            print("   ❌ Масса камней НЕ попадает в диапазон контейнера")
        print()
    
    print("\n💎 ВСЕ БРИЛЛИАНТЫ (перемешанные):")
    print("-" * 45)
    
    # Перенумеровываем камни
    for i, stone in enumerate(all_stones, 1):
        stone['number'] = i
    
    # Группируем камни по строкам для лучшего отображения
    for i in range(0, len(all_stones), 4):
        row_stones = all_stones[i:i+4]
        row_text = " | ".join(
            f"#{s['number']} ({s['mass']:.2f}кт, {s['color_display']})" 
            for s in row_stones
        )
        print(f"   {row_text}")
    
    # Статистика
    total_all_stones_mass = sum(stone['mass'] for stone in all_stones)
    total_containers_capacity = sum(container['max_mass'] for container in containers)
    
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   Всего бриллиантов: {len(all_stones)} шт.")
    print(f"   Общая масса всех бриллиантов: {total_all_stones_mass:.2f} карат")
    print(f"   Общая вместимость контейнеров: {total_containers_capacity:.2f} карат")
    
    if total_containers_capacity > 0:
        ratio = total_all_stones_mass / total_containers_capacity * 100
        print(f"   Соотношение: {ratio:.1f}%")

def save_to_file(containers, all_stones, container_stones, filename="test_data_carat.json"):
    """Сохраняет данные в JSON файл"""
    data = {
        'containers': containers,
        'stones': all_stones,
        'original_distribution': container_stones,
        'units': 'carats'
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Данные сохранены в файл: {filename}")

def quick_test():
    """Быстрый тест с минимальными данными в каратах"""
    print("🚀 БЫСТРЫЙ ТЕСТ В КАРАТАХ")
    print("=" * 35)
    
    containers, all_stones, container_stones = generate_test_data(
        num_containers=2,
        mass_range=(3.0, 8.0),
        max_stones_per_container=4
    )
    
    return containers, all_stones, container_stones

def standard_test():
    """Стандартный тест"""
    print("📊 СТАНДАРТНЫЙ ТЕСТ В КАРАТАХ")
    print("=" * 40)
    
    containers, all_stones, container_stones = generate_test_data(
        num_containers=3,
        mass_range=(5.0, 12.0),
        max_stones_per_container=6
    )
    
    return containers, all_stones, container_stones

if __name__ == "__main__":
    # Примеры использования для карат:
    
    print("💎 ЗАПУСК ГЕНЕРАТОРА ТЕСТОВЫХ ДАННЫХ В КАРАТАХ")
    print("=" * 55)
    
    # 1. Быстрый тест
    quick_test()
    
    # 2. Стандартный тест
    print("\n" + "="*50)
    standard_test()