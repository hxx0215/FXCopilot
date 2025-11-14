#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程终止工具
通过命令行接收PID数组，检查进程是否存在并使用taskkill关闭
运行时不显示控制台窗口
"""

import sys
import subprocess
import psutil
import os
import time

# Windows API for hiding console window
import ctypes

# Windows API常量
SW_HIDE = 0
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_HIDEWINDOW = 0x0080

def hide_console_window():
    """隐藏当前控制台窗口"""
    try:
        if sys.platform == "win32":
            # 获取当前控制台窗口句柄
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            
            # 隐藏窗口
            user32.ShowWindow(hwnd, SW_HIDE)
            
            # 设置为始终置顶并隐藏
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_HIDEWINDOW)
    except Exception:
        # 如果API调用失败，忽略错误
        pass

def show_console_window():
    """显示控制台窗口（主要用于调试）"""
    try:
        if sys.platform == "win32":
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            user32.ShowWindow(hwnd, 5)  # SW_SHOW = 5
            user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
    except Exception:
        pass


def check_process_exists(pid):
    """检查指定PID的进程是否存在"""
    try:
        # 使用psutil检查进程是否存在
        return psutil.pid_exists(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False
    except Exception:
        return False


def terminate_process(pid):
    """使用taskkill终止指定PID的进程"""
    try:
        # 使用taskkill /PID pid /F 强制终止进程
        result = subprocess.run(
            ['taskkill', '/PID', str(pid), '/F'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)


def main():
    """主函数"""
    # 隐藏控制台窗口
    hide_console_window()
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python terminate.py <pid1> [pid2] [pid3] ...", file=sys.stderr)
        sys.exit(1)
    
    # 解析PID列表
    pids = []
    for arg in sys.argv[1:]:
        try:
            pid = int(arg)
            if pid > 0:  # PID必须是正数
                pids.append(pid)
        except ValueError:
            print(f"警告: 无效的PID值 '{arg}'，将被跳过", file=sys.stderr)
            continue
    
    if not pids:
        print("错误: 没有有效的PID值", file=sys.stderr)
        sys.exit(1)
    
    # 处理每个PID
    results = {
        'terminated': [],
        'not_exists': [],
        'failed': []
    }
    
    for pid in pids:
        print(f"正在检查PID {pid}...")
        
        # 检查进程是否存在
        if not check_process_exists(pid):
            print(f"PID {pid}: 进程不存在")
            results['not_exists'].append(pid)
            continue
        
        print(f"PID {pid}: 进程存在，正在终止...")
        
        # 尝试终止进程
        success, stdout, stderr = terminate_process(pid)
        
        if success:
            print(f"PID {pid}: 成功终止")
            results['terminated'].append(pid)
        else:
            print(f"PID {pid}: 终止失败 - {stderr}")
            results['failed'].append((pid, stderr))
        
        # 短暂延迟，避免过于频繁的系统调用
        time.sleep(0.1)
    
    # 输出总结
    print("\n=== 执行总结 ===")
    print(f"成功终止: {len(results['terminated'])} 个进程")
    print(f"不存在: {len(results['not_exists'])} 个PID")
    print(f"失败: {len(results['failed'])} 个进程")
    
    if results['terminated']:
        print(f"已终止的PID: {results['terminated']}")
    if results['not_exists']:
        print(f"不存在的PID: {results['not_exists']}")
    if results['failed']:
        print("失败的PID:")
        for pid, error in results['failed']:
            print(f"  PID {pid}: {error}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断操作", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"程序执行出错: {e}", file=sys.stderr)
        sys.exit(1)