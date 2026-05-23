from __future__ import annotations


def static_site_css() -> str:
    return """
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #5c6975;
      --line: #dbe1e8;
      --accent: #216e7a;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }
    .shell {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }
    header { margin-bottom: 20px; }
    h1, h2 { margin: 0; }
    h1 { font-size: 32px; }
    h2 { font-size: 18px; margin-bottom: 12px; }
    p { margin: 6px 0; color: var(--muted); }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      margin: 14px 0;
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
    }
    th { color: var(--muted); font-weight: 700; }
    .kv th { width: 220px; }
    .empty { color: var(--muted); }
    .badge {
      display: inline-block;
      border: 1px solid var(--accent);
      border-radius: 999px;
      color: var(--accent);
      padding: 2px 8px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    """.strip()
