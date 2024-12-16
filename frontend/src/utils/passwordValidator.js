/**
 * 密码强度验证工具
 */

// 密码强度规则
const PASSWORD_RULES = {
  minLength: 8,
  maxLength: 20,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true
};

/**
 * 验证密码强度
 * @param {string} password - 待验证的密码
 * @returns {Object} 验证结果，包含是否通过和错误信息
 */
export const validatePasswordStrength = (password) => {
  const errors = [];

  // 检查长度
  if (password.length < PASSWORD_RULES.minLength) {
    errors.push(`密码长度不能少于${PASSWORD_RULES.minLength}个字符`);
  }
  if (password.length > PASSWORD_RULES.maxLength) {
    errors.push(`密码长度不能超过${PASSWORD_RULES.maxLength}个字符`);
  }

  // 检查大写字母
  if (PASSWORD_RULES.requireUppercase && !/[A-Z]/.test(password)) {
    errors.push('密码必须包含至少一个大写字母');
  }

  // 检查小写字母
  if (PASSWORD_RULES.requireLowercase && !/[a-z]/.test(password)) {
    errors.push('密码必须包含至少一个小写字母');
  }

  // 检查数字
  if (PASSWORD_RULES.requireNumbers && !/\d/.test(password)) {
    errors.push('密码必须包含至少一个数字');
  }

  // 检查特殊字符
  if (PASSWORD_RULES.requireSpecialChars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('密码必须包含至少一个特殊字符 (!@#$%^&*(),.?":{}|<>)');
  }

  return {
    isValid: errors.length === 0,
    errors: errors
  };
};

/**
 * 获取密码强度等级
 * @param {string} password - 待检查的密码
 * @returns {number} 强度等级（1-4）
 */
export const getPasswordStrength = (password) => {
  let strength = 0;

  // 基础长度检查
  if (password.length >= 8) strength++;

  // 检查复杂性
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;

  return strength;
};
