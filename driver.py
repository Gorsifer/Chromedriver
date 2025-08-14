import os
import re
import sys
import platform
import shutil
import requests
import zipfile
from progressbar import ProgressBar, Percentage, Bar, FileTransferSpeed, ETA
#默认推荐
REC_CHROME_VERSION = "139.0.7258.68"

def get_current_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
def is_64bit_os():
    try:
        return sys.maxsize > 2 ** 32
    except:
        return 'PROGRAMFILES(X86)' in os.environ
def find_chrome_installs():
    possible_paths = []
    program_files = os.environ.get("PROGRAMFILES", "")
    program_files_x86 = os.environ.get("PROGRAMFILES(X86)", "")
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if is_64bit_os():
        possible_paths.append(os.path.join(program_files, "Google\\Chrome\\Application\\chrome.exe"))
        possible_paths.append(os.path.join(program_files_x86, "Google\\Chrome\\Application\\chrome.exe"))
    else:
        possible_paths.append(os.path.join(program_files, "Google\\Chrome\\Application\\chrome.exe"))
    possible_paths.append(os.path.join(local_app_data, "Google\\Chrome\\Application\\chrome.exe"))
    try:
        import winreg
        reg_locations = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
            r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        ]
        for reg_path in reg_locations:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    path, _ = winreg.QueryValueEx(key, "")
                    if path and os.path.exists(path):
                        possible_paths.append(path)
            except:
                continue
    except ImportError:
        pass
    unique_paths = list(set(possible_paths))
    return [p for p in unique_paths if os.path.exists(p) and os.path.isfile(p)]
def get_chrome_version(chrome_path):
    try:
        app_dir = os.path.dirname(chrome_path)
        for item in os.listdir(app_dir):
            item_path = os.path.join(app_dir, item)
            if os.path.isdir(item_path) and re.match(r"^\d+\.\d+\.\d+\.\d+$", item):
                return item
        try:
            import winreg
            reg_paths = [
                r"SOFTWARE\Google\Chrome\BLBeacon",
                r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon"
            ]
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        version, _ = winreg.QueryValueEx(key, "version")
                        if re.match(r"^\d+\.\d+\.\d+\.\d+$", version):
                            return version
                except:
                    continue
        except ImportError:
            pass
        print("无法自动获取Chrome版本号")
        return None
    except Exception as e:
        print(f"获取版本时出错: {str(e)}")
        return None

def get_driver_download_urls(version, is_64bit):
    try:
        main_version = int(version.split('.')[0])
    except (ValueError, IndexError):
        main_version = 115 #官方新版以上
    if main_version <= 114:#官方旧版以下
        print("\n注意：该版本Chrome仅支持32位驱动")
        return {
            "专用32位源": f"https://google.215613.xyz/chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip"
        }
    arch = "win64" if is_64bit else "win32"
    return {
        "国内代理源": f"https://google.215613.xyz/chrome-for-testing-public/{version}/{arch}/chromedriver-{arch}.zip",
        "华为镜像源": f"https://mirrors.huaweicloud.com/chromedriver/{version}/chromedriver-{arch}.zip",
        "官方源": f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{arch}/chromedriver-{arch}.zip"
    }
def download_and_extract_driver(url, target_dir):
    global zip_path, temp_extract_dir
    try:
        zip_name = os.path.basename(url)
        zip_path = os.path.join(target_dir, zip_name)
        print(f"从 {url} 下载中...")
        print(f"保存路径: {zip_path}")
        head_res = requests.head(url, allow_redirects=True, timeout=10)
        file_size = int(head_res.headers.get('content-length', 0))
        with requests.get(url, stream=True, timeout=30) as res:
            res.raise_for_status()
            progress_widgets = [
                zip_name + ': ',
                Percentage(), ' ',
                Bar(marker='#', left='[', right=']'), ' ',
                FileTransferSpeed(), ' ',
                ETA()
            ]
            progress_bar = ProgressBar(widgets=progress_widgets, maxval=file_size).start()
            with open(zip_path, 'wb') as f:
                downloaded = 0
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress_bar.update(min(downloaded, file_size))
            progress_bar.finish()
        print("解压文件中...")
        driver_found = False
        temp_extract_dir = os.path.join(target_dir, "temp_driver_extract")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        for root, _, files in os.walk(temp_extract_dir):
            if 'chromedriver.exe' in files:
                src_path = os.path.join(root, 'chromedriver.exe')
                dest_path = os.path.join(target_dir, 'chromedriver.exe')
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(src_path, dest_path)
                print(f"驱动已提取至: {dest_path}")
                driver_found = True
                break
        shutil.rmtree(temp_extract_dir, ignore_errors=True)
        if not driver_found:
            raise Exception("压缩包中未找到chromedriver.exe")
        while True:
            choice = input("是否保留下载的压缩包? (y/n): ").strip().lower()
            if choice in ['y', 'n']:
                if choice == 'n':
                    os.remove(zip_path)
                    print(f"已删除压缩包: {zip_name}")
                else:
                    print(f"压缩包保留在: {zip_path}")
                break
            print("请输入 'y' 或 'n'")
        return True
    except Exception as e:
        print(f"操作失败: {str(e)}")
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)
        if 'temp_extract_dir' in locals() and os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir, ignore_errors=True)
        return False
