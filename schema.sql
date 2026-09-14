-- お便り。送り主を特定する情報 (IP やメールアドレス) は保存しない
CREATE TABLE IF NOT EXISTS letters (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT    NOT NULL,              -- ISO 8601 (UTC)
  radio_name TEXT    NOT NULL DEFAULT '',
  body       TEXT    NOT NULL,
  read_at    TEXT                            -- ふたりが読んだら日時を入れる
);
