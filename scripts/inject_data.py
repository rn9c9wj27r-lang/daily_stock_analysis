#!/usr/bin/env python3
"""
将雷达全盘搜刮到的美股实时K线与A股主力资金面 JSON 资产，
强行灌入前端静态 index.html 中，实现零后端依赖的纯静态看盘看板。
"""
import os
import json
import glob
from pathlib import Path
from typing import Dict, Any

class DataInjector:
    """生产级静态数据穿透注入器"""
    
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
        """智能扫描、去重、过滤多级目录下的 JSON 数据源"""
        combined_data = {}
        scanned_paths = set()
        
        # 严格黑名单：排除依赖描述与前端配置
        blacklist_keywords = {
            "package", "config", "tsconfig", "webpack", "babel",
            "eslint", ".lock", "docker", "settings", ".json.lock"
        }
        
        for data_dir in self.data_dirs:
            if not data_dir.exists():
                continue
                
            print(f"📁 雷达正在扫描数据目录: {data_dir}")
            
            for json_file in data_dir.rglob("*.json"):
                if json_file in scanned_paths:
                    continue
                    
                if any(kw in json_file.name.lower() for kw in blacklist_keywords):
                    continue
                
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    key = json_file.stem
                    # 处理重名 key 冲突冲突，附加父目录层级做命名空间隔离
                    if key in combined_data:
                        try:
                            relative = json_file.relative_to(self.docs_root)
                            key = f"{relative.parent.name}_{key}"
                        except ValueError:
                            key = f"{json_file.parent.name}_{key}"
                    
                    combined_data[key] = data
                    scanned_paths.add(json_file)
                    print(f"   ✅ 数据资产捕获成功: {key} ({len(str(data))} 字节)")
                    
                except (json.JSONDecodeError, IOError) as e:
                    print(f"   ⚠️ 跳过异常文件: {json_file.name} - {e}")
        
        print(f"📊 资产扫描结束，总计成功装载 {len(combined_data)} 个核心数据源。")
        return combined_data
    
    def inject_into_html(self, data: Dict[str, Any]) -> bool:
        """将数据块作为全局变量深度注入到静态前端单页应用中"""
        # 智能兜底：若docs下由于编译异常没有index.html，全盘搜寻源码主页兜底
        if not self.html_file.exists():
            print(f"⚠️ 未在目标位置发现 {self.html_file}，正在全局检索源码静态主页...")
            found_htmls = glob.glob("**/index.html", recursive=True)
            for fh in found_htmls:
                if "docs" not in fh and ".github" not in fh:
                    self.docs_root.mkdir(parents=True, exist_ok=True)
                    with open(fh, "r", encoding="utf-8") as src, open(self.html_file, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                    print(f"   ✅ 已利用源码模板 {fh} 强制生成部署主页")
                    break

        if not self.html_file.exists():
            print("❌ 致命错误：工作空间中未发现任何可用的 index.html 模板文件。")
            return False
        
        with open(self.html_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "window.__INITIAL_DATA__" in content:
            print("ℹ️ 检测到该静态页面已被成功灌入过行情数据，跳过本次注入。")
            return True
        
        # 编译注入脚本（附带你设计的控制台炫酷 Logger）
        injection_script = f"""<script>
window.__INITIAL_DATA__ = {json.dumps(data, ensure_ascii=False, indent=2)};
window.isStaticPages = true;
window.__DATA_SOURCES__ = {json.dumps(list(data.keys()), ensure_ascii=False)};
console.log('%c💡 云端离线看盘数据流解构成功！', 'color: #39d353; font-size: 14px; font-weight: bold;');
console.log('当前挂载资产底座:', window.__DATA_SOURCES__);
</script>"""
        
        # 强行抢占加载高位，保证前端 React/Vue 组件生命周期安全
        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n{injection_script}", 1)
        elif "<html>" in content:
            content = content.replace("<html>", f"<html>\n{injection_script}", 1)
        else:
            content = injection_script + "\n" + content
            
        with open(self.html_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print("🚀 [完美交割] 数据穿透层组装完毕，前端单页应用正式脱离后端运行！")
        return True

def main():
    print("=" * 60)
    print("⚡ 启动工业级数据穿透与依赖解耦引擎")
    print("=" * 60)
    injector = DataInjector(docs_root="docs")
    data = injector.find_json_files()
    success = injector.inject_into_html(data)
    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
