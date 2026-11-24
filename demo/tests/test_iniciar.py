"""Testa o iniciar.sh com docker, cloudflared, gh e curl falsos. Uso: python3 -m unittest -v"""
import os
import signal
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "iniciar.sh"

FAKES = {
    "docker": """
echo "docker $*" >> "$FAKE/calls"
case "$1" in
  build) [ ! -e "$FAKE/build_fails" ] ;;
  image) [ ! -e "$FAKE/no_image" ] ;;
  restart) rm -f "$FAKE/api_down" ;;
esac
""",
    "cloudflared": """
echo "cloudflared $*" >> "$FAKE/calls"
[ -e "$FAKE/tunnel_fails" ] && { echo "failed to request quick Tunnel" >&2; exec sleep 300; }
n=$(( $(cat "$FAKE/tunnels" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$FAKE/tunnels"
echo $$ > "$FAKE/tunnel_pid_$n"
echo "INF |  https://api.trycloudflare.com  |" >&2
echo "INF |  https://fake-link-$n.trycloudflare.com  |" >&2
[ -e "$FAKE/tunnel_hangs" ] && { trap '' TERM; while :; do sleep 0.1; done; }
exec sleep 300
""",
    "gh": """
echo "gh $*" >> "$FAKE/calls"
[ -e "$FAKE/gh_down" ] && { echo "error connecting to api.github.com" >&2; exit 1; }
case "$*" in
  "gist create"*)
    for arg in "$@"; do [ -f "$arg" ] && cp "$arg" "$FAKE/gist.md"; done
    rm -f "$FAKE/gist_deleted"
    echo "https://gist.github.com/someone/abc123" ;;
  *PATCH*)
    [ -e "$FAKE/update_fails" ] && { echo "gh: Bad Gateway (HTTP 502)" >&2; exit 1; }
    [ -e "$FAKE/gist_deleted" ] && { echo "gh: Not Found (HTTP 404)" >&2; exit 1; }
    for arg in "$@"; do case "$arg" in *=@*) cp "${arg#*=@}" "$FAKE/gist.md" ;; esac; done
    echo "https://gist.github.com/someone/abc123" ;;
esac
""",
    "curl": """
for url in "$@"; do :; done
case "$url" in
  http://127.0.0.1*)
    [ -e "$FAKE/api_fails_once" ] && { rm "$FAKE/api_fails_once"; exit 7; }
    [ -e "$FAKE/api_down" ] && exit 7 ;;
  *fake-link-*)
    echo "curl $*" >> "$FAKE/calls"
    n=${url#*fake-link-}; n=${n%%.*}
    [ -e "$FAKE/internet_down" ] && exit 6
    [ -e "$FAKE/link_down_$n" ] && exit 22 ;;
  *) [ -e "$FAKE/internet_down" ] && exit 6 ;;
esac
echo '{"message":"pong"}'
""",
    "systemd-inhibit": """
echo "systemd-inhibit $*" >> "$FAKE/calls"
echo $$ > "$FAKE/inhibit_pid"
exec sleep 300
""",
}


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return Path(f"/proc/{pid}/stat").read_text().split()[2] != "Z"


class IniciarTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fake = Path(self.tmp.name) / "fake"
        self.state = Path(self.tmp.name) / "state"
        bin_dir = Path(self.tmp.name) / "bin"
        self.fake.mkdir()
        bin_dir.mkdir()
        for name, body in FAKES.items():
            path = bin_dir / name
            path.write_text(f"#!/usr/bin/env bash\n{body}")
            path.chmod(path.stat().st_mode | stat.S_IEXEC)
        self.env = {
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "CLOUDFLARED": str(bin_dir / "cloudflared"),
            "FAKE": str(self.fake),
            "ESTADO_DIR": str(self.state),
            "INTERVALO": "0.2",
            "PASSO": "0.05",
            "ESPERA": "2",  # o bash conta segundos inteiros; com 1 o prazo pode acabar na hora
        }
        self.procs = []

    def tearDown(self):
        for proc in self.procs:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(10)
                except subprocess.TimeoutExpired:
                    proc.kill()
        self.tmp.cleanup()

    def start(self):
        path = Path(self.tmp.name) / f"output-{len(self.procs)}"
        with path.open("w") as output:
            proc = subprocess.Popen(
                ["bash", str(SCRIPT)], env=self.env, start_new_session=True,
                stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
            )
        proc.output = path.read_text
        self.procs.append(proc)
        return proc

    def flag(self, name, on=True):
        path = self.fake / name
        path.touch() if on else path.unlink(missing_ok=True)

    def calls(self, prefix):
        path = self.fake / "calls"
        lines = path.read_text().splitlines() if path.exists() else []
        return [line for line in lines if line.startswith(prefix)]

    def gist(self):
        path = self.fake / "gist.md"
        return path.read_text() if path.exists() else ""

    def wait(self, condition, what, seconds=8):
        limit = time.time() + seconds
        while time.time() < limit:
            if condition():
                return
            time.sleep(0.05)
        self.fail(f"não aconteceu: {what}\n{(self.fake / 'calls').read_text() if (self.fake / 'calls').exists() else ''}")

    def start_ready(self):
        proc = self.start()
        self.wait(lambda: "fake-link-1" in self.gist(), "gist com o primeiro link")
        return proc

    def test_first_start_creates_a_secret_gist_and_prints_the_addresses(self):
        proc = self.start_ready()
        create = self.calls("gh gist create")
        self.assertEqual(len(create), 1)
        self.assertNotIn("--public", create[0])
        self.assertNotIn("-p ", create[0])
        self.assertIn("https://fake-link-1.trycloudflare.com", self.gist())
        self.assertIn("boisterous-moxie-6297bc.netlify.app", self.gist())
        self.assertNotIn("api.trycloudflare.com", self.gist())
        self.assertEqual((self.state / "gist").read_text().strip(), "https://gist.github.com/someone/abc123")
        self.wait(lambda: "Ctrl+C encerra" in proc.output(), "endereços na tela")
        self.assertIn("Endereço fixo (Canva):  https://gist.github.com/someone/abc123", proc.output())
        self.assertIn("https://fake-link-1.trycloudflare.com", proc.output())

    def test_container_is_locked_down_and_only_listens_locally(self):
        self.start_ready()
        run = self.calls("docker run")[0]
        for option in ["--read-only", "--cap-drop ALL", "no-new-privileges", "--memory", "--pids-limit"]:
            self.assertIn(option, run)
        self.assertIn("-p 127.0.0.1:8010:8000", run)
        self.assertNotIn("-v ", run)
        self.assertNotIn("--restart", run)

    def test_second_start_reuses_the_same_gist(self):
        self.start_ready().terminate()
        self.wait(lambda: self.procs[0].poll() is not None, "fim da primeira execução")
        self.start()
        self.wait(lambda: "fake-link-2" in self.gist(), "gist com o segundo link")
        self.assertEqual(len(self.calls("gh gist create")), 1)
        self.assertTrue(any("/gists/abc123" in call for call in self.calls("gh api")))

    def test_deleted_gist_is_replaced_with_a_warning(self):
        self.start_ready().terminate()
        self.wait(lambda: self.procs[0].poll() is not None, "fim da primeira execução")
        self.flag("gist_deleted")
        proc = self.start()
        self.wait(lambda: "endereço fixo mudou" in proc.output(), "aviso de endereço novo")
        self.assertEqual(len(self.calls("gh gist create")), 2)

    def test_one_api_failure_does_not_restart_the_container(self):
        self.start_ready()
        self.flag("api_fails_once")
        self.wait(lambda: not (self.fake / "api_fails_once").exists(), "verificação com falha")
        time.sleep(1)
        self.assertEqual(self.calls("docker restart"), [])

    def test_two_api_failures_restart_the_container_and_keep_the_link(self):
        self.start_ready()
        self.flag("api_down")
        self.wait(lambda: self.calls("docker restart"), "reinício do contêiner")
        time.sleep(1)
        self.assertEqual(len(self.calls("cloudflared")), 1)

    def test_dead_link_opens_another_tunnel_and_updates_the_gist(self):
        self.start_ready()
        old = int((self.fake / "tunnel_pid_1").read_text())
        self.flag("link_down_1")
        self.wait(lambda: "fake-link-2" in self.gist(), "gist com o novo link")
        self.assertNotIn("fake-link-1", self.gist())
        self.wait(lambda: not alive(old), "fim do túnel antigo")

    def test_tunnel_that_ignores_the_stop_request_is_killed(self):
        self.flag("tunnel_hangs")
        proc = self.start_ready()
        old = int((self.fake / "tunnel_pid_1").read_text())
        self.flag("link_down_1")
        self.wait(lambda: "fake-link-2" in self.gist(), "gist com o novo link")
        self.wait(lambda: not alive(old), "fim do túnel travado")
        current = int((self.fake / "tunnel_pid_2").read_text())
        proc.terminate()
        proc.wait(10)
        self.assertFalse(alive(current))

    def test_killed_tunnel_is_replaced(self):
        self.start_ready()
        os.kill(int((self.fake / "tunnel_pid_1").read_text()), signal.SIGKILL)
        self.wait(lambda: "fake-link-2" in self.gist(), "gist com o novo link")

    def test_internet_outage_keeps_the_link(self):
        self.start_ready()
        self.flag("internet_down")
        time.sleep(2)
        self.flag("internet_down", on=False)
        time.sleep(1)
        self.assertEqual(len(self.calls("cloudflared")), 1)
        self.assertIn("fake-link-1", self.gist())

    def test_old_tunnel_stays_while_the_new_one_does_not_answer(self):
        self.start_ready()
        old = int((self.fake / "tunnel_pid_1").read_text())
        self.flag("tunnel_fails")
        self.flag("link_down_1")
        self.wait(lambda: len(self.calls("cloudflared")) >= 2, "tentativa de novo túnel")
        time.sleep(1.5)
        self.assertTrue(alive(old))
        self.assertIn("fake-link-1", self.gist())
        self.flag("tunnel_fails", on=False)
        self.wait(lambda: "fake-link-2" in self.gist(), "gist com o novo link", 12)

    def test_gist_update_is_retried_when_github_is_down(self):
        self.start_ready()
        self.flag("gh_down")
        self.flag("link_down_1")
        self.wait(lambda: len(self.calls("cloudflared")) >= 2, "novo túnel")
        time.sleep(1)
        self.assertIn("fake-link-1", self.gist())
        self.flag("gh_down", on=False)
        self.wait(lambda: "fake-link-2" in self.gist(), "gist atualizado depois")

    def test_failed_update_never_changes_the_fixed_address(self):
        proc = self.start_ready()
        self.flag("update_fails")
        self.flag("link_down_1")
        self.wait(lambda: len(self.calls("gh api")) >= 2, "tentativas de atualização")
        self.assertEqual(len(self.calls("gh gist create")), 1)
        self.assertNotIn("endereço fixo mudou", proc.output())
        self.flag("update_fails", on=False)
        self.wait(lambda: "fake-link-2" in self.gist(), "gist atualizado depois")

    def test_github_down_at_start_still_serves_and_retries(self):
        self.flag("gh_down")
        self.start()
        self.wait(lambda: len(self.calls("gh gist create")) >= 1, "primeira tentativa")
        self.flag("gh_down", on=False)
        self.wait(lambda: "fake-link-1" in self.gist(), "gist criado depois")

    def test_every_stop_signal_cleans_up(self):
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            with self.subTest(sig.name):
                for name in ("calls", "gist.md", "tunnels"):
                    (self.fake / name).unlink(missing_ok=True)
                proc = self.start_ready()
                tunnel = int((self.fake / "tunnel_pid_1").read_text())
                inhibit = int((self.fake / "inhibit_pid").read_text())
                removed = len(self.calls("docker rm"))
                proc.send_signal(sig)
                proc.wait(10)
                self.assertFalse(alive(tunnel))
                self.assertFalse(alive(inhibit))
                self.assertGreater(len(self.calls("docker rm")), removed)
                self.assertIn("não está no ar", self.gist())
                self.assertNotIn("fake-link-1", self.gist())

    def test_second_instance_is_refused_and_leaves_the_first_alone(self):
        self.start_ready()
        before = len(self.calls("docker"))
        second = self.start()
        self.assertNotEqual(second.wait(10), 0)
        self.assertIn("já está rodando", second.output())
        self.assertEqual(len(self.calls("docker")), before)
        self.assertIsNone(self.procs[0].poll())

    def test_tunnel_failure_at_start_exits_and_cleans_up(self):
        self.flag("tunnel_fails")
        proc = self.start()
        self.assertNotEqual(proc.wait(15), 0)
        self.assertGreaterEqual(len(self.calls("docker rm")), 2)
        self.assertEqual(self.calls("gh gist create"), [])

    def test_failed_build_falls_back_to_the_existing_image(self):
        self.flag("build_fails")
        self.start_ready()

    def test_failed_build_without_image_stops(self):
        self.flag("build_fails")
        self.flag("no_image")
        proc = self.start()
        self.assertNotEqual(proc.wait(10), 0)
        self.assertEqual(self.calls("docker run"), [])

    def test_computer_does_not_sleep_while_running(self):
        self.start_ready()
        self.assertIn("sleep", self.calls("systemd-inhibit")[0])


if __name__ == "__main__":
    unittest.main()
