from django.db.models import Count, Q
from users.models import User
from tasks.models import Task


def get_active_statuses():
    """Возвращает список активных статусов задач"""
    return [Task.Status.IN_PROCESS, Task.Status.UNDER_REVIEW, Task.Status.NEEDS_CLARIFICATION]


def get_employees_with_task_count():
    """Возвращает сотрудников с количеством активных задач"""
    active_statuses = get_active_statuses()
    return User.objects.annotate(
        active_tasks_count=Count('executor_tasks',
                                 filter=Q(executor_tasks__status__in=active_statuses))
    ).order_by('-active_tasks_count')


def get_employee_stats():
    """Возвращает статистику загрузки сотрудников"""
    active_statuses = get_active_statuses()
    return User.objects.annotate(
        active_tasks_count=Count('executor_tasks',
                                 filter=Q(executor_tasks__status__in=active_statuses))
    ).values('id', 'active_tasks_count')


def get_important_tasks():
    """Возвращает важные задачи (не начатые, но с активными подзадачами)"""
    active_statuses = get_active_statuses()
    return Task.objects.filter(
        status=Task.Status.CREATED,
        subtasks__status__in=active_statuses
    ).distinct()


def get_min_workload(employee_stats):
    """Возвращает минимальную загрузку из статистики сотрудников"""
    return min([stat['active_tasks_count'] for stat in employee_stats], default=0)


def get_potential_executors(task, employee_stats, min_load):
    """Возвращает список потенциальных исполнителей для задачи"""
    potential_executors = []
    added_emails = set()
    active_statuses = get_active_statuses()

    # Вариант 1: Исполнитель родительской задачи
    if task.parent and task.parent.executor:
        parent_executor = task.parent.executor
        executor_load = next(
            (stat['active_tasks_count'] for stat in employee_stats
             if stat['id'] == parent_executor.id), 0
        )
        if (executor_load <= min_load + 2 and
                parent_executor != task.executor and
                parent_executor != task.owner and
                parent_executor.email not in added_emails):
            potential_executors.append(parent_executor)
            added_emails.add(parent_executor.email)

    # Вариант 2: Наименее загруженные сотрудники
    least_loaded_employees = User.objects.annotate(
        active_tasks_count=Count('executor_tasks',
                                 filter=Q(executor_tasks__status__in=active_statuses))
    ).filter(active_tasks_count__lte=min_load + 2).order_by('active_tasks_count')

    for employee in least_loaded_employees[:5]:
        if (employee != task.executor and
                employee.email not in added_emails):
            potential_executors.append(employee)
            added_emails.add(employee.email)

    return potential_executors


def format_employee_data(employee):
    """Форматирует данные сотрудника для ответа API"""
    return {
        'id': employee.id,
        'surname': employee.surname,
        'name': employee.name,
        'patronymic': employee.patronymic,
        'email': employee.email,
        'position': employee.position,
        'active_tasks_count': employee.active_tasks_count,
        'total_tasks_count': employee.executor_tasks.count()
    }


def format_executor_name(employee):
    """Форматирует ФИО сотрудника"""
    parts = [employee.surname, employee.name]
    if employee.patronymic:
        parts.append(employee.patronymic)
    return ' '.join(parts).strip()


def format_important_task_data(task, potential_executors):
    """Форматирует данные важной задачи для ответа API"""
    return {
        'Важная задача': task.task_name,
        'Срок до': task.deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'Возможные исполнители': [
            format_executor_name(executor) for executor in potential_executors
        ],
    }
