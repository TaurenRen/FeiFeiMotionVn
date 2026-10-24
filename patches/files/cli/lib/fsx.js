// Windows-safe recursive copy.
//
// node's fs.cpSync(..., { recursive: true }) hard-kills the process (exit 127, nothing on stdout or
// stderr) on Windows with Node 22.22 — it takes `om new` / `om fork` down halfway through the copy and
// leaves a project whose vendor/ is missing the clip libs, while `om` still reports success. A manual
// walk uses only mkdir + copyFile, which behave on both platforms.
import { copyFileSync, mkdirSync, readdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';

// Copy `from` to `to`. `filter(rel, dst, src)` returns false to skip a file or a whole folder;
// `rel` is the posix-style path below `from`, which is what callers actually want to test.
export function cpTree(from, to, { filter = () => true, force = true } = {}) {
  const walk = (src, dst, rel) => {
    if (filter(rel, dst, src) === false) return;
    let st;
    try { st = statSync(src); } catch { return; }
    if (st.isDirectory()) {
      mkdirSync(dst, { recursive: true });
      for (const name of readdirSync(src)) walk(join(src, name), join(dst, name), rel ? `${rel}/${name}` : name);
    } else {
      mkdirSync(dirname(dst), { recursive: true }); // a single-file copy into a folder that is not there yet
      try { copyFileSync(src, dst); } catch (e) { if (force || e.code !== 'EEXIST') throw e; }
    }
  };
  walk(from, to, '');
  return to;
}

// How `om new` decides what a template folder must not carry into a project.
export const NOT_A_FILM_FILE = /(^|\/)(out|\.om|snapshots)(\/|$)|(^|\/)template\.json$/;
export const NOT_A_COPY_OF_A_PROJECT = /(^|\/)(out|\.om|snapshots)(\/|$)/;
