# 校园二手交易平台使用说明

## 项目简介

校园二手交易平台是一个基于Python+MySQL实现的Web应用程序，旨在为校园师生提供一个便捷、安全的二手物品交易环境。该平台使用Django框架开发，实现了用户认证、商品管理、交易流程、消息通信和评价系统等核心功能。

## 快速开始

### 环境要求

- Python 3.8+
- Django 4.0+
- MySQL 5.7+ (或SQLite 3)
- 其他依赖见requirements.txt

### 安装步骤

1. 解压项目文件

   ```bash
   unzip campus_trade_project.zip
   cd campus_trade_project/campus_trade
   ```

2. 创建虚拟环境

   ```bash
   python -m venv venv
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖

   ```bash
   pip install -r requirements.txt   //这是统称，缺啥下载啥就行了
   
   ```

4. 配置数据库

   - 默认使用SQLite数据库，无需额外配置
   - 如需使用MySQL，请修改settings.py中的DATABASES配置

5. 运行数据库迁移

   ```bash
   python manage.py migrate
   ```

6. 创建超级用户（可选，已预创建admin用户）

   ```bash
   python manage.py createsuperuser
   ```

7. 运行开发服务器

   ```bash
   python manage.py runserver
   ```

8. 访问网站

   - 网站首页：http://localhost:8000/
   - 管理后台：http://localhost:8000/admin/
   - 默认管理员账号：admin