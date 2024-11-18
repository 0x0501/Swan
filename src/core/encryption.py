from PyQt6.QtCore import QSettings
import base64
from cryptography.fernet import Fernet
from loguru import logger
from pathlib import Path
import os
from typing import Set, Optional


class Encryption:

    def __init__(self, key_file_dir_path: str, settings: QSettings,
                 encrypted_keys: Optional[Set[str]]) -> None:
        self.key_file = Path.joinpath(
            Path(key_file_dir_path), 'SWAN_MEGA_KEY.bin')
        logger.debug('key_file_dir_path: %s' % key_file_dir_path)
        logger.debug('Encryption Key path: %s' % self.key_file)
        self._ensure_encryption_key()
        self.settings = settings
        # 默认加密
        self.encrypted_keys = encrypted_keys or {
            'dzdp_password', 'xiecheng_password', 'red_password'
        }
        self.fernet = Fernet(self._load_key())

    def _ensure_encryption_key(self):
        """确保加密密钥存在，如果不存在则创建新密钥"""
        if not self.key_file.exists():
            logger.debug('Encryption key doesn\'t exist, generate a new one.')
            # create the directory first
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            self._generate_new_key()

    def _generate_new_key(self):
        """生成新的加密密钥并保存"""
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as f:
            f.write(key)
        os.chmod(self.key_file, 0o600)
        logger.debug('Generated new encryption ket at: %s' % self.key_file)
        return key

    def _load_key(self):
        """加载加密密钥"""
        with open(self.key_file, 'rb') as f:
            return f.read()

    def check_encryption_key_status(self):
        return self.key_file.exists()

    def add_encrypted_key(self, key: str):
        """添加需要加密的键"""
        self.encrypted_keys.add(key)

    def remove_encrypted_key(self, key: str):
        """移除需要加密的键"""
        self.encrypted_keys.discard(key)

    def is_encrypted_key(self, key: str) -> bool:
        """检查键是否需要加密"""
        # 如果没有指定encrypted_keys，则所有通过set_encrypted设置的键都视为加密键
        return len(self.encrypted_keys) == 0 or key in self.encrypted_keys

    def regenerate_key(self) -> int:
        """
        重新生成密钥并重新加密所有需要加密的数据
        
        Returns:
            int: 重新加密的数据项数量，失败返回-1
        """
        try:
            # 保存旧的 Fernet 实例
            old_fernet = self.fernet
            
            # 获取所有需要重新加密的数据
            old_data = {}
            
            # 使用旧密钥解密所有加密数据
            for key in self.encrypted_keys:
                try:
                    # 获取加密的base64字符串
                    encrypted_value = self.settings.value(key)
                    if encrypted_value:
                        # 解密数据
                        decrypted_data = self.get_encrypted(key)
                        if decrypted_data is not None:
                            old_data[key] = decrypted_data
                            logger.debug(f"Successfully decrypted old data for key: {key}")
                except Exception as e:
                    logger.error(f"解密键 {key} 时出错: {str(e)}")
                    continue

            # 生成新密钥
            new_key = self._generate_new_key()
            # 使用新密钥创建新的 Fernet 实例
            self.fernet = Fernet(new_key)
            
            # 使用新密钥重新加密数据
            for key, value in old_data.items():
                try:
                    # 加密数据
                    encrypted_data = self.fernet.encrypt(value.encode())
                    # 将加密后的字节转换为base64字符串存储
                    encoded_value = base64.b64encode(encrypted_data).decode()
                    self.settings.setValue(key, encoded_value)
                    logger.debug(f"Successfully re-encrypted data for key: {key}")
                except Exception as e:
                    logger.error(f"重新加密键 {key} 时出错: {str(e)}")
                    # 如果重新加密失败，恢复使用旧密钥
                    self.fernet = old_fernet
                    return -1

            # 确保设置被保存
            self.settings.sync()
            logger.info(f"Successfully regenerated key and re-encrypted {len(old_data)} items")
            return len(old_data)

        except Exception as e:
            logger.error(f"重新生成密钥时发生错误: {str(e)}")
            return -1

    def set_encrypted(self, key: str, value: str):
        """
        加密并存储值
        
        Args:
            key: 设置项的键名
            value: 要加密存储的值
        """
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        if not self.is_encrypted_key(key):
            # 如果不是需要加密的键，直接存储原始值
            self.settings.setValue(key, value)
            return

        try:
            # 获取当前存储的解密值
            current_value = self.get_encrypted(key)
            
            # 若数据没有变动，那么不做任何处理
            if value == current_value:
                logger.debug(f'Value unchanged for key: {key}, skipping encryption')
                return
                
            # 加密数据
            encrypted_data = self.fernet.encrypt(value.encode())
            # 将加密后的字节转换为base64字符串存储
            encoded_value = base64.b64encode(encrypted_data).decode()
            self.settings.setValue(key, encoded_value)
            logger.debug(f'Successfully encrypted new value for key: {key}')
            
            # 确保设置被保存
            self.settings.sync()
            
        except Exception as e:
            logger.error(f"加密失败 - 键: {key}, 错误: {str(e)}")
            raise

    def get_encrypted(self, key: str, default: str = None) -> str:
        """
        获取并解密存储的值
        
        Args:
            key: 设置项的键名
            default: 当键不存在时返回的默认值
            
        Returns:
            解密后的字符串值
        """
        value = self.settings.value(key)
        if value is None:
            return default

        if not self.is_encrypted_key(key):
            # 如果不是加密键，直接返回原始值
            return value

        try:
            # 将base64字符串转换回字节
            encrypted_data = base64.b64decode(value.encode())
            # 解密数据
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"解密失败 - 键: {key}, 错误: {str(e)}")
            # 记录更详细的错误信息用于调试
            logger.debug(f"当前值: {value}")
            return default

    def setValue(self, key: str, value):
        """
        直接存储未加密的值（与QSettings接口兼容）
        
        Args:
            key: 设置项的键名
            value: 要存储的值
        """
        self.settings.setValue(key, value)
        self.settings.sync()

    def value(self, key: str, default=None):
        """
        直接获取未加密的值（与QSettings接口兼容）
        
        Args:
            key: 设置项的键名
            default: 默认值
        """
        return self.settings.value(key, default)
