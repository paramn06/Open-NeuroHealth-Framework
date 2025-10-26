import os, sys, platform, importlib, glob
from textwrap import indent

def check_import(name):
    try:
        m = importlib.import_module(name)
        path = getattr(m, "__file__", "")
        ver = getattr(m, "__version__", "unknown")
        return True, f"{name}={ver} ({path})"
    except Exception as e:
        return False, f"{name} ❌  {e}"

def check_camera():
    try:
        import cv2
        caps = []
        for backend, code in [("DSHOW", cv2.CAP_DSHOW), ("MSMF", cv2.CAP_MSMF)]:
            cap = cv2.VideoCapture(0, code)
            ok = cap.isOpened()
            if ok:
                ok2,_ = cap.read()
                caps.append(f"{backend}: opened={ok} read={ok2}")
            else:
                caps.append(f"{backend}: opened=False")
            cap.release()
        return True, "; ".join(caps)
    except Exception as e:
        return False, f"camera ❌  {e}"

def main():
    print("🧠 Open NeuroHealth — System Check\n")
    print(f"Python: {sys.version.split()[0]}  ({sys.executable})")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Repo CWD: {os.getcwd()}\n")

    ok_cv2, msg_cv2 = check_import("cv2")
    ok_mp,  msg_mp  = check_import("mediapipe")
    ok_np,  msg_np  = check_import("numpy")
    ok_plt, msg_plt = check_import("matplotlib")

    print("Imports:")
    print("  " + msg_cv2)
    print("  " + msg_mp)
    print("  " + msg_np)
    print("  " + msg_plt)

    folders = ["app","modules","onf","data","tools","research","docs"]
    miss = [f for f in folders if not os.path.isdir(f)]
    print("\nFolders:")
    print("  present:", ", ".join([f for f in folders if f not in miss]) or "-")
    print("  missing:", ", ".join(miss) or "-")

    print("\nArtifacts:")
    logs  = glob.glob("data/logs/*.csv")
    exps  = glob.glob("data/exports/*.json")
    plots = glob.glob("data/plots/*.png")
    print(f"  CSV logs: {len(logs)}")
    print(f"  JSON exports: {len(exps)}")
    print(f"  PNG plots: {len(plots)}")

    ok_cam, msg_cam = check_camera()
    print("\nCamera:")
    print("  " + msg_cam)

    status = all([ok_cv2, ok_mp, ok_np, ok_plt, ok_cam])
    print("\n✅ Status: OK" if status else "\n⚠️ Status: Some checks failed")
    sys.exit(0 if status else 1)

if __name__ == "__main__":
    main()
