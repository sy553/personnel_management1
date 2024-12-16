import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication  
from flask import current_app
import re
import ssl
import base64
import os

class EmailService:
    # 支持的邮件服务器配置
    SMTP_SERVERS = {
        'qq.com': {
            'server': 'smtp.qq.com',
            'port': 465,
            'use_ssl': True,
            'auth_required': True
        },
        '163.com': {
            'server': 'smtp.163.com',
            'port': 465,
            'use_ssl': True,
            'auth_required': True  # 163邮箱需要授权码
        },
        'gmail.com': {
            'server': 'smtp.gmail.com',
            'port': 465,
            'use_ssl': True,
            'auth_required': True
        }
    }

    @staticmethod
    def get_smtp_config(email):
        """
        根据邮箱地址获取对应的SMTP服务器配置
        :param email: 邮箱地址
        :return: SMTP服务器配置或None
        """
        domain = email.split('@')[-1].lower()
        return EmailService.SMTP_SERVERS.get(domain)

    @staticmethod
    def is_valid_email(email):
        """
        验证邮箱格式是否正确
        :param email: 邮箱地址
        :return: bool
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def send_email(recipient, subject, content, attachments=None):
        """
        发送邮件的通用方法
        :param recipient: 收件人邮箱
        :param subject: 邮件主题
        :param content: 邮件内容
        :param attachments: 附件列表，每个元素是文件路径
        :return: (success, message) 元组
        """
        try:
            # 验证邮箱格式
            if not EmailService.is_valid_email(recipient):
                return False, "收件人邮箱格式不正确"

            # 获取系统邮箱配置
            system_email = current_app.config.get('MAIL_USERNAME')
            email_password = current_app.config.get('MAIL_PASSWORD')

            if not system_email or not email_password:
                current_app.logger.error("邮箱配置缺失")
                return False, "系统邮箱配置错误"

            # 创建邮件对象
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = system_email
            msg['To'] = recipient

            # 添加邮件正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            # 添加附件
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            attachment = MIMEApplication(f.read())
                            attachment.add_header(
                                'Content-Disposition',
                                'attachment',
                                filename=os.path.basename(file_path)
                            )
                            msg.attach(attachment)

            # 获取SMTP配置
            smtp_config = EmailService.get_smtp_config(system_email)
            if not smtp_config:
                current_app.logger.error(f"不支持的邮箱服务器: {system_email}")
                return False, "不支持的邮箱服务器"

            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 使用SSL连接SMTP服务器
            with smtplib.SMTP_SSL(
                smtp_config['server'], 
                smtp_config['port'],
                context=context,
                timeout=10
            ) as server:
                server.set_debuglevel(1)
                
                try:
                    # 登录验证
                    server.login(system_email, email_password)
                except smtplib.SMTPAuthenticationError as auth_error:
                    current_app.logger.error(f"邮箱认证失败: {str(auth_error)}")
                    if '163.com' in system_email:
                        return False, "邮箱认证失败，请确保使用的是163邮箱的授权码而不是登录密码"
                    return False, "邮箱认证失败，请检查授权码是否正确"
                
                # 发送邮件
                server.send_message(msg)
                current_app.logger.info(f"邮件已发送至: {recipient}")

            return True, "邮件发送成功"

        except smtplib.SMTPException as smtp_error:
            error_msg = f"SMTP错误: {str(smtp_error)}"
            current_app.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"发送邮件错误: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def send_reset_code_email(to_email, reset_code):
        """
        发送重置密码验证码邮件
        :param to_email: 收件人邮箱
        :param reset_code: 验证码
        :return: (success, message) 元组
        """
        subject = '重置密码验证码'
        content = f'''您好！

您正在重置密码，您的验证码是：{reset_code}

该验证码将在30分钟后过期。如果这不是您本人的操作，请忽略此邮件。

此致
人事管理系统团队'''

        return EmailService.send_email(to_email, subject, content)
