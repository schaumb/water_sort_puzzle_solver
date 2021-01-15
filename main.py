import tube_solver
import tube_state_handler

if __name__ == "__main__":
    with tube_state_handler.Task() as task:
        while True:
            start_state = list(map(list, task.get_start_state()))
            task.apply_solution(map(lambda l: l[2], tube_solver.solve_state(start_state)))
