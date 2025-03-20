# LLM文献阅读器

## 项目简介

LLM文献阅读器是一个基于PyQt5开发的PDF文献阅读和管理工具，集成了大语言模型(LLM)功能，可以帮助用户更高效地阅读和理解学术文献。该项目采用MVC架构设计，提供了直观的用户界面和强大的文献分析功能。

## 功能特点

- PDF文献阅读与导航
  - 支持PDF文件的打开、浏览和导航
  - 提供页面缩放和适配功能
  - 支持文本选择和复制

- 文献库管理
  - 文献分类管理
  - 文件浏览和组织
  - 支持多文件同时打开

- 图片查看
  - 支持PDF中图片的提取和查看
  - 图片缩放和保存功能

- 智能对话功能
  - 基于OpenAI API的智能问答
  - 上下文感知的对话系统
  - 支持文献内容分析和解释

## 项目架构

项目采用MVC架构，主要包含以下组件：

```
.
├── app.py                 # 应用程序入口
├── controllers/           # 控制器
│   ├── app_controller.py  # 应用控制器
│   ├── chat_controller.py # 对话控制器
│   ├── file_controller.py # 文件控制器
│   ├── image_controller.py# 图片控制器
│   └── reader_controller.py# 阅读器控制器
├── models/                # 数据模型
│   ├── chat_model.py     # 对话模型
│   ├── config_model.py   # 配置模型
│   └── pdf_model.py      # PDF模型
├── views/                 # 视图
│   ├── file_view.py      # 文件视图
│   ├── main_view.py      # 主视图
│   └── reader_view.py    # 阅读器视图
├── gui/                   # 界面组件
│   ├── chat_list_panel.py # 聊天列表面板
│   ├── chat_panel.py      # 聊天面板
│   ├── file_panel.py      # 文件面板
│   ├── flow_layout.py     # 流式布局
│   ├── image_viewer_panel.py # 图片查看面板
│   ├── main_window.py     # 主窗口
│   ├── menu_manager.py    # 菜单管理
│   ├── reader_panel.py    # 阅读面板
│   └── settings_dialog.py # 设置对话框
├── services/              # 服务层
│   ├── ai_service.py     # AI服务
│   ├── cache_service.py  # 缓存服务
│   ├── config_service.py # 配置服务
│   └── pdf_service.py    # PDF服务
└── utils/                 # 工具函数
    ├── file_utils.py     # 文件工具
    └── __init__.py
```

## 安装与使用

### 环境要求

- Python 3.7+
- PyQt5
- PyMuPDF
- OpenAI API

### 安装步骤

1. 克隆或下载项目代码
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行应用程序：
   ```bash
   python app.py
   ```

### 配置说明

1. 首次运行时，需要在设置中配置OpenAI API密钥
2. 可以通过设置对话框配置以下选项：
   - OpenAI API密钥
   - 默认文献保存路径
   - 界面主题设置

## 使用说明

1. 文献阅读
   - 通过文件面板打开PDF文件
   - 使用阅读面板进行文献浏览
   - 支持文本选择和复制

2. 智能对话
   - 在聊天面板中输入问题
   - 系统会基于文献内容提供智能回答
   - 支持上下文相关的对话

3. 图片查看
   - 点击图片查看器可以放大查看PDF中的图片
   - 支持图片的保存和导出

## 许可证

本项目使用GPL-3许可证。详细信息请参阅LICENSE文件。