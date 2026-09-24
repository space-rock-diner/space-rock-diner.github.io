-- お便り。送り主を特定する情報 (IP やメールアドレス) は保存しない
CREATE TABLE IF NOT EXISTS letters (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT    NOT NULL,              -- ISO 8601 (UTC)
  radio_name TEXT    NOT NULL DEFAULT '',
  body       TEXT    NOT NULL,
  read_at    TEXT,                           -- ふたりが読んだら日時を入れる
  episode    INTEGER                         -- 回のページから「第N回について」で送られたら N。回を決めないお便りは NULL
);
-- episode は 2026-09-24 に足した。それより前に作った D1 には、受け口 (functions/api/otayori.js) が
-- 最初の回つきのお便りのときに ALTER TABLE letters ADD COLUMN episode INTEGER で足す
