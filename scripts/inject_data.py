#!/usr/bin/env python3
"""
将美股/A股 JSON 资产注入 docs/index.html，实现零后端依赖的纯静态看盘。
"""
import json
import glob
from pathlib import Path
from typing import Dict, Any


class DataInjector:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.html_file = self.docs_root / "index.html"
        self.data_dirs = [
            self.docs_root / "data" / "cache",
            Path("data") / "cache",
            self.docs_root / "data",
            Path("data"),
        ]

    def find_json_files(self) -> Dict[str, Any]:
        combined_data: Dict[str, Any] = {}
        scanned_paths: set[str] = set()

        blacklist_names = {
            "package.json", "package-lock.json", "tsconfig.json",
            "tsconfig.node.json", "vite.config.json",
            "vitest.config.json", ".eslintrc.json", "settings.json",
        }

        for data_dir in self.data_dirs:
            if not data_dir.exists():
                continue
            print(f"📁 扫描: {data_dir}")
            for json_file in data_dir.rglob("*.json"):
                resolved = str(json_file.resolve())
                if resolved in scanned_paths:
                    continue
                if json_file.name.lower() in blacklist_names:
                    continue
                if json_file.name.lower().endswith(".lock"):
                    continue
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"   ⚠️ 跳过异常文件: {json_file.name} - {e}")
                    continue

                key = json_file.stem
                if key in combined_data:
                    try:
                        rel = json_file.relative_to(Path("."))
                        key = str(rel.with_suffix("")).replace("/", "_").replace("\\", "_")
                    except ValueError:
                        key = f"{json_file.parent.name}_{key}"

                combined_data[key] = data
                scanned_paths.add(resolved)
                size = len(json.dumps(data, ensure_ascii=False).encode("utf-8"))
                print(f"   ✅ 捕获: {key} ({size} 字节)")

        print(f"📊 共装载 {len(combined_data)} 个数据源。")
        return combined_data

    def _prepare_html(self) -> bool:
        if self.html_file.exists():
            return True

        # 优先使用 Vite 构建产物
        dist_html = Path("apps/dsa-web/dist/index.html")
        if dist_html.exists():
            self.docs_root.mkdir(parents=True, exist_ok=True)
            self.html_file.write_text(
                dist_html.read_text(encoding="utf-8"), encoding="utf-8"
            )
            print(f"   ✅ 使用构建产物 {dist_html}")
            return True

        print(f"⚠️ {self.html_file} 不存在，全局检索模板...")
        for fh in glob.glob("**/index.html", recursive=True):
            if any(seg in fh for seg in ("node_modules", ".github", "dist")):
                continue
            self.docs_root.mkdir(parents=True, exist_ok=True)
            self.html_file.write_text(
                Path(fh).read_text(encoding="utf-8"), encoding="utf-8"
            )
            print(f"   ⚠️ 使用源码模板 {fh}（可能未经 Vite 编译）")
            return True

        print("❌ 未发现可用的 index.html 模板")
        return False

    def inject_into_html(self, data: Dict[str, Any]) -> bool:
        if not self._prepare_html():
            return False

        content = self.html_file.read_text(encoding="utf-8")
        if "window.__INITIAL_DATA__" in content:
            print("ℹ️ 已注入过数据，跳过")
            return True

        # 关键：转义 </script>，避免数据中的 HTML 闭合标签破坏页面
        data_json = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")

        injection_script = f"""<script>
window.__INITIAL_DATA__ = {data_json};
window.isStaticPages = true;
window.__DATA_SOURCES__ = {json.dumps(list(data.keys()), ensure_ascii=False)};
console.log('%c💡 离线看盘数据加载成功', 'color:#39d353;font-size:14px;font-weight:bold;');
console.log('数据源:', window.__DATA_SOURCES__);
</script>"""

        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n{injection_script}", 1)
        elif "<html>" in content:
            content = content.replace("<html>", f"<html>\n{injection_script}", 1)
        else:
            content = injection_script + "\n" + content

        self.html_file.write_text(content, encoding="utf-8")
        print("🚀 数据注入完成")
        return True


def main():
    print("=" * 60)
    print("⚡ 数据穿透注入引擎")
    print("=" * 60)
    injector = DataInjector(docs_root="docs")
    data = injector.find_json_files()
    success = injector.inject_into_html(data)
    print("=" * 60)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
