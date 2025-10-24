import os
import sys
import glob
import shutil
import subprocess
from typing import List, Tuple
from solver import solve_instance


def find_instances() -> List[str]:
    """Retourne la liste de tous les fichiers d'instances (.txt) à traiter."""
    roots = [
        os.path.join(os.path.dirname(__file__), "instances"),
        os.path.join(os.path.dirname(__file__), "instances_exemple"),
    ]
    files: List[str] = []
    for root in roots:
        if os.path.isdir(root):
            files.extend(glob.glob(os.path.join(root, "*.txt")))
    return sorted(files)


def stage_for_checker(instance_path: str, solution_path: str, checker_dir: str) -> Tuple[str, str]:
    """Copie l'instance et sa solution dans le répertoire du checker avec les bons noms."""
    os.makedirs(checker_dir, exist_ok=True)
    base = os.path.basename(instance_path)  # e.g., instance_....txt
    root, _ = os.path.splitext(base)
    inst_dst = os.path.join(checker_dir, base)
    sol_dst = os.path.join(checker_dir, f"{root}_sol.txt")
    shutil.copyfile(instance_path, inst_dst)
    shutil.copyfile(solution_path, sol_dst)
    return inst_dst, sol_dst


def run_checker_for(instance_root: str, checker_dir: str) -> int:
    """Exécute le checker pour une instance (root sans extension). Retourne le code de sortie."""
    try:
        res = subprocess.run([
            "java", "-jar", "CheckerBatchingPicking.jar", instance_root
        ], cwd=checker_dir)
        return res.returncode
    except FileNotFoundError:
        print("Java introuvable: assurez-vous que Java est installé et accessible dans le PATH.")
        return 127


def main():
    # Si un chemin est passé, traiter uniquement cette instance; sinon, traiter toutes.
    to_process: List[str]
    if len(sys.argv) >= 2:
        to_process = [sys.argv[1]]
    else:
        to_process = find_instances()
        if not to_process:
            print("Aucune instance trouvée dans 'instances' ou 'instances_exemple'.")
            sys.exit(1)

    checker_dir = os.path.join(os.path.dirname(__file__), "checker")

    results = []  # (instance_base, returncode)
    for i, inst_path in enumerate(to_process, 1):
        base = os.path.basename(inst_path)
        root, _ = os.path.splitext(base)
        print(f"[{i}/{len(to_process)}] Solving {base} …")
        out = solve_instance(inst_path)
        print(f"  -> {out}")
        sol_path = out.write_solution_file()
        print(f"  -> Solution written: {sol_path}")
        # Copier vers checker
        stage_for_checker(inst_path, sol_path, checker_dir)
        # Lancer le checker
        rc = run_checker_for(root, checker_dir)
        status = "OK" if rc == 0 else f"FAIL({rc})"
        print(f"  -> Checker: {status}")
        results.append((base, rc))

    # Résumé
    ok = sum(1 for _, rc in results if rc == 0)
    ko = len(results) - ok
    print("\nRésumé checker:")
    print(f"  Total: {len(results)}  OK: {ok}  FAIL: {ko}")
    if ko:
        print("  Échecs:")
        for base, rc in results:
            if rc != 0:
                print(f"   - {base} (rc={rc})")


if __name__ == "__main__":
    main()