def get_recommended_chrome_url(is_64bit):
    arch = "win64" if is_64bit else "win32"
    return f"https://google.215613.xyz/chrome-for-testing-public/{REC_CHROME_VERSION}/{arch}/chrome-{arch}.zip"
def get_recommended_driver_url(is_64bit):
    arch = "win64" if is_64bit else "win32"
    return f"https://google.215613.xyz/chrome-for-testing-public/{REC_CHROME_VERSION}/{arch}/chromedriver-{arch}.zip"
def main():
    print("=== Chrome浏览器驱动管理工具 ===")
    print("本工具将帮助你下载匹配的ChromeDriver")
    input("\n按回车键开始环境检测...")
    current_dir = get_current_dir()
    is_64bit = is_64bit_os()
    print(f"\n当前工作目录: {current_dir}")
    print(f"系统类型: Windows {'64位' if is_64bit else '32位'}")
    print("\n正在查找Chrome浏览器...")
    chrome_installs = find_chrome_installs()
    if not chrome_installs:
        print("未检测到已安装的Chrome浏览器")
        print(f"推荐安装版本: {REC_CHROME_VERSION}")
        print(f"Chrome下载地址: {get_recommended_chrome_url(is_64bit)}")
        print(f"对应驱动地址: {get_recommended_driver_url(is_64bit)}")
        while True:
            choice = input("\n是否下载推荐版本的ChromeDriver? (y/n): ").strip().lower()
            if choice in ['y', 'n']:
                break
            print("请输入 'y' 或 'n'")
        if choice == 'y':
            print("\n开始下载推荐驱动...")
            download_and_extract_driver(get_recommended_driver_url(is_64bit), current_dir)
    else:
        print(f"找到{len(chrome_installs)}个Chrome安装:")
        for i, path in enumerate(chrome_installs, 1):
            print(f"  {i}. {path}")
        print("\n正在检测Chrome版本...")
        chrome_version = None
        for path in chrome_installs:
            chrome_version = get_chrome_version(path)
            if chrome_version:
                break
        if not chrome_version:
            print("\n请手动输入Chrome版本号（格式如: 139.0.7258.68）")
            print("获取方法：打开Chrome，访问 chrome://version")
            while True:
                chrome_version = input("版本号: ").strip()
                if re.match(r"^\d+\.\d+\.\d+\.\d+$", chrome_version):
                    break
                print("版本号格式不正确，请重新输入")
        print(f"检测到Chrome版本: {chrome_version}")
        driver_urls = get_driver_download_urls(chrome_version, is_64bit)
        while True:
            choice = input("\n是否下载对应版本的ChromeDriver? (y/n): ").strip().lower()
            if choice in ['y', 'n']:
                break
            print("请输入 'y' 或 'n'")
        if choice == 'y':
            print("\n开始尝试下载...")
            for name, url in driver_urls.items():
                print(f"\n尝试从{name}下载...")
                if download_and_extract_driver(url, current_dir):
                    print("下载成功！")
                    break
            else:
                print("\n所有源下载失败，以下是可用地址：")
                for name, url in driver_urls.items():
                    print(f"{name}: {url}")
                print(f"请手动下载后放到: {current_dir}")
        else:
            print("\n可用的驱动下载地址：")
            for name, url in driver_urls.items():
                print(f"{name}: {url}")
    print("\n操作完成")
    input("按回车键关闭窗口...")
if __name__ == "__main__":
    if platform.system() != "Windows":
        print("本工具仅支持Windows系统")
        input("按回车键关闭...")
        sys.exit(1)

    main()
