from django.shortcuts import render
from django.views import View
import itertools

class StoneSortingView(View):
    template_name = 'core/sorting.html'
    
    def get(self, request):
        containers = request.session.get('containers', [])
        stones = request.session.get('stones', [])
        sorting_result = request.session.get('sorting_result', None)
        
        context = {
            'containers': containers,
            'stones': stones,
            'sorting_result': sorting_result,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        containers = request.session.get('containers', [])
        stones = request.session.get('stones', [])
        
        if 'add_container' in request.POST:
            container_name = request.POST.get('container_name', f'Контейнер {len(containers) + 1}')
            target_mass = float(request.POST.get('target_mass', 0))
            tolerance = float(request.POST.get('tolerance', 0))
            
            if target_mass > 0 and tolerance > 0:
                containers.append({
                    'id': len(containers) + 1,
                    'name': container_name,
                    'target_mass': target_mass,
                    'tolerance': tolerance,
                    'min_mass': target_mass - tolerance,
                    'max_mass': target_mass + tolerance,
                })
                request.session['containers'] = containers
        
        elif 'add_stone' in request.POST:
            mass = float(request.POST.get('mass', 0))
            
            if mass > 0:
                # Автоматическая нумерация и цвет
                next_number = len(stones) + 1
                colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
                color = colors[(next_number - 1) % len(colors)]
                
                stones.append({
                    'number': next_number,
                    'mass': mass,
                    'color': color,
                    'color_display': self.get_color_display(color)
                })
                request.session['stones'] = stones
        
        elif 'sort_stones' in request.POST:
            if containers and stones:
                sorting_result = self.distribute_stones(stones, containers)
                request.session['sorting_result'] = sorting_result
            else:
                request.session['sorting_result'] = {
                    'success': False,
                    'message': 'Добавьте контейнеры и камни для сортировки'
                }
        
        elif 'remove_container' in request.POST:
            container_id = int(request.POST.get('container_id'))
            containers = [c for c in containers if c['id'] != container_id]
            request.session['containers'] = containers
            # Очищаем результат сортировки при изменении контейнеров
            if 'sorting_result' in request.session:
                del request.session['sorting_result']
        
        elif 'remove_stone' in request.POST:
            stone_number = int(request.POST.get('stone_number'))
            stones = [s for s in stones if s['number'] != stone_number]
            request.session['stones'] = stones
            # Очищаем результат сортировки при изменении камней
            if 'sorting_result' in request.session:
                del request.session['sorting_result']
        
        elif 'clear_all' in request.POST:
            request.session['containers'] = []
            request.session['stones'] = []
            if 'sorting_result' in request.session:
                del request.session['sorting_result']
        
        return self.get(request)
    
    def get_color_display(self, color):
        color_map = {
            'red': 'Красный',
            'blue': 'Синий', 
            'green': 'Зеленый',
            'yellow': 'Желтый',
            'purple': 'Фиолетовый',
            'orange': 'Оранжевый',
        }
        return color_map.get(color, 'Красный')
    
    def distribute_stones(self, stones, containers):
        """Распределяет камни по контейнерам используя рекурсивный поиск"""
        # Сортируем контейнеры по целевой массе (от большего к меньшему)
        sorted_containers = sorted(containers, key=lambda x: x['target_mass'], reverse=True)
        
        # Пытаемся найти распределение
        result = self.find_distribution(stones, sorted_containers, 0, {})
        
        if result:
            return {
                'success': True,
                'distribution': result
            }
        else:
            return {
                'success': False,
                'message': 'Не удалось найти подходящее распределение камней по контейнерам'
            }
    
    def find_distribution(self, remaining_stones, containers, container_index, current_assignment):
        """Рекурсивно ищет распределение камней по контейнерам"""
        if container_index >= len(containers):
            # Все контейнеры заполнены
            return current_assignment
        
        current_container = containers[container_index]
        
        # Находим все возможные комбинации камней для текущего контейнера
        valid_combinations = self.find_valid_combinations(remaining_stones, current_container)
        
        for combo in valid_combinations:
            # Создаем копии для рекурсивного вызова
            new_remaining = [s for s in remaining_stones if s not in combo['stones']]
            new_assignment = current_assignment.copy()
            new_assignment[current_container['id']] = {
                'container': current_container,
                'stones': combo['stones'],
                'total_mass': combo['total_mass'],
                'deviation': combo['deviation']
            }
            
            # Рекурсивно заполняем оставшиеся контейнеры
            result = self.find_distribution(new_remaining, containers, container_index + 1, new_assignment)
            if result:
                return result
        
        return None
    
    def find_valid_combinations(self, stones, container):
        """Находит все валидные комбинации камней для контейнера"""
        valid_combinations = []
        min_mass = container['min_mass']
        max_mass = container['max_mass']
        target_mass = container['target_mass']
        
        # Перебираем комбинации разного размера
        for r in range(1, min(6, len(stones) + 1)):  # Ограничиваем размер комбинаций
            for combination in itertools.combinations(stones, r):
                total_mass = sum(stone['mass'] for stone in combination)
                
                if min_mass <= total_mass <= max_mass:
                    valid_combinations.append({
                        'stones': list(combination),
                        'total_mass': total_mass,
                        'deviation': abs(total_mass - target_mass)
                    })
        
        # Сортируем по отклонению от целевой массы
        valid_combinations.sort(key=lambda x: x['deviation'])
        return valid_combinations[:20]  # Ограничиваем количество комбинаций