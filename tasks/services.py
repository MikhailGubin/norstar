from tasks.utils import get_employees_with_task_count, format_employee_data, get_important_tasks, get_employee_stats, \
    get_min_workload, get_potential_executors, format_important_task_data


class EmployeeService:
    """Сервис для работы с сотрудниками"""

    @staticmethod
    def get_busy_employees():
        employees = get_employees_with_task_count()
        return [format_employee_data(employee) for employee in employees]


class TaskService:
    """Сервис для работы с задачами"""

    @staticmethod
    def get_important_tasks_with_suggestions():
        important_tasks = get_important_tasks()
        employee_stats = get_employee_stats()
        min_load = get_min_workload(employee_stats)

        result = []
        for task in important_tasks:
            potential_executors = get_potential_executors(task, employee_stats, min_load)
            task_data = format_important_task_data(task, potential_executors)
            result.append(task_data)

        return result
