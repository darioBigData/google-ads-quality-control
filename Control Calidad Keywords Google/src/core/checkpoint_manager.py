import json
import os


class CheckpointManager:

    def __init__(self, path):
        self.path = path
        self.data = {"processed_keys": []}

        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        # Cargar si existe
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                # Si el fichero está corrupto, reiniciar
                self.data = {"processed_keys": []}

        # 🔥 Siempre trabajar con set internamente (más eficiente)
        self._processed_set = set(self.data.get("processed_keys", []))

    # =========================
    # SAVE
    # =========================
    def save(self):
        self.data["processed_keys"] = list(self._processed_set)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # =========================
    # CHECK
    # =========================
    def has_processed(self, key):
        return key in self._processed_set

    # =========================
    # MARK PROCESSED
    # =========================
    def mark_processed(self, key):
        if key not in self._processed_set:
            self._processed_set.add(key)
            self.save()

    # =========================
    # BULK MARK (opcional, útil)
    # =========================
    def mark_many(self, keys):
        updated = False

        for key in keys:
            if key not in self._processed_set:
                self._processed_set.add(key)
                updated = True

        if updated:
            self.save()

    # =========================
    # STATS
    # =========================
    def get_processed_count(self):
        return len(self._processed_set)

    def get_all(self):
        return list(self._processed_set)

    # =========================
    # RESET
    # =========================
    def delete(self):
        if os.path.exists(self.path):
            os.remove(self.path)

        self._processed_set = set()
        self.data = {"processed_keys": []}