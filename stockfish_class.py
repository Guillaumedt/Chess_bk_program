import subprocess

class Stockfish:
    def __init__(self, path):
        self.process = subprocess.Popen(
            path,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1,
        )
        self._send_command("uci")
        self._wait_for("uciok")
        self._send_command("isready")
        self._wait_for("readyok")

    def _send_command(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def _wait_for(self, keyword):
        while True:
            text = self.process.stdout.readline().strip()
            if keyword in text:
                break

    def set_position(self, fen):
        self._send_command(f"position fen {fen}")

    def go(self, movetime=100):
        self._send_command(f"go movetime {movetime}")

    def get_eval(self):
        while True:
            text = self.process.stdout.readline().strip()
            if text.startswith("info") and "score cp" in text:
                parts = text.split()
                if "score" in parts:
                    i = parts.index("score")
                    if parts[i+1] == "cp":
                        return int(parts[i+2]) / 100  # score centipawns → pawns
                    elif parts[i+1] == "mate":
                        mate_in = int(parts[i+2])
                        # Eval mate = grande valeur avec signe
                        return 10000 if mate_in > 0 else -10000
            elif text.startswith("bestmove"):
                break
        return None

    def quit(self):
        self._send_command("quit")
        self.process.terminate()

    def go_depth(self, depth=15):
        self._send_command(f"go depth {depth}")