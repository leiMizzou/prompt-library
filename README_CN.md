# 📚 prompt-library

提示词模板管理器，内置15个模板。存储、搜索和版本管理你的提示词。

## 功能特点

- **15个内置模板** — 涵盖代码审查、翻译、摘要等常见场景
- **变量插值** — `{{variable}}` 语法动态填充
- **分类标签** — 按用途分类管理
- **版本历史** — 提示词迭代追踪

## 快速开始

```bash
python prompt_library.py list
python prompt_library.py get code_review --lang python --code "def hello(): pass"
python prompt_library.py add --name my_prompt --template "分析: {{topic}}"
python prompt_library.py search "翻译"
```

## 许可证
MIT
