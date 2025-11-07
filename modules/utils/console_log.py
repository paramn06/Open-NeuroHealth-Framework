class Console:
    # simple, emoji-free console to avoid Windows cp1252 issues
    @staticmethod
    def info(msg):  print(f"[INFO]  {msg}")
    @staticmethod
    def ok(msg):    print(f"[OK]    {msg}")
    @staticmethod
    def warn(msg):  print(f"[WARN]  {msg}")
    @staticmethod
    def err(msg):   print(f"[ERROR] {msg}")
