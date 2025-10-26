import cv2, time

print("🔍 Camera backend probe started...\n")

backs = [("DSHOW", cv2.CAP_DSHOW), ("MSMF", cv2.CAP_MSMF), ("ANY", cv2.CAP_ANY)]

for idx in range(0, 3):  # test up to 3 cameras
    for name, flag in backs:
        cap = cv2.VideoCapture(idx, flag)
        opened = cap.isOpened()
        ok, frame = (False, None)
        if opened:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            ok, frame = cap.read()
        print(f"idx={idx} backend={name:5} opened={opened} read={ok}")
        if ok and frame is not None:
            cv2.imshow(f"TEST idx={idx} {name}", frame)
            cv2.waitKey(500)  # show frame briefly
            cv2.destroyAllWindows()
        cap.release()

print("\n✅ Probe complete — note which combination says opened=True read=True.")
