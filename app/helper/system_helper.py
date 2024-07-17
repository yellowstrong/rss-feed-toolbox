import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple


class SystemHelper:

    @staticmethod
    def is_docker() -> bool:
        """
        判断是否为Docker环境
        """
        return Path("/.dockerenv").exists()

    @staticmethod
    def copy(src: Path, dest: Path) -> Tuple[int, str]:
        """
        复制
        """
        try:
            shutil.copy2(src, dest)
            return 0, ""
        except Exception as err:
            print(str(err))
            return -1, str(err)

    @staticmethod
    def move(src: Path, dest: Path) -> Tuple[int, str]:
        """
        移动
        """
        try:
            # 当前目录改名
            temp = src.replace(src.parent / dest.name)
            # 移动到目标目录
            shutil.move(temp, dest)
            return 0, ""
        except Exception as err:
            print(str(err))
            return -1, str(err)

    @staticmethod
    def link(src: Path, dest: Path) -> Tuple[int, str]:
        """
        硬链接
        """
        try:
            # 准备目标路径，增加后缀 .mp
            tmp_path = dest.with_suffix(dest.suffix + ".mp")
            # 检查目标路径是否已存在，如果存在则先unlink
            if tmp_path.exists():
                tmp_path.unlink()
            tmp_path.hardlink_to(src)
            # 硬链接完成，移除 .mp 后缀
            shutil.move(tmp_path, dest)
            return 0, ""
        except Exception as err:
            print(str(err))
            return -1, str(err)

    @staticmethod
    def softlink(src: Path, dest: Path) -> Tuple[int, str]:
        """
        软链接
        """
        try:
            dest.symlink_to(src)
            return 0, ""
        except Exception as err:
            print(str(err))
            return -1, str(err)

    @staticmethod
    def list_files(directory: Path, extensions: list, min_filesize: int = 0) -> List[Path]:
        """
        获取目录下所有指定扩展名的文件（包括子目录）
        """

        if not min_filesize:
            min_filesize = 0

        if not directory.exists():
            return []

        if directory.is_file():
            return [directory]

        if not min_filesize:
            min_filesize = 0

        files = []
        pattern = r".*(" + "|".join(extensions) + ")$"

        # 遍历目录及子目录
        for path in directory.rglob('**/*'):
            if path.is_file() \
                    and re.match(pattern, path.name, re.IGNORECASE) \
                    and path.stat().st_size >= min_filesize * 1024 * 1024:
                files.append(path)

        return files

    @staticmethod
    def exits_files(directory: Path, extensions: list, min_filesize: int = 0) -> bool:
        """
        判断目录下是否存在指定扩展名的文件
        :return True存在 False不存在
        """

        if not min_filesize:
            min_filesize = 0

        if not directory.exists():
            return False

        if directory.is_file():
            return True

        if not min_filesize:
            min_filesize = 0

        pattern = r".*(" + "|".join(extensions) + ")$"

        # 遍历目录及子目录
        for path in directory.rglob('**/*'):
            if path.is_file() \
                    and re.match(pattern, path.name, re.IGNORECASE) \
                    and path.stat().st_size >= min_filesize * 1024 * 1024:
                return True

        return False

    @staticmethod
    def list_sub_files(directory: Path, extensions: list) -> List[Path]:
        """
        列出当前目录下的所有指定扩展名的文件(不包括子目录)
        """
        if not directory.exists():
            return []

        if directory.is_file():
            return [directory]

        files = []
        pattern = r".*(" + "|".join(extensions) + ")$"

        # 遍历目录
        for path in directory.iterdir():
            if path.is_file() and re.match(pattern, path.name, re.IGNORECASE):
                files.append(path)

        return files

    @staticmethod
    def list_sub_directory(directory: Path) -> List[Path]:
        """
        列出当前目录下的所有子目录（不递归）
        """
        if not directory.exists():
            return []

        if directory.is_file():
            return []

        dirs = []

        # 遍历目录
        for path in directory.iterdir():
            if path.is_dir():
                dirs.append(path)

        return dirs

    @staticmethod
    def list_sub_all(directory: Path) -> List[Path]:
        """
        列出当前目录下的所有子目录和文件（不递归）
        """
        if not directory.exists():
            return []

        if directory.is_file():
            return []

        items = []

        # 遍历目录
        for path in directory.iterdir():
            items.append(path)

        return items

    @staticmethod
    def get_directory_size(path: Path) -> float:
        """
        计算目录的大小

        参数:
            directory_path (Path): 目录路径

        返回:
            int: 目录的大小（以字节为单位）
        """
        if not path or not path.exists():
            return 0
        if path.is_file():
            return path.stat().st_size
        total_size = 0
        for path in path.glob('**/*'):
            if path.is_file():
                total_size += path.stat().st_size

        return total_size

    @staticmethod
    def is_hardlink(src: Path, dest: Path) -> bool:
        """
        判断是否为硬链接（可能无法支持宿主机挂载smb盘符映射docker的场景）
        """
        try:
            if not src.exists() or not dest.exists():
                return False
            if src.is_file():
                # 如果是文件，直接比较文件
                return src.samefile(dest)
            else:
                for src_file in src.glob("**/*"):
                    if src_file.is_dir():
                        continue
                    # 计算目标文件路径
                    relative_path = src_file.relative_to(src)
                    target_file = dest.joinpath(relative_path)
                    # 检查是否是硬链接
                    if not target_file.exists() or not src_file.samefile(target_file):
                        return False
                return True
        except Exception as e:
            print(f"Error occurred: {e}")
            return False

    @staticmethod
    def is_same_disk(src: Path, dest: Path) -> bool:
        """
        判断两个路径是否在同一磁盘
        """
        if not src.exists() or not dest.exists():
            return False
        if os.name == "nt":
            return src.drive == dest.drive
        return os.stat(src).st_dev == os.stat(dest).st_dev
