import sys
from solver import solve_instance


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_solver.py <path_to_instance>")
        sys.exit(1)

    filename = sys.argv[1]
    out = solve_instance(filename)
    print(f"Solution summary: {out}")
    path = out.write_solution_file()
    print(f"Solution written to: {path}")


if __name__ == "__main__":
    main()
