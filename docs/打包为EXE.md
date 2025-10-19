# 如何将本项目打包为 Windows 可执行文件（.exe）

本文档介绍如何把本项目打包成可直接在 Windows 上运行的 EXE（Electron 桌面端）。打包产物会包含 Electron 前端以及 Python 后端所需的资源，首次运行会自动执行安装器下载 Python 运行时与依赖。

适用系统：Windows 10/11 x64（建议在 Windows 环境下打包）

## 一、准备环境

- Node.js 18 LTS（建议）
- npm 或 pnpm（本文以 npm 为例）
- Windows 环境（如果在非 Windows 系统上打包 Windows 产物，需要安装 wine，复杂度较高，建议直接在 Windows 上打包）

## 二、安装前端依赖

在项目根目录进入 webapp 目录并安装依赖：

- 方式一（更快更稳定）
  cd webapp
  npm ci

- 方式二
  cd webapp
  npm install

首次安装会自动执行 Electron 版本同步脚本（postinstall）。

## 三、构建与打包

项目已在 electron-builder 配置（webapp/.electron-builder.config.js）中：
- 配置了 Windows 目标（nsis 安装包 + portable 绿色版）
- 通过 extraFiles 将 Python 后端资源（assets、module、tasks、config、deploy 等）拷贝到可执行文件同级目录，便于运行时通过 ./config 等相对路径加载配置

在 webapp 目录执行下面任一脚本完成打包：

- 生成 Windows 全部产物（nsis + portable）
  npm run dist:win

- 仅生成绿色版（单文件可执行，免安装）
  npm run dist:win:portable

- 仅生成安装版（NSIS 安装包）
  npm run dist:win:nsis

打包完成后，产物位于：
- webapp/dist/ 目录
  - FXCopilot-<version>-win-x64.exe（安装包）
  - FXCopilot-<version>-win-x64-portable.exe（绿色版，可直接运行）
  - 或 win-unpacked/（未打包目录形式，便于调试）

## 四、首次运行说明

- 启动 EXE 后，会先运行内置安装器（installer.py）：
  1) 自动下载/准备 Python 运行时（默认放在 ./toolkit/python.exe）
  2) 自动安装 Python 依赖（使用 requirements.txt）
- 之后启动后端 gui.py，并在内置浏览器中打开 WebUI

若网络环境较差，依赖安装可能需要一些时间。

## 五、常见问题

- 运行时提示缺少 deploy.yaml：
  首次运行会在 ./config 目录下自动从模板（deploy.template.yaml）生成 deploy.yaml。你也可以手工复制一份模板为 deploy.yaml 并按需修改。

- 如何更换 Python 镜像/代理：
  修改 ./config/deploy.yaml 中的 Deploy.Python.PypiMirror 或 GitProxy 等字段，保存后重启应用。

- 绿色版与安装版有什么区别：
  绿色版（portable）是单个 EXE，解压到临时目录后运行；安装版（NSIS）提供安装向导，会把应用安装到指定目录并注册卸载信息。

## 六、目录打包规则（参考）

打包时会将以下资源拷贝到 EXE 同级目录：
- assets/**
- bin/**
- config/**
- deploy/**
- module/**
- tasks/**
- requirements.txt、requirements-in.txt、uv-requirements.txt
- gui.py、installer.py、console.bat、fxc.py

如需调整打包内容，可修改 webapp/.electron-builder.config.js 的 extraFiles 配置。

—— 完 ——
