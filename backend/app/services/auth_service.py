from app import db
from app.models import User
from datetime import datetime, timedelta
import random
import string
from flask import current_app
from flask_jwt_extended import create_access_token
from .email_service import EmailService

class AuthService:
    @staticmethod
    def register(username, password, email, role='employee'):
        """
        用户注册服务
        :param username: 用户名
        :param password: 密码
        :param email: 邮箱
        :param role: 角色
        :return: 用户对象或None
        """
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return None, "用户名已存在"
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return None, "邮箱已被注册"
            
        # 创建新用户
        user = User(
            username=username,
            email=email,
            role=role,
            is_active=True,
            created_at=datetime.utcnow()
        )
        user.set_password(password)  # 使用User模型的set_password方法
        
        try:
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def authenticate(username, password):
        """
        验证用户身份
        :param username: 用户名
        :param password: 密码
        :return: (user, error) 元组，user为用户对象，error为错误信息
        """
        try:
            # 查找用户
            user = User.query.filter_by(username=username).first()
            if not user:
                return None, "用户不存在"
            
            try:
                # 检查账户是否被锁定
                if user.account_locked_until and user.account_locked_until > datetime.utcnow():
                    # 计算剩余锁定时间（分钟）
                    remaining_time = (user.account_locked_until - datetime.utcnow()).total_seconds() / 60
                    return None, f"账户已被锁定，请在{int(remaining_time)}分钟后重试"
                
                # 验证密码
                if not user.check_password(password):
                    try:
                        # 更新失败登录次数和时间
                        user.login_attempts = (user.login_attempts or 0) + 1
                        user.last_failed_login = datetime.utcnow()
                        
                        # 如果失败次数达到限制，锁定账户
                        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
                        if user.login_attempts >= max_attempts:
                            # 设置锁定时间（默认30分钟）
                            lock_duration = current_app.config.get('ACCOUNT_LOCK_DURATION', 30)
                            user.account_locked_until = datetime.utcnow() + timedelta(minutes=lock_duration)
                            db.session.commit()
                            return None, f"登录失败次数过多，账户已被锁定{lock_duration}分钟"
                        
                        db.session.commit()
                        # 返回剩余尝试次数
                        remaining_attempts = max_attempts - user.login_attempts
                        return None, f"密码错误，还剩{remaining_attempts}次尝试机会"
                    except Exception as e:
                        # 如果更新失败计数时发生错误，回滚事务并返回一般性错误信息
                        db.session.rollback()
                        current_app.logger.error(f"更新登录尝试次数失败: {str(e)}")
                        return None, "密码错误"
                
                # 检查用户状态
                if not user.is_active:
                    return None, "账户已被禁用"
                
                try:
                    # 登录成功，重置登录尝试次数
                    user.login_attempts = 0
                    user.last_failed_login = None
                    user.account_locked_until = None
                    db.session.commit()
                except Exception as e:
                    # 如果重置计数器失败，记录错误但允许用户登录
                    db.session.rollback()
                    current_app.logger.error(f"重置登录尝试次数失败: {str(e)}")
                
                return user, None
            
            except Exception as e:
                # 如果在处理登录尝试限制时发生错误，回退到基本的密码验证
                current_app.logger.error(f"处理登录尝试限制时发生错误: {str(e)}")
                if not user.check_password(password):
                    return None, "密码错误"
                if not user.is_active:
                    return None, "账户已被禁用"
                return user, None
                
        except Exception as e:
            current_app.logger.error(f"认证错误: {str(e)}")
            return None, "认证过程中发生错误"

    @staticmethod
    def login(username, password):
        """
        用户登录服务
        :param username: 用户名
        :param password: 密码
        :return: 用户对象或None
        """
        try:
            # 添加登录尝试日志
            current_app.logger.info(f"用户登录尝试 - 用户名: {username}")
            
            user, error = AuthService.authenticate(username, password)
            if error:
                current_app.logger.warning(f"用户登录失败 - 用户名: {username}, 原因: {error}")
                return None, error
                
            # 生成访问令牌
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'username': user.username,
                    'role': user.role
                }
            )
            
            current_app.logger.info(f"用户登录成功 - 用户名: {username}")
            return {
                'user': user.to_dict(),
                'access_token': access_token
            }, None
            
        except Exception as e:
            error_msg = f"登录服务错误 - 用户名: {username}, 错误: {str(e)}"
            current_app.logger.error(error_msg, exc_info=True)
            return None, error_msg

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        修改密码服务
        :param user_id: 用户ID
        :param old_password: 旧密码
        :param new_password: 新密码
        :return: 是否成功
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在"
                
            if not user.check_password(old_password):
                return False, "原密码错误"
                
            user.set_password(new_password)  # 使用User模型的set_password方法
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            print(f"修改密码时出错: {str(e)}")
            return False, f"修改密码失败: {str(e)}"

    @staticmethod
    def generate_reset_code():
        """
        生成6位数字验证码
        """
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def send_reset_code(email):
        """
        发送重置密码验证码
        :param email: 用户邮箱
        :return: (success, message) 元组
        """
        try:
            # 查找用户
            user = User.query.filter_by(email=email).first()
            if not user:
                return False, "该邮箱未注册"

            # 生成验证码
            reset_code = AuthService.generate_reset_code()
            
            # 保存验证码和过期时间（30分钟）
            user.reset_code = reset_code
            user.reset_code_expires = datetime.utcnow() + timedelta(minutes=30)
            db.session.commit()

            # 发送验证码邮件
            success, message = EmailService.send_reset_code_email(email, reset_code)
            if not success:
                return False, message

            return True, "验证码已发送到您的邮箱"

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"发送重置码错误: {str(e)}")
            return False, f"发送验证码失败: {str(e)}"

    @staticmethod
    def verify_reset_code(email, code):
        """
        验证重置密码的验证码
        :param email: 用户邮箱
        :param code: 验证码
        :return: (success, message) 元组
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return False, "用户不存在"

            if not user.reset_code or not user.reset_code_expires:
                return False, "请先获取验证码"

            if user.reset_code_expires < datetime.utcnow():
                return False, "验证码已过期，请重新获取"

            if user.reset_code != code:
                return False, "验证码错误"

            return True, None

        except Exception as e:
            current_app.logger.error(f"验证重置码错误: {str(e)}")
            return False, f"验证失败: {str(e)}"

    @staticmethod
    def reset_password_with_code(email, code, new_password):
        """
        使用验证码重置密码
        :param email: 用户邮箱
        :param code: 验证码
        :param new_password: 新密码
        :return: (success, message) 元组
        """
        try:
            # 验证验证码
            success, message = AuthService.verify_reset_code(email, code)
            if not success:
                return False, message

            # 重置密码
            user = User.query.filter_by(email=email).first()
            user.set_password(new_password)
            user.reset_code = None
            user.reset_code_expires = None
            user.updated_at = datetime.utcnow()
            db.session.commit()

            return True, "密码重置成功"

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"重置密码错误: {str(e)}")
            return False, f"重置密码失败: {str(e)}"

    @staticmethod
    def reset_password(email):
        """
        重置密码服务（发送重置密码邮件）
        :param email: 用户邮箱
        :return: 是否成功
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return False, "用户不存在"
            
            # TODO: 实现发送重置密码邮件的逻辑
            # 这里暂时直接重置为默认密码
            user.set_password('123456')  # 使用User模型的set_password方法
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
